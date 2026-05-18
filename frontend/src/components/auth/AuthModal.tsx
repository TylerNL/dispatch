import { useEffect, useRef, useState, type FormEvent } from 'react';
import { X } from 'lucide-react';
import { useAuthModal } from '../../contexts/AuthModalContext';
import { useFocusTrap } from '../../hooks/useFocusTrap';
import Input from '../ui/Input';
import Button from '../ui/Button';

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

function validate(
  email: string,
  password: string,
  confirmPassword: string,
  isSignup: boolean,
): FormErrors {
  const errors: FormErrors = {};

  if (!email.trim()) {
    errors.email = 'Email is required';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = 'Enter a valid email address';
  }

  if (!password) {
    errors.password = 'Password is required';
  } else if (password.length < 8) {
    errors.password = 'Must be at least 8 characters';
  }

  if (isSignup) {
    if (!confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
  }

  return errors;
}

export default function AuthModal() {
  const { isOpen, mode, close, setMode } = useAuthModal();
  const trapRef = useFocusTrap<HTMLDivElement>(isOpen);
  const emailRef = useRef<HTMLInputElement>(null);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitting, setSubmitting] = useState(false);

  const isSignup = mode === 'signup';

  useEffect(() => {
    if (isOpen) {
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setErrors({});
      setSubmitting(false);
    }
  }, [isOpen, mode]);

  // Focus the email input when modal opens
  useEffect(() => {
    if (isOpen) {
      // Small delay to let the DOM render and focus trap initialize
      const timer = setTimeout(() => emailRef.current?.focus(), 50);
      return () => clearTimeout(timer);
    }
  }, [isOpen, mode]);

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        close();
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, close]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
  }, [isOpen]);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();

    const validationErrors = validate(email, password, confirmPassword, isSignup);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) return;

    setSubmitting(true);

    // To-do: add supabase api call
    setTimeout(() => {
      setSubmitting(false);
      close();
    }, 1200);
  }

  function toggleMode() {
    setMode(isSignup ? 'login' : 'signup');
  }

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      role="presentation"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        aria-hidden="true"
        onClick={close}
      />

      {/* Modal */}
      <div
        ref={trapRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-modal-title"
        className="relative w-full max-w-[420px] rounded-2xl bg-bg-card border border-border shadow-2xl shadow-black/40 animate-fade-up [animation-delay:0s] [animation-duration:0.3s]"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-6 pb-0">
          <div className="flex items-center gap-2.5">
            <span className="w-2 h-2 rounded-full bg-accent" />
            <span className="text-[15px] font-medium tracking-[-0.015em] text-text">
              dispatch
            </span>
          </div>
          <button
            type="button"
            onClick={close}
            aria-label="Close"
            className="flex items-center justify-center w-8 h-8 rounded-lg text-text-mute hover:text-text hover:bg-bg-elev transition-colors duration-150"
          >
            <X className="w-4 h-4" strokeWidth={2} />
          </button>
        </div>

        {/* Title */}
        <div className="px-6 pt-6">
          <h2
            id="auth-modal-title"
            className="text-[24px] font-medium tracking-[-0.025em] text-text"
          >
            {isSignup ? 'Create your account' : 'Welcome back'}
          </h2>
          <p className="mt-2 text-[14.5px] text-text-dim leading-[1.5]">
            {isSignup
              ? 'Sign up to get the daily digest and ask the index.'
              : 'Sign in to your dispatch account.'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} noValidate className="px-6 pt-6 pb-6">
          <div className="flex flex-col gap-4">
            <Input
              ref={emailRef}
              label="Email"
              type="email"
              autoComplete={isSignup ? 'email' : 'username'}
              placeholder="you@example.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }));
              }}
              error={errors.email}
            />

            <Input
              label="Password"
              type="password"
              autoComplete={isSignup ? 'new-password' : 'current-password'}
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (errors.password) setErrors((prev) => ({ ...prev, password: undefined }));
              }}
              error={errors.password}
            />

            {isSignup && (
              <Input
                label="Confirm password"
                type="password"
                autoComplete="new-password"
                placeholder="Repeat your password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  if (errors.confirmPassword)
                    setErrors((prev) => ({ ...prev, confirmPassword: undefined }));
                }}
                error={errors.confirmPassword}
              />
            )}
          </div>

          {errors.general && (
            <p role="alert" className="mt-4 text-[13px] text-red-400">
              {errors.general}
            </p>
          )}

          <Button
            type="submit"
            variant="accent"
            disabled={submitting}
            className="w-full mt-6 h-[44px] text-[15px]"
          >
            {submitting
              ? isSignup
                ? 'Creating account...'
                : 'Signing in...'
              : isSignup
                ? 'Create account'
                : 'Sign in'}
          </Button>

          {!isSignup && (
            <button
              type="button"
              className="w-full mt-3 text-center text-[13px] text-text-mute hover:text-text-dim transition-colors duration-150"
            >
              Forgot your password?
            </button>
          )}
        </form>

        {/* Footer toggle */}
        <div className="px-6 pb-6 pt-0 border-t border-border">
          <p className="pt-5 text-center text-[13.5px] text-text-dim">
            {isSignup ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              type="button"
              onClick={toggleMode}
              className="text-accent hover:text-accent-hover font-medium transition-colors duration-150"
            >
              {isSignup ? 'Sign in' : 'Sign up'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
