// frontend/src/utils/dataMappers.js
// API 응답을 컴포넌트 데이터로 변환하는 유틸리티 함수들

/**
 * API 응답을 컴포넌트 데이터로 변환
 * @param {Object} apiResponse - 백엔드 API 응답
 * @param {string} componentType - 컴포넌트 타입 ('theory', 'quiz', 'chat', 'feedback')
 * @returns {Object} 변환된 컴포넌트 데이터
 */
export const mapApiResponseToComponent = (apiResponse, componentType) => {
  if (!apiResponse?.data?.workflow_response) {
    console.warn('Invalid API response structure:', apiResponse)
    return null
  }

  const { workflow_response } = apiResponse.data
  
  switch (componentType) {
    case 'theory':
      return mapTheoryContent(workflow_response)
    case 'quiz':
      return mapQuizData(workflow_response)
    case 'chat':
      return mapChatMessage(workflow_response)
    case 'feedback':
      return mapFeedbackData(workflow_response)
    default:
      return workflow_response.content
  }
}

/**
 * 이론 컨텐츠 매핑 (새로운 JSON 구조 지원)
 * @param {Object} workflowResponse - 워크플로우 응답
 * @returns {Object} 이론 컨텐츠 데이터
 */
export const mapTheoryContent = (workflowResponse) => {
  const content = workflowResponse.content || {}
  
  console.log('🔍 mapTheoryContent - 원본 content:', content)
  
  // 새로운 JSON 구조인지 확인 (chapter_info, title, sections 필드 존재)
  if (content.chapter_info && content.title && content.sections) {
    console.log('🔍 mapTheoryContent - 직접 구조 감지')
    // 새로운 구조화된 JSON 형태 - 그대로 반환
    return {
      chapter_info: content.chapter_info,
      title: content.title,
      sections: content.sections,
      rawContent: content // 원본 데이터도 보관
    }
  }
  
  // 기존 마크다운/텍스트 형태 처리
  let description = content.content || content.description || content.message || ''
  let title = content.title || 'LLM(Large Language Model)이란?'
  
  console.log('🔍 mapTheoryContent - description 타입:', typeof description)
  console.log('🔍 mapTheoryContent - description 내용:', description)
  
  // description이 객체이고 새로운 JSON 구조를 포함하는 경우
  if (description && typeof description === 'object' && description.chapter_info && description.sections) {
    console.log('🔍 mapTheoryContent - description 내부에서 구조 감지')
    return {
      chapter_info: description.chapter_info,
      title: description.title || title,
      sections: description.sections,
      rawContent: content // 원본 데이터도 보관
    }
  }
  
  // 텍스트 포맷팅 개선 (줄바꿈 처리) - description이 문자열인 경우만
  if (description && typeof description === 'string') {
    description = description
      .replace(/\n\n/g, '\n\n') // 이중 줄바꿈 유지
      .replace(/\n/g, '\n') // 단일 줄바꿈 유지
      .trim()
  }
  
  return {
    title,
    description,
    rawContent: content // 원본 데이터도 보관
  }
}

/**
 * 퀴즈 데이터 매핑
 * @param {Object} workflowResponse - 워크플로우 응답
 * @returns {Object} 퀴즈 데이터
 */
export const mapQuizData = (workflowResponse) => {
  const content = workflowResponse.content || {}
  
  return {
    question: content.question || '퀴즈를 로드 중입니다...',
    type: content.quiz_type || content.type || 'multiple_choice',
    // 백엔드 응답은 문자열 배열 형태이므로 그대로 사용
    options: content.options || [
      '로드 중입니다...',
      '로드 중입니다...',
      '로드 중입니다...',
      '로드 중입니다...'
    ],
    hint: content.hint || '잠시만 기다려주세요.'
  }
}

/**
 * 채팅 메시지 매핑
 * @param {Object} workflowResponse - 워크플로우 응답
 * @returns {Object} 채팅 메시지 데이터
 */
export const mapChatMessage = (workflowResponse) => {
  const content = workflowResponse.content || {}
  
  return {
    sender: '튜터',
    message: content.message || content.content || workflowResponse.message || '응답을 받았습니다.',
    type: workflowResponse.current_agent === 'qna_resolver' ? 'qna' : 'system',
    timestamp: new Date()
  }
}

/**
 * 피드백 데이터 매핑
 * @param {Object} workflowResponse - 워크플로우 응답
 * @returns {Object} 피드백 데이터
 */
export const mapFeedbackData = (workflowResponse) => {
  const content = workflowResponse.content || {}
  
  return {
    scoreText: content.score_text || content.scoreText || '평가 완료',
    explanation: content.explanation || content.feedback || '피드백을 확인해주세요.',
    nextStep: content.next_step || content.nextStep || '다음 단계로 진행하세요.'
  }
}

/**
 * API 에러 처리
 * @param {Error} error - 에러 객체
 * @param {Object} fallbackData - 대체 데이터
 * @returns {Object} 에러 처리 결과
 */
export const handleApiError = (error, fallbackData) => {
  console.error('API 요청 실패:', error)
  
  // 에러 타입별 처리
  if (error.response?.status === 401) {
    console.warn('인증 오류 - 로그인이 필요합니다')
  } else if (error.response?.status >= 500) {
    console.error('서버 오류 - 잠시 후 다시 시도해주세요')
  } else if (!navigator.onLine) {
    console.warn('네트워크 연결을 확인해주세요')
  }
  
  return {
    success: false,
    data: fallbackData,
    error: error.message || '알 수 없는 오류가 발생했습니다'
  }
}

/**
 * 안전한 API 호출 래퍼
 * @param {Function} apiFunction - API 호출 함수
 * @param {Object} fallbackData - 실패 시 사용할 대체 데이터
 * @returns {Promise<Object>} API 호출 결과
 */
export const safeApiCall = async (apiFunction, fallbackData) => {
  try {
    const result = await apiFunction()
    
    if (result.success) {
      return { success: true, data: result.data }
    } else {
      console.warn('API 호출 실패:', result.error)
      return { success: false, data: fallbackData, error: result.error }
    }
  } catch (error) {
    return handleApiError(error, fallbackData)
  }
}