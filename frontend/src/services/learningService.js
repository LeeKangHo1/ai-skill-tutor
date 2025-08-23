// frontend/src/services/learningService.js
// 학습 세션 API 서비스 - v2.0 실제 백엔드 연동

import apiClient from './api.js'

/**
 * 학습 세션 API 서비스 클래스
 * API 문서 v2.0에 정의된 4가지 핵심 학습 세션 API와 연동
 */
class LearningService {
  constructor() {
    this.baseURL = '/learning'
    this.defaultTimeout = 10000
  }

  /**
   * 공통 HTTP 요청 처리 메서드
   * JWT 토큰 인증, 에러 처리, 응답 파싱 로직 포함
   * @param {string} method - HTTP 메서드 (GET, POST, PUT, DELETE)
   * @param {string} endpoint - API 엔드포인트
   * @param {Object} data - 요청 데이터 (POST, PUT의 경우)
   * @returns {Promise<Object>} 처리된 응답 객체
   */
  async makeRequest(method, endpoint, data = null) {
    try {
      const config = {
        method: method.toLowerCase(),
        url: `${this.baseURL}${endpoint}`,
        timeout: this.defaultTimeout
      }

      // POST, PUT 요청의 경우 데이터 추가
      if (data && (method === 'POST' || method === 'PUT')) {
        config.data = data
      }

      console.log(`[LearningService] ${method} ${endpoint}`, data || '')

      const response = await apiClient(config)

      // API 응답 구조 검증
      if (!this.validateApiResponse(response.data)) {
        throw new Error('Invalid API response structure')
      }

      return {
        success: true,
        data: response.data.data,
        message: response.data.message,
        status: response.status
      }

    } catch (error) {
      return this.handleApiError(error, endpoint)
    }
  }

  /**
   * API 응답 구조 검증
   * @param {Object} response - API 응답 객체
   * @returns {boolean} 검증 결과
   */
  validateApiResponse(response) {
    if (!response || typeof response !== 'object') {
      return false
    }

    // 기본 응답 구조 검증
    if (!response.hasOwnProperty('success')) {
      return false
    }

    // 성공 응답의 경우 data 필드 검증
    if (response.success && !response.hasOwnProperty('data')) {
      return false
    }

    return true
  }

  /**
   * API 에러 처리 및 분류
   * @param {Error} error - 발생한 에러 객체
   * @param {string} endpoint - 요청한 엔드포인트
   * @returns {Object} 처리된 에러 응답
   */
  handleApiError(error, endpoint) {
    console.error(`[LearningService] Error at ${endpoint}:`, error)

    // 네트워크 에러 (연결 실패, 타임아웃 등)
    if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNABORTED') {
      return {
        success: false,
        error: '네트워크 연결을 확인해주세요.',
        type: 'network',
        retry: true,
        status: 0
      }
    }

    // HTTP 응답 에러
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data

      // 인증 에러 (401) - api.js의 인터셉터에서 처리되지만 추가 처리
      if (status === 401) {
        return {
          success: false,
          error: '인증이 필요합니다. 다시 로그인해주세요.',
          type: 'auth',
          retry: false,
          status
        }
      }

      // 권한 에러 (403)
      if (status === 403) {
        return {
          success: false,
          error: errorData?.error?.message || '접근 권한이 없습니다.',
          type: 'permission',
          retry: false,
          status
        }
      }

      // 요청 데이터 오류 (400)
      if (status === 400) {
        return {
          success: false,
          error: errorData?.error?.message || '요청 데이터가 올바르지 않습니다.',
          type: 'validation',
          retry: false,
          status
        }
      }

      // 서버 에러 (500번대)
      if (status >= 500) {
        return {
          success: false,
          error: '서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.',
          type: 'server',
          retry: true,
          status
        }
      }

