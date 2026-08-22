MetricCardStub.tsx
// components/dashboard/MetricCardStub.tsx
// Phase B: structural placeholder only. Phase C wires in real observations.
 
import { ConfidenceBadge, ConfidenceTier } from '../Confidence/ConfidenceBadge';
 
interface MetricCardStubProps {
  name: string;
  tier: ConfidenceTier;
  methodologySummary: string;
}
 
export function MetricCardStub({ name, tier, methodologySummary }: MetricCardStubProps) {
  return (
    <article className="bg-paper-raised border border-slate-line rounded px-4.5 pt-4.5 pb-4">
      <ConfidenceBadge tier={tier} />
      <h3 className="text-[15px] font-semibold mt-1.5 mb-0">{name}</h3>
 
      <div
        className="h-[90px] my-3 border border-dashed border-slate-line rounded flex items-center justify-center text-slate text-xs"
        role="img"
        aria-label={`Chart for ${name}: data not yet available, pending Phase C ingestion`}
      >
        Chart stub — data pending
      </div>
 
      {/* Methodology panel: non-dismissible per PRD FR-21 — always visible, never collapsible */}
      <div className="mt-3 pt-2.5 border-t border-slate-line text-[11px] text-slate">
        {methodologySummary}
      </div>
    </article>
  );
}
 