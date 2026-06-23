from fastapi import APIRouter, HTTPException

from app.data.universe import UNIVERSES
from app.optimizers import ALL_STRATEGIES
from app.schemas import TickerUniverse

router = APIRouter(prefix="/api/v1", tags=["tickers"])

_DESCRIPTIONS = {
    "NIFTY50": "NIFTY 50 — India's benchmark equity index.",
    "DOW30": "Dow Jones Industrial Average constituents.",
    "DRL_NIFTY20": "20-stock NIFTY subset used to train the bundled DRL agents.",
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
