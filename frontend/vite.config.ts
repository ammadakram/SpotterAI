/// <reference types="vitest/config" />
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // In development the API runs on Django's port; the proxy avoids CORS locally.
    proxy: { '/api': 'http://localhost:8000' },
  },
  test: {
    include: ['src/**/*.test.ts'],
  },
})
