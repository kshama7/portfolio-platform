from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", version=__version__, env=settings.env)


@router.get("/readyz", response_model=HealthResponse)
async def readyz() -> HealthResponse:
    from app.data.fetcher import get_fetcher

    fetcher = get_fetcher()
    fetcher._load_local()  # surface any data-load errors immediately

    settings = get_settings()
    return HealthResponse(status="ready", version=__version__, env=settings.env)
