import { useState } from 'react';
import { ChevronDown, ExternalLink } from 'lucide-react';
import type { Citation } from '../../types/ask';

// For chat page

interface CitationListProps {
  citations: Citation[];
}

const COLLAPSED_COUNT = 3;

export default function CitationList({ citations }: CitationListProps) {
  const [expanded, setExpanded] = useState(false);

  if (citations.length === 0) return null;

  const hasOverflow = citations.length > COLLAPSED_COUNT;
  const visible =
    expanded || !hasOverflow
      ? citations
      : citations.slice(0, COLLAPSED_COUNT);
  const hiddenCount = citations.length - COLLAPSED_COUNT;

  return (
    <div className="mt-3">
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-[11px] font-medium uppercase tracking-wide text-text-mute">
          Sources
        </span>
        <span className="text-[11px] text-text-mute">{citations.length}</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {visible.map((c, i) => (
          <a
            key={c.item_id}
            href={c.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group inline-flex items-center gap-1.5 rounded-full bg-bg-elev border border-border px-2.5 py-1 text-[11.5px] text-text-dim hover:border-border-hover hover:text-text transition-colors duration-150"
          >
            <span className="flex items-center justify-center w-4 h-4 rounded-full bg-accent/15 text-accent text-[9px] font-mono font-medium shrink-0">
              {i + 1}
            </span>
            <span className="font-medium">{c.source}</span>
            <span className="truncate max-w-[180px]">{c.title}</span>
            <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-60 transition-opacity shrink-0" />
          </a>
        ))}
        {hasOverflow && (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="inline-flex items-center gap-1 rounded-full border border-border px-2.5 py-1 text-[11.5px] text-text-dim hover:border-border-hover hover:text-text transition-colors duration-150"
          >
            {expanded ? 'Show less' : `+${hiddenCount} more`}
            <ChevronDown
              className={`w-3 h-3 transition-transform duration-150 ${
                expanded ? 'rotate-180' : ''
              }`}
            />
          </button>
        )}
      </div>
    </div>
  );
}
