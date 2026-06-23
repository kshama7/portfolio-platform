from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from cachetools import TTLCache

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.metrics import market_data_cache_hits_total, market_data_fetch_total

log = get_logger(__name__)


class MarketDataError(RuntimeError):
    pass


class MarketDataFetcher:
    """Fetches OHLCV data via yfinance with TTL cache. Falls back to bundled CSV."""

    def __init__(self) -> None:
        settings = get_settings()
        self._cache: TTLCache[tuple, pd.DataFrame] = TTLCache(
            maxsize=64, ttl=settings.yf_cache_ttl_seconds
        )
        self._local_close_path: Path = settings.data_dir / "close_prices.csv"
        self._local_close: pd.DataFrame | None = None

    def _load_local(self) -> pd.DataFrame:
        if self._local_close is None:
            df = pd.read_csv(self._local_close_path, parse_dates=["date"])
            df = df.set_index("date").sort_index()
            self._local_close = df
        return self._local_close

    async def get_close_prices(
        self,
        tickers: list[str],
        start: date,
        end: date,
        source: str = "auto",
    ) -> pd.DataFrame:
        """Return wide DataFrame of close prices, indexed by date, columns = tickers."""
        key = (tuple(sorted(tickers)), start.isoformat(), end.isoformat(), source)
        if key in self._cache:
            market_data_cache_hits_total.labels(source=source).inc()
            return self._cache[key].copy()

        if source == "local" or source == "auto":
            try:
                df = await asyncio.to_thread(self._from_local, tickers, start, end)
                if not df.empty:
                    market_data_fetch_total.labels(source="local", status="ok").inc()
                    self._cache[key] = df
                    return df.copy()
            except Exception as exc:  # noqa: BLE001
                log.warning("local_fetch_failed", error=str(exc))
                market_data_fetch_total.labels(source="local", status="error").inc()

        if source == "local":
            raise MarketDataError("no local data for requested tickers/range")

        try:
            df = await asyncio.to_thread(self._from_yfinance, tickers, start, end)
            market_data_fetch_total.labels(source="yfinance", status="ok").inc()
            self._cache[key] = df
            return df.copy()
        except Exception as exc:
            market_data_fetch_total.labels(source="yfinance", status="error").inc()
            raise MarketDataError(f"yfinance fetch failed: {exc}") from exc

    def _from_local(self, tickers: list[str], start: date, end: date) -> pd.DataFrame:
        local = self._load_local()
        available = [t for t in tickers if t in local.columns]
        if not available:
            return pd.DataFrame()
        mask = (local.index >= pd.Timestamp(start)) & (local.index <= pd.Timestamp(end))
        df = local.loc[mask, available].dropna(how="all")
        if df.empty:
            return df
        return df

    def _from_yfinance(self, tickers: list[str], start: date, end: date) -> pd.DataFrame:
        import yfinance as yf  # lazy import

        log.info("yf_download", tickers=tickers, start=str(start), end=str(end))
        end_inclusive = end + timedelta(days=1)
        raw = yf.download(
            tickers=tickers,
            start=start.isoformat(),
            end=end_inclusive.isoformat(),
            auto_adjust=True,
            progress=False,
            threads=True,
            group_by="ticker",
        )
        if raw is None or raw.empty:
            raise MarketDataError("empty response from yfinance")

        if isinstance(raw.columns, pd.MultiIndex):
            closes = {}
            for t in tickers:
                if (t, "Close") in raw.columns:
                    closes[t] = raw[(t, "Close")]
            df = pd.DataFrame(closes)
        else:
            df = raw[["Close"]].rename(columns={"Close": tickers[0]})

        df.index = pd.to_datetime(df.index)
        df = df.dropna(how="all").sort_index()
        return df


_fetcher: MarketDataFetcher | None = None


def get_fetcher() -> MarketDataFetcher:
    global _fetcher
    if _fetcher is None:
        _fetcher = MarketDataFetcher()
    return _fetcher


def parse_iso_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()
