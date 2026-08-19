import { Sidebar } from './components/Sidebar';
import { Timeline } from './components/Timeline';

export default function Home() {
  return (
    <div className="flex min-h-screen">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:bg-ink focus:text-paper focus:px-4 focus:py-2 focus:text-sm focus:rounded"
      >
        Skip to main content
      </a>
      <Sidebar />
      <main id="main-content" className="flex-1 p-6">
        <Timeline />
        <p className="mt-6 text-sm text-slate-400">
          Domain dashboards connect here in Phase C.
        </p>
      </main>
    </div>
  );
}
