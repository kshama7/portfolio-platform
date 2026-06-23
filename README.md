# Portfolio Platform

> Production-grade Deep RL + classical portfolio optimization service. Five DRL agents (PPO, DDPG, A2C, SAC, TD3) and four classical optimizers (Markowitz, Max Sharpe, Min Vol, HRP) behind a FastAPI service, Next.js dashboard, GitOps deployment, Prometheus-backed SLOs and a runbook.

[![ci](https://img.shields.io/badge/ci-passing-22c55e)](.github/workflows/ci.yml)
[![image](https://img.shields.io/badge/image-ghcr.io%2Fkshama7%2Fportfolio--platform-blue)](https://github.com/users/kshama7/packages)
[![SLO](https://img.shields.io/badge/SLO-99.5%25%20%E2%80%A2%20p95%20%3C%201s-22d3ee)](docs/SLO.md)
[![helm](https://img.shields.io/badge/helm-v3.17-0f1689)](infra/helm/portfolio-platform)
[![argocd](https://img.shields.io/badge/argocd-v2-ef7b4d)](infra/argocd)

🔗 **Live:** [portfolio.kshama.dev](https://portfolio.kshama.dev) · **API:** [portfolio-api.fly.dev/docs](https://portfolio-api.fly.dev/docs) · **Grafana:** [grafana.kshama.dev](https://grafana.kshama.dev/d/portfolio-platform)

## Why this exists

I'm a Site Reliability Engineer ([IBM, EASeJ + IBM MQ team](https://www.linkedin.com/in/kshama-bhatt-28941724a)) heading to UPenn in Fall 2026. My day job is OpenShift / ArgoCD / Prometheus / SOC2 — but my GitHub used to look like a collection of Jupyter notebooks from undergrad. This project is the bridge: I took the actual ML research from my undergraduate capstone — Deep Reinforcement Learning for portfolio optimization (PPO, DDPG, A2C, SAC, TD3 trained on NIFTY 50) — and rebuilt it as a service I'd be comfortable running on-call.

The point isn't the optimizer. **The point is the wrapper.**

## What's in here

```
portfolio-platform/
├── api/                  FastAPI service · classical + DRL replay · /metrics · /healthz
├── web/                  Next.js 15 dashboard · Tailwind · Recharts · SSR · Dockerized
├── infra/
│   ├── helm/             Helm chart · HPA · PDB · NetworkPolicy · ServiceMonitor
│   ├── argocd/           Application · ApplicationSet · AppProject (dev/staging/prod)
│   ├── terraform/        Fly.io + Cloudflare DNS + Grafana Cloud + PagerDuty
│   └── fly/              fly.toml for api and web
├── observability/
│   ├── prometheus/       recording rules · multi-burn-rate SLO alerts
│   ├── grafana/          dashboard JSON (RED + SLO + business panels)
│   └── slo/              OpenSLO definition (availability + latency)
├── docs/
│   ├── ARCHITECTURE.md   diagram + design rationale
│   ├── SLO.md            objectives + error budget math
│   ├── RUNBOOK.md        per-alert playbook
│   └── POSTMORTEM-…md    practice postmortem
├── tests/
│   ├── load/             k6 smoke + stress scripts with SLO thresholds
│   └── chaos/            Chaos Mesh pod-kill + network-latency experiments
├── .github/workflows/    ci · deploy · helm-release · nightly load-test
├── docker-compose.yml    full local stack: api + web + Prometheus + Grafana
└── Makefile              one-liners for everything
```

## Strategies served

| Family | Strategy | Implementation |
|---|---|---|
| Classical | Equal Weight | numpy |
| Classical | Max Sharpe | `pypfopt.EfficientFrontier` with Ledoit-Wolf shrinkage |
| Classical | Min Volatility | `pypfopt.EfficientFrontier` |
| Classical | HRP (Hierarchical Risk Parity) | `pypfopt.HRPOpt` |
| Deep RL | PPO, DDPG, A2C, SAC, TD3 | Trained offline with [stable-baselines3](https://stable-baselines3.readthedocs.io/) on a 20-stock NIFTY subset; the agents' daily weight trajectories are committed and replayed at inference. No torch needed in the runtime image. |

## Resume signal · what this proves I can do

- **Operate ML services in production.** SLOs, error budgets, burn-rate alerts, runbooks, postmortems — the same primitives I use at IBM for IBM MQ and EASeJ.
- **GitOps end-to-end.** ArgoCD ApplicationSet drives three environments from one chart. Same pattern I ship every week in IBM internal repos.
- **Kubernetes hygiene.** Helm chart with HPA (CPU + memory), PDB, NetworkPolicy, ServiceMonitor, topology spread, non-root user, read-only root FS, dropped caps. `helm lint` + `kubeconform` in CI.
- **CI/CD with the right safety rails.** Lint → test → trivy → multi-arch build → GHCR → deploy. Image-level Trivy with `exit-code=1` on HIGH+CRITICAL.
- **Observability that earns its alerts.** Multi-window multi-burn-rate alerts per the Google SRE Workbook, not "5xx > 0 for 1m" garbage.
- **IaC.** Terraform for Fly, Cloudflare, and Grafana Cloud — one `apply` rebuilds the stack.

## Run it locally

```bash
# 1. Spin up the full stack (api + web + Prometheus + Grafana)
make up
# → web   http://localhost:3000
# → api   http://localhost:8000/docs
# → prom  http://localhost:9090
# → graf  http://localhost:3001  (anonymous admin)

# 2. Or just the api + web for dev iteration
make api-dev   # in one shell
make web-dev   # in another

# 3. Tests
make test         # python: 15 tests
make typecheck    # ts
make lint         # ruff + eslint

# 4. Helm
make helm-lint
make helm-template
```

## Deploy it

```bash
# CI does this on every push to main, but the manual flow is:
make build APP_VERSION=0.1.0
make push  APP_VERSION=0.1.0

# Production cluster (assumes ArgoCD already running):
kubectl apply -f infra/argocd/project.yaml
kubectl apply -f infra/argocd/applicationset.yaml

# Live demo (Fly.io):
make fly-deploy-api
make fly-deploy-web
```

## What I'd build next

- Replace the static DRL replay with **online inference** of a quantized PPO policy via ONNX Runtime — keeps the image small but enables fresh forecasts on live universes.
- Wire up **OpenTelemetry traces** to Grafana Tempo so per-strategy spans show up next to the metrics.
- A **canary deploy** with Flagger driven by SLO burn rate (auto-rollback if a new strategy crashes the dashboard).
- A second SLO for **upstream dependency** (yfinance success rate) — the practice postmortem in `docs/` flagged this as a missing signal.

---

## Acknowledgements

The DRL research and offline training code came from two undergraduate projects of mine — [kshama7/portfolio_optimization_drl](https://github.com/kshama7/portfolio_optimization_drl) and [kshama7/capstone](https://github.com/kshama7/capstone). Those are preserved as historical artifacts; this repo is the production rebuild.

— [Kshama Bhatt](https://www.linkedin.com/in/kshama-bhatt-28941724a) · kshama.bhatt7 @ gmail
