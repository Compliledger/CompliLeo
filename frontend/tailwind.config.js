/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      colors: {
        ink: {
          950: '#05070d',
          900: '#0a0d18',
          800: '#101524',
          700: '#1a2236',
          600: '#2a3450',
        },
        accent: {
          DEFAULT: '#7dd3fc',
          strong: '#38bdf8',
        },
      },
    },
  },
  plugins: [],
};
