// components/navigation/DomainNav.tsx
'use client';
 
import Link from 'next/link';
import { usePathname } from 'next/navigation';
 
const DOMAINS = [
  { slug: 'demographics', name: 'Demographics' },
  { slug: 'immigration', name: 'Immigration' },
  { slug: 'employment', name: 'Employment' },
  { slug: 'economy', name: 'Economy' },
  { slug: 'inflation-cost-of-living', name: 'Inflation & Cost of Living' },
  { slug: 'healthcare', name: 'Healthcare' },
  { slug: 'education', name: 'Education' },
  { slug: 'agriculture-farming', name: 'Agriculture & Farming' },
  { slug: 'politics-government', name: 'Politics & Government' },
  { slug: 'historical-events-legislation', name: 'Historical Events' },
] as const;
 
export function DomainNav() {
  const pathname = usePathname();
 
  return (
    <nav aria-label="Data domains" className="border-r border-slate-line bg-paper-raised py-6 hidden md:block">
      <h2 className="font-mono text-[11px] uppercase tracking-widest text-slate px-5 mb-3">
        Domains
      </h2>
      <ul className="list-none m-0 p-0">
        {DOMAINS.map((d) => {
          const isActive = pathname?.startsWith(`/domains/${d.slug}`);
          return (
            <li key={d.slug}>
              <Link
                href={`/domains/${d.slug}`}
                aria-current={isActive ? 'page' : undefined}
                className={`flex items-center gap-2.5 px-5 py-2 text-sm no-underline border-l-[3px] transition-colors
                  ${isActive
                    ? 'border-brass text-brass-dark bg-paper'
                    : 'border-transparent text-ink hover:bg-paper hover:border-slate-line'}`}
              >
                <span
                  aria-hidden="true"
                  className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${isActive ? 'bg-brass' : 'bg-slate-line'}`}
                />
                {d.name}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
 