      // 기타 HTTP 에러
      return {
        success: false,
        error: errorData?.error?.message || `HTTP ${status} 에러가 발생했습니다.`,
        type: 'http',
        retry: false,
        status
      }
    }

    // 기타 에러 (요청 설정 오류 등)
    return {
      success: false,
      error: error.message || '알 수 없는 오류가 발생했습니다.',
      type: 'unknown',
      retry: false,
      status: 0
    }
  }

  /**
   * 학습 세션 시작 API
   * POST /learning/session/start
   * @param {number} chapterNumber - 챕터 번호
   * @param {number} sectionNumber - 섹션 번호
   * @param {string} userMessage - 사용자 메시지
   * @returns {Promise<Object>} 세션 시작 결과 및 워크플로우 응답
   */
  async startLearningSession(chapterNumber, sectionNumber, userMessage) {
    const payload = {
      chapter_number: chapterNumber,
      section_number: sectionNumber,
      user_message: userMessage
    }

    const result = await this.makeRequest('POST', '/session/start', payload)

    // 성공 시 워크플로우 응답 검증
    if (result.success && result.data) {
      const { session_info, workflow_response } = result.data

      if (!this.validateWorkflowResponse(workflow_response)) {
        console.warn('[LearningService] Invalid workflow_response structure')
      }

      if (!session_info) {
        console.warn('[LearningService] Missing session_info in response')
      }
    }

    return result
  }

  /**
   * 세션 메시지 전송 API
   * POST /learning/session/message
   * @param {string} userMessage - 사용자 메시지
   * @param {string} messageType - 메시지 타입 (기본값: 'user')
   * @returns {Promise<Object>} 워크플로우 응답
   */
  async sendSessionMessage(userMessage, messageType = 'user') {
    const payload = {
      user_message: userMessage,
      message_type: messageType
    }

    const result = await this.makeRequest('POST', '/session/message', payload)

    // 성공 시 워크플로우 응답 검증
    if (result.success && result.data?.workflow_response) {
      if (!this.validateWorkflowResponse(result.data.workflow_response)) {
        console.warn('[LearningService] Invalid workflow_response structure')
      }
    }

    return result
  }

  /**
   * 퀴즈 답안 제출 API
   * POST /learning/quiz/submit
   * @param {string} userAnswer - 사용자 답안
   * @returns {Promise<Object>} 평가 결과 및 워크플로우 응답
   */
  async submitQuizAnswer(userAnswer) {
    const payload = {
      user_answer: userAnswer
    }

    const result = await this.makeRequest('POST', '/quiz/submit', payload)

    // 성공 시 워크플로우 응답 및 평가 결과 검증
    if (result.success && result.data?.workflow_response) {
      const { workflow_response } = result.data

      if (!this.validateWorkflowResponse(workflow_response)) {
        console.warn('[LearningService] Invalid workflow_response structure')
      }

      // evaluation_result 검증
      if (workflow_response.evaluation_result) {
        if (!this.validateEvaluationResult(workflow_response.evaluation_result)) {
          console.warn('[LearningService] Invalid evaluation_result structure')
        }
      }
    }

    return result
  }

  /**
   * 학습 세션 완료 API
   * POST /learning/session/complete
   * @param {string} proceedDecision - 진행 결정 ('proceed' 또는 'retry', 기본값: 'proceed')
   * @returns {Promise<Object>} 세션 완료 결과
   */
  async completeSession(proceedDecision = 'proceed') {
    const payload = {
      proceed_decision: proceedDecision
    }

    const result = await this.makeRequest('POST', '/session/complete', payload)

    // 성공 시 세션 완료 정보 검증
    if (result.success && result.data?.workflow_response?.session_completion) {
      const { session_completion } = result.data.workflow_response

      if (!this.validateSessionCompletion(session_completion)) {
        console.warn('[LearningService] Invalid session_completion structure')
      }
    }

    return result
  }

  /**
   * 워크플로우 응답 구조 검증
   * @param {Object} workflowResponse - 워크플로우 응답 객체
   * @returns {boolean} 검증 결과
   */
  validateWorkflowResponse(workflowResponse) {
    if (!workflowResponse || typeof workflowResponse !== 'object') {
      return false
    }

    const required = ['current_agent', 'session_progress_stage', 'ui_mode']
    for (const field of required) {
      if (!workflowResponse.hasOwnProperty(field)) {
        console.warn(`[LearningService] Missing required field: ${field}`)
        return false
      }
    }

    // current_agent 값 검증
    const validAgents = ['theory_educator', 'quiz_generator', 'evaluation_feedback_agent', 'qna_resolver', 'session_manager']
    if (!validAgents.includes(workflowResponse.current_agent)) {
      console.warn(`[LearningService] Invalid current_agent: ${workflowResponse.current_agent}`)
    }

    // ui_mode 값 검증
    const validUIModes = ['chat', 'quiz']
    if (!validUIModes.includes(workflowResponse.ui_mode)) {
      console.warn(`[LearningService] Invalid ui_mode: ${workflowResponse.ui_mode}`)
    }

    return true
  }

  /**
   * 평가 결과 구조 검증
   * @param {Object} evaluationResult - 평가 결과 객체
   * @returns {boolean} 검증 결과
   */
  validateEvaluationResult(evaluationResult) {
    if (!evaluationResult || typeof evaluationResult !== 'object') {
      return false
    }

    const required = ['quiz_type', 'is_answer_correct', 'score', 'feedback']
    for (const field of required) {
      if (!evaluationResult.hasOwnProperty(field)) {
        console.warn(`[LearningService] Missing required evaluation field: ${field}`)
        return false
      }
    }

    return true
  }

  /**
   * 세션 완료 정보 구조 검증
   * @param {Object} sessionCompletion - 세션 완료 정보 객체
   * @returns {boolean} 검증 결과
   */
  validateSessionCompletion(sessionCompletion) {
    if (!sessionCompletion || typeof sessionCompletion !== 'object') {
      return false
    }

    const required = ['completed_chapter', 'completed_section', 'session_summary']
    for (const field of required) {
      if (!sessionCompletion.hasOwnProperty(field)) {
        console.warn(`[LearningService] Missing required completion field: ${field}`)
        return false
      }
    }

    return true
  }

  /**
   * 요청 재시도 메서드 (에러 복구용)
   * @param {string} method - HTTP 메서드
   * @param {string} endpoint - API 엔드포인트
   * @param {Object} data - 요청 데이터
   * @param {number} maxRetries - 최대 재시도 횟수
   * @returns {Promise<Object>} 재시도 결과
   */
  async retryRequest(method, endpoint, data = null, maxRetries = 3) {
    let lastError = null

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`[LearningService] Retry attempt ${attempt}/${maxRetries} for ${method} ${endpoint}`)
        
        const result = await this.makeRequest(method, endpoint, data)
        
        if (result.success) {
          console.log(`[LearningService] Retry successful on attempt ${attempt}`)
          return result
        }
        
        lastError = result
        
        // 재시도 불가능한 에러인 경우 즉시 중단
        if (!result.retry) {
          break
        }
        
        // 재시도 전 대기 (지수 백오프)
        if (attempt < maxRetries) {
          const delay = Math.pow(2, attempt) * 1000 // 2초, 4초, 8초...
          await new Promise(resolve => setTimeout(resolve, delay))
        }
        
      } catch (error) {
        lastError = this.handleApiError(error, endpoint)
        
        if (!lastError.retry) {
          break
        }
      }
    }

    console.error(`[LearningService] All retry attempts failed for ${method} ${endpoint}`)
    return lastError || {
      success: false,
      error: '모든 재시도 시도가 실패했습니다.',
      type: 'retry_failed',
      retry: false,
      status: 0
    }
  }
}

