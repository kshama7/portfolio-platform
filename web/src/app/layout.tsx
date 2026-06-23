import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Portfolio Platform — Production ML Optimization',
  description:
    'Classical (Markowitz, HRP) and Deep RL portfolio optimizers behind a production-grade FastAPI service.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
