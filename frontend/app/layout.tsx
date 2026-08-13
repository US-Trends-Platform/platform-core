import React from 'react';

export const metadata = {
  title: 'US Socioeconomic, Political & Agricultural Trends Platform',
  description: 'Evidence-based historical data tracking 1776–present.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 min-h-screen antialiased flex">
        {children}
      </body>
    </html>
  );
}
