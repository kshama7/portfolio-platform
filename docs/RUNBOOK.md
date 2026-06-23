# Runbook

Per-alert playbooks. Each section is named to match the `alertname` in
`observability/prometheus/alerts.yaml`.

---

## APIErrorBudgetBurnFast

**Page severity. Acknowledge within 5 minutes.**

### What it means
We're burning 2% of the 30-day error budget every hour. At this rate, the
budget is exhausted in 50 hours.

### First steps
1. Acknowledge the page.
2. Open the Grafana dashboard:
   `https://grafana.kshama.dev/d/portfolio-platform/portfolio-platform-service-overview`
   - Look at **5xx error rate** stat — is it concentrated on one route?
   - Look at **Optimizer compute time** — is one strategy slow/erroring?
3. `kubectl -n portfolio-platform logs -l app.kubernetes.io/component=api --tail=200 | jq '.'`
   Filter by `level=error`.

### Likely causes
- **yfinance upstream down** → look for `market_data_fetch_total{status="error"}` spike.
  - Mitigation: the API automatically falls back to `local` source for tickers in the bundled dataset. Confirm fallback is firing.
- **Optimizer regression** → recent deploy introduced a math error. Check ArgoCD for the most recent sync.
  - Mitigation: `argocd app rollback portfolio-platform`.
- **Resource exhaustion** → CPU throttling under HPA min. Check `kube_pod_status_phase`.
  - Mitigation: bump `api.autoscaling.minReplicas` in the active values file.

### Rollback
```
argocd app rollback portfolio-platform --revision <previous>
```

### Postmortem
Required if the burn-rate alert was true positive *and* lasted > 30 minutes.

---

## APIErrorBudgetBurnSlow

**Ticket severity. Triage within one business day.**

### What it means
Sustained 6× burn rate over 6 hours — not enough to page, but enough that we
will exhaust the budget within 5 days if it continues.

### First steps
Same dashboard, same logs. Difference: there is time to be thorough rather
than reactive. Pair with a teammate, file a tracking issue.

---

## APIDown

**Page severity. Acknowledge within 5 minutes.**

### What it means
Prometheus has not been able to scrape `/metrics` for 1 minute.

### First steps
1. `kubectl -n portfolio-platform get pods -l app.kubernetes.io/component=api`
2. `kubectl -n portfolio-platform describe pod <pod>` — look for OOMKilled, CrashLoopBackOff, ImagePullBackOff.
3. `kubectl -n portfolio-platform logs <pod> --previous` if the pod is restarting.

### Likely causes
- Image pull failure (new tag was pushed with wrong digest) → roll back via ArgoCD.
- OOMKilled → bump `api.resources.limits.memory`.
- Liveness probe regression → check `/healthz` returns 200 from inside the pod with `kubectl exec`.

---

## APIHighLatency

**Ticket severity.**

p95 > 2s on `/api/v1/optimize` or `/api/v1/backtest` for 10 minutes.

### Investigation
- `optimize_duration_seconds` histogram by strategy — find the offender.
- Did the user submit an unusually large ticker universe? Check request log for `tickers` count.
- yfinance latency from outside the cluster — try `curl -w '%{time_total}' https://query1.finance.yahoo.com/...`.

### Mitigation
- Short-term: increase HPA `targetCPUUtilizationPercentage` *down* (more aggressive scale-up).
- Medium-term: cache result of identical (tickers, start, end, strategy) keys for ~5 minutes.

---

## APIErrorRateHigh

**Page severity.**

5xx rate > 5% for 5 minutes on any route.

### First steps
Same as `APIErrorBudgetBurnFast`. The two will usually fire together; if only
this fires, the issue is sharp and recent (< 5 min) rather than sustained.

---

## OptimizerFailureRateHigh

**Ticket severity.**

One specific optimization strategy is failing > 10% of runs.

### Investigation
- Filter logs to `strategy=<name>` and `event=optimize_failed`.
- Check the most recent change to `app/optimizers/` in `git log`.
- Replay the failing request locally with `pytest tests/test_optimize.py::<closest_test> -k <strategy>`.

### Mitigation
- If the failure is in one DRL strategy, disable it from the public strategy list temporarily by removing it from `app/optimizers/__init__.py:DRL_REGISTRY` and shipping a hotfix.
- Open a tracking issue with a representative payload from the access log.

---

## On-call expectations

- Page acknowledged in **5 minutes** during US business hours, **15 minutes** otherwise.
- Mitigation in place within **30 minutes** (need not be a full fix).
- Postmortem within **5 business days** for every user-visible page that confirmed-true.
