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
        """Per-ticker fetch via yf.Ticker.history() — more reliable than bulk download.

        yf.download() returns garbage / hits rate limits on some IP ranges;
        Ticker.history() goes through a different endpoint and is far more stable.
        We make N small requests serially; for typical portfolio sizes (≤30) the
        wall-clock cost is acceptable and the result is deterministic.
        """
        import yfinance as yf  # lazy import

        log.info("yf_download", tickers=tickers, start=str(start), end=str(end))
        end_inclusive = end + timedelta(days=1)
        closes: dict[str, pd.Series] = {}
        failures: list[str] = []

        for t in tickers:
            try:
                hist = yf.Ticker(t).history(
                    start=start.isoformat(),
                    end=end_inclusive.isoformat(),
                    auto_adjust=True,
                    raise_errors=False,
                )
                if hist is None or hist.empty or "Close" not in hist.columns:
                    failures.append(t)
                    continue
                series = hist["Close"].copy()
                series.index = pd.to_datetime(series.index).tz_localize(None)
                closes[t] = series
            except Exception as exc:
                log.warning("yf_ticker_failed", ticker=t, error=str(exc))
                failures.append(t)

        if failures:
            log.warning("yf_partial_failure", failed=failures)
        if not closes:
            raise MarketDataError(
                f"yfinance returned no data for any of: {', '.join(tickers)}"
            )

        df = pd.DataFrame(closes)
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
