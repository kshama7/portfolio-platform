import http from 'k6/http';
import { check } from 'k6';

const BASE = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  scenarios: {
    ramp: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m',  target: 50 },
        { duration: '2m',  target: 100 },
        { duration: '1m',  target: 100 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    // Stricter: at 100 VUs we expect the HPA to scale and keep p95 < 1.5s.
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<1500'],
  },
};

const PAYLOAD = JSON.stringify({
  tickers: ['INFY.NS', 'TCS.NS', 'WIPRO.NS', 'HDFCBANK.NS', 'RELIANCE.NS'],
  start: '2020-01-01',
  end: '2021-12-31',
  strategies: ['equal_weight', 'max_sharpe', 'hrp'],
  data_source: 'local',
});

export default function () {
  const r = http.post(`${BASE}/api/v1/optimize`, PAYLOAD, {
    headers: { 'content-type': 'application/json' },
  });
  check(r, { 'status=200': (x) => x.status === 200 });
}
