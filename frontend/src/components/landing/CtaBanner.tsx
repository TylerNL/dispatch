import SectionLabel from '../ui/SectionLabel';
import Button from '../ui/Button';

export default function CtaBanner() {
  return (
    <section className="relative overflow-hidden px-5 md:px-8 pt-[120px] pb-[140px] border-t border-border">
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-[80px] -translate-x-1/2 w-[800px] h-[400px] -z-0"
        style={{
          background:
            'radial-gradient(ellipse at center, rgba(232,163,61,0.14), transparent 70%)',
        }}
      />
      <div className="relative mx-auto max-w-container flex flex-col items-center text-center">
        <SectionLabel className="mb-6">Start your morning better</SectionLabel>
        <h2
          className="headline headline-tight max-w-[1000px]"
          style={{ fontSize: 'clamp(40px, 5.6vw, 72px)' }}
        >
          Your timeline is <span className="accent-italic">reading</span> this. Are you?
        </h2>
        <div className="mt-9">
          <a href="#signup">
            <Button variant="accent">Get the digest →</Button>
          </a>
        </div>
      </div>
    </section>
  );
}
