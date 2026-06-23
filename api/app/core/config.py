from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    env: str = Field(default="dev", description="dev | staging | prod")
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json", description="json | console")

    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    data_dir: Path = Field(default=Path(__file__).resolve().parent.parent / "data_files")

    yf_cache_ttl_seconds: int = Field(default=900)
    yf_max_tickers: int = Field(default=30)
    yf_max_days: int = Field(default=365 * 10)

    optimize_max_assets: int = Field(default=30)
    backtest_max_days: int = Field(default=365 * 5)

    metrics_enabled: bool = Field(default=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
