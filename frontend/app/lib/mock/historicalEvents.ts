export interface HistoricalEvent {
  slug: string;
  title: string;
  year: number;
  category: 'wars' | 'economic-crises' | 'legislation' | 'financial-system' | 'agricultural-policy';
}

export const MOCK_EVENTS: HistoricalEvent[] = [
  { slug: 'fed-created', title: 'Federal Reserve created', year: 1913, category: 'financial-system' },
  { slug: 'great-depression', title: 'Great Depression begins', year: 1929, category: 'economic-crises' },
  { slug: 'ss-act', title: 'Social Security Act', year: 1935, category: 'legislation' },
  { slug: 'ina-1965', title: 'Immigration and Nationality Act', year: 1965, category: 'legislation' },
  { slug: 'nixon-shock', title: 'Nixon Shock — gold standard suspended', year: 1971, category: 'financial-system' },
  { slug: 'ira-1980', title: 'Federal Crop Insurance Reform', year: 1980, category: 'agricultural-policy' },
  { slug: 'irca-1986', title: 'Immigration Reform and Control Act', year: 1986, category: 'legislation' },
  { slug: 'financial-crisis-2008', title: '2008 Financial Crisis', year: 2008, category: 'economic-crises' },
  { slug: 'aca-2010', title: 'Affordable Care Act', year: 2010, category: 'legislation' },
  { slug: 'covid-recession', title: 'COVID Recession', year: 2020, category: 'economic-crises' },
];

export const TIMELINE_START = 1776;
export const TIMELINE_END = new Date().getFullYear();
