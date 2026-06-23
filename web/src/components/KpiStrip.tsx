'use client';

import { ArrowDown, ArrowUp, Minus } from 'lucide-react';
import type { BacktestStrategyResult } from '@/lib/api';
import { strategyLabel } from '@/lib/api';
import { num, pct } from '@/lib/format';

export function KpiStrip({ results }: { results: BacktestStrategyResult[] }) {
  if (results.length === 0) return null;

  const winner = [...results].sort((a, b) => b.metrics.sharpe - a.metrics.sharpe)[0];
  const baseline = results.find((r) => r.strategy === 'equal_weight') ?? results[0];

  const tiles = [
    {
      label: 'Winning strategy',
      value: strategyLabel(winner.strategy).label,
      sub: `Sharpe ${num(winner.metrics.sharpe, 2)}`,
      color: strategyLabel(winner.strategy).color,
    },
    {
      label: 'Total return',
      value: pct(winner.metrics.total_return_pct, 1),
      sub: `vs ${pct(baseline.metrics.total_return_pct, 1)} baseline`,
      delta: winner.metrics.total_return_pct - baseline.metrics.total_return_pct,
    },
    {
      label: 'Max drawdown',
      value: pct(winner.metrics.max_drawdown_pct, 1),
      sub: `vs ${pct(baseline.metrics.max_drawdown_pct, 1)} baseline`,
      delta: -(winner.metrics.max_drawdown_pct - baseline.metrics.max_drawdown_pct),
      reverse: true,
    },
    {
      label: 'Annualized vol',
      value: pct(winner.metrics.annualized_volatility_pct, 1),
      sub: `${winner.metrics.n_periods} trading days`,
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
