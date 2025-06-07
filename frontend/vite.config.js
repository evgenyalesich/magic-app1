import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'https://full-resist-florist-faculty.trycloudflare.com',
        changeOrigin: true,
      }
    }
  }
})