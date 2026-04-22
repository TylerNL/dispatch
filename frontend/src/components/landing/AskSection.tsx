import { useRef, type FormEvent } from 'react';
import SectionHead from '../ui/SectionHead';
import { chips } from '../../lib/chips';

export default function AskSection() {
  const inputRef = useRef<HTMLInputElement>(null);
  const boxRef = useRef<HTMLDivElement>(null);

  const handleChip = (value: string) => {
    if (!inputRef.current) return;
    inputRef.current.value = value;
    inputRef.current.focus();
    boxRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    // TODO: POST to RAG endpoint and stream result below.
  };

  return (
    <section id="ask" className="px-5 md:px-8 py-24 border-t border-border">
      <div className="mx-auto max-w-container flex flex-col items-center">
        <SectionHead
          kicker="Ask the index"
          title={
            <>
              Don&apos;t scroll. <span className="accent-italic">Ask.</span>
            </>
          }
          description="Chat with everything dispatch indexed today, this week, or this year. Every answer cites its sources."
          align="center"
        />

        <div
          ref={boxRef}
          className="mt-14 w-full max-w-[780px] rounded-2xl bg-bg-card border border-border transition-colors duration-200 focus-within:border-accent"
        >
          <div className="flex items-center justify-between px-5 pt-4 pb-3 border-b border-border">
            <span className="font-mono text-[11.5px] uppercase tracking-[0.14em] text-text-mute">
              dispatch / ask
            </span>
            <span className="inline-flex items-center gap-2 font-mono text-[11.5px] text-text-mute">
              <span className="w-1.5 h-1.5 rounded-full bg-green animate-dot-pulse" />
              2,431 items indexed today
            </span>
          </div>
          <form
            onSubmit={handleSubmit}
            className="flex items-center gap-3 px-5 py-4"
          >
            <span className="text-accent text-[18px] font-medium select-none">?</span>
            <input
              ref={inputRef}
              type="text"
              placeholder="What did Anthropic ship this week?"
              className="flex-1 bg-transparent outline-none text-[16px] text-text placeholder:text-text-mute"
            />
            <button
              type="submit"
              className="inline-flex items-center gap-1 rounded-full bg-accent text-bg hover:bg-accent-hover px-3.5 h-8 text-[13px] font-medium transition-colors duration-150"
            >
              Ask →
            </button>
          </form>
        </div>

        <div className="mt-6 flex flex-wrap items-center justify-center gap-2 max-w-[820px]">
          {chips.map((chip) => (
            <button
              key={chip}
              type="button"
              onClick={() => handleChip(chip)}
              className="rounded-full bg-bg-elev border border-border px-3 py-1.5 text-[12.5px] text-text-dim hover:border-border-hover hover:text-text transition-colors duration-150"
            >
              {chip}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
