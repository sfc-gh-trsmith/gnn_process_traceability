/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#29B5E8',
        secondary: '#11567F',
        accent: '#FF9F0A',
        purple: '#8B5CF6',
        background: '#0f172a',
        card: '#1e293b',
        text: '#e2e8f0',
        'text-primary': '#e2e8f0',
        'text-secondary': '#94a3b8',
        border: '#334155',
        critical: '#ef4444',
        warning: '#f59e0b',
        success: '#22c55e',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
