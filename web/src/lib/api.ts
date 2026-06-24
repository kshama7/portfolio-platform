export const API_BASE =
  typeof window === 'undefined'
    ? process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
    : '/proxy';

export type Universe = { name: string; tickers: string[]; description: string };

export type OptimizeRequest = {
  tickers: string[];
  start: string;
  end: string;
  strategies: string[];
  data_source?: 'auto' | 'local' | 'yfinance';
  risk_free_rate?: number;
};

export type OptimizeStrategyResult = {
  strategy: string;
  weights: Record<string, number>;
  expected_annual_return: number | null;
  expected_annual_volatility: number | null;
  expected_sharpe: number | null;
  notes: string | null;
};

export type OptimizeResponse = {
  tickers: string[];
  start: string;
  end: string;
  n_observations: number;
  results: OptimizeStrategyResult[];
  compute_ms: number;
};

export type BacktestMetrics = {
  total_return_pct: number;
  annualized_return_pct: number;
  annualized_volatility_pct: number;
  sharpe: number;
  sortino: number;
  max_drawdown_pct: number;
  calmar: number;
  win_rate_pct: number;
  n_periods: number;
};

export type BacktestStrategyResult = {
  strategy: string;
  dates: string[];
  equity_curve: number[];
  daily_returns: number[];
  drawdown: number[];
  metrics: BacktestMetrics;
  weights: Record<string, number> | null;
  notes: string | null;
};

export type BenchmarkResult = {
  ticker: string;
  dates: string[];
  equity_curve: number[];
  metrics: BacktestMetrics;
};

export type BacktestResponse = {
  tickers: string[];
  start: string;
  end: string;
  initial_capital: number;
  results: BacktestStrategyResult[];
  benchmark: BenchmarkResult | null;
  compute_ms: number;
};

export type BacktestRequest = {
  tickers: string[];
  start: string;
  end: string;
  strategies: string[];
  data_source?: 'auto' | 'local' | 'yfinance';
  initial_capital?: number;
  rebalance?: string;
  benchmark?: string | null;
};

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'content-type': 'application/json', ...(init?.headers || {}) },
    cache: 'no-store',
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return (await res.json()) as T;
}

export const api = {
  universes: () => jsonFetch<Universe[]>('/api/v1/universes'),
  strategies: () => jsonFetch<string[]>('/api/v1/strategies'),
  strategyUniverseMap: () => jsonFetch<Record<string, string>>('/api/v1/strategies/universe-map'),
  benchmarks: () => jsonFetch<Record<string, string>>('/api/v1/benchmarks'),
  optimize: (req: OptimizeRequest) =>
    jsonFetch<OptimizeResponse>('/api/v1/optimize', {
      method: 'POST',
      body: JSON.stringify(req),
    }),
  backtest: (req: BacktestRequest) =>
    jsonFetch<BacktestResponse>('/api/v1/backtest', {
      method: 'POST',
      body: JSON.stringify(req),
    }),
};

export const STRATEGY_LABELS: Record<string, { label: string; color: string; category: string }> = {
  equal_weight: { label: 'Equal Weight', color: '#9ca3af', category: 'Classical' },
  max_sharpe: { label: 'Max Sharpe', color: '#22d3ee', category: 'Classical' },
  min_volatility: { label: 'Min Volatility', color: '#34d399', category: 'Classical' },
  hrp: { label: 'HRP', color: '#fbbf24', category: 'Classical' },

  // Live DRL — real PPO/A2C policies trained on US data 2015-2022, served via ONNX
  drl_ppo_dow30: { label: 'PPO · Dow 30', color: '#a78bfa', category: 'DRL (live)' },
  drl_a2c_dow30: { label: 'A2C · Dow 30', color: '#60a5fa', category: 'DRL (live)' },
  drl_ppo_mag7: { label: 'PPO · MAG7', color: '#a78bfa', category: 'DRL (live)' },
  drl_a2c_mag7: { label: 'A2C · MAG7', color: '#60a5fa', category: 'DRL (live)' },

  // Legacy NIFTY replay (precomputed action CSVs)
  drl_ppo_nifty: { label: 'PPO · NIFTY-20', color: '#a78bfa', category: 'DRL (replay)' },
  drl_ddpg_nifty: { label: 'DDPG · NIFTY-20', color: '#f87171', category: 'DRL (replay)' },
  drl_a2c_nifty: { label: 'A2C · NIFTY-20', color: '#60a5fa', category: 'DRL (replay)' },
  drl_sac_nifty: { label: 'SAC · NIFTY-20', color: '#f472b6', category: 'DRL (replay)' },
  drl_td3_nifty: { label: 'TD3 · NIFTY-20', color: '#fde68a', category: 'DRL (replay)' },
};

export function strategyLabel(s: string) {
  return STRATEGY_LABELS[s] || { label: s, color: '#9ca3af', category: 'Other' };
}

export const BENCHMARK_COLOR = '#fb923c';

export const DATE_PRESETS = [
  { label: '1Y', years: 1 },
  { label: '3Y', years: 3 },
  { label: '5Y', years: 5 },
  { label: '10Y', years: 10 },
] as const;

export function presetRange(years: number): { start: string; end: string } {
  const end = new Date();
  const start = new Date();
  start.setFullYear(end.getFullYear() - years);
  return { start: start.toISOString().slice(0, 10), end: end.toISOString().slice(0, 10) };
}
