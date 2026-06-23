from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.metrics import set_build_info
from app.core.middleware import MetricsMiddleware, RequestContextMiddleware
from app.routers import backtest, health, metrics, optimize, tickers


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    set_build_info(version=__version__, env=settings.env)
    log = get_logger("startup")
    log.info("starting", version=__version__, env=settings.env)

    from app.data.fetcher import get_fetcher

    fetcher = get_fetcher()
    fetcher._load_local()
    log.info("local_data_loaded", rows=len(fetcher._local_close))
    yield
    log.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Portfolio Platform API",
        description="Production-grade portfolio optimization & backtesting service.",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(RequestContextMiddleware)

    app.include_router(health.router)
    app.include_router(metrics.router)
    app.include_router(tickers.router)
    app.include_router(optimize.router)
    app.include_router(backtest.router)

    @app.get("/", include_in_schema=False)
    async def root() -> JSONResponse:
        return JSONResponse(
            {
                "service": "portfolio-platform-api",
                "version": __version__,
                "docs": "/docs",
                "health": "/healthz",
                "metrics": "/metrics",
            }
        )

    return app


app = create_app()
