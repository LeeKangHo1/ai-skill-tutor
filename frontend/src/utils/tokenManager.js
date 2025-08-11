// src/utils/tokenManager.js

/**
 * JWT 토큰 관리 유틸리티
 * - localStorage를 통한 토큰 저장/조회/삭제
 * - 토큰 만료 검사 및 자동 갱신
 */

const TOKEN_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info'
}

class TokenManager {
  /**
   * Access Token 저장
   */
  setAccessToken(token) {
    if (token) {
      localStorage.setItem(TOKEN_KEYS.ACCESS_TOKEN, token)
    }
  }

  /**
   * Refresh Token 저장
   */
  setRefreshToken(token) {
    if (token) {
      localStorage.setItem(TOKEN_KEYS.REFRESH_TOKEN, token)
    }
  }

  /**
   * 사용자 정보 저장
   */
  setUserInfo(userInfo) {
    if (userInfo) {
      localStorage.setItem(TOKEN_KEYS.USER_INFO, JSON.stringify(userInfo))
    }
  }

  /**
   * Access Token 조회
   */
  getAccessToken() {
    return localStorage.getItem(TOKEN_KEYS.ACCESS_TOKEN)
  }

  /**
   * Refresh Token 조회
   */
  getRefreshToken() {
    return localStorage.getItem(TOKEN_KEYS.REFRESH_TOKEN)
  }

  /**
   * 사용자 정보 조회
   */
  getUserInfo() {
    const userInfo = localStorage.getItem(TOKEN_KEYS.USER_INFO)
    return userInfo ? JSON.parse(userInfo) : null
  }

  /**
   * 모든 토큰 및 사용자 정보 삭제
   */
  clearAll() {
    localStorage.removeItem(TOKEN_KEYS.ACCESS_TOKEN)
    localStorage.removeItem(TOKEN_KEYS.REFRESH_TOKEN)
    localStorage.removeItem(TOKEN_KEYS.USER_INFO)
  }

  /**
   * 토큰 존재 여부 확인 (HttpOnly 쿠키 방식에 맞게 수정)
   */
  hasTokens() {
    // Access Token만 확인 (Refresh Token은 HttpOnly 쿠키로 관리됨)
    return !!this.getAccessToken()
  }

  /**
   * JWT 토큰 페이로드 파싱
   */
  parseToken(token) {
    if (!token) return null
    
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      return JSON.parse(jsonPayload)
    } catch (error) {
      console.error('토큰 파싱 오류:', error)
      return null
    }
  }

  /**
   * 토큰 만료 여부 확인
   * @param {string} token - 확인할 토큰
   * @param {number} bufferMinutes - 만료 전 버퍼 시간 (분)
   */
  isTokenExpired(token, bufferMinutes = 5) {
    const payload = this.parseToken(token)
    if (!payload || !payload.exp) return true

    const currentTime = Math.floor(Date.now() / 1000)
    const bufferTime = bufferMinutes * 60
    
    return payload.exp <= (currentTime + bufferTime)
  }

  /**
   * Access Token 만료 여부 확인
   */
  isAccessTokenExpired() {
    const accessToken = this.getAccessToken()
    return !accessToken || this.isTokenExpired(accessToken)
  }

  /**
   * Refresh Token 만료 여부 확인
   */
  isRefreshTokenExpired() {
    const refreshToken = this.getRefreshToken()
    return !refreshToken || this.isTokenExpired(refreshToken, 0) // 버퍼 시간 없음
  }

  /**
   * 토큰에서 사용자 정보 추출
   */
  getUserInfoFromToken() {
    const accessToken = this.getAccessToken()
    if (!accessToken) return null

    const payload = this.parseToken(accessToken)
    if (!payload) return null

    return {
      user_id: payload.user_id,
      login_id: payload.login_id,
      user_type: payload.user_type
    }
  }

  /**
   * 토큰 유효성 검증 (HttpOnly 쿠키 방식에 맞게 수정)
   */
  validateTokens() {
    const accessToken = this.getAccessToken()

    // Access Token이 없는 경우
    if (!accessToken) {
      return { valid: false, reason: 'NO_ACCESS_TOKEN' }
    }

    // Access Token이 만료된 경우 (갱신 필요)
    if (this.isAccessTokenExpired()) {
      return { valid: false, reason: 'ACCESS_TOKEN_EXPIRED' }
    }

    return { valid: true }
  }

  /**
   * 토큰 정보 디버깅 (개발용)
   */
  debugTokenInfo() {
    const accessToken = this.getAccessToken()
    const refreshToken = this.getRefreshToken()

    console.log('=== Token Debug Info ===')
    console.log('Access Token:', accessToken ? '존재' : '없음')
    console.log('Refresh Token:', refreshToken ? '존재' : '없음')
    
    if (accessToken) {
      const payload = this.parseToken(accessToken)
      console.log('Access Token Payload:', payload)
      console.log('Access Token Expired:', this.isAccessTokenExpired())
    }
    
    if (refreshToken) {
      const refreshPayload = this.parseToken(refreshToken)
      console.log('Refresh Token Payload:', refreshPayload)
      console.log('Refresh Token Expired:', this.isRefreshTokenExpired())
    }
    
    console.log('========================')
  }
}

// 싱글톤 인스턴스 생성
const tokenManager = new TokenManager()

export default tokenManager