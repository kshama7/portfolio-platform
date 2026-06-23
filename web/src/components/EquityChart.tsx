'use client';

import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from 'recharts';
import type { BacktestStrategyResult } from '@/lib/api';
import { strategyLabel } from '@/lib/api';
import { compact, money } from '@/lib/format';

export function EquityChart({ results }: { results: BacktestStrategyResult[] }) {
  if (results.length === 0) return null;

  const dates = results[0].dates;
  const data = dates.map((d, i) => {
    const row: Record<string, number | string> = { date: d };
    for (const r of results) row[r.strategy] = r.equity_curve[i];
    return row;
  });

  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="text-sm font-semibold">Equity curve</div>
          <div className="text-xs text-ink-dim">
            $100k notional, compounded daily — strategy comparison
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
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
            tickFormatter={(v) => `$${compact(v)}`}
            domain={['auto', 'auto']}
            width={64}
          />
          <Tooltip
            contentStyle={{
              background: '#111114',
              border: '1px solid #1f1f25',
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: '#9ca3af' }}
            formatter={(v: number, name: string) => [money(v), strategyLabel(name).label]}
          />
          <Legend
            wrapperStyle={{ fontSize: 12 }}
            formatter={(v) => strategyLabel(v).label}
            iconType="circle"
          />
          {results.map((r) => (
            <Line
              key={r.strategy}
              type="monotone"
              dataKey={r.strategy}
              stroke={strategyLabel(r.strategy).color}
              strokeWidth={1.75}
              dot={false}
              activeDot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
