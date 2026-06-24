from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.core.metrics import optimize_duration_seconds, optimize_runs_total
from app.data.fetcher import MarketDataError, get_fetcher
from app.optimizers import (
    AVAILABLE_LIVE_DRL,
    CLASSICAL_REGISTRY,
    DRL_REPLAY_REGISTRY,
    DRLReplayOptimizer,
    LiveDRLOptimizer,
)
from app.schemas import OptimizeRequest, OptimizeResponse, OptimizeStrategyResult

router = APIRouter(prefix="/api/v1", tags=["optimize"])
log = get_logger(__name__)


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(req: OptimizeRequest) -> OptimizeResponse:
    fetcher = get_fetcher()
    try:
        prices = await fetcher.get_close_prices(
            tickers=req.tickers, start=req.start, end=req.end, source=req.data_source
        )
    except MarketDataError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if prices.empty:
        raise HTTPException(status_code=400, detail="no data for selected tickers/range")
    if len(prices) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"insufficient observations ({len(prices)}); need >= 30 trading days",
        )

    start_total = time.perf_counter()
    results: list[OptimizeStrategyResult] = []

    for strategy in req.strategies:
        per_start = time.perf_counter()
        try:
            optimizer = _build_optimizer(strategy)
            result = optimizer.fit(prices)
            results.append(
                OptimizeStrategyResult(
                    strategy=result.strategy,
                    weights=result.weights,
                    expected_annual_return=result.expected_annual_return,
                    expected_annual_volatility=result.expected_annual_volatility,
                    expected_sharpe=result.expected_sharpe,
                    notes=result.notes,
                )
            )
            optimize_runs_total.labels(strategy=strategy, status="ok").inc()
        except HTTPException:
            raise
        except Exception as exc:
            optimize_runs_total.labels(strategy=strategy, status="error").inc()
            log.exception("optimize_failed", strategy=strategy)
            raise HTTPException(
                status_code=500, detail=f"{strategy} failed: {exc}"
            ) from exc
        finally:
            optimize_duration_seconds.labels(strategy=strategy).observe(
                time.perf_counter() - per_start
            )

    return OptimizeResponse(
        tickers=list(prices.columns),
        start=str(prices.index.min().date()),
        end=str(prices.index.max().date()),
        n_observations=len(prices),
        results=results,
        compute_ms=(time.perf_counter() - start_total) * 1000,
    )


def _build_optimizer(strategy: str):
    if strategy in CLASSICAL_REGISTRY:
        return CLASSICAL_REGISTRY[strategy]()
    if strategy in AVAILABLE_LIVE_DRL:
        return LiveDRLOptimizer(strategy=strategy, model_id=AVAILABLE_LIVE_DRL[strategy])
    if strategy in DRL_REPLAY_REGISTRY:
        return DRLReplayOptimizer(
            strategy=strategy, filename=DRL_REPLAY_REGISTRY[strategy]
        )
    raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
