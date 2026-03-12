import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api/agent': {
        target: 'http://localhost:8847',
        changeOrigin: true,
      },
      '/summary': {
        target: 'http://localhost:8847',
        changeOrigin: true,
      },
      '/defects': {
        target: 'http://localhost:8847',
        changeOrigin: true,
      },
      '/risk': {
        target: 'http://localhost:8847',
        changeOrigin: true,
      },
      '/network': {
        target: 'http://localhost:8847',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8847',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
