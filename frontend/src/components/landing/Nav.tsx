import { useEffect, useState } from 'react';
import Button from '../ui/Button';

const links = [
  { label: 'How it works', href: '#how-it-works' },
  { label: "What's inside", href: '#whats-inside' },
  { label: 'Ask', href: '#ask' },
  { label: 'Archive', href: '#archive' },
];

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-50 backdrop-blur-md bg-bg/70 transition-colors duration-200 ${
        scrolled ? 'border-b border-border' : 'border-b border-transparent'
      }`}
    >
      <div className="mx-auto max-w-container px-5 md:px-8 h-[64px] flex items-center justify-between">
        <a href="#" className="flex items-center gap-2.5 group">
          <span className="w-2 h-2 rounded-full bg-accent" />
          <span className="text-[17px] font-medium tracking-[-0.015em]">dispatch</span>
        </a>
        <nav className="hidden md:flex items-center gap-8">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-[14px] text-text-dim hover:text-text transition-colors duration-150"
            >
              {l.label}
            </a>
          ))}
        </nav>
        <a href="#signup">
          <Button variant="accent">Get the digest →</Button>
        </a>
      </div>
    </header>
  );
}
