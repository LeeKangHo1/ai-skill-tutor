// src/stores/authStore.js

/**
 * 인증 상태 관리 스토어 (Pinia)
 * - 로그인 상태 및 사용자 정보 관리
 * - 인증 관련 액션들
 * - HttpOnly 쿠키 방식 지원
 */

import { defineStore } from 'pinia'
import authService from '../services/authService'
import tokenManager from '../utils/tokenManager'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // 사용자 정보
    user: null,
    
    // 로그인 상태
    isAuthenticated: false,
    
    // 로딩 상태
    isLoading: false,
    
    // 에러 상태
    error: null,
    
    // 토큰 갱신 상태
    isRefreshing: false,
    
    // 초기화 완료 여부
    isInitialized: false
  }),

  getters: {
    /**
     * 사용자 유형 조회
     */
    userType: (state) => state.user?.user_type || null,
    
    /**
     * 진단 완료 여부
     */
    isDiagnosisCompleted: (state) => state.user?.diagnosis_completed || false,
    
    /**
     * 현재 챕터
     */
    currentChapter: (state) => state.user?.current_chapter || 1,
    
    /**
     * 사용자 ID
     */
    userId: (state) => state.user?.user_id || null,
    
    /**
     * 로그인 ID
     */
    loginId: (state) => state.user?.login_id || null,
    
    /**
     * 사용자명
     */
    username: (state) => state.user?.username || null,
    
    /**
     * 이메일
     */
    email: (state) => state.user?.email || null,
    
    /**
     * 인증 필요 여부 (진단 미완료자 포함)
     */
    requiresAuth: (state) => !state.isAuthenticated,
    
    /**
     * 진단 필요 여부
     */
    requiresDiagnosis: (state) => state.isAuthenticated && !state.user?.diagnosis_completed,
    
    /**
     * 학습 접근 가능 여부
     */
    canAccessLearning: (state) => state.isAuthenticated && state.user?.diagnosis_completed,
    
    /**
     * 사용자 유형별 접근 권한
     */
    hasUserTypeAccess: (state) => (requiredType) => {
      return state.user?.user_type === requiredType
    }
  },

  actions: {
    /**
     * 초기화 - 앱 시작 시 토큰 확인
     */
    async initialize() {
      if (this.isInitialized) return
      
      this.isLoading = true
      
      try {
        // 저장된 Access Token이 있는지 확인
        if (tokenManager.hasTokens()) {
          const validation = tokenManager.validateTokens()
          
          if (validation.valid) {
            // 유효한 토큰이 있으면 사용자 정보 복원
            await this.restoreUserFromToken()
          } else if (validation.reason === 'ACCESS_TOKEN_EXPIRED') {
            // Access Token만 만료된 경우 갱신 시도
            await this.refreshTokens()
          } else {
            // Access Token이 없는 경우 로그아웃
            this.clearAuth()
          }
        } else {
          // 토큰이 없는 경우 쿠키에 refresh_token이 있는지 확인
          await this.checkForValidRefreshToken()
        }
      } catch (error) {
        console.error('인증 초기화 실패:', error)
        this.clearAuth()
      } finally {
        this.isLoading = false
        this.isInitialized = true
      }
    },

    /**
     * 쿠키에 유효한 refresh_token이 있는지 확인
     */
    async checkForValidRefreshToken() {
      try {
        // refresh_token 쿠키가 있다면 토큰 갱신 시도
        await this.refreshTokens()
      } catch (error) {
        // refresh_token이 없거나 만료된 경우 로그아웃 상태 유지
        this.clearAuth()
      }
    },

    /**
     * 저장된 토큰으로 사용자 정보 복원
     */
    async restoreUserFromToken() {
      try {
        // localStorage의 사용자 정보 먼저 확인
        const storedUser = tokenManager.getUserInfo()
        if (storedUser) {
          this.user = storedUser
          this.isAuthenticated = true
        }

        // 서버에서 최신 사용자 정보 조회
        const response = await authService.getCurrentUser()
        if (response.success) {
          this.user = response.data.data
          this.isAuthenticated = true
        }
      } catch (error) {
        console.error('사용자 정보 복원 실패:', error)
        this.clearAuth()
      }
    },

    /**
     * 토큰 갱신
     */
    async refreshTokens() {
      if (this.isRefreshing) return

      this.isRefreshing = true
      
      try {
        const response = await authService.refreshToken()
        
        if (response.success && response.data) {
          // 사용자 정보 업데이트
          if (response.data.user_info) {
            this.user = response.data.user_info
            this.isAuthenticated = true
          }
        } else {
          throw new Error('토큰 갱신 실패')
        }
      } catch (error) {
        console.error('토큰 갱신 실패:', error)
        this.clearAuth()
        throw error
      } finally {
        this.isRefreshing = false
      }
    },

    /**
     * 로그인
     */
    async login(credentials) {
      this.isLoading = true
      this.error = null

      try {
        const response = await authService.login(credentials)
        
        if (response.success) {
          this.user = response.data.user_info
          this.isAuthenticated = true
          return response
        } else {
          throw new Error(response.error?.message || '로그인 실패')
        }
      } catch (error) {
        this.error = error.message || '로그인 중 오류가 발생했습니다'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 회원가입
     */
    async register(userData) {
      this.isLoading = true
      this.error = null

      try {
        const response = await authService.register(userData)
        
        if (response.success) {
          // 회원가입 후 자동 로그인된 경우
          if (response.data.access_token && response.data.user_id) {
            this.user = {
              user_id: response.data.user_id,
              login_id: response.data.login_id,
              username: response.data.username,
              user_type: response.data.user_type,
              diagnosis_completed: response.data.diagnosis_completed
            }
            this.isAuthenticated = true
          }
          return response
        } else {
          throw new Error(response.error?.message || '회원가입 실패')
        }
      } catch (error) {
        this.error = error.message || '회원가입 중 오류가 발생했습니다'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 로그아웃
     */
    async logout() {
      this.isLoading = true

      try {
        await authService.logout()
      } catch (error) {
        console.error('로그아웃 API 호출 실패:', error)
      } finally {
        this.clearAuth()
        this.isLoading = false
      }
    },

    /**
     * 모든 디바이스에서 로그아웃
     */
    async logoutAll() {
      this.isLoading = true

      try {
        await authService.logoutAll()
      } catch (error) {
        console.error('전체 로그아웃 API 호출 실패:', error)
      } finally {
        this.clearAuth()
        this.isLoading = false
      }
    },

    /**
     * 사용자 정보 업데이트
     */
    async updateUserInfo() {
      try {
        const response = await authService.getCurrentUser()
        if (response.success) {
          this.user = response.data.data
          return response
        }
      } catch (error) {
        console.error('사용자 정보 업데이트 실패:', error)
        throw error
      }
    },

    /**
     * 진단 완료 상태 업데이트
     */
    updateDiagnosisStatus(userType) {
      if (this.user) {
        this.user.diagnosis_completed = true
        this.user.user_type = userType
        // localStorage도 업데이트
        tokenManager.setUserInfo(this.user)
      }
    },

    /**
     * 현재 챕터 업데이트
     */
    updateCurrentChapter(chapterNumber) {
      if (this.user) {
        this.user.current_chapter = chapterNumber
        // localStorage도 업데이트
        tokenManager.setUserInfo(this.user)
      }
    },

    /**
     * 인증 상태 초기화
     */
    clearAuth() {
      this.user = null
      this.isAuthenticated = false
      this.error = null
      this.isRefreshing = false
      authService.clearTokens()
    },

    /**
     * 에러 초기화
     */
    clearError() {
      this.error = null
    },

    /**
     * 토큰 유효성 확인
     */
    async ensureAuthenticated() {
      if (!this.isAuthenticated) {
        await this.initialize()
      }
      
      if (!this.isAuthenticated) {
        throw new Error('인증이 필요합니다')
      }
      
      return authService.ensureValidToken()
    },

    /**
     * 권한 확인
     */
    checkPermission(requiredUserType = null, requiresDiagnosis = true) {
      if (!this.isAuthenticated) {
        return { allowed: false, reason: 'NOT_AUTHENTICATED' }
      }

      if (requiresDiagnosis && !this.isDiagnosisCompleted) {
        return { allowed: false, reason: 'DIAGNOSIS_NOT_COMPLETED' }
      }

      if (requiredUserType && this.userType !== requiredUserType) {
        return { allowed: false, reason: 'INSUFFICIENT_USER_TYPE' }
      }

      return { allowed: true }
    }
  }
})

export default useAuthStore