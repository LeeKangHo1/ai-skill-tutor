// src/services/authService.js

/**
 * 인증 관련 API 서비스 (HttpOnly 쿠키 방식)
 * - Access Token: 응답으로 받아서 localStorage 저장
 * - Refresh Token: HttpOnly 쿠키로 자동 관리
 * - 쿠키 자동 전송으로 보안성 강화
 */

import api from './api'
import tokenManager from '../utils/tokenManager'

class AuthService {
  /**
   * 로그인 ID 중복 확인
   */
  async checkLoginIdAvailability(loginId) {
    try {
      const response = await api.post('/auth/check-availability', {
        login_id: loginId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 이메일 중복 확인
   */
  async checkEmailAvailability(email) {
    try {
      const response = await api.post('/auth/check-availability', {
        email: email
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 회원가입
   */
  async register(userData) {
    try {
      const response = await api.post('/auth/register', {
        login_id: userData.loginId,
        username: userData.username,
        email: userData.email,
        password: userData.password
      })

      // 회원가입 성공 시 토큰 자동 저장 (refresh_token은 쿠키로 자동 저장됨)
      if (response.data.success && response.data.data.access_token) {
        const { access_token } = response.data.data
        const userInfo = response.data.data
        
        this.saveTokens(access_token, null, userInfo)
      }

      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 로그인
   */
  async login(credentials) {
    try {
      const response = await api.post('/auth/login', {
        login_id: credentials.loginId,
        password: credentials.password,
        remember_me: credentials.rememberMe || false  // 로그인 상태 유지 옵션 전송
      })

      // 로그인 성공 시 토큰 자동 저장 (refresh_token은 쿠키로 자동 저장됨)
      if (response.data.success && response.data.data) {
        const { access_token, user_info } = response.data.data
        this.saveTokens(access_token, null, user_info)
      }

      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 로그아웃 (HttpOnly 쿠키는 서버에서 자동 삭제)
   */
  async logout() {
    try {
      // 서버에 로그아웃 요청 (refresh_token 쿠키 자동 전송됨)
      await api.post('/auth/logout')
    } catch (error) {
      // 서버 요청 실패해도 로컬 토큰은 삭제
      console.error('로그아웃 API 호출 실패:', error)
    } finally {
      // 로컬 토큰 정리
      this.clearTokens()
    }
  }

  /**
   * 모든 디바이스에서 로그아웃
   */
  async logoutAll() {
    try {
      await api.post('/auth/logout-all')
    } catch (error) {
      console.error('전체 로그아웃 API 호출 실패:', error)
    } finally {
      this.clearTokens()
    }
  }

  /**
   * 토큰 갱신 (HttpOnly 쿠키 자동 전송)
   */
  async refreshToken() {
    try {
      // refresh_token은 쿠키로 자동 전송되므로 요청 본문 불필요
      const response = await api.post('/auth/refresh')

      if (response.data.success && response.data.data) {
        const { access_token } = response.data.data
        
        // 새 Access Token 저장 (Refresh Token은 쿠키로 자동 갱신됨)
        tokenManager.setAccessToken(access_token)

        return response.data
      }
      
      throw new Error('토큰 갱신 실패')
    } catch (error) {
      // 토큰 갱신 실패 시 로그아웃 처리
      this.clearTokens()
      throw this.handleError(error)
    }
  }

  /**
   * 현재 사용자 정보 조회
   */
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me')
      console.log('getCurrentUser - 원본 응답:', response)
      console.log('getCurrentUser - response.data:', response.data)
      console.log('getCurrentUser - response.data.success:', response.data.success)
      console.log('getCurrentUser - response.data.data:', response.data.data)
      
      if (response.data.success) {
        // 서버 응답 구조 확인: data.data가 있으면 사용, 없으면 data 사용
        const userData = response.data.data || response.data
        console.log('getCurrentUser - 사용할 사용자 데이터:', userData)
        
        // 사용자 정보 업데이트 (success, message 등 제외하고 실제 사용자 정보만)
        const userInfo = response.data.data ? response.data.data : {
          user_id: userData.user_id,
          login_id: userData.login_id,
          username: userData.username,
          email: userData.email,
          user_type: userData.user_type,
          diagnosis_completed: userData.diagnosis_completed,
          current_chapter: userData.current_chapter,
          current_section: userData.current_section,
          created_at: userData.created_at,
          updated_at: userData.updated_at
        }
        
        tokenManager.setUserInfo(userInfo)
        return { success: true, data: userInfo }
      }
      
      throw new Error('사용자 정보 조회 실패')
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 토큰 검증
   */
  async verifyToken() {
    try {
      const accessToken = tokenManager.getAccessToken()
      if (!accessToken) {
        return { valid: false, reason: 'NO_TOKEN' }
      }

      const response = await api.post('/auth/verify', {
        access_token: accessToken
      })

      return response.data
    } catch (error) {
      return { valid: false, reason: 'VERIFICATION_FAILED' }
    }
  }

  /**
   * 활성 세션 목록 조회
   */
  async getActiveSessions() {
    try {
      const response = await api.get('/auth/sessions')
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 특정 세션 무효화
   */
  async revokeSession(tokenId) {
    try {
      const response = await api.delete(`/auth/revoke/${tokenId}`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 로그인 상태 확인
   */
  isAuthenticated() {
    const validation = tokenManager.validateTokens()
    return validation.valid
  }

  /**
   * 사용자 정보 조회
   */
  getUserInfo() {
    return tokenManager.getUserInfo()
  }

  /**
   * 사용자 유형 확인
   */
  getUserType() {
    const userInfo = this.getUserInfo()
    return userInfo ? userInfo.user_type : null
  }

  /**
   * 진단 완료 여부 확인
   */
  isDiagnosisCompleted() {
    const userInfo = this.getUserInfo()
    return userInfo ? userInfo.diagnosis_completed : false
  }

  /**
   * 토큰 저장 헬퍼 (refresh_token은 제외)
   */
  saveTokens(accessToken, refreshToken, userInfo) {
    tokenManager.setAccessToken(accessToken)
    // refresh_token은 HttpOnly 쿠키로 관리되므로 저장하지 않음
    if (userInfo) {
      tokenManager.setUserInfo(userInfo)
    }
  }

  /**
   * 토큰 삭제 헬퍼
   */
  clearTokens() {
    tokenManager.clearAll()
  }

  /**
   * 에러 처리 헬퍼
   */
  handleError(error) {
    if (error.response) {
      // 서버 응답이 있는 경우
      const errorData = error.response.data
      
      if (errorData && !errorData.success) {
        return {
          message: errorData.error.message,
          code: errorData.error.code,
          details: errorData.error.details || null,
          status: error.response.status
        }
      }
    }

    // 네트워크 오류 또는 기타 오류
    return {
      message: error.message || '알 수 없는 오류가 발생했습니다',
      code: 'UNKNOWN_ERROR',
      details: null,
      status: error.response?.status || 0
    }
  }

  /**
   * 자동 토큰 갱신 확인 및 처리
   */
  async ensureValidToken() {
    const validation = tokenManager.validateTokens()
    
    if (!validation.valid) {
      if (validation.reason === 'ACCESS_TOKEN_EXPIRED') {
        try {
          await this.refreshToken()
          return true
        } catch (error) {
          return false
        }
      }
      return false
    }
    
    return true
  }
}

// 싱글톤 인스턴스 생성
const authService = new AuthService()

export default authService