import React from 'react';

const DOMAINS = [
  'Demographics',
  'Economy',
  'Labor & Employment',
  'Agriculture & Land',
  'Politics & Governance',
  'Healthcare & Health',
  'Education',
  'Housing & Infrastructure',
  'Trade & Industry',
  'Immigration & Migration'
];

export const Sidebar: React.FC = () => {
  return (
    <aside 
      className="w-64 bg-slate-900 text-slate-100 h-screen p-4 flex flex-col border-r border-slate-800"
      aria-label="Domain Navigation"
    >
      <h2 className="text-xl font-bold mb-6 text-slate-50 tracking-wide">
        US Trends Platform
      </h2>
      <nav aria-label="Content Domains">
        <ul className="space-y-1">
          {DOMAINS.map((domain) => (
            <li key={domain}>
              <button className="w-full text-left px-3 py-2 rounded-md hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium transition-colors">
                {domain}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};
