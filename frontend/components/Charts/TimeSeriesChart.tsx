// components/charts/TimeSeriesChart.tsx
// Wired for Phase C: pass real observations and it renders. Empty/undefined
// data renders the "awaiting data" empty state instead of a broken chart.
 
'use client';
 
import { useEffect, useRef } from 'react';
import type { ConfidenceTier } from '../Confidence/ConfidenceBadge';
import { TIER_META } from '../Confidence/ConfidenceBadge';
 
export interface Observation {
  date: string; // ISO date
  value: number;
}
 
export interface Series {
  tier: ConfidenceTier;
  label: string;
  observations: Observation[];
}
 
interface TimeSeriesChartProps {
  metricName: string;
  units: string;
  series?: Series[]; // undefined/empty = Phase B empty state
}
 
// Confidence tier -> line dash pattern (never rely on color alone, per ADR-005 / WCAG)
const LINE_DASH: Record<ConfidenceTier, number[] | undefined> = {
  OFFICIAL_MEASUREMENT: undefined, // solid
  ADMINISTRATIVE_RECORD: undefined, // solid
  SURVEY_ESTIMATE: [6, 4], // dashed
  HISTORICAL_RECONSTRUCTION: [6, 4], // dashed
  ACADEMIC_ESTIMATE: [2, 3], // dotted
  MODELED_DERIVED: [2, 3], // dotted
  UNKNOWN: [2, 3],
};
 
export function TimeSeriesChart({ metricName, units, series }: TimeSeriesChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
 
  const hasData = series && series.length > 0 && series.some((s) => s.observations.length > 0);
 
  useEffect(() => {
    if (!hasData || !containerRef.current) return;
 
    let disposed = false;
    // Lazy-load echarts client-side only
    import('echarts').then((echarts) => {
      if (disposed || !containerRef.current) return;
      const chart = echarts.init(containerRef.current);
      chartRef.current = chart;
 
      chart.setOption({
        grid: { left: 48, right: 20, top: 30, bottom: 40 },
        legend: { show: (series?.length ?? 0) > 1, top: 0 },
        tooltip: {
          trigger: 'axis',
          formatter: (params: any[]) =>
            params
              .map((p) => `${p.seriesName}<br/>${p.axisValueLabel}: ${p.value[1]} ${units}<br/><small>${p.seriesName}</small>`)
              .join('<br/>'),
        },
        xAxis: { type: 'time' },
        yAxis: { type: 'value', name: units, nameTextStyle: { fontSize: 11 } },
        series: (series ?? []).map((s) => ({
          name: `${s.label} — ${TIER_META[s.tier].label}`,
          type: 'line',
          data: s.observations.map((o) => [o.date, o.value]),
          lineStyle: LINE_DASH[s.tier] ? { type: 'dashed' } : { type: 'solid' },
          symbol: 'circle',
          symbolSize: 4,
        })),
      });
 
      const resize = () => chart.resize();
      window.addEventListener('resize', resize);
      return () => window.removeEventListener('resize', resize);
    });
 
    return () => {
      disposed = true;
      chartRef.current?.dispose();
    };
  }, [hasData, series, units]);
 
  if (!hasData) {
    return (
      <div
        role="img"
        aria-label={`Chart for ${metricName}: data not yet available, pending Phase C ingestion`}
        className="h-[220px] border border-dashed border-slate-line rounded flex items-center justify-center text-slate text-sm bg-[repeating-linear-gradient(135deg,transparent,transparent_8px,#E3E5DF_8px,#E3E5DF_9px)]"
      >
        Awaiting data — connected in Phase C
      </div>
    );
  }
 
  return (
    <div>
      <div ref={containerRef} className="h-[220px]" role="img" aria-label={`Time series chart: ${metricName}`} />
      {/* Accessible data-table alternative, required alongside every chart per FR-17 */}
      <details className="mt-2 text-xs">
        <summary className="cursor-pointer text-slate">View as data table</summary>
        <table className="w-full mt-2 text-xs border-collapse">
          <caption className="sr-only">{metricName} — tabular data</caption>
          <thead>
            <tr>
              <th className="text-left border-b border-slate-line py-1">Date</th>
              {series?.map((s) => (
                <th key={s.label} className="text-left border-b border-slate-line py-1">{s.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {series?.[0]?.observations.map((o, i) => (
              <tr key={o.date}>
                <td className="py-1">{o.date}</td>
                {series.map((s) => (
                  <td key={s.label} className="py-1">{s.observations[i]?.value ?? '—'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
 