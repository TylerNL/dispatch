import { useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

interface FormErrors {
  password?: string;
  confirmPassword?: string;
  general?: string;
}

function validate(password: string, confirmPassword: string): FormErrors {
  const errors: FormErrors = {};

  if (!password) {
    errors.password = 'Password is required';
  } else if (password.length < 8) {
    errors.password = 'Must be at least 8 characters';
  }

  if (!confirmPassword) {
    errors.confirmPassword = 'Please confirm your password';
  } else if (password !== confirmPassword) {
    errors.confirmPassword = 'Passwords do not match';
  }

  return errors;
}

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const passwordRef = useRef<HTMLInputElement>(null);

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    const validationErrors = validate(password, confirmPassword);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    setSubmitting(true);
    const { error } = await supabase.auth.updateUser({ password });
    setSubmitting(false);

    if (error) {
      setErrors({ general: error.message });
      return;
    }

    setDone(true);
    setTimeout(() => navigate('/'), 1500);
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
            {done ? 'Password updated' : 'Set a new password'}
          </h1>
          <p className="mt-2 text-[14.5px] text-text-dim leading-[1.5]">
            {done
              ? 'You\u2019re signed in. Redirecting you home...'
              : 'Choose a new password for your dispatch account.'}
          </p>
        </div>

        {done ? (
          <div className="px-6 pt-6 pb-6">
            <Link to="/">
              <Button variant="accent" className="w-full h-[44px] text-[15px]">
                Go home
              </Button>
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} noValidate className="px-6 pt-6 pb-6">
            <div className="flex flex-col gap-4">
              <Input
                ref={passwordRef}
                label="New password"
                type="password"
                autoComplete="new-password"
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errors.password)
                    setErrors((prev) => ({ ...prev, password: undefined }));
                }}
                error={errors.password}
              />

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
              {submitting ? 'Updating...' : 'Update password'}
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
