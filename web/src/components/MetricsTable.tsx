'use client';

import { clsx } from 'clsx';
import type { BacktestStrategyResult } from '@/lib/api';
import { strategyLabel } from '@/lib/api';
import { num, pct } from '@/lib/format';

type ColDef = {
  key: string;
  label: string;
  fmt: (v: number) => string;
  highlight?: boolean;
};

const COLS: ColDef[] = [
  { key: 'total_return_pct', label: 'Total Ret', fmt: (v) => pct(v, 1), highlight: true },
  { key: 'annualized_return_pct', label: 'Ann. Ret', fmt: (v) => pct(v, 1) },
  { key: 'annualized_volatility_pct', label: 'Ann. Vol', fmt: (v) => pct(v, 1) },
  { key: 'sharpe', label: 'Sharpe', fmt: (v) => num(v, 2), highlight: true },
  { key: 'sortino', label: 'Sortino', fmt: (v) => num(v, 2) },
  { key: 'max_drawdown_pct', label: 'Max DD', fmt: (v) => pct(v, 1) },
  { key: 'calmar', label: 'Calmar', fmt: (v) => num(v, 2) },
  { key: 'win_rate_pct', label: 'Win %', fmt: (v) => pct(v, 1) },
];

export function MetricsTable({ results }: { results: BacktestStrategyResult[] }) {
  if (results.length === 0) return null;

  // best Sharpe per column highlight
  const bestSharpe = Math.max(...results.map((r) => r.metrics.sharpe));
  const bestTotal = Math.max(...results.map((r) => r.metrics.total_return_pct));

  return (
    <div className="panel p-4">
      <div className="mb-3">
        <div className="text-sm font-semibold">Performance metrics</div>
        <div className="text-xs text-ink-dim">
          full-period stats; higher Sharpe + lower drawdown wins
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-ink-dim uppercase tracking-wider border-b border-line">
              <th className="text-left font-medium py-2 pr-3">Strategy</th>
              {COLS.map((c) => (
                <th key={c.key} className="text-right font-medium py-2 px-2">
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((r) => {
              const meta = strategyLabel(r.strategy);
              return (
                <tr key={r.strategy} className="border-b border-line/50 hover:bg-bg-subtle/50">
                  <td className="py-2.5 pr-3">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full" style={{ background: meta.color }} />
                      <span className="font-medium">{meta.label}</span>
                      <span className="text-xs text-ink-dim">{meta.category}</span>
                    </div>
                  </td>
                  {COLS.map((c) => {
                    const v = r.metrics[c.key as keyof typeof r.metrics] as number;
                    const isBest =
                      (c.key === 'sharpe' && v === bestSharpe) ||
                      (c.key === 'total_return_pct' && v === bestTotal);
                    return (
                      <td
                        key={c.key}
                        className={clsx(
                          'py-2.5 px-2 text-right font-mono tabular-nums',
                          isBest && 'text-accent-green font-semibold',
                          !isBest && c.highlight && 'text-ink',
                          !isBest && !c.highlight && 'text-ink-muted',
                        )}
                      >
                        {c.fmt(v)}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
