import { Sidebar } from './components/Sidebar';
import { Timeline } from './components/Timeline';
import { ConfidenceBadge } from '@/components/Confidence/ConfidenceBadge';
import { GdpChart } from './components/GdpChart';
import { UnemploymentChart } from './components/UnemploymentChart';

export default function Home() {
  return (
    <div className="flex min-h-screen">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:bg-ink focus:text-paper focus:px-4 focus:py-2 focus:text-sm focus:rounded">
        Skip to main content
      </a>
      <Sidebar />
      <main id="main-content" className="flex-1 p-6">
        <Timeline />
        <div className="flex gap-2 flex-wrap mt-4">
          <ConfidenceBadge tier="OFFICIAL_MEASUREMENT" />
          <ConfidenceBadge tier="ADMINISTRATIVE_RECORD" />
          <ConfidenceBadge tier="SURVEY_ESTIMATE" />
          <ConfidenceBadge tier="HISTORICAL_RECONSTRUCTION" />
          <ConfidenceBadge tier="ACADEMIC_ESTIMATE" />
          <ConfidenceBadge tier="MODELED_DERIVED" />
          <ConfidenceBadge tier="UNKNOWN" />
        </div>
        <GdpChart />
        <UnemploymentChart />
      </main>
    </div>
  );
}
