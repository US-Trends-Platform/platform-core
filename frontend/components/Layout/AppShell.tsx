import { ReactNode } from 'react';
import Link from 'next/link';
import { DomainNav } from '../Navigation/DomainNav';

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-paper text-ink font-sans">
      
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:bg-ink focus:text-paper focus:px-5 focus:py-3 focus:text-sm"
      >
        Skip to main content
      </a>

      <header className="flex items-center justify-between px-7 py-4.5 border-b border-slate-line bg-paper-raised">
        <div>
          <Link href="/" className="font-display font-semibold text-xl no-underline text-ink">
            US Trends<span className="text-brass">.</span>Observatory
          </Link>
          <div className="font-mono text-[11px] uppercase tracking-wide text-slate mt-0.5">
            Evidence based infrastructure tracking data trends — 1776 to present
          </div>
        </div>
        <nav aria-label="Primary" className="flex gap-4.5 text-sm">
          <Link href="/methodology" className="text-ink no-underline hover:border-b hover:border-brass">Methodology</Link>
          <Link href="/sources" className="text-ink no-underline hover:border-b hover:border-brass">Sources</Link>
          <Link href="/about" className="text-ink no-underline hover:border-b hover:border-brass">About</Link>
        </nav>
      </header>

      <div className="grid md:grid-cols-[240px_1fr] min-h-[calc(100vh-73px)]">
        <DomainNav />
        <main id="main-content" className="px-8 py-7 pb-16">
          {children}
        </main>
      </div>
    </div>
  );
}