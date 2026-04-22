import type { ReactNode } from 'react';

type Props = {
  children: ReactNode;
  className?: string;
};

export default function Card({ children, className = '' }: Props) {
  return (
    <div
      className={`group rounded-[14px] bg-bg-card border border-border p-6 transition-all duration-200 hover:border-border-hover hover:-translate-y-0.5 ${className}`}
    >
      {children}
    </div>
  );
}
