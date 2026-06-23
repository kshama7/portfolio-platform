'use client';

import { Plus, X } from 'lucide-react';
import { useState } from 'react';
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
  const [draft, setDraft] = useState('');

  const toggle = (t: string) => {
    if (selected.includes(t)) {
      onChange(selected.filter((x) => x !== t));
    } else if (selected.length < max) {
      onChange([...selected, t]);
    }
  };

  const addCustom = () => {
    if (!draft.trim()) return;
    const parts = draft
      .toUpperCase()
      .split(/[,\s]+/)
      .map((p) => p.trim())
      .filter(Boolean);
    const next = [...selected];
    for (const p of parts) {
      if (!next.includes(p) && next.length < max) next.push(p);
    }
    onChange(next);
    setDraft('');
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="text-xs font-medium text-ink-muted uppercase tracking-wider">
          Tickers
        </div>
        <div className="text-xs text-ink-dim font-mono">
          {selected.length} / {max}
        </div>
      </div>

      {/* Custom input */}
      <div className="flex gap-1.5">
        <input
          type="text"
          placeholder="Type tickers: AAPL, MSFT, NVDA…"
          className="flex-1 bg-bg-subtle border border-line rounded-md px-2 py-1.5 text-sm font-mono uppercase placeholder:normal-case placeholder:text-ink-dim focus:outline-none focus:border-accent/60"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              addCustom();
            }
          }}
        />
        <button
          onClick={addCustom}
          disabled={!draft.trim()}
          className="px-2 py-1.5 rounded-md bg-accent text-black hover:bg-cyan-300 disabled:opacity-40 disabled:cursor-not-allowed"
          title="Add ticker"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {/* Selected chips */}
      {selected.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {selected.map((t) => (
            <button
              key={t}
              onClick={() => onChange(selected.filter((x) => x !== t))}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono bg-accent text-black hover:bg-accent-red hover:text-white transition-colors"
              title="Remove"
            >
              {t.replace('.NS', '')}
              <X className="w-3 h-3" />
            </button>
          ))}
        </div>
      )}

      {/* Universe quick-pick */}
      <div>
        <div className="text-[10px] font-medium text-ink-dim uppercase tracking-wider mb-1">
          From selected universe
        </div>
        <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto p-1.5 bg-bg-subtle rounded-md border border-line">
          {universe.map((t) => {
            const on = selected.includes(t);
            return (
              <button
                key={t}
                onClick={() => toggle(t)}
                className={clsx(
                  'px-1.5 py-0.5 rounded text-[11px] font-mono transition-colors',
                  on
                    ? 'bg-accent/30 text-accent border border-accent/40'
                    : 'text-ink-muted hover:text-ink hover:bg-bg-panel border border-line',
                )}
              >
                {t.replace('.NS', '')}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
