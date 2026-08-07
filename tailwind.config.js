/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#090d16",
          card: "#111827",
          border: "#1f293d",
          accent: "#00f0ff",
          purple: "#7000ff",
          emerald: "#10b981",
          amber: "#f59e0b",
          rose: "#f43f5e",
          slate: "#94a3b8"
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s infinite ease-in-out',
        'scanline': 'scanline 6s linear infinite'
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: 0.8, filter: 'drop-shadow(0 0 8px rgba(0, 240, 255, 0.6))' },
          '50%': { opacity: 0.4, filter: 'drop-shadow(0 0 2px rgba(0, 240, 255, 0.2))' }
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(1000%)' }
        }
      }
    },
  },
  plugins: [],
}
