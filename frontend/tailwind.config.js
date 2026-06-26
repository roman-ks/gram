import daisyui from 'daisyui'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{svelte,js,ts}'],
  theme: { extend: {} },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        light: {
          primary: '#E8B89F',
          'primary-content': '#ffffff',
          secondary: '#D4956E',
          'secondary-content': '#ffffff',
          accent: '#E8B89F',
          'accent-content': '#ffffff',
          neutral: '#2b3440',
          'neutral-content': '#d7dde4',
          'base-100': '#ffffff',
          'base-200': '#f2f2f2',
          'base-300': '#e5e6e6',
          'base-content': '#1f2937',
          info: '#3b82f6',
          'info-content': '#ffffff',
          success: '#10b981',
          'success-content': '#ffffff',
          warning: '#f59e0b',
          'warning-content': '#ffffff',
          error: '#ef4444',
          'error-content': '#ffffff',
        },
      },
      'dark',
    ],
  },
}
