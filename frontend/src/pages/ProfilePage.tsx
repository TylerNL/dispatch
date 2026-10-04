import { useEffect, useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Building2,
  Check,
  Clock,
  FlaskConical,
  LogOut,
  Mail,
  Rocket,
  ShieldCheck,
  Wrench,
} from 'lucide-react';
import type { User } from '@supabase/supabase-js';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import {
  getSubscriberPreferences,
  updateSubscriberPreferences,
  type DigestTopic,
} from '../lib/api';

const TOPICS: {
  id: DigestTopic;
  label: string;
  description: string;
  icon: typeof Rocket;
}[] = [
  {
    id: 'labs',
    label: 'AI labs',
    description: 'Model releases and updates from leading AI labs.',
    icon: Building2,
  },
  {
    id: 'research',
    label: 'Research',
    description: 'Papers, benchmarks, and new architectures.',
    icon: FlaskConical,
  },
  {
    id: 'startups',
    label: 'Startups',
    description: 'Funding rounds, launches, and acquisitions.',
    icon: Rocket,
  },
  {
    id: 'security',
    label: 'Security',
    description: 'AI safety, security research, and emerging risks.',
    icon: ShieldCheck,
  },
  {
    id: 'tooling',
    label: 'Tooling',
    description: 'Developer tools, frameworks, SDKs, and infrastructure.',
    icon: Wrench,
  },
];

export default function ProfilePage() {
  const { user, session, loading, signOut } = useAuth();
  const navigate = useNavigate();

  if (loading) return null;
  if (!user) return <Navigate to="/" replace />;

  const metadata = (user.user_metadata ?? {}) as {
    full_name?: string;
    name?: string;
    avatar_url?: string;
  };
  const displayName =
    metadata.full_name ?? metadata.name ?? user.email?.split('@')[0] ?? 'there';
  const initial = displayName.charAt(0).toUpperCase();
  const avatarUrl = metadata.avatar_url;
  const memberSince = user.created_at
    ? new Date(user.created_at).toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric',
      })
    : '—';
  const digestTime = '8:00 AM PT';

  async function handleSignOut() {
    await signOut();
    navigate('/');
  }

  return (
    <div className="relative min-h-screen bg-bg text-text">
      {/* Top bar — back on the left, dispatch mark on the right */}
      <header className="relative mx-auto max-w-[760px] px-5 md:px-8 pt-6 flex items-center justify-between">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-[13.5px] text-text-mute hover:text-text transition-colors duration-150"
        >
          <ArrowLeft className="w-4 h-4" strokeWidth={2} />
          Back
        </Link>
        <div className="flex items-center gap-2.5">
          <span className="w-2 h-2 rounded-full bg-accent" />
          <span className="text-[15px] font-medium tracking-[-0.015em] text-text">
            dispatch
          </span>
        </div>
      </header>

      <main className="relative mx-auto max-w-[760px] px-5 md:px-8 pb-16">
        {/* Welcome hero */}
        <section className="mt-10 flex items-center gap-5 animate-fade-up [animation-delay:0.05s]">
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt={displayName}
              referrerPolicy="no-referrer"
              className="w-[72px] h-[72px] shrink-0 rounded-2xl object-cover border border-accent/25"
            />
          ) : (
            <div className="flex items-center justify-center w-[72px] h-[72px] shrink-0 rounded-2xl bg-accent/10 border border-accent/25 text-accent text-[28px] font-medium tracking-[-0.02em]">
              {initial}
            </div>
          )}
          <div className="min-w-0">
            <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-text-mute">
              Your account
            </p>
            <h1 className="mt-1.5 text-[30px] leading-[1.1] font-medium tracking-[-0.025em]">
              Welcome back, {displayName}
            </h1>
            <p className="mt-1.5 text-[14.5px] text-text-dim truncate">
              Signed in as <span className="text-text">{user.email}</span>
            </p>
          </div>
        </section>

        {/* Account overview */}
        <section className="mt-10 animate-fade-up [animation-delay:0.15s]">
          <h2 className="text-[15px] font-medium text-text">Account</h2>
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <InfoCard icon={Mail} label="Email" value={user.email ?? '—'} />
            <InfoCard icon={Clock} label="Digest" value={digestTime} />
          </div>
          <p className="mt-3 text-[13px] text-text-mute">
            Member since {memberSince}.
          </p>
        </section>

        <DisplayNameSection user={user} />

        <TopicPreferencesSection token={session?.access_token ?? ''} />

        {/* Sign out */}
        <section className="mt-10 pt-8 border-t border-border animate-fade-up [animation-delay:0.35s]">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <p className="text-[14.5px] font-medium text-text">Sign out</p>
              <p className="mt-0.5 text-[13px] text-text-dim">
                You can sign back in any time to pick up where you left off.
              </p>
            </div>
            <Button variant="primary" onClick={handleSignOut}>
              <LogOut className="w-4 h-4" strokeWidth={2} />
              Sign out
            </Button>
          </div>
        </section>
      </main>
    </div>
  );
}

