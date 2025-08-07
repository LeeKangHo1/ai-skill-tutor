// frontend/src/services/authService.js
// 인증 관련 API 서비스 함수들

import apiClient from './api.js'

/**
 * 인증 관련 API 서비스
 * 로그인, 회원가입, 토큰 관리 등의 기능을 제공
 */
export const authService = {
  /**
   * 사용자 로그인
   * @param {Object} credentials - 로그인 정보
   * @param {string} credentials.email - 이메일
   * @param {string} credentials.password - 비밀번호
   * @returns {Promise<Object>} 로그인 결과
   */
  async login(credentials) {
    try {
      const response = await apiClient.post('/auth/login', credentials)
      return {
        success: true,
        data: response.data,
        status: response.status
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status || 0
      }
    }
  },

  /**
   * 사용자 회원가입
   * @param {Object} userData - 회원가입 정보
   * @param {string} userData.email - 이메일
   * @param {string} userData.password - 비밀번호
   * @param {string} userData.name - 사용자 이름
   * @returns {Promise<Object>} 회원가입 결과
   */
  async register(userData) {
    try {
      const response = await apiClient.post('/auth/register', userData)
      return {
        success: true,
        data: response.data,
        status: response.status
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status || 0
      }
    }
  },

  /**
   * 사용자 로그아웃
   * @returns {Promise<Object>} 로그아웃 결과
   */
  async logout() {
    try {
      const response = await apiClient.post('/auth/logout')
      return {
        success: true,
        data: response.data,
        status: response.status
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status || 0
      }
    }
  },

  /**
   * 토큰 갱신
   * @param {string} refreshToken - 리프레시 토큰
   * @returns {Promise<Object>} 토큰 갱신 결과
   */
  async refreshToken(refreshToken) {
    try {
      const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken })
      return {
        success: true,
        data: response.data,
        status: response.status
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status || 0
      }
    }
  },

  /**
   * 현재 사용자 정보 조회
   * @returns {Promise<Object>} 사용자 정보
   */
  async getCurrentUser() {
    try {
      const response = await apiClient.get('/auth/me')
      return {
        success: true,
        data: response.data,
        status: response.status
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status || 0
      }
    }
  },

  /**
   * 비밀번호 변경
   * @param {Object} passwordData - 비밀번호 변경 정보
   * @param {string} passwordData.currentPassword - 현재 비밀번호
   * @param {string} passwordData.newPassword - 새 비밀번호
   * @returns {Promise<Object>} 비밀번호 변경 결과
   */
  async changePassword(passwordData) {
    try {
      const response = await apiClient.put('/auth/change-password', passwordData)
      return {
        success: true,
        data: response.data,
        status: response.status
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status || 0
      }
    }
  }
}

export default authService