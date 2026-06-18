import { useRef, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function ForgotPasswordPage() {
  const { resetPassword } = useAuth();
  const emailRef = useRef<HTMLInputElement>(null);

  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | undefined>();
  const [general, setGeneral] = useState<string | undefined>();
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setGeneral(undefined);

    if (!email.trim()) {
      setError('Email is required');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Enter a valid email address');
      return;
    }
    setError(undefined);

    setSubmitting(true);
    const { error: resetError } = await resetPassword(email);
    setSubmitting(false);

    if (resetError) {
      setGeneral(resetError);
      return;
    }
    setSent(true);
  }

  return (
    <div className="min-h-screen bg-bg text-text flex items-center justify-center p-4">
      <div className="relative w-full max-w-[420px] rounded-2xl bg-bg-card border border-border shadow-2xl shadow-black/40">
        {/* Header */}
        <div className="flex items-center gap-2.5 px-6 pt-6">
          <span className="w-2 h-2 rounded-full bg-accent" />
          <span className="text-[15px] font-medium tracking-[-0.015em] text-text">
            dispatch
          </span>
        </div>

        {/* Title */}
        <div className="px-6 pt-6">
          <h1 className="text-[24px] font-medium tracking-[-0.025em] text-text">
            {sent ? 'Check your email' : 'Reset your password'}
          </h1>
          <p className="mt-2 text-[14.5px] text-text-dim leading-[1.5]">
            {sent
              ? `We sent a reset link to ${email}. Follow it to choose a new password.`
              : 'Enter your email and we\u2019ll send you a link to reset your password.'}
          </p>
        </div>

        {sent ? (
          <div className="px-6 pt-6 pb-6">
            <Link to="/">
              <Button variant="accent" className="w-full h-[44px] text-[15px]">
                Back to home
              </Button>
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} noValidate className="px-6 pt-6 pb-6">
            <Input
              ref={emailRef}
              label="Email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (error) setError(undefined);
              }}
              error={error}
            />

            {general && (
              <p role="alert" className="mt-4 text-[13px] text-red-400">
                {general}
              </p>
            )}

            <Button
              type="submit"
              variant="accent"
              disabled={submitting}
              className="w-full mt-6 h-[44px] text-[15px]"
            >
              {submitting ? 'Sending...' : 'Send reset link'}
            </Button>

            <Link
              to="/"
              className="block w-full mt-3 text-center text-[13px] text-text-mute hover:text-text-dim transition-colors duration-150"
            >
              Back to sign in
            </Link>
          </form>
        )}
      </div>
    </div>
  );
}
