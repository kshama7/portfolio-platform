import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

const BASE = __ENV.BASE_URL || 'http://localhost:8000';

const optimizeLatency = new Trend('optimize_latency');
const backtestLatency = new Trend('backtest_latency');
const errorRate = new Rate('errors');

export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-vus',
      vus: 2,
      duration: '1m',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<1000', 'p(99)<2000'],
    optimize_latency: ['p(95)<800'],
    backtest_latency: ['p(95)<1200'],
    errors: ['rate<0.01'],
  },
};

const TICKERS = [
  'INFY.NS', 'TCS.NS', 'WIPRO.NS', 'HDFCBANK.NS', 'RELIANCE.NS',
];

export default function () {
  const h = http.get(`${BASE}/healthz`);
  check(h, { 'healthz=200': (r) => r.status === 200 }) || errorRate.add(1);

  const optBody = JSON.stringify({
    tickers: TICKERS,
    start: '2020-01-01',
    end: '2021-12-31',
    strategies: ['equal_weight', 'max_sharpe', 'hrp'],
    data_source: 'local',
  });
  const opt = http.post(`${BASE}/api/v1/optimize`, optBody, {
    headers: { 'content-type': 'application/json' },
    tags: { route: 'optimize' },
  });
  optimizeLatency.add(opt.timings.duration);
  check(opt, {
    'optimize=200': (r) => r.status === 200,
    'optimize has results': (r) => JSON.parse(r.body).results.length === 3,
  }) || errorRate.add(1);

  const btBody = JSON.stringify({
    tickers: TICKERS,
    start: '2019-01-01',
    end: '2021-12-31',
    strategies: ['equal_weight', 'max_sharpe'],
    data_source: 'local',
    initial_capital: 100000,
    rebalance: 'monthly',
  });
  const bt = http.post(`${BASE}/api/v1/backtest`, btBody, {
    headers: { 'content-type': 'application/json' },
    tags: { route: 'backtest' },
  });
  backtestLatency.add(bt.timings.duration);
  check(bt, {
    'backtest=200': (r) => r.status === 200,
    'backtest has equity curve': (r) => JSON.parse(r.body).results[0].equity_curve.length > 100,
  }) || errorRate.add(1);

  sleep(1);
}
