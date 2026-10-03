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
              <span className="inline-flex items-center gap-2 rounded-md border border-border px-3.5 py-1.5 text-[13px] text-text-dim hover:border-border-hover hover:text-text transition-colors duration-150">
                <span className="w-1 h-1 bg-text-mute" />
                {s}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
