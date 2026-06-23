from __future__ import annotations

import time

import numpy as np
from fastapi import APIRouter, HTTPException

from app.backtest.engine import _compute_metrics, run_backtest
from app.core.logging import get_logger
from app.core.metrics import backtest_duration_seconds
from app.data.fetcher import MarketDataError, get_fetcher
from app.optimizers import CLASSICAL_REGISTRY, DRL_REGISTRY
from app.optimizers.drl import DRLReplayOptimizer
from app.schemas import (
    BacktestMetricsModel,
    BacktestRequest,
    BacktestResponse,
    BacktestStrategyResult,
    BenchmarkResult,
)

router = APIRouter(prefix="/api/v1", tags=["backtest"])
log = get_logger(__name__)


@router.post("/backtest", response_model=BacktestResponse)
async def backtest(req: BacktestRequest) -> BacktestResponse:
    fetcher = get_fetcher()
    try:
        prices = await fetcher.get_close_prices(
            tickers=req.tickers, start=req.start, end=req.end, source=req.data_source
        )
    except MarketDataError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if prices.empty:
        raise HTTPException(status_code=400, detail="no data for selected tickers/range")

    start_total = time.perf_counter()
    results: list[BacktestStrategyResult] = []

    for strategy in req.strategies:
        per_start = time.perf_counter()
        try:
            if strategy in CLASSICAL_REGISTRY:
                opt = CLASSICAL_REGISTRY[strategy]()
                fit = opt.fit(prices)
                bt = run_backtest(
                    prices=prices,
                    weights=fit.weights,
                    strategy=strategy,
                    initial_capital=req.initial_capital,
                    rebalance=req.rebalance,
                )
                results.append(_to_response(bt, weights=fit.weights, notes=fit.notes))
            elif strategy in DRL_REGISTRY:
                drl = DRLReplayOptimizer(strategy=strategy, filename=DRL_REGISTRY[strategy])
                weights_df = drl.action_sequence()
                bt = run_backtest(
                    prices=prices,
                    weights=weights_df,
                    strategy=strategy,
                    initial_capital=req.initial_capital,
                    rebalance=req.rebalance,
                )
                final_w = {c: float(weights_df.iloc[-1][c]) for c in weights_df.columns}
                results.append(
                    _to_response(
                        bt,
                        weights=final_w,
                        notes="DRL replay using recorded daily weight trajectory.",
                    )
                )
            else:
                raise HTTPException(
                    status_code=400, detail=f"unknown strategy: {strategy}"
                )
        except HTTPException:
            raise
        except Exception as exc:
            log.exception("backtest_failed", strategy=strategy)
            raise HTTPException(
                status_code=500, detail=f"{strategy} failed: {exc}"
            ) from exc
        finally:
            backtest_duration_seconds.labels(strategy=strategy).observe(
                time.perf_counter() - per_start
            )

    # Optional benchmark — buy-and-hold the benchmark ticker over the same window
    benchmark_result: BenchmarkResult | None = None
    if req.benchmark:
        benchmark_result = await _build_benchmark(
            ticker=req.benchmark,
            start=req.start,
            end=req.end,
            initial_capital=req.initial_capital,
        )

    return BacktestResponse(
        tickers=list(prices.columns),
        start=str(prices.index.min().date()),
        end=str(prices.index.max().date()),
        initial_capital=req.initial_capital,
        results=results,
        benchmark=benchmark_result,
        compute_ms=(time.perf_counter() - start_total) * 1000,
    )


async def _build_benchmark(
    ticker: str, start, end, initial_capital: float
) -> BenchmarkResult | None:
    """Fetch the benchmark ticker's price series and compute a buy-and-hold equity curve."""
    fetcher = get_fetcher()
    try:
        bench_df = await fetcher.get_close_prices(
            tickers=[ticker], start=start, end=end, source="yfinance"
        )
    except MarketDataError as exc:
        log.warning("benchmark_fetch_failed", ticker=ticker, error=str(exc))
        return None

    if bench_df.empty or ticker not in bench_df.columns:
        return None

    series = bench_df[ticker].dropna()
    if len(series) < 2:
        return None

    daily_ret = series.pct_change().fillna(0.0)
    equity = (1.0 + daily_ret).cumprod() * initial_capital
    metrics = _compute_metrics(daily_ret, equity)

    return BenchmarkResult(
        ticker=ticker,
        dates=[d.strftime("%Y-%m-%d") for d in series.index],
        equity_curve=[float(x) for x in equity.values],
        metrics=BacktestMetricsModel(**metrics.__dict__),
    )


def _to_response(bt, weights: dict[str, float], notes: str | None) -> BacktestStrategyResult:
    return BacktestStrategyResult(
        strategy=bt.strategy,
        dates=bt.dates,
        equity_curve=bt.equity_curve,
        daily_returns=bt.daily_returns,
        drawdown=bt.drawdown,
        metrics=BacktestMetricsModel(**bt.metrics.__dict__),
        weights=weights,
        notes=notes,
    )