// 싱글톤 인스턴스 생성 및 export
const learningService = new LearningService()

/**
 * 레거시 호환성을 위한 객체 형태 export
 * 기존 코드에서 learningService.startSession() 형태로 사용 가능
 */
export const learningServiceCompat = {
  // 4가지 핵심 API 메서드
  startLearningSession: (chapterNumber, sectionNumber, userMessage) => 
    learningService.startLearningSession(chapterNumber, sectionNumber, userMessage),
  
  sendSessionMessage: (userMessage, messageType = 'user') => 
    learningService.sendSessionMessage(userMessage, messageType),
  
  submitQuizAnswer: (userAnswer) => 
    learningService.submitQuizAnswer(userAnswer),
  
  completeSession: (proceedDecision = 'proceed') => 
    learningService.completeSession(proceedDecision),

  // 유틸리티 메서드
  retryRequest: (method, endpoint, data, maxRetries) => 
    learningService.retryRequest(method, endpoint, data, maxRetries)
}

// 기본 export (클래스 인스턴스)
export default learningService

// 디버그 모드에서 추가 로깅
if (import.meta.env.MODE === 'development') {
  console.log('[LearningService] v2.0 초기화 완료 - 실제 백엔드 API 연동')
  console.log('[LearningService] 지원 API: startLearningSession, sendSessionMessage, submitQuizAnswer, completeSession')
}