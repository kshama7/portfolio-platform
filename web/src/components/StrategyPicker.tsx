'use client';

import { clsx } from 'clsx';
import { STRATEGY_LABELS } from '@/lib/api';

const ORDER = [
  'equal_weight',
  'max_sharpe',
  'min_volatility',
  'hrp',
  'drl_ppo',
  'drl_ddpg',
  'drl_a2c',
  'drl_sac',
  'drl_td3',
];

export function StrategyPicker({
  selected,
  onChange,
}: {
  selected: string[];
  onChange: (next: string[]) => void;
}) {
  const toggle = (s: string) => {
    onChange(selected.includes(s) ? selected.filter((x) => x !== s) : [...selected, s]);
  };

  return (
    <div>
      <div className="text-xs font-medium text-ink-muted uppercase tracking-wider mb-2">
        Strategies to compare
      </div>
      <div className="grid grid-cols-2 gap-1.5">
        {ORDER.map((s) => {
          const meta = STRATEGY_LABELS[s];
          const on = selected.includes(s);
          return (
            <button
              key={s}
              onClick={() => toggle(s)}
              className={clsx(
                'px-2.5 py-1.5 rounded text-xs font-medium transition-all flex items-center gap-2 text-left',
                on
                  ? 'bg-bg-subtle border border-accent/40 text-ink'
                  : 'border border-line text-ink-muted hover:text-ink hover:bg-bg-subtle',
              )}
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ background: meta.color, opacity: on ? 1 : 0.4 }}
              />
              <span className="truncate">{meta.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
