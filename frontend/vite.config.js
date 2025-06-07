import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  root: path.resolve(__dirname),   // папка, где лежит ваш index.html
  base: 'https://full-resist-florist-faculty.trycloudflare.com',                      // базовый URL (если нужен относительный — './')
  plugins: [react()],
  build: {
    outDir: path.resolve(__dirname, '../dist/assets'), // куда складывать бандл
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'index.html'),
      // не выносить React наружу
      // external: []
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
})
