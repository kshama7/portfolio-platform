'use client';

import type { BacktestStrategyResult } from '@/lib/api';
import { strategyLabel } from '@/lib/api';
import { money, pct } from '@/lib/format';

export function AllocationCard({
  result,
  capital,
}: {
  result: BacktestStrategyResult;
  capital: number;
}) {
  const meta = strategyLabel(result.strategy);
  const entries = Object.entries(result.weights ?? {})
    .filter(([, w]) => w > 0.001)
    .sort((a, b) => b[1] - a[1]);

  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="text-sm font-semibold flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ background: meta.color }} />
            How to allocate: {meta.label}
          </div>
          <div className="text-xs text-ink-dim mt-0.5">
            Initial capital {money(capital)} · split per the optimizer's recommended weights
          </div>
        </div>
      </div>
      <div className="space-y-1.5">
        {entries.map(([t, w]) => (
          <div key={t} className="flex items-center gap-3">
            <div className="font-mono text-sm w-20 truncate">{t.replace('.NS', '')}</div>
            <div className="flex-1 bg-bg-subtle h-5 rounded overflow-hidden border border-line">
              <div
                className="h-full"
                style={{ width: `${w * 100}%`, background: meta.color, opacity: 0.85 }}
              />
            </div>
            <div className="font-mono text-xs text-ink-muted w-14 text-right tabular-nums">
              {pct(w * 100, 1)}
            </div>
            <div className="font-mono text-xs text-ink w-20 text-right tabular-nums">
              {money(w * capital)}
            </div>
          </div>
        ))}
        {entries.length === 0 && (
          <div className="text-xs text-ink-dim font-mono">no positive weights</div>
        )}
      </div>
    </div>
  );
}
