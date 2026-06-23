from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

REGISTRY = CollectorRegistry()

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status"],
    registry=REGISTRY,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=REGISTRY,
)

http_requests_in_flight = Gauge(
    "http_requests_in_flight",
    "Number of in-flight HTTP requests",
    registry=REGISTRY,
)

optimize_runs_total = Counter(
    "optimize_runs_total",
    "Total portfolio optimization runs",
    ["strategy", "status"],
    registry=REGISTRY,
)

optimize_duration_seconds = Histogram(
    "optimize_duration_seconds",
    "Optimization compute time (seconds)",
    ["strategy"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=REGISTRY,
)

backtest_duration_seconds = Histogram(
    "backtest_duration_seconds",
    "Backtest compute time (seconds)",
    ["strategy"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=REGISTRY,
)

market_data_fetch_total = Counter(
    "market_data_fetch_total",
    "Market data fetches",
    ["source", "status"],
    registry=REGISTRY,
)

market_data_cache_hits_total = Counter(
    "market_data_cache_hits_total",
    "Market data cache hits",
    ["source"],
    registry=REGISTRY,
)

build_info = Gauge(
    "portfolio_platform_build_info",
    "Static build info (always 1)",
    ["version", "env"],
    registry=REGISTRY,
)


def set_build_info(version: str, env: str) -> None:
    build_info.labels(version=version, env=env).set(1)
