'use client';

import { ArrowDown, ArrowUp, Minus } from 'lucide-react';
import type { BacktestStrategyResult, BenchmarkResult } from '@/lib/api';
import { strategyLabel } from '@/lib/api';
import { num, pct } from '@/lib/format';

export function KpiStrip({
  results,
  benchmark,
}: {
  results: BacktestStrategyResult[];
  benchmark?: BenchmarkResult | null;
}) {
  if (results.length === 0) return null;

  const winner = [...results].sort((a, b) => b.metrics.sharpe - a.metrics.sharpe)[0];
  const reference = benchmark ?? null;

  const tiles = [
    {
      label: 'Best strategy',
      value: strategyLabel(winner.strategy).label,
      sub: `Sharpe ${num(winner.metrics.sharpe, 2)}`,
      color: strategyLabel(winner.strategy).color,
    },
    {
      label: 'Total return',
      value: pct(winner.metrics.total_return_pct, 1),
      sub: reference
        ? `vs ${pct(reference.metrics.total_return_pct, 1)} ${reference.ticker}`
        : `${winner.metrics.n_periods} days`,
      delta: reference
        ? winner.metrics.total_return_pct - reference.metrics.total_return_pct
        : undefined,
    },
    {
      label: 'Max drawdown',
      value: pct(winner.metrics.max_drawdown_pct, 1),
      sub: reference
        ? `vs ${pct(reference.metrics.max_drawdown_pct, 1)} ${reference.ticker}`
        : 'peak-to-trough',
      delta: reference
        ? -(winner.metrics.max_drawdown_pct - reference.metrics.max_drawdown_pct)
        : undefined,
      reverse: true,
    },
    {
      label: 'Annualized vol',
      value: pct(winner.metrics.annualized_volatility_pct, 1),
      sub: reference
        ? `vs ${pct(reference.metrics.annualized_volatility_pct, 1)} ${reference.ticker}`
        : `${winner.metrics.n_periods} trading days`,
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {tiles.map((t) => (
        <div key={t.label} className="panel p-4">
          <div className="text-xs text-ink-dim uppercase tracking-wider">{t.label}</div>
          <div className="mt-1 flex items-baseline gap-2">
            <div
              className="text-xl font-semibold tabular-nums"
              style={t.color ? { color: t.color } : undefined}
            >
              {t.value}
            </div>
            {typeof t.delta === 'number' && (
              <span
                className={
                  t.delta > 0
                    ? 'text-accent-green text-xs flex items-center gap-0.5'
                    : t.delta < 0
                      ? 'text-accent-red text-xs flex items-center gap-0.5'
                      : 'text-ink-dim text-xs flex items-center gap-0.5'
                }
              >
                {t.delta > 0 ? <ArrowUp className="w-3 h-3" /> : t.delta < 0 ? <ArrowDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                {pct(Math.abs(t.delta), 1)}
              </span>
            )}
          </div>
          <div className="text-xs text-ink-dim mt-0.5 font-mono">{t.sub}</div>
        </div>
      ))}
    </div>
  );
}
