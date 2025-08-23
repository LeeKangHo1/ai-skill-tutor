// frontend/src/composables/useErrorHandler.js
// 에러 처리 및 사용자 친화적 메시지 표시를 위한 컴포저블

import { ref, computed } from 'vue'
import { useLearningStore } from '../stores/learningStore.js'

/**
 * 에러 처리 컴포저블
 * learningStore의 에러 상태를 기반으로 사용자 친화적 에러 표시 기능 제공
 */
export function useErrorHandler() {
  const learningStore = useLearningStore()
  
  // 에러 알림 표시 상태
  const showErrorAlert = ref(false)
  const currentErrorContext = ref('')
  
  // learningStore의 에러 상태를 기반으로 한 컴퓨티드 속성들
  const errorInfo = computed(() => {
    const { errorState } = learningStore
    
    if (!learningStore.hasError) {
      return null
    }
    
    // 에러 타입 결정
    let errorType = 'unknown'
    if (errorState.network_error) errorType = 'network'
    else if (errorState.auth_error) errorType = 'auth'
    else if (errorState.server_error) errorType = 'server'
    else if (errorState.validation_error) errorType = 'validation'
    
    return {
      type: errorType,
      message: errorState.error_message,
      code: errorState.error_code,
      canRetry: errorState.can_retry && learningStore.canRetry,
      context: currentErrorContext.value
    }
  })
  
  // 에러 메시지 개선 (더 사용자 친화적으로)
  const friendlyErrorMessage = computed(() => {
    if (!errorInfo.value) return ''
    
    const { type, message, context } = errorInfo.value
    
    // 컨텍스트별 메시지 개선
    const contextMessages = {
      startSession: {
        network: '학습 세션을 시작할 수 없습니다. 인터넷 연결을 확인해주세요.',
        auth: '로그인이 필요합니다. 다시 로그인 후 학습을 시작해주세요.',
        server: '학습 서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.',
        validation: '학습 정보가 올바르지 않습니다. 챕터와 섹션을 다시 선택해주세요.'
      },
      sendMessage: {
        network: '메시지를 전송할 수 없습니다. 네트워크 연결을 확인해주세요.',
        auth: '세션이 만료되었습니다. 다시 로그인해주세요.',
        server: '메시지 처리 중 서버 오류가 발생했습니다. 다시 시도해주세요.',
        validation: '메시지 형식이 올바르지 않습니다. 다시 입력해주세요.'
      },
      submitQuiz: {
        network: '퀴즈 답안을 제출할 수 없습니다. 연결 상태를 확인해주세요.',
        auth: '인증이 만료되었습니다. 다시 로그인 후 답안을 제출해주세요.',
        server: '답안 채점 중 오류가 발생했습니다. 다시 제출해주세요.',
        validation: '답안 형식이 올바르지 않습니다. 다시 선택하거나 입력해주세요.'
      },
      completeSession: {
        network: '세션을 완료할 수 없습니다. 네트워크 상태를 확인해주세요.',
        auth: '세션 완료 권한이 없습니다. 다시 로그인해주세요.',
        server: '세션 완료 처리 중 오류가 발생했습니다. 다시 시도해주세요.',
        validation: '세션 완료 정보가 올바르지 않습니다.'
      }
    }
    
    // 컨텍스트와 타입에 맞는 메시지 반환
    if (contextMessages[context] && contextMessages[context][type]) {
      return contextMessages[context][type]
    }
    
    // 기본 메시지 반환
    return message || '알 수 없는 오류가 발생했습니다.'
  })
  
  // 도움말 정보
  const helpInfo = computed(() => {
    if (!errorInfo.value) return null
    
    const { type, context } = errorInfo.value
    
    const helpMessages = {
      network: {
        title: '네트워크 연결 문제 해결',
        content: [
          '1. 인터넷 연결 상태를 확인해주세요',
          '2. Wi-Fi 또는 모바일 데이터 연결을 다시 시도해주세요',
          '3. 방화벽이나 보안 프로그램이 차단하고 있지 않은지 확인해주세요',
          '4. 문제가 지속되면 네트워크 관리자에게 문의하세요'
        ]
      },
      auth: {
        title: '인증 문제 해결',
        content: [
          '1. 로그아웃 후 다시 로그인해주세요',
          '2. 브라우저 쿠키와 캐시를 삭제해보세요',
          '3. 비밀번호가 변경되었다면 새 비밀번호로 로그인하세요',
          '4. 계정 문제가 있다면 고객지원에 문의하세요'
        ]
      },
      server: {
        title: '서버 오류 해결',
        content: [
          '1. 잠시 후 다시 시도해주세요',
          '2. 페이지를 새로고침해보세요',
          '3. 다른 브라우저에서 시도해보세요',
          '4. 문제가 계속되면 고객지원에 신고해주세요'
        ]
      },
      validation: {
        title: '입력 데이터 문제 해결',
        content: [
          '1. 입력한 정보가 올바른지 확인해주세요',
          '2. 필수 항목이 모두 입력되었는지 확인하세요',
          '3. 특수문자나 형식이 올바른지 확인하세요',
          '4. 문제가 지속되면 다른 방법으로 시도해보세요'
        ]
      }
    }
    
    return helpMessages[type] || {
      title: '일반적인 문제 해결',
      content: [
        '1. 페이지를 새로고침해보세요',
        '2. 브라우저를 다시 시작해보세요',
        '3. 다른 기기에서 시도해보세요',
        '4. 고객지원에 문의하세요'
      ]
    }
  })
  
  /**
   * 에러 표시
   * @param {string} context - 에러 발생 컨텍스트
   */
  const showError = (context = '') => {
    currentErrorContext.value = context
    showErrorAlert.value = true
  }
  
  /**
   * 에러 숨기기
   */
  const hideError = () => {
    showErrorAlert.value = false
    currentErrorContext.value = ''
    learningStore.clearErrors()
  }
  
  /**
   * 에러 재시도
   * @param {string} lastAction - 마지막 실행한 액션
   * @param {Array} args - 액션 인자들
   */
  const retryLastAction = async (lastAction, ...args) => {
    try {
      hideError()
      const result = await learningStore.retryLastAction(lastAction, ...args)
      
      if (!result.success) {
        showError(lastAction)
      }
      
      return result
    } catch (error) {
      console.error('재시도 중 오류:', error)
      showError(lastAction)
      return { success: false, error: error.message }
    }
  }
  
  /**
   * 에러 발생 시 자동으로 알림 표시
   * learningStore의 에러 상태 변화를 감지
   */
  const watchForErrors = () => {
    // learningStore의 hasError 상태를 감시하여 자동으로 에러 표시
    const unwatch = learningStore.$subscribe((mutation, state) => {
      if (state.hasError && !showErrorAlert.value) {
        showError()
      }
    })
    
    return unwatch
  }
  
  /**
   * 특정 액션 실행 시 에러 처리 래퍼
   * @param {Function} action - 실행할 액션
   * @param {string} context - 액션 컨텍스트
   * @param {Array} args - 액션 인자들
   */
  const executeWithErrorHandling = async (action, context, ...args) => {
    try {
      hideError()
      const result = await action(...args)
      
      if (!result.success) {
        showError(context)
      }
      
      return result
    } catch (error) {
      console.error(`액션 실행 중 오류 [${context}]:`, error)
      learningStore.handleApiError(error, context)
      showError(context)
      return { success: false, error: error.message }
    }
  }
  
  return {
    // 상태
    showErrorAlert,
    errorInfo,
    friendlyErrorMessage,
    helpInfo,
    
    // 메서드
    showError,
    hideError,
    retryLastAction,
    watchForErrors,
    executeWithErrorHandling
  }
}

/**
 * 전역 에러 핸들러 설정
 * Vue 앱 전체에서 발생하는 에러를 처리
 */
export function setupGlobalErrorHandler(app) {
  // Vue 에러 핸들러
  app.config.errorHandler = (error, instance, info) => {
    console.error('Vue 에러:', error, info)
    
    // learningStore 에러로 처리
    const learningStore = useLearningStore()
    learningStore.handleApiError(error, 'vue_error')
  }
  
  // 전역 Promise rejection 핸들러
  window.addEventListener('unhandledrejection', (event) => {
    console.error('처리되지 않은 Promise rejection:', event.reason)
    
    const learningStore = useLearningStore()
    learningStore.handleApiError(event.reason, 'promise_rejection')
  })
}