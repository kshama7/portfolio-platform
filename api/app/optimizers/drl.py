from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.core.config import get_settings
from app.optimizers.base import OptimizerResult


@lru_cache(maxsize=8)
def _load_action_sequence(filename: str) -> pd.DataFrame:
    """Load a precomputed DRL action sequence.

    The source CSVs from training have a known issue: every row's `date`
    column is the test-period start date. We reconstruct the real index
    by mapping each row to a sequential business day starting from the
    first row's date.
    """
    path: Path = get_settings().data_dir / filename
    df = pd.read_csv(path)
    start = pd.to_datetime(df["date"].iloc[0])
    df = df.drop(columns=["date"])
    df.index = pd.bdate_range(start=start, periods=len(df))
    df.index.name = "date"
    return df


class DRLReplayOptimizer:
    """Replays a precomputed DRL agent action sequence (daily weights).

    The DRL agents (PPO, DDPG, A2C, SAC, TD3) were trained offline; their
    test-period weight trajectories are stored as CSVs. This class exposes
    them through the same Optimizer interface as the classical strategies.
    """

    def __init__(self, strategy: str, filename: str) -> None:
        self.name = strategy
        self._filename = filename

    def fit(self, prices: pd.DataFrame) -> OptimizerResult:
        sequence = _load_action_sequence(self._filename)

        common_dates = sequence.index.intersection(prices.index)
        if len(common_dates) == 0:
            # fall back to the last available action vector
            row = sequence.iloc[-1]
            notes = (
                "DRL replay: requested date range outside test window; "
                "returning last recorded weight vector."
            )
        else:
            row = sequence.loc[common_dates[-1]]
            notes = (
                f"DRL replay: weights from precomputed test-window action "
                f"at {common_dates[-1].date().isoformat()}."
            )

        weights = {col: float(row[col]) for col in sequence.columns if col in prices.columns}
        if not weights:
            weights = {col: float(row[col]) for col in sequence.columns}

        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

        return OptimizerResult(
            strategy=self.name,
            weights=weights,
            expected_annual_return=None,
            expected_annual_volatility=None,
            expected_sharpe=None,
            notes=notes,
        )

    def action_sequence(self) -> pd.DataFrame:
        return _load_action_sequence(self._filename)
