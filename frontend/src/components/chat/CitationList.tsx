import { ExternalLink } from 'lucide-react';
import type { Citation } from '../../types/ask';

// For chat page

interface CitationListProps {
  citations: Citation[];
}

export default function CitationList({ citations }: CitationListProps) {
  if (citations.length === 0) return null;

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {citations.map((c, i) => (
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
    </div>
  );
}
