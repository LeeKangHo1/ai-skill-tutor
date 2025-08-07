// frontend/src/services/dashboardService.js
// 대시보드 관련 API 서비스 함수들

import apiClient from './api.js'

/**
 * 대시보드 관련 API 서비스
 * 사용자 통계, 학습 현황, 챕터 정보 등의 기능을 제공
 */
export const dashboardService = {
  /**
   * 사용자 대시보드 전체 데이터 조회
   * @returns {Promise<Object>} 대시보드 데이터
   */
  async getDashboardData() {
    try {
      const response = await apiClient.get('/dashboard')
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
   * 사용자 학습 통계 조회
   * @param {Object} params - 조회 파라미터
   * @param {string} params.period - 조회 기간 (week, month, all)
   * @returns {Promise<Object>} 학습 통계
   */
  async getUserStatistics(params = {}) {
    try {
      const response = await apiClient.get('/dashboard/statistics', { params })
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
   * 사용자 학습 진행률 조회
   * @returns {Promise<Object>} 학습 진행률
   */
  async getLearningProgress() {
    try {
      const response = await apiClient.get('/dashboard/progress')
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
   * 최근 학습 활동 조회
   * @param {Object} params - 조회 파라미터
   * @param {number} params.limit - 조회할 활동 수
   * @returns {Promise<Object>} 최근 학습 활동
   */
  async getRecentActivities(params = { limit: 10 }) {
    try {
      const response = await apiClient.get('/dashboard/activities', { params })
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
   * 추천 학습 콘텐츠 조회
   * @returns {Promise<Object>} 추천 콘텐츠
   */
  async getRecommendedContent() {
    try {
      const response = await apiClient.get('/dashboard/recommendations')
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
   * 모든 챕터 목록 조회
   * @returns {Promise<Object>} 챕터 목록
   */
  async getChapters() {
    try {
      const response = await apiClient.get('/dashboard/chapters')
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
   * 특정 챕터 상세 정보 조회
   * @param {number} chapterId - 챕터 ID
   * @returns {Promise<Object>} 챕터 상세 정보
   */
  async getChapterDetail(chapterId) {
    try {
      const response = await apiClient.get(`/dashboard/chapters/${chapterId}`)
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
   * 사용자 성취도 조회
   * @returns {Promise<Object>} 성취도 정보
   */
  async getAchievements() {
    try {
      const response = await apiClient.get('/dashboard/achievements')
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
   * 학습 목표 설정
   * @param {Object} goalData - 목표 데이터
   * @param {string} goalData.type - 목표 타입 (daily, weekly, monthly)
   * @param {number} goalData.target - 목표 수치
   * @returns {Promise<Object>} 목표 설정 결과
   */
  async setLearningGoal(goalData) {
    try {
      const response = await apiClient.post('/dashboard/goals', goalData)
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
   * 학습 목표 조회
   * @returns {Promise<Object>} 현재 학습 목표
   */
  async getLearningGoals() {
    try {
      const response = await apiClient.get('/dashboard/goals')
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

export default dashboardService