import SectionHead from '../ui/SectionHead';
import { steps } from '../../lib/steps';

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="px-5 md:px-8 py-24 border-t border-border">
      <div className="mx-auto max-w-container">
        <SectionHead
          kicker="How it works"
          title={
            <>
              Everything you need to keep up with tech —{' '}
              <span className="accent-italic">in one place.</span>
            </>
          }
          description="Three things happen every morning before you open your laptop. None of them require you to open twelve tabs."
          align="left"
        />

        <div className="mt-14 rounded-2xl border border-border bg-bg-card/40 grid grid-cols-1 md:grid-cols-3 overflow-hidden">
          {steps.map((step, i) => {
            const Icon = step.icon;
            const last = i === steps.length - 1;
            return (
              <div
                key={step.number}
                className={`p-8 md:p-10 flex flex-col ${
                  last ? '' : 'border-b md:border-b-0 md:border-r border-border'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent" />
                  <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-text-dim">
                    Step {step.number}
                  </span>
                </div>
                <div className="mt-6 w-10 h-10 rounded-lg bg-bg-elev border border-border flex items-center justify-center">
                  <Icon className="w-[18px] h-[18px] text-text" strokeWidth={1.75} />
                </div>
                <h3 className="mt-6 text-[22px] font-medium tracking-[-0.02em] text-text">
                  {step.title}
                </h3>
                <p className="mt-3 text-[14.5px] leading-[1.55] text-text-dim">
                  {step.body}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
