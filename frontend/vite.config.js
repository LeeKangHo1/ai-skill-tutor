// frontend/vite.config.js
// AI 활용법 학습 튜터 Vite 설정

import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // 개발 서버 설정
  server: {
    port: 5173,
    host: true,
    open: true
  },
  // 빌드 설정
  build: {
    outDir: 'dist',
    sourcemap: true
  },
  // 환경변수 설정
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false
  },
  // 테스트 설정
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test-setup.js']
  }
})
