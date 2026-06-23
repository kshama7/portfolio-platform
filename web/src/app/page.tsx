'use client';

import { useState } from 'react';
import { AlertCircle } from 'lucide-react';

import { Header } from '@/components/Header';
import { ControlPanel, type RunRequest } from '@/components/ControlPanel';
import { EquityChart } from '@/components/EquityChart';
import { DrawdownChart } from '@/components/DrawdownChart';
import { MetricsTable } from '@/components/MetricsTable';
import { WeightsBar } from '@/components/WeightsBar';
import { KpiStrip } from '@/components/KpiStrip';
import { api, type BacktestResponse } from '@/lib/api';

export default function Page() {
  const [data, setData] = useState<BacktestResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (req: RunRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.backtest(req);
      setData(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <div className="max-w-7xl mx-auto px-6 py-6 w-full">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight">
            Compare classical & deep-RL portfolio strategies
          </h1>
          <p className="text-sm text-ink-muted mt-1 max-w-2xl">
            Markowitz, HRP and four DRL agents (PPO, DDPG, A2C, SAC, TD3) run behind a FastAPI
            service with Prometheus metrics, an SLO, GitOps deployment and a runbook. Pick a
            universe, hit run.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-3">
            <ControlPanel onRun={run} loading={loading} />
          </div>

          <div className="lg:col-span-9 space-y-4">
            {error && (
              <div className="panel p-4 border-accent-red/40 bg-accent-red/5 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-accent-red shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-accent-red">Backtest failed</div>
                  <div className="text-xs text-ink-muted font-mono mt-1">{error}</div>
                </div>
              </div>
            )}

            {!data && !error && (
              <EmptyState />
            )}

            {data && (
              <>
                <KpiStrip results={data.results} />
                <EquityChart results={data.results} />
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  <DrawdownChart results={data.results} />
                  <WeightsBar results={data.results} />
                </div>
                <MetricsTable results={data.results} />
                <div className="text-xs text-ink-dim font-mono text-right">
                  compute_ms = {data.compute_ms.toFixed(1)} · n_obs ={' '}
                  {data.results[0]?.metrics.n_periods}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      <footer className="border-t border-line mt-12">
        <div className="max-w-7xl mx-auto px-6 py-4 text-xs text-ink-dim flex justify-between">
          <span>
            Built with FastAPI, Next.js, Helm, ArgoCD, Prometheus & Grafana. Deployed on Fly.io.
          </span>
          <span className="font-mono">v0.1.0</span>
        </div>
      </footer>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="panel p-8 text-center">
      <div className="text-sm text-ink-muted">
        Pick tickers, choose strategies, then hit{' '}
        <span className="kbd">Run backtest</span>.
      </div>
      <div className="text-xs text-ink-dim mt-4 max-w-md mx-auto">
        Default selection compares Equal Weight, Max Sharpe, HRP and the PPO DRL agent over the
        20-stock NIFTY subset used to train the bundled agents.
      </div>
    </div>
  );
}
