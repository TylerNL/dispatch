import { Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Button from '../ui/Button';
import { useAuthModal } from '../../contexts/AuthModalContext';
import { useAuth } from '../../contexts/AuthContext';

const metaItems = ['One email, 7 AM PT', 'Free forever', 'No tracking'];

export default function Hero() {
  const { open } = useAuthModal();
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleGetDigest = () =>
    user ? navigate('/profile') : open('signup');

  return (
    <section
      id="signup"
      className="px-5 md:px-8 pt-24 pb-[110px]"
    >
      <div className="mx-auto max-w-container flex flex-col items-center text-center">
        <div className="animate-fade-up [animation-delay:0.05s]">
          <span className="inline-flex items-center gap-2.5 font-mono text-[11px] uppercase tracking-[0.14em] text-text-mute">
            <span className="text-text">
              New
            </span>
            <span aria-hidden className="h-3 w-px bg-border-hover" />
            <span>Ask the index — now in beta</span>
          </span>
        </div>
        <h1
          className="mt-8 headline headline-tight text-text max-w-[1000px] animate-fade-up [animation-delay:0.15s]"
          style={{ fontSize: 'clamp(44px, 7.2vw, 88px)' }}
        >
          The tech news firehose,{' '}
          <span className="editorial-italic">filtered</span> &amp;{' '}
          <span className="editorial-italic">answered</span>.
        </h1>
        <p className="mt-6 text-[19px] leading-[1.5] text-text-dim max-w-[640px] animate-fade-up [animation-delay:0.25s]">
          One email every morning at 8 AM PT, built from everything that happened across
          Hacker News, arXiv, the labs, and the rest of the firehose — then ask it anything.
        </p>
        <div className="mt-9 flex flex-wrap items-center justify-center gap-3 animate-fade-up [animation-delay:0.35s]">
          <Button variant="contrast" onClick={handleGetDigest}>
            Get the digest →
          </Button>
          <Button variant="ghost" onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}>
            See how it works
          </Button>
        </div>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 font-mono text-[11.5px] text-text-mute uppercase tracking-[0.12em] animate-fade-up [animation-delay:0.45s]">
          {metaItems.map((item) => (
            <span key={item} className="inline-flex items-center gap-1.5">
              <Check className="w-3.5 h-3.5 text-text-dim" strokeWidth={2} />
              {item}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
