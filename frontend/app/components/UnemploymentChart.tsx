'use client';

import { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';

interface SeriesResponse {
  metric: string;
  units: string;
  observations: { date: string; value: number; confidence_tier: string }[];
  missing: { date: string; reason: string; explanation: string }[];
}

export function UnemploymentChart() {
  const [data, setData] = useState<SeriesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/unemployment')
      .then((res) => {
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="mt-6 p-4 border border-dashed border-slate-line rounded text-sm text-slate">
        Could not load Unemployment data: {error}
      </div>
    );
  }

  if (!data) {
    return <div className="mt-6 text-sm text-slate">Loading Unemployment data...</div>;
  }

  const option = {
    title: { text: 'US Unemployment Rate', subtext: `Source: FRED · ${data.units}`, textStyle: { fontFamily: 'var(--font-display)' } },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.observations.map((o) => o.date) },
    yAxis: { type: 'value', name: data.units },
    series: [
      {
        name: 'Unemployment Rate (Survey Estimate)',
        type: 'line',
        data: data.observations.map((o) => o.value),
        smooth: true,
        lineStyle: { color: '#3D6B8C', type: 'dashed' },
        itemStyle: { color: '#3D6B8C' },
      },
    ],
  };

  return (
    <div className="mt-6">
      <ReactECharts option={option} style={{ height: 400 }} />
      {data.missing.length > 0 && (
        <p className="mt-2 text-xs text-slate">
          {data.missing.length} date(s) not shown — no data available: {data.missing.map((m) => m.date).join(', ')}
        </p>
      )}
    </div>
  );
}
