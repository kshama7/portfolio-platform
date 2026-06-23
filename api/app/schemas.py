from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, model_validator


class OptimizeRequest(BaseModel):
    tickers: list[str] = Field(min_length=2, max_length=30)
    start: date
    end: date
    strategies: list[str] = Field(min_length=1, max_length=10)
    data_source: str = Field(default="auto", description="auto | local | yfinance")
    risk_free_rate: float = Field(default=0.02, ge=0, le=0.20)

    @model_validator(mode="after")
    def _validate_dates(self) -> "OptimizeRequest":
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self


class OptimizeStrategyResult(BaseModel):
    strategy: str
    weights: dict[str, float]
    expected_annual_return: float | None = None
    expected_annual_volatility: float | None = None
    expected_sharpe: float | None = None
    notes: str | None = None


class OptimizeResponse(BaseModel):
    tickers: list[str]
    start: str
    end: str
    n_observations: int
    results: list[OptimizeStrategyResult]
    compute_ms: float


class BacktestRequest(BaseModel):
    tickers: list[str] = Field(min_length=2, max_length=30)
    start: date
    end: date
    strategies: list[str] = Field(min_length=1, max_length=10)
    initial_capital: float = Field(default=100_000.0, gt=0)
    rebalance: str = Field(default="monthly", pattern="^(monthly|never)$")
    data_source: str = Field(default="auto")
    benchmark: str | None = Field(
        default=None,
        description="Optional benchmark ticker (e.g. SPY) to overlay on the equity curve",
    )

    @model_validator(mode="after")
    def _validate_dates(self) -> "BacktestRequest":
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self


class BacktestMetricsModel(BaseModel):
    total_return_pct: float
    annualized_return_pct: float
    annualized_volatility_pct: float
    sharpe: float
    sortino: float
    max_drawdown_pct: float
    calmar: float
    win_rate_pct: float
    n_periods: int


class BacktestStrategyResult(BaseModel):
    strategy: str
    dates: list[str]
    equity_curve: list[float]
    daily_returns: list[float]
    drawdown: list[float]
    metrics: BacktestMetricsModel
    weights: dict[str, float] | None = None
    notes: str | None = None


class BenchmarkResult(BaseModel):
    ticker: str
    dates: list[str]
    equity_curve: list[float]
    metrics: BacktestMetricsModel


class BacktestResponse(BaseModel):
    tickers: list[str]
    start: str
    end: str
    initial_capital: float
    results: list[BacktestStrategyResult]
    benchmark: BenchmarkResult | None = None
    compute_ms: float


class HealthResponse(BaseModel):
    status: str
    version: str
    env: str


class TickerUniverse(BaseModel):
    name: str
    tickers: list[str]
    description: str
