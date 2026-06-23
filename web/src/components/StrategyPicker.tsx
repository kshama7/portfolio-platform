'use client';

import { clsx } from 'clsx';
import { Info } from 'lucide-react';
import { useState } from 'react';
import { STRATEGY_LABELS } from '@/lib/api';

const CLASSICAL = ['equal_weight', 'max_sharpe', 'min_volatility', 'hrp'];
const DRL = ['drl_ppo', 'drl_ddpg', 'drl_a2c', 'drl_sac', 'drl_td3'];

export function StrategyPicker({
  selected,
  onChange,
  isNiftyUniverse,
}: {
  selected: string[];
  onChange: (next: string[]) => void;
  isNiftyUniverse: boolean;
}) {
  const [showDrl, setShowDrl] = useState(isNiftyUniverse);

  const toggle = (s: string) => {
    onChange(selected.includes(s) ? selected.filter((x) => x !== s) : [...selected, s]);
  };

  const renderBtn = (s: string, disabled = false) => {
    const meta = STRATEGY_LABELS[s];
    const on = selected.includes(s);
    return (
      <button
        key={s}
        onClick={() => !disabled && toggle(s)}
        disabled={disabled}
        title={disabled ? 'DRL agents only work on the NIFTY-20 universe they were trained on' : ''}
        className={clsx(
          'px-2.5 py-1.5 rounded text-xs font-medium transition-all flex items-center gap-2 text-left',
          disabled && 'opacity-40 cursor-not-allowed',
          !disabled && on
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
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs font-medium text-ink-muted uppercase tracking-wider">
          Strategies
        </div>
      </div>
      <div className="grid grid-cols-2 gap-1.5">
        {CLASSICAL.map((s) => renderBtn(s))}
      </div>

      <div className="mt-3">
        <button
          onClick={() => setShowDrl((v) => !v)}
          className="flex items-center gap-1 text-[11px] text-ink-dim hover:text-ink-muted"
        >
          <Info className="w-3 h-3" />
          {showDrl ? 'Hide' : 'Show'} DRL strategies (research)
        </button>
        {showDrl && (
          <>
            <div className="grid grid-cols-2 gap-1.5 mt-2">
              {DRL.map((s) => renderBtn(s, !isNiftyUniverse))}
            </div>
            {!isNiftyUniverse && (
              <div className="text-[10px] text-ink-dim mt-1.5 leading-relaxed">
                Disabled — DRL agents (PPO/DDPG/A2C/SAC/TD3) were trained offline
                on a 20-stock NIFTY-50 subset. Switch the universe to DRL_NIFTY20
                to use them.
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
