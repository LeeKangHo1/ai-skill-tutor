// frontend/src/test-setup.js
// Vitest 테스트 환경 설정 파일

import { vi } from 'vitest'

// 전역 모킹 설정
global.console = {
  ...console,
  // 테스트 중 불필요한 로그 출력 방지 (필요시 주석 해제)
  // log: vi.fn(),
  // warn: vi.fn(),
  // error: vi.fn(),
}

// DOM 환경 설정
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// localStorage 모킹
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

// sessionStorage 모킹
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.sessionStorage = sessionStorageMock

// fetch 모킹 (API 호출 테스트용)
global.fetch = vi.fn()

// 테스트 환경에서 사용할 유틸리티 함수들
global.testUtils = {
  // 비동기 작업 대기
  waitFor: (ms = 0) => new Promise(resolve => setTimeout(resolve, ms)),
  
  // 다음 틱 대기
  nextTick: () => new Promise(resolve => setTimeout(resolve, 0)),
  
  // 모킹된 API 응답 생성
  createMockApiResponse: (data, success = true) => ({
    success,
    data,
    message: success ? 'Success' : 'Error',
    ...(success ? {} : { error: 'Mock error' })
  })
}

// 테스트 시작 전 초기화
beforeEach(() => {
  // 모든 모킹 함수 초기화
  vi.clearAllMocks()
  
  // localStorage/sessionStorage 초기화
  localStorageMock.getItem.mockClear()
  localStorageMock.setItem.mockClear()
  localStorageMock.removeItem.mockClear()
  localStorageMock.clear.mockClear()
  
  sessionStorageMock.getItem.mockClear()
  sessionStorageMock.setItem.mockClear()
  sessionStorageMock.removeItem.mockClear()
  sessionStorageMock.clear.mockClear()
  
  // fetch 모킹 초기화
  global.fetch.mockClear()
})

console.log('✅ 테스트 환경 설정 완료')