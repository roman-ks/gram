import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// Dev: proxy /api to the FastAPI backend so the SPA stays same-origin.
// Prod: the SPA is built to dist/ and served by FastAPI directly.
export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
