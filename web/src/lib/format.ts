export const pct = (v: number | null | undefined, digits = 2) =>
  v == null || Number.isNaN(v) ? '—' : `${v.toFixed(digits)}%`;

export const num = (v: number | null | undefined, digits = 2) =>
  v == null || Number.isNaN(v) ? '—' : v.toFixed(digits);

export const money = (v: number | null | undefined) =>
  v == null || Number.isNaN(v)
    ? '—'
    : new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

export const compact = (v: number) =>
  new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(v);
