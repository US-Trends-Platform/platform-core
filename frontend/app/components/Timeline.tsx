'use client';

import { useState, useCallback, useRef } from 'react';
import { MOCK_EVENTS, TIMELINE_START, TIMELINE_END, HistoricalEvent } from '../lib/mock/historicalEvents';

interface TimelineProps {
  onRangeChange?: (start: number, end: number) => void;
  onEventSelect?: (event: HistoricalEvent) => void;
}

const CENTURY_MARKS = [1776, 1837, 1913, 1945, 1990, TIMELINE_END];

function yearToPercent(year: number) {
  return ((year - TIMELINE_START) / (TIMELINE_END - TIMELINE_START)) * 100;
}

export function Timeline({ onRangeChange, onEventSelect }: TimelineProps) {
  const [selectedYear, setSelectedYear] = useState(TIMELINE_END);
  const [activeEvent, setActiveEvent] = useState<HistoricalEvent | null>(null);
  const trackRef = useRef<HTMLDivElement>(null);

  const commitYear = useCallback(
    (year: number) => {
      const clamped = Math.min(TIMELINE_END, Math.max(TIMELINE_START, year));
      setSelectedYear(clamped);
      onRangeChange?.(TIMELINE_START, clamped);
    },
    [onRangeChange]
  );

  function handleKeyDown(e: React.KeyboardEvent) {
    const step = e.shiftKey ? 10 : 1;
    if (e.key === 'ArrowRight') { commitYear(selectedYear + step); e.preventDefault(); }
    if (e.key === 'ArrowLeft') { commitYear(selectedYear - step); e.preventDefault(); }
    if (e.key === 'Home') { commitYear(TIMELINE_START); e.preventDefault(); }
    if (e.key === 'End') { commitYear(TIMELINE_END); e.preventDefault(); }
  }

  function handleTrackClick(e: React.MouseEvent) {
    if (!trackRef.current) return;
    const rect = trackRef.current.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    commitYear(Math.round(TIMELINE_START + pct * (TIMELINE_END - TIMELINE_START)));
  }

  function selectEvent(event: HistoricalEvent) {
    setActiveEvent(event);
    onEventSelect?.(event);
  }

  return (
    <section aria-label="Historical timeline, 1776 to present" className="bg-ink text-paper rounded px-6 pt-5 pb-4 relative overflow-hidden">
      <h2 className="font-display text-[17px] font-normal m-0 mb-1">Timeline</h2>
      <p className="font-mono text-xs text-[#B7BDB6] mb-4">
        {TIMELINE_START} — {selectedYear} · drag or use arrow keys · event markers show context, not causation
      </p>

      <div
        ref={trackRef}
        role="slider"
        tabIndex={0}
        aria-label="Select end year for data range"
        aria-valuemin={TIMELINE_START}
        aria-valuemax={TIMELINE_END}
        aria-valuenow={selectedYear}
        aria-valuetext={`${selectedYear}`}
        onKeyDown={handleKeyDown}
        onClick={handleTrackClick}
        className="relative h-[70px] mx-1 border-t border-[#3A3D3A] cursor-pointer"
      >
        {CENTURY_MARKS.map((year) => (
          <div key={year}>
            <div
              className="absolute top-0 w-px h-[22px] bg-[#6B6F6A]"
              style={{ left: `${yearToPercent(year)}%` }}
              aria-hidden="true"
            />
            <div
              className="absolute top-[26px] font-mono text-[10px] text-[#8A8E86] -translate-x-1/2"
              style={{ left: `${yearToPercent(year)}%` }}
              aria-hidden="true"
            >
              {year}
            </div>
          </div>
        ))}

        <div
          className="absolute top-0 w-0.5 h-[70px] bg-brass"
          style={{ left: `${yearToPercent(selectedYear)}%` }}
          aria-hidden="true"
        />

        {MOCK_EVENTS.map((event) => (
          <button
            key={event.slug}
            type="button"
            onClick={(e) => { e.stopPropagation(); selectEvent(event); }}
            aria-label={`Event: ${event.title}, ${event.year}`}
            className="absolute -top-1.5 w-2 h-2 rounded-full bg-brass -translate-x-1/2 hover:scale-125 transition-transform"
            style={{ left: `${yearToPercent(event.year)}%` }}
            title={`${event.title} (${event.year})`}
          />
        ))}
      </div>

      <p className="mt-3.5 text-[11px] font-mono text-[#8A8E86]">
        Keyboard: ←/→ adjust by year, Shift+←/→ by decade, Home/End for range bounds · gaps in underlying data render as visible white space, never interpolated
      </p>

      {activeEvent && (
        <div role="status" aria-live="polite" className="mt-3 text-sm bg-paper-raised text-ink rounded px-3 py-2">
          <strong>{activeEvent.title}</strong> ({activeEvent.year}) — {activeEvent.category.replace('-', ' ')}
        </div>
      )}
    </section>
  );
}
