'use client';

import React, { useState } from 'react';

export const Timeline: React.FC = () => {
  const [startYear, setStartYear] = useState(1776);
  const [endYear, setEndYear] = useState(new Date().getFullYear());

  return (
    <header 
      className="bg-slate-800 text-slate-100 p-4 border-b border-slate-700 flex flex-col md:flex-row items-center justify-between gap-4"
      role="banner"
    >
      <div className="flex items-center gap-2">
        <h1 className="text-lg font-semibold text-slate-100">Historical Timeline</h1>
        <span className="text-xs px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 font-mono border border-blue-700/50">
          {startYear} – {endYear}
        </span>
      </div>
      <div className="flex items-center gap-4 text-sm">
        <label className="flex items-center gap-2">
          <span>Start:</span>
          <input 
            type="number" 
            min="1776" 
            max={endYear}
            value={startYear}
            onChange={(e) => setStartYear(Number(e.target.value))}
            className="bg-slate-900 border border-slate-700 rounded px-2 py-1 w-20 text-center focus:ring-2 focus:ring-blue-500 outline-none"
            aria-label="Start Year"
          />
        </label>
        <label className="flex items-center gap-2">
          <span>End:</span>
          <input 
            type="number" 
            min={startYear} 
            max={new Date().getFullYear()}
            value={endYear}
            onChange={(e) => setEndYear(Number(e.target.value))}
            className="bg-slate-900 border border-slate-700 rounded px-2 py-1 w-20 text-center focus:ring-2 focus:ring-blue-500 outline-none"
            aria-label="End Year"
          />
        </label>
      </div>
    </header>
  );
};
