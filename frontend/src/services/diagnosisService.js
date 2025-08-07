// frontend/src/services/diagnosisService.js
// 사용자 진단 관련 API 서비스 함수들

import apiClient from './api.js'

/**
 * 사용자 진단 관련 API 서비스
 * AI 활용 수준 진단, 학습 경로 추천 등의 기능을 제공
 */
export const diagnosisService = {
  /**
   * 사용자 진단 시작
   * @returns {Promise<Object>} 진단 시작 결과
   */
  async startDiagnosis() {
    try {
      const response = await apiClient.post('/diagnosis/start')
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
   * 진단 질문 목록 조회
   * @param {string} diagnosisId - 진단 ID
   * @returns {Promise<Object>} 진단 질문 목록
   */
  async getDiagnosisQuestions(diagnosisId) {
    try {
      const response = await apiClient.get(`/diagnosis/${diagnosisId}/questions`)
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
   * 진단 답변 제출
   * @param {string} diagnosisId - 진단 ID
   * @param {Object} answerData - 답변 데이터
   * @param {number} answerData.questionId - 질문 ID
   * @param {string} answerData.answer - 사용자 답변
   * @param {number} answerData.score - 답변 점수 (선택사항)
   * @returns {Promise<Object>} 답변 제출 결과
   */
  async submitAnswer(diagnosisId, answerData) {
    try {
      const response = await apiClient.post(`/diagnosis/${diagnosisId}/answers`, answerData)
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
   * 진단 완료 및 결과 조회
   * @param {string} diagnosisId - 진단 ID
   * @returns {Promise<Object>} 진단 결과
   */
  async completeDiagnosis(diagnosisId) {
    try {
      const response = await apiClient.post(`/diagnosis/${diagnosisId}/complete`)
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
   * 진단 결과 상세 조회
   * @param {string} diagnosisId - 진단 ID
   * @returns {Promise<Object>} 진단 결과 상세
   */
  async getDiagnosisResult(diagnosisId) {
    try {
      const response = await apiClient.get(`/diagnosis/${diagnosisId}/result`)
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
   * 사용자의 모든 진단 기록 조회
   * @param {Object} params - 조회 파라미터
   * @param {number} params.page - 페이지 번호
   * @param {number} params.limit - 페이지당 항목 수
   * @returns {Promise<Object>} 진단 기록 목록
   */
  async getUserDiagnoses(params = {}) {
    try {
      const response = await apiClient.get('/diagnosis/history', { params })
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
   * 진단 기반 학습 경로 추천
   * @param {string} diagnosisId - 진단 ID
   * @returns {Promise<Object>} 추천 학습 경로
   */
  async getRecommendedPath(diagnosisId) {
    try {
      const response = await apiClient.get(`/diagnosis/${diagnosisId}/recommendations`)
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
   * 진단 재시작 (기존 진단 무효화)
   * @returns {Promise<Object>} 진단 재시작 결과
   */
  async restartDiagnosis() {
    try {
      const response = await apiClient.post('/diagnosis/restart')
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
   * 현재 사용자의 AI 활용 수준 조회
   * @returns {Promise<Object>} 현재 AI 활용 수준
   */
  async getCurrentLevel() {
    try {
      const response = await apiClient.get('/diagnosis/current-level')
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
   * 진단 진행 상태 조회
   * @param {string} diagnosisId - 진단 ID
   * @returns {Promise<Object>} 진단 진행 상태
   */
  async getDiagnosisProgress(diagnosisId) {
    try {
      const response = await apiClient.get(`/diagnosis/${diagnosisId}/progress`)
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

export default diagnosisService