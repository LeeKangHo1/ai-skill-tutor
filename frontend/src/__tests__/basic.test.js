// frontend/src/__tests__/basic.test.js
// 기본 기능 테스트

import { describe, it, expect } from 'vitest'

describe('기본 기능 테스트', () => {
  it('테스트 환경이 올바르게 설정되었다', () => {
    expect(true).toBe(true)
  })

  it('환경변수가 올바르게 설정되었다', () => {
    expect(import.meta.env.VITE_API_BASE_URL).toBe('http://localhost:5000')
    expect(import.meta.env.VITE_APP_TITLE).toBe('AI 활용법 학습 튜터')
  })

  it('기본 JavaScript 기능이 작동한다', () => {
    const testArray = [1, 2, 3]
    expect(testArray.length).toBe(3)
    expect(testArray.includes(2)).toBe(true)
  })
})