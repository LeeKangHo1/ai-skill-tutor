// src/composables/useAuth.js

/**
 * 인증 관련 컴포저블
 * - 인증 상태 확인 및 관리
 * - 사용자 정보 접근
 * - 권한 확인 헬퍼 함수들
 * - 인증 관련 유틸리티 함수들
 */

import { computed, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()
  const route = useRoute()

  // 반응형 상태
  const isInitializing = ref(false)

  // 계산된 속성들
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const user = computed(() => authStore.user)
  const isLoading = computed(() => authStore.isLoading)
  const error = computed(() => authStore.error)

  // 사용자 정보 관련
  const userId = computed(() => authStore.userId)
  const username = computed(() => authStore.username)
  const loginId = computed(() => authStore.loginId)
  const email = computed(() => authStore.email)
  const userType = computed(() => authStore.userType)
  const currentChapter = computed(() => authStore.currentChapter)
  const isDiagnosisCompleted = computed(() => authStore.isDiagnosisCompleted)

  // 권한 관련
  const requiresAuth = computed(() => authStore.requiresAuth)
  const requiresDiagnosis = computed(() => authStore.requiresDiagnosis)
  const canAccessLearning = computed(() => authStore.canAccessLearning)

  /**
   * 인증 시스템 초기화
   */
  const initialize = async () => {
    if (isInitializing.value || authStore.isInitialized) {
      return authStore.isAuthenticated
    }

    isInitializing.value = true
    try {
      await authStore.initialize()
      return authStore.isAuthenticated
    } catch (error) {
      console.error('인증 초기화 실패:', error)
      return false
    } finally {
      isInitializing.value = false
    }
  }

  /**
   * 로그인
   */
  const login = async (credentials) => {
    try {
      const result = await authStore.login(credentials)
      return { success: true, data: result }
    } catch (error) {
      return { success: false, error }
    }
  }

  /**
   * 회원가입
   */
  const register = async (userData) => {
    try {
      const result = await authStore.register(userData)
      return { success: true, data: result }
    } catch (error) {
      return { success: false, error }
    }
  }

  /**
   * 로그아웃
   */
  const logout = async (redirectToLogin = true) => {
    try {
      await authStore.logout()
      
      if (redirectToLogin) {
        router.push('/login')
      }
      
      return { success: true }
    } catch (error) {
      console.error('로그아웃 오류:', error)
      
      // 에러가 발생해도 로컬 상태는 정리하고 리다이렉트
      if (redirectToLogin) {
        router.push('/login')
      }
      
      return { success: false, error }
    }
  }

  /**
   * 모든 디바이스에서 로그아웃
   */
  const logoutAll = async (redirectToLogin = true) => {
    try {
      await authStore.logoutAll()
      
      if (redirectToLogin) {
        router.push('/login')
      }
      
      return { success: true }
    } catch (error) {
      console.error('전체 로그아웃 오류:', error)
      
      if (redirectToLogin) {
        router.push('/login')
      }
      
      return { success: false, error }
    }
  }

  /**
   * 사용자 정보 새로고침
   */
  const refreshUser = async () => {
    try {
      await authStore.updateUserInfo()
      return { success: true, user: authStore.user }
    } catch (error) {
      return { success: false, error }
    }
  }

  /**
   * 권한 확인
   */
  const checkPermission = (requiredUserType = null, requiresDiagnosis = true) => {
    return authStore.checkPermission(requiredUserType, requiresDiagnosis)
  }

  /**
   * 특정 사용자 유형 확인
   */
  const hasUserType = (requiredType) => {
    return authStore.hasUserTypeAccess(requiredType)
  }

  /**
   * AI 입문자 여부 확인
   */
  const isBeginner = computed(() => userType.value === 'beginner')

  /**
   * 실무 응용형 여부 확인
   */
  const isAdvanced = computed(() => userType.value === 'advanced')

  /**
   * 챕터 접근 권한 확인
   */
  const canAccessChapter = (chapterNumber) => {
    if (!isAuthenticated.value || !isDiagnosisCompleted.value) {
      return false
    }
    
    return chapterNumber <= currentChapter.value
  }

  /**
   * 인증이 필요한 작업 수행
   */
  const requireAuth = async (action) => {
    if (!isAuthenticated.value) {
      router.push({
        name: 'login',
        query: { redirect: route.fullPath }
      })
      return { success: false, reason: 'NOT_AUTHENTICATED' }
    }

    try {
      const result = await action()
      return { success: true, data: result }
    } catch (error) {
      return { success: false, error }
    }
  }

  /**
   * 진단이 필요한 작업 수행
   */
  const requireDiagnosis = async (action) => {
    if (!isAuthenticated.value) {
      router.push({
        name: 'login',
        query: { redirect: route.fullPath }
      })
      return { success: false, reason: 'NOT_AUTHENTICATED' }
    }

    if (!isDiagnosisCompleted.value) {
      router.push({ name: 'diagnosis' })
      return { success: false, reason: 'DIAGNOSIS_NOT_COMPLETED' }
    }

    try {
      const result = await action()
      return { success: true, data: result }
    } catch (error) {
      return { success: false, error }
    }
  }

  /**
   * 진단 완료 상태 업데이트
   */
  const updateDiagnosisStatus = (userType) => {
    authStore.updateDiagnosisStatus(userType)
  }

  /**
   * 현재 챕터 업데이트
   */
  const updateCurrentChapter = (chapterNumber) => {
    authStore.updateCurrentChapter(chapterNumber)
  }

  /**
   * 에러 초기화
   */
  const clearError = () => {
    authStore.clearError()
  }

  /**
   * 인증 상태 확인 및 보장
   */
  const ensureAuthenticated = async () => {
    try {
      return await authStore.ensureAuthenticated()
    } catch (error) {
      router.push({
        name: 'login',
        query: { redirect: route.fullPath }
      })
      return false
    }
  }

  /**
   * 로그인이 필요한 페이지로 리다이렉트
   */
  const redirectToLogin = (message = null) => {
    const query = { redirect: route.fullPath }
    if (message) {
      query.message = message
    }
    
    router.push({
      name: 'login',
      query
    })
  }

  /**
   * 적절한 페이지로 리다이렉트
   */
  const redirectToAppropriate = () => {
    if (!isAuthenticated.value) {
      redirectToLogin()
    } else if (!isDiagnosisCompleted.value) {
      router.push({ name: 'diagnosis' })
    } else {
      router.push({ name: 'dashboard' })
    }
  }

  /**
   * 사용자 유형 텍스트 변환
   */
  const getUserTypeText = (type = null) => {
    const targetType = type || userType.value
    const typeMap = {
      'beginner': 'AI 입문자',
      'advanced': '실무 응용형',
      'unassigned': '미설정'
    }
    return typeMap[targetType] || '알 수 없음'
  }

  /**
   * 로그인 상태 변화 감지
   */
  const onAuthChange = (callback) => {
    return watch(isAuthenticated, callback, { immediate: true })
  }

  /**
   * 사용자 정보 변화 감지
   */
  const onUserChange = (callback) => {
    return watch(user, callback, { immediate: true, deep: true })
  }

  /**
   * 진단 상태 변화 감지
   */
  const onDiagnosisChange = (callback) => {
    return watch(isDiagnosisCompleted, callback, { immediate: true })
  }

  /**
   * 토큰 갱신 (수동)
   */
  const refreshTokens = async () => {
    try {
      await authStore.refreshTokens()
      return { success: true }
    } catch (error) {
      return { success: false, error }
    }
  }

  /**
   * 개발/디버깅용 헬퍼
   */
  const debugAuth = () => {
    console.log('=== 인증 상태 디버그 ===')
    console.log('isAuthenticated:', isAuthenticated.value)
    console.log('user:', user.value)
    console.log('userType:', userType.value)
    console.log('isDiagnosisCompleted:', isDiagnosisCompleted.value)
    console.log('currentChapter:', currentChapter.value)
    console.log('canAccessLearning:', canAccessLearning.value)
    console.log('isLoading:', isLoading.value)
    console.log('error:', error.value)
    console.log('========================')
  }

  return {
    // 상태
    isAuthenticated,
    user,
    isLoading,
    error,
    isInitializing,

    // 사용자 정보
    userId,
    username,
    loginId,
    email,
    userType,
    currentChapter,
    isDiagnosisCompleted,

    // 권한
    requiresAuth,
    requiresDiagnosis,
    canAccessLearning,
    isBeginner,
    isAdvanced,

    // 메서드
    initialize,
    login,
    register,
    logout,
    logoutAll,
    refreshUser,
    checkPermission,
    hasUserType,
    canAccessChapter,
    requireAuth,
    requireDiagnosis,
    updateDiagnosisStatus,
    updateCurrentChapter,
    clearError,
    ensureAuthenticated,
    redirectToLogin,
    redirectToAppropriate,
    getUserTypeText,
    onAuthChange,
    onUserChange,
    onDiagnosisChange,
    refreshTokens,
    debugAuth
  }
}