'use client';

import { Loader2, Play } from 'lucide-react';
import { useEffect, useState } from 'react';

import { TickerPicker } from './TickerPicker';
import { StrategyPicker } from './StrategyPicker';
import { api, DATE_PRESETS, presetRange, type Universe } from '@/lib/api';

export type RunRequest = {
  tickers: string[];
  start: string;
  end: string;
  strategies: string[];
  initial_capital: number;
  rebalance: string;
  data_source: 'auto' | 'yfinance' | 'local';
  benchmark: string | null;
};

const DEFAULT_UNIVERSE_NAME = 'MAG7';
const DEFAULT_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA'];

export function ControlPanel({
  onRun,
  loading,
}: {
  onRun: (req: RunRequest) => void;
  loading: boolean;
}) {
  const [universes, setUniverses] = useState<Universe[]>([]);
  const [benchmarks, setBenchmarks] = useState<Record<string, string>>({});
  const [universeName, setUniverseName] = useState(DEFAULT_UNIVERSE_NAME);
  const [tickers, setTickers] = useState<string[]>(DEFAULT_TICKERS);
  const [strategies, setStrategies] = useState<string[]>([
    'equal_weight',
    'max_sharpe',
    'min_volatility',
    'hrp',
  ]);
  const initial = presetRange(3);
  const [start, setStart] = useState(initial.start);
  const [end, setEnd] = useState(initial.end);
  const [capital, setCapital] = useState(100000);
  const [benchmark, setBenchmark] = useState<string>('SPY');

  useEffect(() => {
    api.universes().then(setUniverses).catch(console.error);
    api.benchmarks().then(setBenchmarks).catch(console.error);
  }, []);

  const activeUniverse = universes.find((u) => u.name === universeName)?.tickers ?? [];
  const isNifty = universeName === 'NIFTY50' || universeName === 'DRL_NIFTY20';

  const onUniverseChange = (name: string) => {
    setUniverseName(name);
    const next = universes.find((u) => u.name === name)?.tickers ?? [];
    setTickers(next.slice(0, 20));
    // If switching to NIFTY, default benchmark off (no NIFTY benchmark wired)
    if (name === 'NIFTY50' || name === 'DRL_NIFTY20') {
      setBenchmark('');
    } else if (!benchmark) {
      setBenchmark('SPY');
    }
  };

  const applyPreset = (years: number) => {
    const r = presetRange(years);
    setStart(r.start);
    setEnd(r.end);
  };

  const canRun = tickers.length >= 2 && strategies.length >= 1 && !loading;

  return (
    <div className="panel p-5 space-y-4 sticky top-24 max-h-[calc(100vh-120px)] overflow-y-auto">
      <div>
        <div className="text-xs font-medium text-ink-muted uppercase tracking-wider mb-2">
          Universe
        </div>
        <select
          className="w-full bg-bg-subtle border border-line rounded-md px-2 py-1.5 text-sm font-mono"
          value={universeName}
          onChange={(e) => onUniverseChange(e.target.value)}
        >
          {universes.map((u) => (
            <option key={u.name} value={u.name}>
              {u.name} ({u.tickers.length})
            </option>
          ))}
        </select>
        {universes.find((u) => u.name === universeName)?.description && (
          <div className="text-[10px] text-ink-dim mt-1 leading-snug">
            {universes.find((u) => u.name === universeName)?.description}
          </div>
        )}
      </div>

      <TickerPicker universe={activeUniverse} selected={tickers} onChange={setTickers} max={30} />

      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs font-medium text-ink-muted uppercase tracking-wider">
            Date range
          </div>
          <div className="flex gap-1">
            {DATE_PRESETS.map((p) => (
              <button
                key={p.label}
                onClick={() => applyPreset(p.years)}
                className="px-1.5 py-0.5 text-[11px] font-mono text-ink-muted hover:text-ink hover:bg-bg-subtle border border-line rounded"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <input
            type="date"
            className="bg-bg-subtle border border-line rounded-md px-2 py-1.5 text-sm font-mono"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
          <input
            type="date"
            className="bg-bg-subtle border border-line rounded-md px-2 py-1.5 text-sm font-mono"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
          />
        </div>
      </div>

      <div>
        <div className="text-xs font-medium text-ink-muted uppercase tracking-wider mb-2">
          Initial capital
        </div>
        <input
          type="number"
          className="w-full bg-bg-subtle border border-line rounded-md px-2 py-1.5 text-sm font-mono"
          value={capital}
          step={10000}
          min={1000}
          onChange={(e) => setCapital(Number(e.target.value))}
        />
      </div>

      <div>
        <div className="text-xs font-medium text-ink-muted uppercase tracking-wider mb-2">
          Benchmark
        </div>
        <select
          className="w-full bg-bg-subtle border border-line rounded-md px-2 py-1.5 text-sm font-mono"
          value={benchmark}
          onChange={(e) => setBenchmark(e.target.value)}
          disabled={isNifty}
        >
          <option value="">— None —</option>
          {Object.entries(benchmarks).map(([k, v]) => (
            <option key={k} value={k}>
              {k} · {v}
            </option>
          ))}
        </select>
        {isNifty && (
          <div className="text-[10px] text-ink-dim mt-1">
            Benchmarks are US ETFs — not comparable to NIFTY.
          </div>
        )}
      </div>

      <StrategyPicker selected={strategies} onChange={setStrategies} isNiftyUniverse={isNifty} />

      <button
        className="btn btn-primary w-full flex items-center justify-center gap-2"
        disabled={!canRun}
        onClick={() =>
          onRun({
            tickers,
            start,
            end,
            strategies,
            initial_capital: capital,
            rebalance: 'monthly',
            data_source: isNifty ? 'local' : 'yfinance',
            benchmark: benchmark || null,
          })
        }
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" /> Running backtest…
          </>
        ) : (
          <>
            <Play className="w-4 h-4" /> Run backtest
          </>
        )}
      </button>
      <div className="text-[10px] text-ink-dim font-mono text-center leading-snug">
        {isNifty ? 'Offline data · sub-second' : 'Live Yahoo Finance · 1-5 sec'}
      </div>
    </div>
  );
}
