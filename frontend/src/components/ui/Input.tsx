import { forwardRef, type InputHTMLAttributes } from 'react';

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
};

const Input = forwardRef<HTMLInputElement, Props>(
  ({ label, error, id, className = '', ...rest }, ref) => {
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor={inputId}
          className="font-mono text-[11px] uppercase tracking-[0.14em] text-text-dim"
        >
          {label}
        </label>
        <input
          ref={ref}
          id={inputId}
          aria-invalid={!!error}
          aria-describedby={error ? `${inputId}-error` : undefined}
          className={`w-full rounded-lg bg-bg-elev border px-3.5 py-2.5 text-[15px] text-text placeholder:text-text-mute outline-none transition-colors duration-150 ${
            error
              ? 'border-red-500/60 focus:border-red-500'
              : 'border-border focus:border-accent'
          } ${className}`}
          {...rest}
        />
        {error && (
          <p
            id={`${inputId}-error`}
            role="alert"
            className="text-[12.5px] text-red-400"
          >
            {error}
          </p>
        )}
      </div>
    );
  },
);

Input.displayName = 'Input';

export default Input;
