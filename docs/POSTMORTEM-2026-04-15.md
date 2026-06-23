# Postmortem — 2026-04-15 — yfinance regression caused 12% error rate on /api/v1/optimize

**Status:** resolved
**Authors:** kshama
**Date:** 2026-04-15
**Duration:** 47 minutes (14:12 UTC → 14:59 UTC)
**Severity:** SEV-2
**User impact:** ~38% of `/api/v1/optimize` requests using `data_source: auto` returned a 502 for 47 minutes.

> *Practice postmortem for the project. The platform is real, the incident is illustrative — written to show that postmortem discipline is in place.*

## Summary

A breaking change in `yfinance==0.2.51` removed the `auto_adjust` keyword argument from `download()`. We pulled this version in via a transitive dependency on Mon 04-14 21:30 UTC during an unrelated lockfile refresh, but the impact only surfaced after the local cache TTL expired at 14:12 UTC the next day, because cached responses had kept the live path warm.

## Timeline (UTC)

| Time | Event |
|---|---|
| Mon 21:30 | PR #214 merged: lockfile bump; yfinance 0.2.50 → 0.2.51. CI was green (no yfinance-touching tests in CI; local fallback path served them). |
| Tue 14:12 | First 5m window with error rate > 5% on `/api/v1/optimize`. |
| Tue 14:13 | `APIErrorRateHigh` fires (5 min `for` clause); pages on-call. |
| Tue 14:18 | On-call ack. Dashboard shows error rate climbing, request rate stable, optimizer compute time normal. |
| Tue 14:24 | Pod logs filtered to `event=optimize_failed`: stack trace shows `TypeError: download() got an unexpected keyword argument 'auto_adjust'`. |
| Tue 14:31 | Decided to roll back lockfile rather than push a fix forward — faster MTTR. |
| Tue 14:42 | `argocd app rollback portfolio-platform --revision 0.1.4` triggered. |
| Tue 14:52 | Rollback rollout finished. Error rate falling. |
| Tue 14:59 | Error rate back below 0.1%. Page resolved. |

## Root cause

`yfinance==0.2.51` was released with a breaking change to the `download()` signature. Our `MarketDataFetcher._from_yfinance` passes `auto_adjust=True`, which is now invalid. The function raises `TypeError`, which our handler maps to a 502 response.

## What went well
- Burn-rate alert fired on the *right* signal (sustained 5xx) rather than a false-positive single-request spike.
- Dashboard had the symptom on the front page (5xx stat).
- ArgoCD rollback was one command, completed in under 10 minutes.
- Postmortem assigned same-day.

## What went poorly
- We had no CI job that exercises the live yfinance path. The dep bump merged green and broke production.
- The local-fallback path (which served traffic during the 17-hour gap) masked the underlying issue. Logs would have flagged it earlier had we been alerting on `market_data_fetch_total{source="yfinance",status="error"}`.

## Action items

| Owner | Due | Action |
|---|---|---|
| kshama | 2026-04-22 | Pin yfinance version exactly in `pyproject.toml` and add a Renovate label that requires a manual ✅ for bumps. |
| kshama | 2026-04-22 | Add a `nightly-live-data.yml` GitHub Action that hits yfinance end-to-end with one ticker; alerts on failure. |
| kshama | 2026-04-29 | New Prometheus alert: `MarketDataFetchErrorRateHigh` on `market_data_fetch_total{status="error",source="yfinance"} / total > 5%` for 10m. Add to runbook. |
| kshama | 2026-04-29 | Update `MarketDataFetcher` to capture and log the yfinance version on each fetch, surfaced in `event=yf_download`. |

## Detection time → mitigation time

- **Time to detect (TTD):** 1 minute (alert fired on first 5-min window over threshold).
- **Time to mitigate (TTM):** 41 minutes from ack (14:18 → 14:59).
- **Time to recover (TTR):** 47 minutes total.

The TTM is too high; the bulk of it was diagnosis. Pinning the dep + adding the upstream alert should cut TTM in half for the next occurrence by removing the "guess which dep" step.
