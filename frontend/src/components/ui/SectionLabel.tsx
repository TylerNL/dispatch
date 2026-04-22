import type { ReactNode } from 'react';

type Props = {
  children: ReactNode;
  className?: string;
};

export default function SectionLabel({ children, className = '' }: Props) {
  return (
    <span
      className={`font-mono text-[11px] uppercase tracking-[0.14em] text-text-dim ${className}`}
    >
      {children}
    </span>
  );
}
