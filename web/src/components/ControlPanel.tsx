'use client';

import { Loader2, Play } from 'lucide-react';
import { useEffect, useState } from 'react';

import { TickerPicker } from './TickerPicker';
import { StrategyPicker } from './StrategyPicker';
import { api, type Universe } from '@/lib/api';

export type RunRequest = {
  tickers: string[];
  start: string;
  end: string;
  strategies: string[];
  initial_capital: number;
  rebalance: string;
  data_source: 'local' | 'auto';
};

const DRL_UNIVERSE = [
  'ASIANPAINT.NS', 'CIPLA.NS', 'DRREDDY.NS', 'GAIL.NS', 'GRASIM.NS',
  'HDFCBANK.NS', 'HEROMOTOCO.NS', 'HINDUNILVR.NS', 'INFY.NS', 'ITC.NS',
  'LT.NS', 'M&M.NS', 'MARUTI.NS', 'NTPC.NS', 'POWERGRID.NS',
  'SUNPHARMA.NS', 'TATACHEM.NS', 'TCS.NS', 'ULTRACEMCO.NS', 'WIPRO.NS',
];

export function ControlPanel({
  onRun,
  loading,
}: {
  onRun: (req: RunRequest) => void;
  loading: boolean;
}) {
  const [universes, setUniverses] = useState<Universe[]>([]);
  const [universeName, setUniverseName] = useState('DRL_NIFTY20');
  const [tickers, setTickers] = useState<string[]>(DRL_UNIVERSE);
  const [strategies, setStrategies] = useState<string[]>([
    'equal_weight',
    'max_sharpe',
    'hrp',
    'drl_ppo',
  ]);
  const [start, setStart] = useState('2021-03-01');
  const [end, setEnd] = useState('2023-12-31');
  const [capital, setCapital] = useState(100000);

  useEffect(() => {
    api.universes().then(setUniverses).catch(console.error);
  }, []);

  const activeUniverse =
    universes.find((u) => u.name === universeName)?.tickers ?? DRL_UNIVERSE;

  const onUniverseChange = (name: string) => {
    setUniverseName(name);
    const next = universes.find((u) => u.name === name)?.tickers ?? [];
    setTickers(next.slice(0, 20));
  };

  const canRun = tickers.length >= 2 && strategies.length >= 1 && !loading;

  return (
    <div className="panel p-5 space-y-4 sticky top-24">
      <div>
        <div className="text-xs font-medium text-ink-muted uppercase tracking-wider mb-2">
          Universe
        </div>
        <div className="grid grid-cols-3 gap-1.5">
          {universes.map((u) => (
            <button
              key={u.name}
              onClick={() => onUniverseChange(u.name)}
              className={
                universeName === u.name
                  ? 'btn bg-bg-subtle border border-accent/40 text-ink text-xs'
                  : 'btn border border-line text-ink-muted hover:text-ink text-xs'
              }
            >
              {u.name}
            </button>
          ))}
        </div>
      </div>

      <TickerPicker universe={activeUniverse} selected={tickers} onChange={setTickers} max={30} />

      <div className="grid grid-cols-2 gap-3">
        <div>
          <div className="text-xs font-medium text-ink-muted uppercase tracking-wider mb-2">
            Start
          </div>
          <input
            type="date"
            className="w-full bg-bg-subtle border border-line rounded-md px-2 py-1.5 text-sm font-mono"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
        </div>
        <div>
          <div className="text-xs font-medium text-ink-muted uppercase tracking-wider mb-2">
            End
          </div>
          <input
            type="date"
            className="w-full bg-bg-subtle border border-line rounded-md px-2 py-1.5 text-sm font-mono"
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

      <StrategyPicker selected={strategies} onChange={setStrategies} />

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
            data_source: 'local',
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
      <div className="text-xs text-ink-dim font-mono text-center">
        compute happens server-side · sub-second for most runs
      </div>
    </div>
  );
}
