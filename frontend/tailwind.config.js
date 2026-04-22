/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0a0a0b',
        'bg-elev': '#111113',
        'bg-card': '#0e0e10',
        border: '#1d1d20',
        'border-hover': '#2a2a2e',
        text: '#f2f1ee',
        'text-dim': '#a5a3a0',
        'text-mute': '#6b6966',
        accent: '#e8a33d',
        'accent-hover': '#f2b04d',
        green: '#7cc49a',
      },
      fontFamily: {
        sans: ['Geist', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono', 'ui-monospace', 'monospace'],
      },
      maxWidth: {
        container: '1280px',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(14px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'dot-pulse': {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '1' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) both',
        'dot-pulse': 'dot-pulse 2.4s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
