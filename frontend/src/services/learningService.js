// frontend/src/services/learningService.js

import apiClient from './api.js'

/**
 * 학습 관련 API 서비스 (v2.0 리팩토링)
 *
 * @description
 * - 학습 세션과 관련된 모든 백엔드 API 호출을 담당합니다.
 * - Pinia 스토어(learningStore)에서만 호출되어야 합니다.
 * - 모든 메소드는 API 응답을 일관된 형식({ success, data, error, status })으로 래핑하여 반환합니다.
 * - 캐싱 방지를 위한 로직을 포함합니다.
 */
export const learningService = {
  /**
   * 학습 세션 시작 (v2.0 API)
   * @param {number} chapterNumber - 챕터 번호
   * @param {number} sectionNumber - 섹션 번호
   * @param {string} userMessage - 시작 메시지
   * @returns {Promise<Object>} 세션 시작 결과
   */
  async startLearningSession(chapterNumber, sectionNumber, userMessage) {
    try {
      const response = await apiClient.post('/learning/session/start', {
        chapter_number: chapterNumber,
        section_number: sectionNumber,
        user_message: userMessage
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || error.message,
        status: error.response?.status || 0
      };
    }
  },

  /**
   * 세션 메시지 전송 (v2.0 API - 통합 워크플로우)
   * @param {string} userMessage - 사용자 메시지
   * @param {string} messageType - 메시지 타입 (기본값: 'user')
   * @returns {Promise<Object>} AI 워크플로우 응답
   */
  async sendSessionMessage(userMessage, messageType = 'user') {
    try {
      const response = await apiClient.post('/learning/session/message', {
        user_message: userMessage,
        message_type: messageType,
        // 캐시 방지를 위한 타임스탬프 추가
        timestamp: Date.now(),
        force_new_response: true
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || error.message,
        status: error.response?.status || 0
      };
    }
  },

  /**
   * 퀴즈 답안 제출 (v2.0 API - 통합 워크플로우)
   * @param {string} userAnswer - 사용자 답안
   * @returns {Promise<Object>} 퀴즈 평가 결과
   */
  async submitQuizAnswerV2(userAnswer) {
    try {
      const response = await apiClient.post('/learning/quiz/submit', {
        user_answer: userAnswer,
        // 캐시 방지를 위한 타임스탬프 추가
        timestamp: Date.now(),
        force_new_evaluation: true
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || error.message,
        status: error.response?.status || 0
      };
    }
  },

  /**
   * 학습 세션 완료 (v2.0 API)
   * @param {string} proceedDecision - 다음 단계 진행 여부 ('proceed' | 'retry')
   * @returns {Promise<Object>} 세션 완료 결과
   */
  async completeSession(proceedDecision) {
    try {
      const response = await apiClient.post('/learning/session/complete', {
        proceed_decision: proceedDecision
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || error.message,
        status: error.response?.status || 0
      };
    }
  }
};

export default learningService;