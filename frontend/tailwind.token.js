// Canonical confidence-tier design tokens for the US Trends Platform.
// Keep this file synchronized with frontend/tailwind.config.ts.

module.exports = {
  colors: {
    ink: '#1B1D1F',
    paper: '#EEF0EC',
    'paper-raised': '#F7F8F5',
    brass: '#A6742C',
    'brass-dark': '#7C5A20',
    slate: '#64748B',
    'slate-line': '#E3E5DF',
    tier: {
      official: '#2F6B3C',
      admin: '#2C5F8A',
      survey: '#A6742C',
      historical: '#8B4A9C',
      academic: '#C4622D',
      modeled: '#5A5F66',
      unknown: '#9A9A9A',
    },
  },
  fontFamily: {
    display: ['Fraunces', 'serif'],
    sans: ['IBM Plex Sans', 'sans-serif'],
    mono: ['IBM Plex Mono', 'monospace'],
  },
};
