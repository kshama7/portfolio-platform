# Portfolio Platform

> **A production ML service that optimizes US-stock portfolios — and an SRE platform wrapped around it.** Five deep-RL agents (PPO, DDPG, A2C, SAC, TD3) trained on US equities, plus four classical optimizers (Markowitz, Min-Variance, Max-Sharpe, HRP), served behind a FastAPI inference API and a Next.js dashboard, with Helm/ArgoCD GitOps, Prometheus SLOs, and a runbook.

[![live demo](https://img.shields.io/badge/▶_live_demo-try_it-22d3ee)](https://portfolio-web-iu0h.onrender.com)
[![api docs](https://img.shields.io/badge/api-swagger-22d3ee)](https://portfolio-api-9exp.onrender.com/docs)
[![SLO](https://img.shields.io/badge/SLO-99.5%25%20%E2%80%A2%20p95%20%3C%201s-22d3ee)](docs/SLO.md)
[![helm](https://img.shields.io/badge/helm-v3.17-0f1689)](infra/helm/portfolio-platform)
[![argocd](https://img.shields.io/badge/argocd-gitops-ef7b4d)](infra/argocd)

🔗 **[Open the live dashboard →](https://portfolio-web-iu0h.onrender.com)** · [API docs](https://portfolio-api-9exp.onrender.com/docs) · [Prometheus metrics](https://portfolio-api-9exp.onrender.com/metrics)

---

## The headline result

I trained five deep reinforcement-learning agents to allocate a portfolio across the Magnificent 7 (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA), using only US price data through 2022, then backtested them out-of-sample on **2023–2024**:

| Strategy | Sharpe | Total return | Max drawdown | $100k became | Diversification |
|---|---:|---:|---:|---:|---|
| **SAC** (deep RL) | **2.95** | +325% | −16.6% | **$425,510** | 7 / 7 stocks |
| A2C (deep RL) | 2.56 | +284% | **−14.3%** | $384,260 | 6 / 7 stocks |
| PPO (deep RL) | 2.55 | +249% | −18.6% | $349,163 | 7 / 7 stocks |
| TD3 (deep RL) | 2.50 | +235% | −16.0% | $334,947 | 7 / 7 stocks |
| DDPG (deep RL) | 2.06 | +185% | −20.6% | $285,434 | 5 / 7 stocks |
| Max Sharpe (Markowitz) | 2.82 | +620% | −19.6% | $720,242 | 2 / 7 (concentrated) |
| **S&P 500 (SPY)** | 1.86 | +58% | −10.0% | $158,243 | benchmark |

**The SAC agent delivered the best risk-adjusted return** (Sharpe 2.95) and beat the S&P 500 by **5.6×** while spreading risk across all seven names — where the classical Max-Sharpe optimizer just dumped everything into NVDA. Every RL agent beat the index by 3–6×.

> These are real out-of-sample backtests on live Yahoo Finance data, reproducible with `scripts/train_drl.py`. Not investment advice; past performance does not predict future returns.

---

## Why this project exists

I'm a Site Reliability Engineer ([IBM — EASeJ + IBM MQ](https://www.linkedin.com/in/kshama-bhatt-28941724a)) heading to UPenn for a Masters in Fall 2026. My day job is OpenShift / ArgoCD / Prometheus / SOC2 and leading Sev1/Sev2 on-call. My undergraduate capstone was deep RL for portfolio optimization — but it lived in Jupyter notebooks.

This repo is the bridge: I took that ML research and rebuilt it as a service I'd be comfortable running on-call. **The optimizer is the payload; the production engineering around it is the point.**

What it demonstrates end-to-end:

- **A real ML lifecycle** — train (Stable-Baselines3) → export (ONNX) → serve (FastAPI + onnxruntime, no torch in the runtime image) → backtest → measure (Prometheus). Five RL algorithms across three policy architectures (on-policy, deterministic-actor, stochastic-actor), all exported to a single inference path.
- **SRE rigor around an ML service** — Helm chart (HPA, PDB, NetworkPolicy, ServiceMonitor), ArgoCD ApplicationSet across dev/staging/prod, multi-window multi-burn-rate SLO alerts per the Google SRE Workbook, a per-alert runbook, and a practice post-mortem.
- **CI/CD with the right rails** — lint → test → Trivy → multi-arch build → GHCR → deploy.

---

## What you can do with it

1. Pick a universe (Dow 30, MAG7, FAANG, S&P 100, …) or **type any US tickers** — `AAPL, COIN, PLTR`, sector ETFs, anything Yahoo Finance supports.
2. Choose strategies: four classical optimizers and, for universes with trained agents, five deep-RL policies.
3. Set a date window (1Y / 3Y / 5Y / 10Y presets) and a benchmark (SPY, QQQ, DIA, …).
4. Get a full backtest: equity curve vs benchmark, drawdown, per-strategy Sharpe / Sortino / Calmar / max-DD, and a **dollar-by-dollar allocation card** telling you how to split your capital.

---

## Architecture

![Architecture](docs/architecture.svg)

```
portfolio-platform/
├── api/                  FastAPI · classical + DRL optimizers · /metrics · /healthz
│   ├── app/optimizers/   Markowitz, Min-Vol, Max-Sharpe, HRP + ONNX DRL inference
│   ├── app/data_files/models/   10 trained ONNX policies (5 algos × 2 universes)
│   └── scripts/train_drl.py     reproducible SB3 training → ONNX export
├── web/                  Next.js 15 · Tailwind · Recharts · runtime API proxy
├── infra/
│   ├── helm/             Helm chart · HPA · PDB · NetworkPolicy · ServiceMonitor
│   ├── argocd/           Application · ApplicationSet · AppProject (dev/staging/prod)
│   ├── terraform/        Fly.io + Cloudflare DNS + Grafana Cloud
│   └── fly/              fly.toml per service
├── observability/        Prometheus recording + burn-rate alert rules · Grafana JSON · OpenSLO
├── docs/                 ARCHITECTURE · SLO · RUNBOOK · POSTMORTEM
├── tests/load/           k6 smoke + stress with SLO thresholds
├── tests/chaos/          Chaos Mesh pod-kill + network-latency
└── .github/workflows/    ci · deploy · helm-release · nightly load-test
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the design rationale.

---

## How the DRL works

Each agent sees the last 20 days of returns for every asset (flattened), outputs an action vector, and softmaxes it into portfolio weights. Reward is the next-day log-return minus a transaction-cost penalty on weight churn. Trained offline on 2015–2022 US data with Stable-Baselines3, then exported to ONNX so the **runtime image needs only `onnxruntime`, not torch** (keeps the container ~200 MB and cold-starts fast).

At backtest time the API loads the ONNX policy and runs a fresh forward pass for **every trading day** — this is live inference, not a replay of precomputed weights.

Reproduce any agent from scratch:

```bash
cd api
.venv/bin/python scripts/train_drl.py --universe MAG7 --algo sac --timesteps 20000
# → app/data_files/models/sac_mag7.onnx  +  _meta.json
```

| Family | Strategy | Implementation |
|---|---|---|
| Classical | Equal Weight, Max Sharpe, Min Volatility, HRP | `pyportfolioopt` (Ledoit-Wolf shrinkage, hierarchical risk parity) |
| Deep RL | PPO, A2C, DDPG, SAC, TD3 | Trained with Stable-Baselines3, served via ONNX runtime |

---

## Run it locally

```bash
make up            # full stack: api + web + Prometheus + Grafana (docker-compose)
# → web   http://localhost:3000
# → api   http://localhost:8000/docs
# → prom  http://localhost:9090
# → graf  http://localhost:3001

make test          # 15 pytest tests
make typecheck     # web TypeScript
make lint          # ruff + eslint
make helm-lint     # render + lint the chart
```

---

## Deploy it

```bash
# CI builds + pushes multi-arch images to GHCR on every push to main.
# Public demo runs on Render (render.yaml blueprint).

# Kubernetes (GitOps) — the production path the infra/ directory targets:
kubectl apply -f infra/argocd/project.yaml
kubectl apply -f infra/argocd/applicationset.yaml
```

---

## What I'd build next

- **MLflow** model registry + a nightly GitHub Actions job that retrains and commits ONNX artifacts (reproducibility in CI, not on a laptop).
- **Evidently** drift monitoring with a third SLO on feature-distribution drift.
- Richer observation space (technical indicators, a Sharpe-shaped reward) and **Optuna** hyperparameter search.
- A **canary deploy** with Flagger gated on SLO burn rate.

---

## Acknowledgements

The DRL research originated in two undergraduate projects of mine —
[kshama7/portfolio_optimization_drl](https://github.com/kshama7/portfolio_optimization_drl)
and [kshama7/capstone](https://github.com/kshama7/capstone). Those are preserved as
historical artifacts; this repo is the production rebuild.

— [Kshama Bhatt](https://www.linkedin.com/in/kshama-bhatt-28941724a) · kshama.bhatt7 @ gmail
