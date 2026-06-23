'use client';

import { useState } from 'react';
import { AlertCircle, TrendingUp } from 'lucide-react';

import { Header } from '@/components/Header';
import { ControlPanel, type RunRequest } from '@/components/ControlPanel';
import { EquityChart } from '@/components/EquityChart';
import { DrawdownChart } from '@/components/DrawdownChart';
import { MetricsTable } from '@/components/MetricsTable';
import { AllocationCard } from '@/components/AllocationCard';
import { KpiStrip } from '@/components/KpiStrip';
import { api, type BacktestResponse } from '@/lib/api';

export default function Page() {
  const [data, setData] = useState<BacktestResponse | null>(null);
  const [capital, setCapital] = useState(100000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (req: RunRequest) => {
    setLoading(true);
    setError(null);
    setCapital(req.initial_capital);
    try {
      const res = await api.backtest(req);
      setData(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  // Pick the best Sharpe strategy to highlight in allocation card
  const bestStrategy = data?.results.length
    ? [...data.results].sort((a, b) => b.metrics.sharpe - a.metrics.sharpe)[0]
    : null;

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <div className="max-w-7xl mx-auto px-6 py-6 w-full">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-accent" />
            US-stocks portfolio optimizer
          </h1>
          <p className="text-sm text-ink-muted mt-1 max-w-2xl">
            Pick any US tickers (Dow 30, MAG7, S&P 100, or type your own). Compare
            Markowitz, Min-Variance, and HRP optimization against the S&P 500. Live
            prices via Yahoo Finance. Real backtest with Sharpe, Sortino, max
            drawdown.
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

            {!data && !error && <EmptyState />}

            {data && (
              <>
                <KpiStrip results={data.results} benchmark={data.benchmark} />
                <EquityChart results={data.results} benchmark={data.benchmark} />
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  <DrawdownChart results={data.results} />
                  {bestStrategy && (
                    <AllocationCard result={bestStrategy} capital={capital} />
                  )}
                </div>
                <MetricsTable results={data.results} benchmark={data.benchmark} />
                <div className="text-xs text-ink-dim font-mono text-right">
                  {data.start} → {data.end} ·{' '}
                  {data.results[0]?.metrics.n_periods} trading days ·{' '}
                  compute {data.compute_ms.toFixed(0)} ms
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      <footer className="border-t border-line mt-12">
        <div className="max-w-7xl mx-auto px-6 py-4 text-xs text-ink-dim flex justify-between">
          <span>
            Live data via Yahoo Finance · Not investment advice · Past performance
            doesn't predict future returns
          </span>
          <span className="font-mono">v0.2.0</span>
        </div>
      </footer>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="panel p-8 text-center">
      <div className="text-sm text-ink-muted">
        Pick a universe, choose strategies, hit <span className="kbd">Run backtest</span>.
      </div>
      <div className="text-xs text-ink-dim mt-4 max-w-md mx-auto leading-relaxed">
        Default compares Equal Weight, Max Sharpe, Min Volatility and HRP on the
        Magnificent 7 over the last 3 years, vs SPY. Type any other US tickers in
        the input box to add them — single stocks, sector ETFs, anything yfinance
        supports.
      </div>
    </div>
  );
}
