import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User } from 'lucide-react';
import type { ChatMessage } from '../../types/ask';
import CitationList from './CitationList';

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const content = linkInlineCitations(message.content, message.citations);

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="flex items-start gap-3 max-w-[75%]">
          <div className="rounded-2xl rounded-tr-sm bg-bg-elev border border-border px-4 py-3">
            <p className="text-[14.5px] text-text leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          </div>
          <div className="flex items-center justify-center w-7 h-7 rounded-full bg-bg-elev border border-border shrink-0 mt-0.5">
            <User className="w-3.5 h-3.5 text-text-dim" />
          </div>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex justify-start">
      <div className="flex items-start gap-3 max-w-[80%]">
        <div className="flex items-center justify-center w-7 h-7 rounded-full bg-accent/15 shrink-0 mt-0.5">
          <span className="w-2 h-2 rounded-full bg-accent" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="markdown-body text-[14.5px] text-text leading-relaxed">
            {message.content ? (
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  a: ({ href, children }) => {
                    const marker = /^\[(\d+)\]$/.exec(String(children));
                    const citation = marker
                      ? message.citations?.[Number(marker[1]) - 1]
                      : undefined;

                    return (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label={
                          citation
                            ? `Source ${marker?.[1]}: ${citation.title}`
                            : undefined
                        }
                        title={citation?.title}
                      >
                        {marker ? (
                          <sup className="font-mono text-[10px] font-semibold">
                            {children}
                          </sup>
                        ) : (
                          children
                        )}
                      </a>
                    );
                  },
                }}
              >
                {content}
              </ReactMarkdown>
            ) : message.isStreaming ? (
              <span className="inline-flex items-center gap-1.5 text-text-mute">
                <span className="w-1.5 h-1.5 rounded-full bg-accent animate-dot-pulse" />
                Thinking...
              </span>
            ) : null}
            {message.isStreaming && message.content && (
              <span className="inline-block w-[2px] h-[16px] bg-accent ml-0.5 animate-pulse align-middle" />
            )}
          </div>
          {!message.isStreaming && message.citations && (
            <CitationList citations={message.citations} />
          )}
        </div>
      </div>
    </div>
  );
}

function linkInlineCitations(
  content: string,
  citations: ChatMessage['citations'],
): string {
  if (!citations?.length) return content;

  return content.replace(/(?<!\[)\[(\d+)\](?!\()/g, (marker, rawNumber: string) => {
    const citation = citations[Number(rawNumber) - 1];
    if (!citation || !isSafeExternalUrl(citation.url)) return marker;

    const destination = citation.url.replace(/</g, '%3C').replace(/>/g, '%3E');
    return `[[${rawNumber}]](<${destination}>)`;
  });
}

function isSafeExternalUrl(value: string): boolean {
  try {
    return ['http:', 'https:'].includes(new URL(value).protocol);
  } catch {
    return false;
  }
}
