// components/confidence/ConfidenceBadge.tsx
// Per ADR-005: every observation has exactly one confidence tier.
// Color-blind safe by design — tier is always conveyed by label text +
// dot icon + (on charts) line style, never by color alone.
 
export type ConfidenceTier =
  | 'OFFICIAL_MEASUREMENT'
  | 'ADMINISTRATIVE_RECORD'
  | 'SURVEY_ESTIMATE'
  | 'HISTORICAL_RECONSTRUCTION'
  | 'ACADEMIC_ESTIMATE'
  | 'MODELED_DERIVED'
  | 'UNKNOWN';
 
const TIER_META: Record<
  ConfidenceTier,
  { label: string; className: string; lineStyle: string; description: string }
> = {
  OFFICIAL_MEASUREMENT: {
    label: 'Official',
    className: 'text-tier-official border-tier-official',
    lineStyle: 'solid',
    description: 'Directly measured by a government agency',
  },
  ADMINISTRATIVE_RECORD: {
    label: 'Administrative Record',
    className: 'text-tier-admin border-tier-admin',
    lineStyle: 'solid',
    description: 'Derived from agency administrative records',
  },
  SURVEY_ESTIMATE: {
    label: 'Survey Estimate',
    className: 'text-tier-survey border-tier-survey',
    lineStyle: 'dashed',
    description: 'Sampled government survey (e.g. Current Population Survey)',
  },
  HISTORICAL_RECONSTRUCTION: {
    label: 'Historical Reconstruction',
    className: 'text-tier-historical border-tier-historical',
    lineStyle: 'dashed',
    description: 'Estimated via historical/economic research',
  },
  ACADEMIC_ESTIMATE: {
    label: 'Academic Estimate',
    className: 'text-tier-academic border-tier-academic',
    lineStyle: 'dotted',
    description: 'Peer-reviewed estimation',
  },
  MODELED_DERIVED: {
    label: 'Modeled/Derived',
    className: 'text-tier-modeled border-tier-modeled',
    lineStyle: 'dotted',
    description: 'Calculated from other tracked metrics',
  },
  UNKNOWN: {
    label: 'Unknown',
    className: 'text-tier-unknown border-tier-unknown',
    lineStyle: 'dotted',
    description: 'Confidence classification not yet assigned — not published without review',
  },
};
 
export function ConfidenceBadge({ tier }: { tier: ConfidenceTier }) {
  const meta = TIER_META[tier];
  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wide px-2 py-0.5 rounded-full border ${meta.className}`}
      title={meta.description}
      role="img"
      aria-label={`Confidence tier: ${meta.label}. ${meta.description}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" aria-hidden="true" />
      {meta.label}
    </span>
  );
}
 
export { TIER_META }; 