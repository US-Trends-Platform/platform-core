import React from 'react';
import { Sidebar } from './components/Sidebar';
import { Timeline } from './components/Timeline';

export default function HomePage() {
  return (
    <div className="flex w-full min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Timeline />
        <main className="flex-1 p-6 space-y-6 overflow-y-auto" id="main-content">
          <section className="border border-dashed border-slate-800 rounded-lg p-12 text-center bg-slate-900/30">
            <h2 className="text-xl font-semibold text-slate-300 mb-2">
              Metric Dashboard Shell
            </h2>
            <p className="text-slate-400 text-sm max-w-md mx-auto">
              Select a domain from the sidebar or adjust the timeline above to view historical trend metrics and visualizations.
            </p>
          </section>
        </main>
      </div>
    </div>
  );
}
