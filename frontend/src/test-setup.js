// frontend/src/test-setup.js
// 테스트 환경 설정

import { vi } from 'vitest'

// 전역 모킹 설정
global.console = {
  ...console,
  // 테스트 중 불필요한 로그 출력 방지
  log: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
}

// 환경변수 모킹
Object.defineProperty(import.meta, 'env', {
  value: {
    VITE_API_BASE_URL: 'http://localhost:5000',
    VITE_APP_TITLE: 'AI 활용법 학습 튜터',
    VITE_DEV_MODE: 'true'
  },
  writable: true
})