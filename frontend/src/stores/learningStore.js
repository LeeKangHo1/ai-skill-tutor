// frontend/src/stores/learningStore.js
// 학습 세션 전용 상태 관리 Pinia Store
// API 호출과 관련된 모든 상태를 관리하며 tutorStore와 분리된 역할을 담당

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import learningService from '../services/learningService.js'

export const useLearningStore = defineStore('learning', () => {
  // ===== 세션 관리 상태 =====
  
  // 현재 활성 세션 정보
  const sessionState = ref({
    session_id: null,
    is_active: false,
    start_time: null,
    chapter_number: null,
    section_number: null,
    chapter_title: '',
    section_title: '',
    estimated_duration: '',
    // 세션 완료 관련 필드
    completed_at: null,
    final_score: null,
    next_chapter: null,
    next_section: null
  })
  
  // ===== API 호출 상태 =====
  
  // API 요청 상태 관리
  const apiState = ref({
    loading: false,
    error: null,
    last_request: null,
    retry_count: 0,
    request_timestamp: null
  })
  
  // ===== 워크플로우 응답 상태 =====
  
  // 백엔드 워크플로우 응답 데이터
  const workflowState = ref({
    current_agent: null,
    session_progress_stage: null,
    ui_mode: null,
    content: null,
    evaluation_result: null,
    metadata: {}
  })
  
  // ===== 에러 처리 상태 =====
  
  // 에러 분류 및 처리 상태
  const errorState = ref({
    network_error: false,
    auth_error: false,
    server_error: false,
    validation_error: false,
    error_message: '',
    error_code: null,
    can_retry: false
  })
  
  // ===== 컴퓨티드 속성 =====
  
  // 세션 활성 상태 확인
  const isSessionActive = computed(() => sessionState.value.is_active && sessionState.value.session_id)
  
  // API 로딩 상태 확인
  const isLoading = computed(() => apiState.value.loading)
  
  // 에러 발생 여부 확인
  const hasError = computed(() => {
    const { network_error, auth_error, server_error, validation_error } = errorState.value
    return network_error || auth_error || server_error || validation_error
  })
  
  // 재시도 가능 여부 확인
  const canRetry = computed(() => errorState.value.can_retry && apiState.value.retry_count < 3)
  
  // 현재 세션 정보 요약
  const sessionSummary = computed(() => {
    if (!sessionState.value.session_id) return null
    
    return {
      session_id: sessionState.value.session_id,
      chapter: `${sessionState.value.chapter_number}장 - ${sessionState.value.chapter_title}`,
      section: `${sessionState.value.section_number}절 - ${sessionState.value.section_title}`,
      duration: sessionState.value.estimated_duration,
      current_agent: workflowState.value.current_agent,
      progress_stage: workflowState.value.session_progress_stage,
      is_active: sessionState.value.is_active,
      is_completed: !sessionState.value.is_active && sessionState.value.completed_at
    }
  })
  
  // 세션 완료 상태 확인
  const isSessionCompleted = computed(() => {
    return !sessionState.value.is_active && sessionState.value.completed_at !== null
  })
  
  // 다음 단계 정보
  const nextStepInfo = computed(() => {
    if (!isSessionCompleted.value) return null
    
    return {
      has_next_step: sessionState.value.next_chapter !== null && sessionState.value.next_section !== null,
      next_chapter: sessionState.value.next_chapter,
      next_section: sessionState.value.next_section,
      completion_data: workflowState.value.content?.completion_data || null
    }
  })
  
  // ===== 핵심 액션 메서드 =====
  
  /**
   * 학습 세션 시작
   * POST /learning/session/start API 호출
   * @param {number} chapterNumber - 챕터 번호
   * @param {number} sectionNumber - 섹션 번호
   * @param {string} userMessage - 사용자 초기 메시지
   * @returns {Promise<Object>} API 응답 결과
   */
  const startSession = async (chapterNumber, sectionNumber, userMessage = '학습을 시작합니다') => {
    console.log('학습 세션 시작 요청:', { chapterNumber, sectionNumber, userMessage })
    
    // API 상태 초기화
    setApiLoading(true)
    clearErrors()
    
    try {
      // API 요청 데이터 구성
      const requestData = {
        chapter_number: chapterNumber,
        section_number: sectionNumber,
        user_message: userMessage
      }
      
      // learningService를 통한 실제 API 호출
      const response = await learningService.startLearningSession(chapterNumber, sectionNumber, userMessage)
      
      if (response.success || response.isFallback) {
        // 세션 상태 업데이트 (기본값 포함)
        updateSessionState({
          session_id: response.data.session_info.session_id || `session_${Date.now()}`,
          is_active: true,
          start_time: new Date(),
          chapter_number: response.data.session_info.chapter_number,
          section_number: response.data.session_info.section_number,
          chapter_title: response.data.session_info.chapter_title,
          section_title: response.data.session_info.section_title,
          estimated_duration: response.data.session_info.estimated_duration
        })
        
        // 워크플로우 응답 업데이트
        updateWorkflowState(response.data.workflow_response)
        
        // 기본값 사용 시 사용자에게 알림
        if (response.isFallback) {
          console.warn('세션 시작 - 기본값 모드:', sessionState.value)
          // 기본값 사용 상태를 별도로 저장할 수 있음
          workflowState.value.metadata.isFallbackMode = true
        } else {
          console.log('세션 시작 성공:', sessionState.value)
        }
        
        return response
      } else {
        // learningService에서 반환한 에러 응답 처리
        handleApiError(response, 'startSession')
        return response
      }
      
    } catch (error) {
      console.error('세션 시작 오류:', error)
      handleApiError(error, 'startSession')
      return {
        success: false,
        error: error.message,
        type: 'session_start_error'
      }
    } finally {
      setApiLoading(false)
    }
  }
  
  /**
   * 세션 메시지 전송
   * POST /learning/session/message API 호출
   * @param {string} userMessage - 사용자 메시지
   * @param {string} messageType - 메시지 타입 (기본값: 'user')
   * @returns {Promise<Object>} API 응답 결과
   */
  const sendMessage = async (userMessage, messageType = 'user') => {
    console.log('메시지 전송 요청:', { userMessage, messageType })
    
    if (!isSessionActive.value) {
      const error = new Error('활성 세션이 없습니다. 먼저 세션을 시작해주세요.')
      handleApiError(error, 'sendMessage')
      return { success: false, error: error.message }
    }
    
    setApiLoading(true)
    clearErrors()
    
    try {
      const requestData = {
        user_message: userMessage,
        message_type: messageType
      }
      
      // learningService를 통한 실제 API 호출
      const response = await learningService.sendSessionMessage(userMessage, messageType)
      
      if (response.success || response.isFallback) {
        // 워크플로우 응답 업데이트
        updateWorkflowState(response.data.workflow_response)
        
        if (response.isFallback) {
          console.warn('메시지 전송 - 기본값 모드:', response.data)
          workflowState.value.metadata.isFallbackMode = true
        } else {
          console.log('메시지 전송 성공:', response.data)
        }
        
        return response
      } else {
        // learningService에서 반환한 에러 응답 처리
        handleApiError(response, 'sendMessage')
        return response
      }
      
    } catch (error) {
      console.error('메시지 전송 오류:', error)
      handleApiError(error, 'sendMessage')
      return {
        success: false,
        error: error.message,
        type: 'message_send_error'
      }
    } finally {
      setApiLoading(false)
    }
  }
  
  /**
   * 퀴즈 답안 제출
   * POST /learning/quiz/submit API 호출
   * @param {string} userAnswer - 사용자 답안
   * @returns {Promise<Object>} API 응답 결과
   */
  const submitQuiz = async (userAnswer) => {
    console.log('퀴즈 답안 제출 요청:', { userAnswer })
    
    if (!isSessionActive.value) {
      const error = new Error('활성 세션이 없습니다. 먼저 세션을 시작해주세요.')
      handleApiError(error, 'submitQuiz')
      return { success: false, error: error.message }
    }
    
    setApiLoading(true)
    clearErrors()
    
    try {
      const requestData = {
        user_answer: userAnswer
      }
      
      // learningService를 통한 실제 API 호출
      const response = await learningService.submitQuizAnswer(userAnswer)
      
      if (response.success || response.isFallback) {
        // 워크플로우 응답 및 평가 결과 업데이트
        updateWorkflowState(response.data.workflow_response)
        
        if (response.data.evaluation_result) {
          workflowState.value.evaluation_result = response.data.evaluation_result
        }
        
        if (response.isFallback) {
          console.warn('퀴즈 제출 - 기본값 모드:', response.data)
          workflowState.value.metadata.isFallbackMode = true
        } else {
          console.log('퀴즈 제출 성공:', response.data)
        }
        
        return response
      } else {
        // learningService에서 반환한 에러 응답 처리
        handleApiError(response, 'submitQuiz')
        return response
      }
      
    } catch (error) {
      console.error('퀴즈 제출 오류:', error)
      handleApiError(error, 'submitQuiz')
      return {
        success: false,
        error: error.message,
        type: 'quiz_submit_error'
      }
    } finally {
      setApiLoading(false)
    }
  }
  
  /**
   * 학습 세션 완료
   * POST /learning/session/complete API 호출
   * @param {string} proceedDecision - 진행 결정 ('proceed' | 'retry' | 'dashboard')
   * @returns {Promise<Object>} API 응답 결과
   */
  const completeSession = async (proceedDecision = 'proceed') => {
    console.log('세션 완료 요청:', { proceedDecision })
    
    if (!isSessionActive.value) {
      const error = new Error('활성 세션이 없습니다.')
      handleApiError(error, 'completeSession')
      return { success: false, error: error.message }
    }
    
    setApiLoading(true)
    clearErrors()
    
    try {
      const requestData = {
        proceed_decision: proceedDecision
      }
      
      // learningService를 통한 실제 API 호출
      const response = await learningService.completeSession(proceedDecision)
      
      if (response.success || response.isFallback) {
        // 세션 완료 처리
        const completionData = response.data.session_completion
        
        // 세션 상태 업데이트
        sessionState.value.is_active = false
        sessionState.value.completed_at = completionData.completed_at
        sessionState.value.final_score = completionData.final_score
        
        // 다음 단계 정보 저장
        sessionState.value.next_chapter = completionData.next_chapter
        sessionState.value.next_section = completionData.next_section
        
        // 워크플로우 상태를 완료 상태로 업데이트
        workflowState.value.session_progress_stage = 'session_completed'
        workflowState.value.ui_mode = 'completion'
        workflowState.value.content = {
          type: 'completion',
          title: response.isFallback ? '세션 완료 (오프라인 모드)' : '세션 완료',
          completion_data: completionData,
          proceed_decision: proceedDecision
        }
        
        if (response.isFallback) {
          console.warn('세션 완료 - 기본값 모드:', {
            completion_data: completionData,
            next_step: {
              chapter: completionData.next_chapter,
              section: completionData.next_section
            }
          })
          workflowState.value.metadata.isFallbackMode = true
        } else {
          console.log('세션 완료 성공:', {
            completion_data: completionData,
            next_step: {
              chapter: completionData.next_chapter,
              section: completionData.next_section
            }
          })
        }
        
        return response
      } else {
        // learningService에서 반환한 에러 응답 처리
        handleApiError(response, 'completeSession')
        return response
      }
      
    } catch (error) {
      console.error('세션 완료 오류:', error)
      handleApiError(error, 'completeSession')
      return {
        success: false,
        error: error.message,
        type: 'session_complete_error'
      }
    } finally {
      setApiLoading(false)
    }
  }
  
  // ===== 에러 처리 메서드 =====
  
  /**
   * API 에러 처리 (learningService 응답 구조에 맞게 개선)
   * @param {Error|Object} error - 발생한 에러 또는 learningService 에러 응답
   * @param {string} context - 에러 발생 컨텍스트
   */
  const handleApiError = (error, context = '') => {
    console.error(`API 에러 [${context}]:`, error)
    
    // learningService에서 반환하는 에러 응답 구조 처리
    if (error && typeof error === 'object' && error.hasOwnProperty('success') && !error.success) {
      const errorType = error.type || 'unknown'
      const errorMessage = error.error || '알 수 없는 오류가 발생했습니다.'
      const canRetry = error.retry || false
      
      // 에러 타입별 상태 설정
      switch (errorType) {
        case 'network':
          errorState.value.network_error = true
          errorState.value.error_message = errorMessage
          errorState.value.can_retry = canRetry
          break
          
        case 'auth':
          errorState.value.auth_error = true
          errorState.value.error_message = errorMessage
          errorState.value.can_retry = canRetry
          break
          
        case 'server':
          errorState.value.server_error = true
          errorState.value.error_message = errorMessage
          errorState.value.can_retry = canRetry
          break
          
        case 'validation':
        case 'permission':
          errorState.value.validation_error = true
          errorState.value.error_message = errorMessage
          errorState.value.can_retry = canRetry
          break
          
        default:
          errorState.value.server_error = true
          errorState.value.error_message = errorMessage
          errorState.value.can_retry = canRetry
      }
      
      errorState.value.error_code = error.status || null
      apiState.value.error = errorMessage
      
    } else {
      // 일반 Error 객체 처리 (기존 로직 유지)
      if (error.code === 'NETWORK_ERROR' || error.message.includes('network')) {
        errorState.value.network_error = true
        errorState.value.error_message = '네트워크 연결을 확인해주세요.'
        errorState.value.can_retry = true
      } else if (error.status === 401 || error.message.includes('auth')) {
        errorState.value.auth_error = true
        errorState.value.error_message = '인증이 필요합니다. 다시 로그인해주세요.'
        errorState.value.can_retry = false
      } else if (error.status >= 500) {
        errorState.value.server_error = true
        errorState.value.error_message = '서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.'
        errorState.value.can_retry = true
      } else if (error.status >= 400 && error.status < 500) {
        errorState.value.validation_error = true
        errorState.value.error_message = error.message || '요청 데이터를 확인해주세요.'
        errorState.value.can_retry = false
      } else {
        errorState.value.server_error = true
        errorState.value.error_message = error.message || '알 수 없는 오류가 발생했습니다.'
        errorState.value.can_retry = true
      }
      
      errorState.value.error_code = error.status || error.code
      apiState.value.error = error.message
    }
  }
  
  /**
   * 에러 상태 초기화
   */
  const clearErrors = () => {
    errorState.value = {
      network_error: false,
      auth_error: false,
      server_error: false,
      validation_error: false,
      error_message: '',
      error_code: null,
      can_retry: false
    }
    apiState.value.error = null
  }
  
  // ===== 상태 업데이트 메서드 =====
  
  /**
   * API 로딩 상태 설정
   * @param {boolean} loading - 로딩 상태
   */
  const setApiLoading = (loading) => {
    apiState.value.loading = loading
    if (loading) {
      apiState.value.request_timestamp = new Date()
    }
  }
  
  /**
   * 세션 상태 업데이트
   * @param {Object} updates - 업데이트할 세션 상태
   */
  const updateSessionState = (updates) => {
    sessionState.value = { ...sessionState.value, ...updates }
  }
  
  /**
   * 워크플로우 상태 업데이트
   * @param {Object} workflowResponse - 워크플로우 응답 데이터
   */
  const updateWorkflowState = (workflowResponse) => {
    if (!workflowResponse) return
    
    workflowState.value = {
      ...workflowState.value,
      ...workflowResponse
    }
    
    console.log('워크플로우 상태 업데이트:', workflowState.value)
  }
  
  // ===== 상태 초기화 메서드 =====
  
  /**
   * 세션 상태 완전 초기화
   */
  const resetSessionState = () => {
    console.log('세션 상태 초기화')
    
    sessionState.value = {
      session_id: null,
      is_active: false,
      start_time: null,
      chapter_number: null,
      section_number: null,
      chapter_title: '',
      section_title: '',
      estimated_duration: '',
      // 세션 완료 관련 필드 초기화
      completed_at: null,
      final_score: null,
      next_chapter: null,
      next_section: null
    }
    
    workflowState.value = {
      current_agent: null,
      session_progress_stage: null,
      ui_mode: null,
      content: null,
      evaluation_result: null,
      metadata: {}
    }
    
    clearErrors()
    
    apiState.value = {
      loading: false,
      error: null,
      last_request: null,
      retry_count: 0,
      request_timestamp: null
    }
  }
  
  /**
   * API 재시도
   * @param {string} lastAction - 마지막 실행한 액션
   * @param {Array} args - 액션 인자들
   */
  const retryLastAction = async (lastAction, ...args) => {
    if (!canRetry.value) {
      console.warn('재시도 불가능한 상태입니다.')
      return { success: false, error: '재시도할 수 없습니다.' }
    }
    
    apiState.value.retry_count += 1
    console.log(`API 재시도 (${apiState.value.retry_count}/3): ${lastAction}`)
    
    switch (lastAction) {
      case 'startSession':
        return await startSession(...args)
      case 'sendMessage':
        return await sendMessage(...args)
      case 'submitQuiz':
        return await submitQuiz(...args)
      case 'completeSession':
        return await completeSession(...args)
      default:
        console.error('알 수 없는 액션:', lastAction)
        return { success: false, error: '재시도할 수 없는 액션입니다.' }
    }
  }
  
  // ===== 임시 시뮬레이션 메서드 (실제 API 연동 시 제거) =====
  
  /**
   * API 호출 시뮬레이션 (개발용)
   * 실제 백엔드 연동 시 이 메서드는 제거하고 learningService 사용
   * @param {string} endpoint - API 엔드포인트
   * @param {Object} data - 요청 데이터
   * @returns {Promise<Object>} 시뮬레이션 응답
   */
  const simulateApiCall = async (endpoint, data) => {
    // 네트워크 지연 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000))
    
    // 시뮬레이션 응답 생성
    switch (endpoint) {
      case '/learning/session/start':
        return {
          success: true,
          data: {
            session_info: {
              session_id: `session_${Date.now()}`,
              chapter_number: data.chapter_number,
              section_number: data.section_number,
              chapter_title: `${data.chapter_number}장 - LLM 기초`,
              section_title: `${data.section_number}절 - 기본 개념`,
              estimated_duration: '15분'
            },
            workflow_response: {
              current_agent: 'theory_educator',
              session_progress_stage: 'session_start',
              ui_mode: 'chat',
              content: {
                type: 'theory',
                title: 'LLM 기본 개념',
                content: '대규모 언어 모델(LLM)에 대해 학습해보겠습니다.'
              }
            }
          }
        }
      
      case '/learning/session/message':
        return {
          success: true,
          data: {
            workflow_response: {
              current_agent: 'quiz_generator',
              session_progress_stage: 'theory_completed',
              ui_mode: 'quiz',
              content: {
                type: 'quiz',
                question: 'LLM의 정의는 무엇인가요?',
                quiz_type: 'multiple_choice',
                options: ['대규모 언어 모델', '작은 언어 모델', '번역 모델', '이미지 모델'],
                hint: 'Large Language Model의 줄임말입니다.'
              }
            }
          }
        }
      
      case '/learning/quiz/submit':
        return {
          success: true,
          data: {
            evaluation_result: {
              is_correct: true,
              score: 100,
              feedback: '정답입니다! 잘 이해하고 계시네요.',
              explanation: 'LLM은 Large Language Model의 줄임말로 대규모 언어 모델을 의미합니다.'
            },
            workflow_response: {
              current_agent: 'evaluation_feedback_agent',
              session_progress_stage: 'quiz_and_feedback_completed',
              ui_mode: 'chat',
              content: {
                type: 'feedback',
                title: '평가 완료',
                content: '이번 섹션을 성공적으로 완료했습니다!',
                next_step_decision: 'proceed'
              }
            }
          }
        }
      
      case '/learning/session/complete':
        const currentChapter = sessionState.value.chapter_number || 2
        const currentSection = sessionState.value.section_number || 1
        
        return {
          success: true,
          data: {
            session_completion: {
              completed_at: new Date().toISOString(),
              final_score: 100,
              session_summary: {
                chapter_number: currentChapter,
                section_number: currentSection,
                total_duration: '12분',
                concepts_learned: ['LLM 기본 개념', '언어 모델의 특징', '실제 활용 사례']
              },
              next_chapter: data.proceed_decision === 'proceed' ? (currentSection >= 3 ? currentChapter + 1 : currentChapter) : null,
              next_section: data.proceed_decision === 'proceed' ? (currentSection >= 3 ? 1 : currentSection + 1) : null,
              next_chapter_title: data.proceed_decision === 'proceed' ? 
                (currentSection >= 3 ? `${currentChapter + 1}장 - 프롬프트 엔지니어링` : `${currentChapter}장 - LLM 기초`) : null,
              next_section_title: data.proceed_decision === 'proceed' ? 
                (currentSection >= 3 ? '1절 - 프롬프트 기본 원리' : `${currentSection + 1}절 - LLM 활용 방법`) : null,
              proceed_options: {
                can_proceed: data.proceed_decision === 'proceed',
                can_retry: true,
                can_dashboard: true
              }
            }
          }
        }
      
      default:
        throw new Error(`알 수 없는 엔드포인트: ${endpoint}`)
    }
  }
  
  // ===== Store 반환 =====
  
  return {
    // 상태
    sessionState,
    apiState,
    workflowState,
    errorState,
    
    // 컴퓨티드
    isSessionActive,
    isLoading,
    hasError,
    canRetry,
    sessionSummary,
    isSessionCompleted,
    nextStepInfo,
    
    // 핵심 액션
    startSession,
    sendMessage,
    submitQuiz,
    completeSession,
    
    // 에러 처리
    handleApiError,
    clearErrors,
    retryLastAction,
    
    // 상태 관리
    setApiLoading,
    updateSessionState,
    updateWorkflowState,
    resetSessionState
  }
})