import { Check } from 'lucide-react';
import Button from '../ui/Button';

const metaItems = ['One email, 7 AM PT', 'Free forever', 'No tracking'];

export default function Hero() {
  return (
    <section
      id="signup"
      className="relative overflow-hidden px-5 md:px-8 pt-24 pb-[110px]"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-[120px] -translate-x-1/2 w-[900px] h-[520px] -z-0"
        style={{
          background:
            'radial-gradient(ellipse at center, rgba(232,163,61,0.14), transparent 70%)',
        }}
      />
      <div className="relative mx-auto max-w-container flex flex-col items-center text-center">
        <div className="animate-fade-up [animation-delay:0.05s]">
          <span className="inline-flex items-center gap-2 rounded-full bg-bg-elev border border-border px-3 py-1.5 text-[12.5px] text-text-dim">
            <span className="rounded-full bg-accent/15 text-accent px-2 py-0.5 text-[10.5px] font-mono uppercase tracking-[0.12em]">
              New
            </span>
            <span>Ask the index — now in beta</span>
          </span>
        </div>
        <h1
          className="mt-8 headline headline-tight text-text max-w-[1000px] animate-fade-up [animation-delay:0.15s]"
          style={{ fontSize: 'clamp(44px, 7.2vw, 88px)' }}
        >
          The tech news firehose,{' '}
          <span className="accent-italic">filtered</span> &amp;{' '}
          <span className="accent-italic">answered</span>.
        </h1>
        <p className="mt-6 text-[19px] leading-[1.5] text-text-dim max-w-[640px] animate-fade-up [animation-delay:0.25s]">
          One email every morning at 8 AM PT, built from everything that happened across
          Hacker News, arXiv, the labs, and the rest of the firehose — then ask it anything.
        </p>
        <div className="mt-9 flex flex-wrap items-center justify-center gap-3 animate-fade-up [animation-delay:0.35s]">
          <Button variant="accent">Get the digest →</Button>
          <a href="#how-it-works">
            <Button variant="ghost">See how it works</Button>
          </a>
        </div>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 font-mono text-[11.5px] text-text-mute uppercase tracking-[0.12em] animate-fade-up [animation-delay:0.45s]">
          {metaItems.map((item) => (
            <span key={item} className="inline-flex items-center gap-1.5">
              <Check className="w-3.5 h-3.5 text-green" strokeWidth={2.5} />
              {item}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
