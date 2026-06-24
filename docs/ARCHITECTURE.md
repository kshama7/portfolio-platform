# Architecture

![Architecture](./architecture.svg)

## High level

A two-tier service: a Next.js dashboard talks to a FastAPI inference backend.
The backend serves classical optimizers (Markowitz / Max-Sharpe / Min-Vol / HRP
via `pyportfolioopt`) and five deep-RL agents (PPO, A2C, DDPG, SAC, TD3) trained
offline with Stable-Baselines3 and served through ONNX runtime. Live prices come
from Yahoo Finance, with a bundled NIFTY-50 CSV as offline fallback for the
legacy India dataset.

That's the *payload*. The reason this repo exists is the production engineering
around that payload.

## Two deployment targets (important — read this)

This repo has **two** deployment paths, and it's worth being precise about which
one is actually running:

| | What it is | Status |
|---|---|---|
| **Render** (`render.yaml`) | The **live public demo**. Two Docker web services (api + web) wired together by a Blueprint, on Render's free tier. This is what the URLs in the README point to. | ✅ **running** |
| **Kubernetes** (`infra/helm`, `infra/argocd`) | A **portable production target**: a Helm chart (HPA, PDB, NetworkPolicy, ServiceMonitor) driven by an ArgoCD ApplicationSet across dev/staging/prod. | 📦 **reference — not currently deployed to a live cluster** |

Why both? Render is a one-click way to get a real, clickable demo with zero infra
to manage. The Kubernetes manifests are the artifact that demonstrates the SRE
skill set I use day-to-day at IBM (OpenShift / ArgoCD / Prometheus) — they
`helm lint` and `kubeconform`-validate in CI, and would deploy to any cluster,
but standing up a paid cluster 24/7 for a portfolio demo isn't worth it. The
Helm/ArgoCD path is honestly labeled as reference architecture, not presented as
if it were live.

The Terraform under `infra/terraform` (Fly.io + Cloudflare + Grafana Cloud) is
likewise a reference IaC module, not the current live path.

## What the production wrapper demonstrates

| Concern | How it's addressed |
|---|---|
| Cold start, image size | Multi-stage Docker; runtime image ~200 MB. **No torch at inference** — DRL policies run through `onnxruntime` only. |
| Repeatable deploys | Render Blueprint for the live demo; Helm chart with `values.{dev,staging,prod}.yaml` + ArgoCD ApplicationSet for the K8s target. |
| Safe rollouts (K8s target) | Rolling update `maxUnavailable: 0`, PDB `minAvailable: 1`, startup + readiness + liveness probes. |
| Observability | Prometheus `/metrics` with RED + business metrics, recording rules, ServiceMonitor, Grafana dashboard committed as JSON. |
| Alerting that pages on real problems | Multi-window multi-burn-rate alerts per the Google SRE Workbook. Two SLOs: 99.5% availability, 95% < 1s. |
| Security posture (K8s target) | NetworkPolicy, non-root user, read-only root FS, seccomp `RuntimeDefault`, all caps dropped. Trivy scans on every PR + image. |
| Real workflows | Per-alert runbook; one full practice post-mortem. |

## Stack

| Layer | Choice | Why |
|---|---|---|
| Inference API | Python 3.11 · FastAPI · pyportfolioopt · onnxruntime | Mature, fast, type-friendly; ONNX keeps the runtime torch-free. |
| ML training | Stable-Baselines3 · Gymnasium · PyTorch | Industry-standard RL; only needed offline, not in the runtime image. |
| Dashboard | Next.js 15 · Tailwind · Recharts | SSR, good cold-start, tight visual budget. |
| Packaging | Multi-stage Docker, arm64 + amd64 | Apple-Silicon dev + cheap x86 hosting. |
| **Live hosting** | **Render** (Docker web services, free tier) | One-click Blueprint, TLS included, real clickable URL. |
| Orchestration (target) | Kubernetes + Helm | Same primitives as IBM ROKS/OpenShift; portable to any cluster. |
| GitOps (target) | ArgoCD ApplicationSet | The pattern I ship in production at IBM. |
| Observability | Prometheus + Grafana | `/metrics` scrape, recording rules, dashboard-as-code. |
| IaC (reference) | Terraform (Fly + Cloudflare + Grafana Cloud) | Single `apply` brings an alternate environment up. |
| CI/CD | GitHub Actions | lint → test → Trivy → multi-arch build → GHCR → deploy. |
| Load testing | k6 | Smoke nightly; stress on demand. |

## Request flow (live, on Render)

1. Browser loads the Next.js app at `portfolio-web-*.onrender.com`.
2. Browser issues `POST /proxy/api/v1/backtest`.
3. The Next.js **runtime route handler** (`app/proxy/[...path]/route.ts`) forwards
   it to the FastAPI service at `portfolio-api-*.onrender.com`, reading the target
   from the `API_BASE_URL` env var at request time.
4. The API fetches prices from Yahoo Finance, then runs the requested strategies:
   classical optimizers compute weights in-process; **DRL strategies load their
   ONNX policy and run a fresh forward pass for every trading day** (live
   inference, not a replay).
5. The backtest engine compounds daily returns and computes Sharpe / Sortino /
   Calmar / max-DD / win-rate, plus an optional benchmark (SPY, QQQ, …).
6. JSON comes back; the dashboard renders the equity curve vs benchmark,
   drawdown, allocation card, KPI strip, and metrics table.

Per-strategy compute time is recorded as the `optimize_duration_seconds`
histogram (labelled by `strategy`), so the Grafana dashboard surfaces which
optimizer is dragging if latency degrades.
