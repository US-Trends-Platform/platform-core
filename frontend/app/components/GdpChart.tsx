'use client';

import { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';

interface GdpResponse {
  metric: string;
  units: string;
  observations: { date: string; value: number; confidence_tier: string }[];
  missing: { date: string; reason: string; explanation: string }[];
}

export function GdpChart() {
  const [data, setData] = useState<GdpResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/gdp')
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
        Could not load GDP data: {error}. Is the backend running? (uvicorn app.main:app --reload)
      </div>
    );
  }

  if (!data) {
    return <div className="mt-6 text-sm text-slate">Loading GDP data...</div>;
  }

  const option = {
    title: { text: 'US Nominal GDP', subtext: `Source: FRED · ${data.units.replace(/_/g, ' ')}`, textStyle: { fontFamily: 'var(--font-display)' } },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.observations.map((o) => o.date) },
    yAxis: { type: 'value', name: data.units },
    series: [
      {
        name: 'GDP (Official Measurement)',
        type: 'line',
        data: data.observations.map((o) => o.value),
        smooth: true,
        lineStyle: { color: '#2E6B3E' },
        itemStyle: { color: '#2E6B3E' },
      },
    ],
  };

  return (
    <div className="mt-6">
      <ReactECharts option={option} style={{ height: 400 }} />
      {data.missing.length > 0 && (
        <p className="mt-2 text-xs text-slate">
          {data.missing.length} quarter(s) not shown — no data available: {data.missing.map((m) => m.date).join(', ')}
        </p>
      )}
    </div>
  );
}
