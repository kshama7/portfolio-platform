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

export type BacktestResponse = {
  tickers: string[];
  start: string;
  end: string;
  initial_capital: number;
  results: BacktestStrategyResult[];
  compute_ms: number;
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
  optimize: (req: OptimizeRequest) =>
    jsonFetch<OptimizeResponse>('/api/v1/optimize', {
      method: 'POST',
      body: JSON.stringify(req),
    }),
  backtest: (req: OptimizeRequest & { initial_capital?: number; rebalance?: string }) =>
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
  drl_ppo: { label: 'PPO (DRL)', color: '#a78bfa', category: 'Deep RL' },
  drl_ddpg: { label: 'DDPG (DRL)', color: '#f87171', category: 'Deep RL' },
  drl_a2c: { label: 'A2C (DRL)', color: '#60a5fa', category: 'Deep RL' },
  drl_sac: { label: 'SAC (DRL)', color: '#f472b6', category: 'Deep RL' },
  drl_td3: { label: 'TD3 (DRL)', color: '#fde68a', category: 'Deep RL' },
};

export function strategyLabel(s: string) {
  return STRATEGY_LABELS[s] || { label: s, color: '#9ca3af', category: 'Other' };
}
