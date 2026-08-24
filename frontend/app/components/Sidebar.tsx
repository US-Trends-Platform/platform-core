import React from 'react';

const DOMAINS = [
  { slug: 'demographics', name: 'Demographics' },
  { slug: 'employment', name: 'Employment' },
  { slug: 'economy', name: 'Economy' },
  { slug: 'inflation-cost-of-living', name: 'Inflation & Cost of Living' },
  { slug: 'healthcare', name: 'Healthcare' },
  { slug: 'education', name: 'Education' },
  { slug: 'politics-government', name: 'Politics & Government' },
  { slug: 'immigration', name: 'Immigration' },
  { slug: 'agriculture-farming', name: 'Agriculture & Farming' },
  { slug: 'historical-events-legislation', name: 'Historical Events & Legislation' },
];

export const Sidebar: React.FC = () => {
  return (
    <aside
      className="w-64 bg-slate-900 text-slate-100 h-screen p-4 flex flex-col border-r border-slate-800"
      aria-label="Domain Navigation"
    >
      <h2 className="text-xl font-bold text-slate-50 tracking-wide">
        US Trends Observatory
      </h2>
      <p className="text-xs text-slate-400 mb-6 mt-1">
        Evidence based infrastructure tracking data trends — 1776 to present
      </p>
      <nav aria-label="Content Domains">
        <ul className="space-y-1">
          {DOMAINS.map((domain) => (
            <li key={domain.slug}>
              <button className="w-full text-left px-3 py-2 rounded-md hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium transition-colors">
                {domain.name}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};
