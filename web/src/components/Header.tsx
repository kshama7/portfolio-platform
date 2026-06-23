import { Activity, GitBranch, Github, ExternalLink } from 'lucide-react';

export function Header() {
  return (
    <header className="border-b border-line bg-bg-panel/40 backdrop-blur sticky top-0 z-20">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent to-accent-violet flex items-center justify-center shadow-glow">
            <Activity className="w-5 h-5 text-black" strokeWidth={2.5} />
          </div>
          <div>
            <div className="font-semibold tracking-tight">Portfolio Platform</div>
            <div className="text-xs text-ink-dim font-mono">
              prod-grade DRL + classical optimization
            </div>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-2 text-xs">
          <span className="chip text-accent-green border-accent-green/30">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-green animate-pulse" />
            healthy
          </span>
          <span className="chip">
            <GitBranch className="w-3 h-3" /> main
          </span>
          <a
            className="chip hover:text-ink transition-colors"
            href="https://github.com/kshama7/portfolio-platform"
            target="_blank"
            rel="noreferrer"
          >
            <Github className="w-3 h-3" /> source
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </header>
  );
}
