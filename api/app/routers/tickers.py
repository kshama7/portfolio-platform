from fastapi import APIRouter, HTTPException

from app.data.universe import BENCHMARKS, UNIVERSES
from app.optimizers import ALL_STRATEGIES
from app.schemas import TickerUniverse

router = APIRouter(prefix="/api/v1", tags=["tickers"])

_DESCRIPTIONS = {
    "DOW30": "Dow Jones Industrial Average — 30 US large caps. Good starter universe.",
    "MAG7": "The Magnificent 7 — AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA.",
    "FAANG": "Classic FAANG: META, AAPL, AMZN, NFLX, GOOGL.",
    "TECH_GIANTS": "Top US tech mega-caps.",
    "NASDAQ100_TOP": "50 most-liquid NASDAQ-100 names.",
    "SP100": "S&P 100 — broad large-cap US exposure.",
    "DIVIDEND_KINGS": "Dividend Aristocrats subset — income-focused.",
    "NIFTY50": "NIFTY 50 — India's benchmark equity index (offline data bundled).",
    "DRL_NIFTY20": "20-stock NIFTY subset the bundled DRL agents were trained on.",
}


@router.get("/universes", response_model=list[TickerUniverse])
async def list_universes() -> list[TickerUniverse]:
    return [
        TickerUniverse(name=k, tickers=v, description=_DESCRIPTIONS.get(k, ""))
        for k, v in UNIVERSES.items()
    ]


@router.get("/universes/{name}", response_model=TickerUniverse)
async def get_universe(name: str) -> TickerUniverse:
    if name not in UNIVERSES:
        raise HTTPException(status_code=404, detail=f"unknown universe: {name}")
    return TickerUniverse(
        name=name, tickers=UNIVERSES[name], description=_DESCRIPTIONS.get(name, "")
    )


@router.get("/strategies", response_model=list[str])
async def list_strategies() -> list[str]:
    return ALL_STRATEGIES


@router.get("/benchmarks", response_model=dict[str, str])
async def list_benchmarks() -> dict[str, str]:
    """Return supported benchmark tickers → human descriptions."""
    return BENCHMARKS
