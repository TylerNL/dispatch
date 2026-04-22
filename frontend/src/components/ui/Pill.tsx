import type { ReactNode } from 'react';

type Props = {
  children: ReactNode;
  className?: string;
};

export default function Pill({ children, className = '' }: Props) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full bg-bg-elev border border-border px-3.5 py-1.5 text-[13px] text-text-dim hover:border-border-hover hover:text-text transition-colors duration-150 ${className}`}
    >
      {children}
    </span>
  );
}