function TopicPreferencesSection({ token }: { token: string }) {
  const [selected, setSelected] = useState<DigestTopic[]>(
    TOPICS.map((topic) => topic.id),
  );
  const [enabled, setEnabled] = useState(false);
  const [baseline, setBaseline] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string>();

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const preferences = await getSubscriberPreferences(token);
        if (cancelled) return;
        setEnabled(preferences.enabled);
        setSelected(preferences.topics);
        setBaseline(preferenceKey(preferences.enabled, preferences.topics));
      } catch {
        if (!cancelled) setError('Could not load your digest preferences.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    if (token) load();
    else {
      setError('Your session is unavailable. Please sign in again.');
      setLoading(false);
    }

    return () => {
      cancelled = true;
    };
  }, [token]);

  const dirty = baseline !== preferenceKey(enabled, selected);

  function toggle(id: DigestTopic) {
    setSaved(false);
    setError(undefined);
    setSelected((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return TOPICS.map((topic) => topic.id).filter((topic) => next.has(topic));
    });
  }

  async function handleSave() {
    if (!dirty || saving || selected.length === 0) return;
    setSaving(true);
    setSaved(false);
    setError(undefined);
    try {
      const preferences = await updateSubscriberPreferences(token, {
        enabled,
        topics: selected,
      });
      setEnabled(preferences.enabled);
      setSelected(preferences.topics);
      setBaseline(preferenceKey(preferences.enabled, preferences.topics));
      setSaved(true);
    } catch {
      setError('Could not save your digest preferences.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="mt-10 animate-fade-up [animation-delay:0.25s]">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h2 className="text-[15px] font-medium text-text">Daily digest</h2>
          <p className="mt-1 text-[13.5px] text-text-dim">
            Choose the topics sent to your inbox each morning.
          </p>
        </div>
        <button
          type="button"
          role="switch"
          aria-checked={enabled}
          aria-label="Receive the daily digest"
          disabled={loading}
          onClick={() => {
            setEnabled((current) => !current);
            setSaved(false);
            setError(undefined);
          }}
          className={`mt-0.5 h-6 w-11 shrink-0 overflow-hidden rounded-full border p-[3px] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 focus-visible:ring-offset-2 focus-visible:ring-offset-bg ${
            enabled ? 'border-accent bg-accent' : 'border-border bg-bg-elev'
          } disabled:opacity-50`}
        >
          <span
            className={`block h-4 w-4 rounded-full transition-[transform,background-color] ${
              enabled ? 'translate-x-5 bg-bg' : 'translate-x-0 bg-text-dim'
            }`}
          />
        </button>
      </div>

      <div className="mt-5 flex flex-col gap-3" aria-busy={loading}>
        {TOPICS.map((topic) => {
          const isSelected = selected.includes(topic.id);
          const Icon = topic.icon;
          return (
            <button
              key={topic.id}
              type="button"
              onClick={() => toggle(topic.id)}
              aria-pressed={isSelected}
              disabled={loading}
              className={`group flex items-center gap-4 rounded-2xl border p-5 text-left transition-all duration-200 disabled:opacity-50 ${
                isSelected
                  ? 'border-accent bg-accent/[0.06]'
                  : 'border-border bg-bg-card hover:border-border-hover'
              }`}
            >
              <span
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-colors duration-200 ${
                  isSelected ? 'bg-accent/15 text-accent' : 'bg-bg-elev text-text-dim'
                }`}
              >
                <Icon className="h-5 w-5" strokeWidth={2} />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-[15px] font-medium text-text">
                  {topic.label}
                </span>
                <span className="mt-0.5 block text-[13px] text-text-dim">
                  {topic.description}
                </span>
              </span>
              <span
                className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition-colors duration-200 ${
                  isSelected
                    ? 'border-accent bg-accent text-bg'
                    : 'border-border text-transparent'
                }`}
              >
                <Check className="h-3.5 w-3.5" strokeWidth={3} />
              </span>
            </button>
          );
        })}
      </div>

      {selected.length === 0 && (
        <p className="mt-3 text-[13px] text-red-400">
          Select at least one topic before saving.
        </p>
      )}
      {error && <p className="mt-3 text-[13px] text-red-400">{error}</p>}

      <div className="mt-4 flex items-center gap-3">
        <Button
          variant="accent"
          onClick={handleSave}
          disabled={loading || saving || !dirty || selected.length === 0}
        >
          {saving ? 'Saving...' : saved && !dirty ? 'Saved' : 'Save preferences'}
        </Button>
        <span className="text-[13px] text-text-mute">
          {enabled ? 'Daily email enabled' : 'Daily email off'}
        </span>
      </div>
    </section>
  );
}

