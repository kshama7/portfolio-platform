'use client';

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { BacktestStrategyResult } from '@/lib/api';
import { strategyLabel } from '@/lib/api';
import { pct } from '@/lib/format';

export function WeightsBar({ results }: { results: BacktestStrategyResult[] }) {
  if (results.length === 0) return null;

  const tickers = new Set<string>();
  for (const r of results) for (const t of Object.keys(r.weights ?? {})) tickers.add(t);
  const sortedTickers = Array.from(tickers).sort();

  const data = sortedTickers.map((t) => {
    const row: Record<string, number | string> = { ticker: t.replace('.NS', '') };
    for (const r of results) row[r.strategy] = (r.weights?.[t] ?? 0) * 100;
    return row;
  });

  return (
    <div className="panel p-4">
      <div className="mb-3">
        <div className="text-sm font-semibold">Final portfolio weights</div>
        <div className="text-xs text-ink-dim">
          allocation per ticker at end of backtest window
        </div>
      </div>
      <ResponsiveContainer width="100%" height={Math.max(180, sortedTickers.length * 22)}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="#1f1f25" strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" stroke="#6b7280" fontSize={11} tickFormatter={(v) => `${v}%`} />
          <YAxis
            type="category"
            dataKey="ticker"
            stroke="#6b7280"
            fontSize={11}
            width={88}
            interval={0}
          />
          <Tooltip
            contentStyle={{
              background: '#111114',
              border: '1px solid #1f1f25',
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(v: number, name: string) => [pct(v), strategyLabel(name).label]}
          />
          {results.map((r) => (
            <Bar key={r.strategy} dataKey={r.strategy} stackId={undefined}>
              {data.map((_, idx) => (
                <Cell key={idx} fill={strategyLabel(r.strategy).color} fillOpacity={0.85} />
              ))}
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
