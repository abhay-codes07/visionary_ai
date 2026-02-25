/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--bg-0)',
        foreground: 'var(--text-primary)',
        glass: 'var(--glass-fill)',
        neon: {
          cyan: 'var(--neon-cyan)',
          blue: 'var(--neon-blue)',
          teal: 'var(--neon-teal)',
        },
      },
      boxShadow: {
        glow: '0 0 60px rgba(83, 198, 255, 0.25)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};