function preferenceKey(enabled: boolean, topics: DigestTopic[]): string {
  return `${enabled}:${[...topics].sort().join(',')}`;
}

function InfoCard({
  icon: Icon,
  label,
  value,
  accent = false,
}: {
  icon: typeof Mail;
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-border bg-bg-card p-4">
      <div className="flex items-center gap-2">
        <span
          className={`flex items-center justify-center w-7 h-7 rounded-lg shrink-0 ${
            accent ? 'bg-accent/15 text-accent' : 'bg-bg-elev text-text-dim'
          }`}
        >
          <Icon className="w-4 h-4" strokeWidth={2} />
        </span>
        <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-text-mute">
          {label}
        </span>
      </div>
      <p className="mt-3 text-[14.5px] font-medium text-text truncate" title={value}>
        {value}
      </p>
    </div>
  );
}

function DisplayNameSection({ user }: { user: User }) {
  const { updateDisplayName } = useAuth();
  const metadata = (user.user_metadata ?? {}) as { full_name?: string; name?: string };
  const initial = metadata.full_name ?? metadata.name ?? user.email?.split('@')[0] ?? '';

  const [name, setName] = useState(initial);
  const [savedName, setSavedName] = useState(initial);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const trimmed = name.trim();
  const dirty = trimmed.length > 0 && trimmed !== savedName;

  async function handleSave() {
    if (!dirty || saving) return;
    setSaving(true);
    setSaved(false);
    setError(undefined);
    const { error: saveError } = await updateDisplayName(trimmed);
    setSaving(false);
    if (saveError) {
      setError(saveError);
      return;
    }
    setSavedName(trimmed);
    setSaved(true);
  }

  return (
    <section className="mt-10 animate-fade-up [animation-delay:0.2s]">
      <h2 className="text-[15px] font-medium text-text">Display name</h2>
      <p className="mt-1 text-[13.5px] text-text-dim">
        How dispatch greets you. Defaults to your account name - change it any time.
      </p>
      <div className="mt-4 flex flex-col sm:flex-row sm:items-start gap-3">
        <div className="flex-1">
          <Input
            label="Display name"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              setSaved(false);
              if (error) setError(undefined);
            }}
            placeholder="Your name"
            error={error}
            maxLength={50}
          />
        </div>
        <Button
          variant="accent"
          onClick={handleSave}
          disabled={!dirty || saving}
          className="sm:mt-[26px]"
        >
          {saving ? (
            'Saving...'
          ) : saved && !dirty ? (
            <>
              <Check className="w-4 h-4" strokeWidth={2.5} />
              Saved
            </>
          ) : (
            'Save'
          )}
        </Button>
      </div>
    </section>
  );
}
