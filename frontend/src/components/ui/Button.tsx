import type { ButtonHTMLAttributes, ReactNode } from 'react';

type Variant = 'primary' | 'accent' | 'ghost';

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  children: ReactNode;
};

const base =
  'inline-flex items-center justify-center gap-1.5 rounded-full font-medium text-[14.5px] transition-colors duration-150 whitespace-nowrap';

const variants: Record<Variant, string> = {
  accent:
    'bg-accent text-bg hover:bg-accent-hover px-[18px] h-[42px] shadow-[0_0_0_1px_rgba(232,163,61,0.25),0_8px_24px_-8px_rgba(232,163,61,0.4)]',
  primary:
    'bg-bg-elev text-text border border-border hover:border-border-hover px-[18px] h-[42px]',
  ghost:
    'text-text-dim hover:text-text px-[14px] h-[42px]',
};

export default function Button({
  variant = 'primary',
  className = '',
  children,
  ...rest
}: Props) {
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...rest}>
      {children}
    </button>
  );
}
