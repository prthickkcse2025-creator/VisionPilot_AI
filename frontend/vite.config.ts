import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/upload': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/optimize': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/predict_policy': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/detect': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ocr': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/package': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/dashboard': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/history': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/analytics': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
});
