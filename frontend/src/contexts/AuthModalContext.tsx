import { createContext, useCallback, useContext, useState, type ReactNode } from 'react';

type AuthMode = 'login' | 'signup';

type AuthIntent =
  | { status: 'closed' }
  | { status: 'open'; mode: AuthMode; returnTo: string | null };

interface AuthModalState {
  isOpen: boolean;
  mode: AuthMode;
  returnTo: string | null;
  open: (mode?: AuthMode, returnTo?: string | null) => void;
  close: () => void;
  setMode: (mode: AuthMode) => void;
}

const AuthModalContext = createContext<AuthModalState | null>(null);

export function AuthModalProvider({ children }: { children: ReactNode }) {
  const [intent, setIntent] = useState<AuthIntent>({ status: 'closed' });

  const open = useCallback(
    (mode: AuthMode = 'signup', returnTo: string | null = null) => {
      setIntent({ status: 'open', mode, returnTo });
    },
    [],
  );

  const close = useCallback(() => {
    setIntent({ status: 'closed' });
  }, []);

  const setMode = useCallback((mode: AuthMode) => {
    setIntent((prev) => (prev.status === 'open' ? { ...prev, mode } : prev));
  }, []);

  return (
    <AuthModalContext.Provider
      value={{
        isOpen: intent.status === 'open',
        mode: intent.status === 'open' ? intent.mode : 'signup',
        returnTo: intent.status === 'open' ? intent.returnTo : null,
        open,
        close,
        setMode,
      }}
    >
      {children}
    </AuthModalContext.Provider>
  );
}

export function useAuthModal(): AuthModalState {
  const ctx = useContext(AuthModalContext);
  if (!ctx) {
    throw new Error('useAuthModal must be used within an AuthModalProvider');
  }
  return ctx;
}
