'use client';

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { BacktestStrategyResult } from '@/lib/api';
import { strategyLabel } from '@/lib/api';
import { pct } from '@/lib/format';

export function DrawdownChart({ results }: { results: BacktestStrategyResult[] }) {
  if (results.length === 0) return null;
  const dates = results[0].dates;
  const data = dates.map((d, i) => {
    const row: Record<string, number | string> = { date: d };
    for (const r of results) row[r.strategy] = (r.drawdown[i] ?? 0) * 100;
    return row;
  });

  return (
    <div className="panel p-4">
      <div className="mb-3">
        <div className="text-sm font-semibold">Drawdown</div>
        <div className="text-xs text-ink-dim">
          peak-to-trough loss; how deep each strategy went under water
        </div>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="#1f1f25" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="date"
            stroke="#6b7280"
            fontSize={11}
            tickFormatter={(d) => d.slice(0, 7)}
            minTickGap={48}
          />
          <YAxis
            stroke="#6b7280"
            fontSize={11}
            tickFormatter={(v) => `${v.toFixed(0)}%`}
            domain={['auto', 0]}
            width={48}
          />
          <Tooltip
            contentStyle={{
              background: '#111114',
              border: '1px solid #1f1f25',
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: '#9ca3af' }}
            formatter={(v: number, name: string) => [pct(v), strategyLabel(name).label]}
          />
          <Legend
            wrapperStyle={{ fontSize: 12 }}
            formatter={(v) => strategyLabel(v).label}
            iconType="circle"
          />
          {results.map((r) => (
            <Area
              key={r.strategy}
              type="monotone"
              dataKey={r.strategy}
              stroke={strategyLabel(r.strategy).color}
              fill={strategyLabel(r.strategy).color}
              fillOpacity={0.12}
              strokeWidth={1.5}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
