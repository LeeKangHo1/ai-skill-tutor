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
   */
  async sendSessionMessage(userMessage, messageType = 'user') {
    try {
      const response = await apiClient.post('/learning/session/message', {
        user_message: userMessage,
        message_type: messageType,
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
   */
  async submitQuizAnswerV2(userAnswer) {
    try {
      const response = await apiClient.post('/learning/quiz/submit', {
        user_answer: userAnswer,
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
  },

  // =============================================================
  // ===== 🚀 QnA 스트리밍 2단계 요청 방식으로 수정한 함수들 =====
  // =============================================================

  /**
   * [1단계: 인증] QnA 스트리밍 세션 시작 및 임시 ID 요청
   * @param {object} params - 요청 파라미터
   * @returns {Promise<Object>} API 응답 (임시 세션 ID 포함)
   */
  async startQnAStreamSession({ user_message, chapter, section }) {
    try {
      // apiClient는 자동으로 Authorization 헤더를 포함하여 요청합니다.
      const response = await apiClient.post('/learning/qna-stream/start', {
        user_message,
        chapter,
        section
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
   * [2단계: 연결] EventSource를 사용하여 스트리밍 엔드포인트에 연결
   * @param {object} params - 연결 파라미터
   * @returns {EventSource} EventSource 인스턴스
   */
  connectQnAStream({ tempId, onMessage, onError, onClose }) {
    const url = `${import.meta.env.VITE_API_BASE_URL}/learning/qna-stream/stream/${tempId}`;
    
    console.log(`[SSE] Connecting to: ${url}`);
    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      console.log('[SSE] Connection opened.');
    };

    eventSource.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);
        if (onMessage) onMessage(parsedData);
      } catch (e) {
        console.error('[SSE] Failed to parse message data:', event.data, e);
        if (onError) onError({ message: '메시지 파싱 오류', data: event.data });
      }
    };

    eventSource.onerror = (error) => {
      console.error('[SSE] Connection error:', error);
      if (onError) onError(error);
      eventSource.close();
    };

    // onclose는 표준 이벤트가 아니지만, 명시적으로 닫혔을 때를 위해 추가
    // 정상 종료 시 onerror가 먼저 호출될 수 있습니다.
    eventSource.addEventListener('close', () => {
        if(onClose) onClose();
    });
    
    return eventSource;
  }
};

export default learningService;