import SectionHead from '../ui/SectionHead';
import Card from '../ui/Card';
import { cards } from '../../lib/cards';

export default function WhatsInside() {
  return (
    <section id="whats-inside" className="px-5 md:px-8 py-24 border-t border-border">
      <div className="mx-auto max-w-container">
        <SectionHead
          kicker="What's inside"
          title={
            <>
              Four topics. <span className="accent-italic">Zero noise.</span>
            </>
          }
          description="Every item is classified, ranked, and linked back to the original source. Skip what you don't care about."
          align="left"
        />

        <div className="mt-14 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {cards.map((c) => {
            const tagClasses =
              c.tint === 'amber'
                ? 'bg-accent/10 text-accent'
                : 'bg-green/15 text-green';
            return (
              <Card key={c.title}>
                <span
                  className={`inline-flex items-center rounded-full px-2.5 py-1 font-mono text-[10.5px] uppercase tracking-[0.14em] ${tagClasses}`}
                >
                  {c.tag}
                </span>
                <h4 className="mt-5 text-[18px] font-medium tracking-[-0.015em] text-text">
                  {c.title}
                </h4>
                <p className="mt-2.5 text-[14px] leading-[1.55] text-text-dim">{c.body}</p>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}
