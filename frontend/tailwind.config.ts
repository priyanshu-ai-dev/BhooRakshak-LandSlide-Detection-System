import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Brand palette — will be expanded in Phase 1
        risk: {
          low: '#22c55e',       // green-500
          moderate: '#f59e0b',  // amber-500
          high: '#ef4444',      // red-500
          critical: '#7f1d1d',  // red-950
        },
      },
    },
  },
  plugins: [],
}

export default config
