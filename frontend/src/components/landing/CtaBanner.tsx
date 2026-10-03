import { useNavigate } from 'react-router-dom';
import SectionLabel from '../ui/SectionLabel';
import Button from '../ui/Button';
import { useAuthModal } from '../../contexts/AuthModalContext';
import { useAuth } from '../../contexts/AuthContext';

export default function CtaBanner() {
  const { open } = useAuthModal();
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleGetDigest = () =>
    user ? navigate('/profile') : open('signup');

  return (
    <section className="px-5 md:px-8 pt-[120px] pb-[140px] border-t border-border">
      <div className="mx-auto max-w-container flex flex-col items-center text-center">
        <SectionLabel className="mb-6">Start your morning better</SectionLabel>
        <h2
          className="headline headline-tight max-w-[1000px]"
          style={{ fontSize: 'clamp(40px, 5.6vw, 72px)' }}
        >
          Your timeline is <span className="editorial-italic">reading</span> this. Are you?
        </h2>
        <div className="mt-9">
          <Button variant="contrast" onClick={handleGetDigest}>
            Get the digest →
          </Button>
        </div>
      </div>
    </section>
  );
}
