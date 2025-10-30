import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/static/dist/',
  build: {
    outDir: '../app/static/dist',
    emptyOutDir: true,
    // Swagger UI is 1.2MB uncompressed but only 352KB gzipped
    // It's lazy loaded and cached separately, so this is acceptable
    chunkSizeWarningLimit: 1300,
    rollupOptions: {
      output: {
        manualChunks: {
          // React core - used everywhere, cache separately
          'react-vendor': ['react', 'react-dom', 'react-router-dom', 'framer-motion'],
          
          // Markdown rendering - only for DevDocs
          'markdown': ['react-markdown', 'remark-gfm'],
          
          // Syntax highlighting - only for DevDocs, split separately for better caching
          'syntax-highlighter': ['react-syntax-highlighter'],
          
          // Swagger UI - only for API Docs, large but lazy loaded
          'swagger-ui': ['swagger-ui-react'],
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})

