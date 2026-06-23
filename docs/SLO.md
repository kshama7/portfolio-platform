# Service Level Objectives

## Service surface

User-facing routes under `/api/v1/*`: `optimize`, `backtest`, `universes`,
`strategies`. Health endpoints (`/healthz`, `/readyz`, `/metrics`) are excluded
from SLO calculations — they are probes, not user requests.

## SLOs

| SLI | Objective | Window | Source |
|---|---|---|---|
| Availability | 99.5% non-5xx | 30 days rolling | `http_requests_total` |
| Latency | 95% < 1s | 30 days rolling | `http_request_duration_seconds_bucket` |

## Error budget

- **Availability budget:** 0.5% of requests per 30 days = **~3h 36m** of full outage equivalent.
- **Latency budget:** 5% of requests can exceed 1s.

## Burn-rate alerts

Multi-window, multi-burn-rate alerting per [Google SRE Workbook](https://sre.google/workbook/alerting-on-slos/):

| Alert | Burn rate | Long window | Short window | Severity | Budget consumed |
|---|---|---|---|---|---|
| `APIErrorBudgetBurnFast` | 14.4× | 1h | 5m | page | 2% in 1h |
| `APIErrorBudgetBurnSlow` | 6× | 6h | 5m | ticket | 5% in 6h |

## Why these numbers

- **99.5% availability** is realistic for a single-region demo deployment on Fly.io. We do not need 99.9% for a non-money-handling portfolio optimization service.
- **1s p95** is comfortable for in-process classical optimizers and DRL replays over a 20-stock universe. Anything above means we're hitting yfinance live or the optimizer is misconfigured.
- **30-day rolling window** matches the typical hiring/review cadence and gives enough signal for burn-rate alerts to be meaningful.

## What is *not* covered by SLO

- Public marketing pages (the Next.js home page) — best-effort.
- `/metrics` endpoint — scraped, not user-served.
- yfinance upstream — out of our control; we treat its failures as 502 to the user and they *do* count against the SLO.
