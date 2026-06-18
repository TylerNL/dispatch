import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Button from '../ui/Button';
import { useAuthModal } from '../../contexts/AuthModalContext';
import { useAuth } from '../../contexts/AuthContext';

const links = [
  { label: 'How it works', href: '#how-it-works' },
  { label: "What's inside", href: '#whats-inside' },
  { label: 'Ask', href: '#ask' },
  { label: 'Archive', href: '#archive' },
];

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const { open } = useAuthModal();
  const { user, loading } = useAuth();

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
        <div className="flex items-center gap-3">
          <Link
            to="/chat"
            className="text-[14px] text-text-dim hover:text-text transition-colors duration-150"
          >
            Open chat
          </Link>
          {!loading &&
            (user ? (
              <Link
                to="/profile"
                className="text-[14px] text-text-dim hover:text-text transition-colors duration-150"
              >
                Profile
              </Link>
            ) : (
              <>
                <Button variant="ghost" onClick={() => open('login')}>
                  Sign in
                </Button>
                <Button variant="accent" onClick={() => open('signup')}>
                  Get the digest →
                </Button>
              </>
            ))}
        </div>
      </div>
    </header>
  );
}
