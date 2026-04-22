import SectionLabel from '../ui/SectionLabel';
import { sources } from '../../lib/sources';

export default function SourcesStrip() {
  return (
    <section className="px-5 md:px-8 py-16 border-t border-border">
      <div className="mx-auto max-w-container flex flex-col items-center">
        <SectionLabel className="mb-6">Indexing, right now, from</SectionLabel>
        <ul className="flex flex-wrap items-center justify-center gap-2.5">
          {sources.map((s) => (
            <li key={s}>
              <span className="inline-flex items-center gap-2 rounded-full bg-bg-elev border border-border px-3.5 py-1.5 text-[13px] text-text-dim hover:border-border-hover hover:text-text transition-colors duration-150">
                <span className="relative flex w-1.5 h-1.5">
                  <span className="absolute inset-0 rounded-full bg-green animate-dot-pulse" />
                  <span className="relative rounded-full bg-green w-1.5 h-1.5" />
                </span>
                {s}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
