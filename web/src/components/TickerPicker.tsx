'use client';

import { X } from 'lucide-react';
import { clsx } from 'clsx';

export function TickerPicker({
  universe,
  selected,
  onChange,
  max = 30,
}: {
  universe: string[];
  selected: string[];
  onChange: (next: string[]) => void;
  max?: number;
}) {
  const toggle = (t: string) => {
    if (selected.includes(t)) {
      onChange(selected.filter((x) => x !== t));
    } else if (selected.length < max) {
      onChange([...selected, t]);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs font-medium text-ink-muted uppercase tracking-wider">
          Tickers
        </div>
        <div className="text-xs text-ink-dim font-mono">
          {selected.length} / {max}
        </div>
      </div>
      <div className="flex flex-wrap gap-1.5 max-h-44 overflow-y-auto p-2 bg-bg-subtle rounded-md border border-line">
        {universe.map((t) => {
          const on = selected.includes(t);
          return (
            <button
              key={t}
              onClick={() => toggle(t)}
              className={clsx(
                'px-2 py-1 rounded text-xs font-mono transition-colors',
                on
                  ? 'bg-accent text-black'
                  : 'text-ink-muted hover:text-ink hover:bg-bg-panel border border-line',
              )}
            >
              {t.replace('.NS', '')}
              {on && <X className="inline w-3 h-3 ml-1" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
