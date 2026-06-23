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
import type { BacktestResponse, BacktestStrategyResult, BenchmarkResult } from '@/lib/api';
import { strategyLabel, BENCHMARK_COLOR } from '@/lib/api';
import { compact, money } from '@/lib/format';

export function EquityChart({
  results,
  benchmark,
}: {
  results: BacktestStrategyResult[];
  benchmark?: BenchmarkResult | null;
}) {
  if (results.length === 0) return null;

  const dates = results[0].dates;
  const dateSet = new Set(dates);

  // Build a benchmark lookup keyed on the strategy dates
  const benchMap: Record<string, number> = {};
  if (benchmark) {
    for (let i = 0; i < benchmark.dates.length; i++) {
      benchMap[benchmark.dates[i]] = benchmark.equity_curve[i];
    }
  }

  const data = dates.map((d, i) => {
    const row: Record<string, number | string> = { date: d };
    for (const r of results) row[r.strategy] = r.equity_curve[i];
    if (benchmark && benchMap[d] !== undefined) row['__benchmark__'] = benchMap[d];
    return row;
  });

  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="text-sm font-semibold">Equity curve</div>
          <div className="text-xs text-ink-dim">
            Compounded portfolio value · daily, monthly rebalance
            {benchmark && (
              <>
                {' '}· <span style={{ color: BENCHMARK_COLOR }}>—— {benchmark.ticker}</span> benchmark
              </>
            )}
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
            formatter={(v: number, name: string) => [
              money(v),
              name === '__benchmark__' ? `${benchmark?.ticker} (benchmark)` : strategyLabel(name).label,
            ]}
          />
          <Legend
            wrapperStyle={{ fontSize: 12 }}
            formatter={(v) =>
              v === '__benchmark__' ? `${benchmark?.ticker} (benchmark)` : strategyLabel(v).label
            }
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
          {benchmark && (
            <Line
              type="monotone"
              dataKey="__benchmark__"
              stroke={BENCHMARK_COLOR}
              strokeWidth={1.75}
              strokeDasharray="6 4"
              dot={false}
              activeDot={{ r: 4 }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
