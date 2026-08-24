import type { Config } from "tailwindcss";
const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Keep these confidence-tier token values in sync with frontend/tailwind.token.js.
        ink: "#1B1D1F",
        paper: "#EEF0EC",
        "paper-raised": "#F7F8F5",
        brass: "#A6742C",
        "brass-dark": "#7C5A20",
        slate: "#64748B",
        "slate-line": "#E3E5DF",
        tier: {
          official: "#2F6B3C",
          admin: "#2C5F8A",
          survey: "#A6742C",
          historical: "#8B4A9C",
          academic: "#C4622D",
          modeled: "#5A5F66",
          unknown: "#9A9A9A",
        },
      },
      fontFamily: {
        display: ['var(--font-display)', 'serif'],
        sans: ['var(--font-sans)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
    },
  },
  plugins: [],
};
export default config;