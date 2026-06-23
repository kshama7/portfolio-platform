import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: '#0a0a0b',
          panel: '#111114',
          subtle: '#16161a',
        },
        line: '#1f1f25',
        ink: {
          DEFAULT: '#f3f4f6',
          muted: '#9ca3af',
          dim: '#6b7280',
        },
        accent: {
          DEFAULT: '#22d3ee',
          green: '#34d399',
          amber: '#fbbf24',
          red: '#f87171',
          violet: '#a78bfa',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(34, 211, 238, 0.2), 0 8px 32px -8px rgba(34, 211, 238, 0.15)',
      },
    },
  },
  plugins: [],
};
export default config;
