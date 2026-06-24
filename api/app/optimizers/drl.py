from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.core.config import get_settings
from app.optimizers.base import OptimizerResult


def _models_dir() -> Path:
    return get_settings().data_dir / "models"


# ────────────────────────────────────────────────────────────────────────────
# Legacy DRL replay (NIFTY-20, precomputed action CSVs from undergrad capstone)
# Kept for completeness so the NIFTY backtest still works.
# ────────────────────────────────────────────────────────────────────────────


@lru_cache(maxsize=8)
def _load_action_sequence(filename: str) -> pd.DataFrame:
    """Load a precomputed DRL action sequence (legacy NIFTY-20 only)."""
    path: Path = get_settings().data_dir / filename
    df = pd.read_csv(path)
    start = pd.to_datetime(df["date"].iloc[0])
    df = df.drop(columns=["date"])
    df.index = pd.bdate_range(start=start, periods=len(df))
    df.index.name = "date"
    return df


class DRLReplayOptimizer:
    """Replay precomputed daily weight trajectory (legacy NIFTY-20 agents)."""

    def __init__(self, strategy: str, filename: str) -> None:
        self.name = strategy
        self._filename = filename

    def fit(self, prices: pd.DataFrame) -> OptimizerResult:
        sequence = _load_action_sequence(self._filename)
        common = sequence.index.intersection(prices.index)
        row = sequence.loc[common[-1]] if len(common) else sequence.iloc[-1]
        weights = {c: float(row[c]) for c in sequence.columns if c in prices.columns}
        if not weights:
            weights = {c: float(row[c]) for c in sequence.columns}
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        return OptimizerResult(
            strategy=self.name,
            weights=weights,
            expected_annual_return=None,
            expected_annual_volatility=None,
            expected_sharpe=None,
            notes="DRL replay from precomputed action sequence (NIFTY-20 only).",
        )

    def action_sequence(self) -> pd.DataFrame:
        return _load_action_sequence(self._filename)


# ────────────────────────────────────────────────────────────────────────────
# Real-time ONNX DRL inference (US universes — PPO, A2C trained 2015-2022)
# ────────────────────────────────────────────────────────────────────────────


@lru_cache(maxsize=8)
def _load_onnx_policy(model_id: str) -> tuple[Any, dict]:
    """Load an ONNX policy + its metadata. Cached after first call."""
    import onnxruntime as ort  # lazy: only the LiveDRL path needs this

    onnx_path = _models_dir() / f"{model_id}.onnx"
    meta_path = _models_dir() / f"{model_id}_meta.json"

    if not onnx_path.exists():
        raise FileNotFoundError(f"trained model not found: {model_id}")

    sess = ort.InferenceSession(onnx_path.as_posix(), providers=["CPUExecutionProvider"])
    meta = json.loads(meta_path.read_text())
    return sess, meta


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


class LiveDRLOptimizer:
    """Daily-rebalance DRL policy: load ONNX, infer on rolling observations.

    For each trading day after the warmup period, build the observation (last
    `lookback` days of returns, flattened), forward-pass through the trained
    policy, softmax the action vector, record as the day's weights. The result
    is a (n_days × n_assets) DataFrame the backtest engine can consume the
    same way it consumes the legacy NIFTY replay.
    """

    def __init__(self, strategy: str, model_id: str) -> None:
        self.name = strategy
        self.model_id = model_id

    def _build_sequence(self, prices: pd.DataFrame) -> pd.DataFrame:
        sess, meta = _load_onnx_policy(self.model_id)
        trained_tickers: list[str] = list(meta["tickers"])
        lookback: int = int(meta["lookback"])

        usable = [t for t in trained_tickers if t in prices.columns]
        if len(usable) != len(trained_tickers):
            missing = sorted(set(trained_tickers) - set(usable))
            raise ValueError(
                f"DRL agent {self.model_id} was trained on {len(trained_tickers)} "
                f"tickers; missing from input: {missing[:5]}"
                + ("…" if len(missing) > 5 else "")
            )

        # Align to the agent's expected ticker order
        ordered = prices[trained_tickers].dropna()
        returns = ordered.pct_change().fillna(0.0).clip(-1.0, 1.0)

        ret_arr = returns.values.astype(np.float32)
        n_days, n_assets = ret_arr.shape

        if n_days < lookback + 1:
            raise ValueError(
                f"need at least {lookback + 1} days, got {n_days}"
            )

        input_name = sess.get_inputs()[0].name
        weights_per_day = np.zeros_like(ret_arr)
        uniform = np.full(n_assets, 1.0 / n_assets, dtype=np.float32)
        weights_per_day[:lookback] = uniform

        for t in range(lookback, n_days):
            obs = ret_arr[t - lookback : t].reshape(1, -1)
            action = sess.run(None, {input_name: obs})[0][0]
            weights_per_day[t] = _softmax(action.astype(np.float32))

        return pd.DataFrame(weights_per_day, index=ordered.index, columns=trained_tickers)

    def action_sequence(self, prices: pd.DataFrame) -> pd.DataFrame:
        return self._build_sequence(prices)

    def fit(self, prices: pd.DataFrame) -> OptimizerResult:
        seq = self._build_sequence(prices)
        last = seq.iloc[-1]
        weights = {t: float(last[t]) for t in seq.columns}
        sess, meta = _load_onnx_policy(self.model_id)
        return OptimizerResult(
            strategy=self.name,
            weights=weights,
            expected_annual_return=None,
            expected_annual_volatility=None,
            expected_sharpe=None,
            notes=(
                f"Real-time ONNX inference. Trained {meta['timesteps']} timesteps on "
                f"{meta['train_start']}→{meta['train_end']}."
            ),
        )


def list_live_models() -> list[str]:
    """Enumerate trained models available on disk as `<algo>_<universe>`."""
    out: list[str] = []
    for p in _models_dir().glob("*.onnx"):
        out.append(p.stem)
    return sorted(out)
