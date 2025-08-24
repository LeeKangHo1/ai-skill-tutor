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
 * 이론 컨텐츠 매핑
 * @param {Object} workflowResponse - 워크플로우 응답
 * @returns {Object} 이론 컨텐츠 데이터
 */
export const mapTheoryContent = (workflowResponse) => {
  const content = workflowResponse.content || {}
  
  // API 응답에서 실제 컨텐츠 추출
  let description = content.content || content.description || content.message || ''
  let title = content.title || 'LLM(Large Language Model)이란?'
  
  // 텍스트 포맷팅 개선 (줄바꿈 처리)
  if (description) {
    description = description
      .replace(/\n\n/g, '\n\n') // 이중 줄바꿈 유지
      .replace(/\n/g, '\n') // 단일 줄바꿈 유지
      .trim()
  }
  
  // API 응답에서 핵심 포인트와 예시 추출 시도
  let keyPoints = content.key_points || content.keyPoints || []
  let examples = content.examples || []
  
  // 만약 API에서 구조화된 데이터가 없다면 텍스트에서 추출 시도
  if (keyPoints.length === 0 && description) {
    // 텍스트에서 핵심 포인트 패턴 찾기
    const keyPointsMatch = description.match(/💡 핵심 포인트:?\s*([\s\S]*?)(?=📋|$)/i)
    if (keyPointsMatch) {
      keyPoints = keyPointsMatch[1]
        .split('\n')
        .map(point => point.replace(/^[-•*]\s*/, '').trim())
        .filter(point => point.length > 0)
    }
  }
  
  if (examples.length === 0 && description) {
    // 텍스트에서 예시 패턴 찾기
    const examplesMatch = description.match(/📋 대표 예시:?\s*([\s\S]*?)(?=💡|$)/i)
    if (examplesMatch) {
      examples = examplesMatch[1]
        .split('\n')
        .map(example => example.replace(/^[-•*]\s*/, '').trim())
        .filter(example => example.length > 0)
    }
  }
  
  // 기본값 설정 (API에서 데이터를 추출하지 못한 경우)
  if (keyPoints.length === 0) {
    keyPoints = [
      '대규모 데이터 학습',
      '언어 이해 및 생성',
      '문맥 파악 능력'
    ]
  }
  
  if (examples.length === 0) {
    examples = [
      'ChatGPT (OpenAI)',
      'Claude (Anthropic)',
      'Bard (Google)'
    ]
  }
  
  return {
    title,
    description,
    keyPoints,
    examples,
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
    question: content.question || '다음 중 LLM의 특징이 아닌 것은?',
    type: content.quiz_type || content.type || 'multiple_choice',
    options: content.options?.map((option, index) => ({
      value: (index + 1).toString(),
      text: option
    })) || [
      { value: '1', text: '대규모 데이터 학습' },
      { value: '2', text: '실시간 인터넷 검색' },
      { value: '3', text: '언어 이해 능력' },
      { value: '4', text: '텍스트 생성 능력' }
    ],
    hint: content.hint || 'LLM의 핵심 특징을 생각해보세요.'
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