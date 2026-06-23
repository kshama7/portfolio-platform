from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BacktestMetrics:
    total_return_pct: float
    annualized_return_pct: float
    annualized_volatility_pct: float
    sharpe: float
    sortino: float
    max_drawdown_pct: float
    calmar: float
    win_rate_pct: float
    n_periods: int


@dataclass(frozen=True)
class BacktestResult:
    strategy: str
    dates: list[str]
    equity_curve: list[float]
    daily_returns: list[float]
    drawdown: list[float]
    metrics: BacktestMetrics


def run_backtest(
    prices: pd.DataFrame,
    weights: dict[str, float] | pd.DataFrame,
    strategy: str,
    initial_capital: float = 100_000.0,
    rebalance: str = "monthly",
) -> BacktestResult:
    """Backtest using either a static weight vector or a daily weight DataFrame.

    Static weights: rebalanced at the configured frequency (monthly/never).
    DataFrame weights: used as-is (daily rebalance based on the table).
    """
    aligned = prices.dropna(axis=0, how="any").sort_index()
    if aligned.empty:
        raise ValueError("price frame empty after dropping NaNs")

    if isinstance(weights, dict):
        w_series = pd.Series(weights).reindex(aligned.columns).fillna(0.0)
        if w_series.sum() <= 0:
            raise ValueError("weights sum to zero")
        w_series = w_series / w_series.sum()
        weights_df = pd.DataFrame(
            np.tile(w_series.values, (len(aligned), 1)),
            index=aligned.index,
            columns=aligned.columns,
        )
        if rebalance == "monthly":
            month_keys = aligned.index.to_period("M")
            first_of_month = pd.Series(month_keys).drop_duplicates(keep="first").index
            mask = np.zeros(len(aligned), dtype=bool)
            mask[first_of_month] = True
            weights_df.loc[~mask, :] = np.nan
            weights_df = weights_df.ffill()
    else:
        weights_df = weights.reindex(aligned.index).ffill().fillna(0.0)
        weights_df = weights_df.reindex(columns=aligned.columns).fillna(0.0)
        row_sums = weights_df.sum(axis=1).replace(0, np.nan)
        weights_df = weights_df.div(row_sums, axis=0).fillna(0.0)

    daily_returns = aligned.pct_change().fillna(0.0)
    port_returns = (weights_df.shift(1).fillna(0.0) * daily_returns).sum(axis=1)
    equity = (1.0 + port_returns).cumprod() * initial_capital

    metrics = _compute_metrics(port_returns, equity)

    drawdown_series = equity / equity.cummax() - 1.0

    return BacktestResult(
        strategy=strategy,
        dates=[d.strftime("%Y-%m-%d") for d in aligned.index],
        equity_curve=[float(x) for x in equity.values],
        daily_returns=[float(x) for x in port_returns.values],
        drawdown=[float(x) for x in drawdown_series.values],
        metrics=metrics,
    )


def _compute_metrics(returns: pd.Series, equity: pd.Series) -> BacktestMetrics:
    n = len(returns)
    if n == 0:
        return BacktestMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)

    mean = float(returns.mean())
    std = float(returns.std())
    downside = returns[returns < 0]
    downside_std = float(downside.std()) if len(downside) > 0 else 0.0

    ann_return = mean * 252
    ann_vol = std * np.sqrt(252)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0
    sortino = (ann_return / (downside_std * np.sqrt(252))) if downside_std > 0 else 0.0

    peak = equity.cummax()
    dd = equity / peak - 1.0
    max_dd = float(dd.min())
    calmar = ann_return / abs(max_dd) if max_dd < 0 else 0.0

    win_rate = float((returns > 0).sum() / max(1, (returns != 0).sum()))
    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1.0)

    return BacktestMetrics(
        total_return_pct=total_return * 100,
        annualized_return_pct=ann_return * 100,
        annualized_volatility_pct=ann_vol * 100,
        sharpe=sharpe,
        sortino=sortino,
        max_drawdown_pct=max_dd * 100,
        calmar=calmar,
        win_rate_pct=win_rate * 100,
        n_periods=n,
    )
