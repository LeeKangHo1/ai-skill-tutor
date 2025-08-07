// frontend/src/composables/useAuth.js
// 인증 관련 컴포저블 - 로그인, 로그아웃, 토큰 관리 등의 인증 로직을 담당

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/authService'

// 전역 상태로 관리할 인증 정보
const user = ref(null)
const token = ref(localStorage.getItem('auth_token'))
const isLoading = ref(false)

export function useAuth() {
  const router = useRouter()

  // 로그인 상태 계산 속성
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 로그인 함수
  const login = async (credentials) => {
    try {
      isLoading.value = true
      const response = await authService.login(credentials)
      
      if (response.success) {
        token.value = response.token
        user.value = response.user
        localStorage.setItem('auth_token', response.token)
        return { success: true }
      } else {
        return { success: false, error: response.message }
      }
    } catch (error) {
      console.error('로그인 오류:', error)
      return { success: false, error: '로그인 중 오류가 발생했습니다.' }
    } finally {
      isLoading.value = false
    }
  }

  // 로그아웃 함수
  const logout = async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('로그아웃 오류:', error)
    } finally {
      // 로컬 상태 초기화
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
      router.push('/login')
    }
  }

  // 회원가입 함수
  const register = async (userData) => {
    try {
      isLoading.value = true
      const response = await authService.register(userData)
      
      if (response.success) {
        return { success: true, message: '회원가입이 완료되었습니다.' }
      } else {
        return { success: false, error: response.message }
      }
    } catch (error) {
      console.error('회원가입 오류:', error)
      return { success: false, error: '회원가입 중 오류가 발생했습니다.' }
    } finally {
      isLoading.value = false
    }
  }

  // 토큰 검증 및 사용자 정보 로드
  const validateToken = async () => {
    if (!token.value) return false

    try {
      const response = await authService.validateToken(token.value)
      if (response.success) {
        user.value = response.user
        return true
      } else {
        // 토큰이 유효하지 않으면 로그아웃 처리
        logout()
        return false
      }
    } catch (error) {
      console.error('토큰 검증 오류:', error)
      logout()
      return false
    }
  }

  // 사용자 정보 업데이트
  const updateUser = (userData) => {
    user.value = { ...user.value, ...userData }
  }

  return {
    // 상태
    user: computed(() => user.value),
    token: computed(() => token.value),
    isAuthenticated,
    isLoading: computed(() => isLoading.value),

    // 메서드
    login,
    logout,
    register,
    validateToken,
    updateUser
  }
}