// frontend/src/services/learningService.js
// 학습 관련 API 서비스 함수들

import apiClient from './api.js'

/**
 * 학습 관련 API 서비스
 * 학습 세션, 대화, 퀴즈 등의 기능을 제공
 */
export const learningService = {
  /**
   * 새로운 학습 세션 시작
   * @param {Object} sessionData - 세션 시작 정보
   * @param {number} sessionData.chapterId - 챕터 ID
   * @param {string} sessionData.sessionType - 세션 타입 (theory, quiz, practice)
   * @returns {Promise<Object>} 세션 시작 결과
   */
  async startSession(sessionData) {
    try {
      const response = await apiClient.post('/learning/sessions', sessionData)
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
   * 학습 세션 정보 조회
   * @param {string} sessionId - 세션 ID
   * @returns {Promise<Object>} 세션 정보
   */
  async getSession(sessionId) {
    try {
      const response = await apiClient.get(`/learning/sessions/${sessionId}`)
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
   * 사용자의 모든 학습 세션 조회
   * @param {Object} params - 조회 파라미터
   * @param {number} params.page - 페이지 번호
   * @param {number} params.limit - 페이지당 항목 수
   * @returns {Promise<Object>} 세션 목록
   */
  async getUserSessions(params = {}) {
    try {
      const response = await apiClient.get('/learning/sessions', { params })
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
   * 학습 세션에 메시지 전송 (AI와 대화)
   * @param {string} sessionId - 세션 ID
   * @param {Object} messageData - 메시지 데이터
   * @param {string} messageData.message - 사용자 메시지
   * @param {string} messageData.messageType - 메시지 타입
   * @returns {Promise<Object>} AI 응답
   */
  async sendMessage(sessionId, messageData) {
    try {
      const response = await apiClient.post(`/learning/sessions/${sessionId}/messages`, messageData)
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
   * 세션의 대화 기록 조회
   * @param {string} sessionId - 세션 ID
   * @returns {Promise<Object>} 대화 기록
   */
  async getSessionConversations(sessionId) {
    try {
      const response = await apiClient.get(`/learning/sessions/${sessionId}/conversations`)
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
   * 퀴즈 답안 제출
   * @param {string} sessionId - 세션 ID
   * @param {Object} answerData - 답안 데이터
   * @param {string} answerData.answer - 사용자 답안
   * @param {number} answerData.questionId - 문제 ID
   * @returns {Promise<Object>} 채점 결과
   */
  async submitQuizAnswer(sessionId, answerData) {
    try {
      const response = await apiClient.post(`/learning/sessions/${sessionId}/quiz/submit`, answerData)
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
   * 학습 세션 완료
   * @param {string} sessionId - 세션 ID
   * @param {Object} completionData - 완료 데이터
   * @param {number} completionData.score - 점수
   * @param {string} completionData.feedback - 피드백
   * @returns {Promise<Object>} 완료 결과
   */
  async completeSession(sessionId, completionData) {
    try {
      const response = await apiClient.put(`/learning/sessions/${sessionId}/complete`, completionData)
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
   * 챕터별 학습 진행률 조회
   * @param {number} chapterId - 챕터 ID (선택사항)
   * @returns {Promise<Object>} 학습 진행률
   */
  async getLearningProgress(chapterId = null) {
    try {
      const url = chapterId ? `/learning/progress/${chapterId}` : '/learning/progress'
      const response = await apiClient.get(url)
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

export default learningService