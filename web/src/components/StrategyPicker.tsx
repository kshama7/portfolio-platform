'use client';

import { clsx } from 'clsx';
import { Cpu } from 'lucide-react';
import { STRATEGY_LABELS } from '@/lib/api';

const CLASSICAL = ['equal_weight', 'max_sharpe', 'min_volatility', 'hrp'];

export function StrategyPicker({
  selected,
  onChange,
  availableDrl,
  universeName,
}: {
  selected: string[];
  onChange: (next: string[]) => void;
  availableDrl: string[];
  universeName: string;
}) {
  const toggle = (s: string) => {
    onChange(selected.includes(s) ? selected.filter((x) => x !== s) : [...selected, s]);
  };

  const renderBtn = (s: string) => {
    const meta = STRATEGY_LABELS[s] ?? { label: s, color: '#9ca3af', category: 'Other' };
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
  };

  return (
    <div className="space-y-3">
      <div>
        <div className="text-xs font-medium text-ink-muted uppercase tracking-wider mb-2">
          Classical
        </div>
        <div className="grid grid-cols-2 gap-1.5">{CLASSICAL.map(renderBtn)}</div>
      </div>

      {availableDrl.length > 0 && (
        <div>
          <div className="text-xs font-medium text-ink-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Cpu className="w-3 h-3" />
            Deep RL — trained for {universeName}
          </div>
          <div className="grid grid-cols-2 gap-1.5">{availableDrl.map(renderBtn)}</div>
          <div className="text-[10px] text-ink-dim mt-1.5 leading-relaxed">
            Real policies. Trained 2015–2022 on the {universeName} universe. Daily
            re-inference at backtest time via ONNX runtime.
          </div>
        </div>
      )}
    </div>
  );
}
