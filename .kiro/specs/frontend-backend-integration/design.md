# Design Document

## Overview

프론트엔드 컴포넌트들을 백엔드 API와 연동하는 시스템을 설계합니다. 기존 더미데이터 기반 컴포넌트 구조를 유지하면서 실제 API 호출로 전환하는 것이 목표입니다. MainContentArea → QuizInteraction → ChatInteraction 순서로 단계별 구현하며, 각 단계마다 ComponentTest.vue로 검증합니다.

## Architecture

### 전체 아키텍처 구조

```
Frontend Components
├── MainContentArea.vue (이론/퀴즈/피드백 컨텐츠 표시)
├── QuizInteraction.vue (퀴즈 상호작용)
├── ChatInteraction.vue (채팅 상호작용)
└── ComponentTest.vue (통합 테스트)

API Service Layer
└── learningService.js (통합 학습 API 서비스)

State Management (Pinia)
└── learningStore.js (전역 상태 관리)

Backend API Endpoints
├── POST /learning/session/start
├── POST /learning/session/message
├── POST /learning/quiz/submit
└── POST /learning/session/complete
```

### 데이터 흐름

```
1. 컴포넌트 마운트 → API 서비스 호출 → 백엔드 요청
2. 백엔드 응답 → API 서비스 처리 → Pinia 스토어 업데이트
3. 스토어 변경 → 컴포넌트 반응형 업데이트 → UI 갱신
4. 에러 발생 시 → 더미데이터 fallback → 사용자 경험 보장
```

## Components and Interfaces

### 1. MainContentArea.vue 연동

#### API 연동 포인트
- **컴포넌트 마운트 시**: learningService.startSession()으로 학습 세션 시작
- **에이전트 변경 시**: learningService.sendMessage()로 컨텐츠 요청

#### 백엔드 API 매핑
```javascript
// 기존 더미데이터 구조
const theoryContent = {
  description: "LLM은 대규모 언어 모델로...",
  keyPoints: ["대규모 데이터 학습", "언어 이해 및 생성"],
  examples: ["ChatGPT", "Claude", "Bard"]
}

// learningService 호출
const sessionData = {
  chapterId: 2,
  sessionType: 'theory'
}
const result = await learningService.startSession(sessionData)

// 백엔드 API 응답 구조
{
  "success": true,
  "data": {
    "workflow_response": {
      "current_agent": "theory_educator",
      "content": {
        "type": "theory",
        "title": "LLM(Large Language Model)이란?",
        "content": "LLM은 대규모 언어 모델로...",
        "key_points": ["대규모 데이터 학습", "언어 이해 및 생성"],
        "examples": ["ChatGPT", "Claude", "Bard"]
      }
    }
  }
}
```

#### 데이터 매핑 함수
```javascript
const mapTheoryContent = (apiResponse) => ({
  description: apiResponse.data.workflow_response.content.content,
  keyPoints: apiResponse.data.workflow_response.content.key_points || [],
  examples: apiResponse.data.workflow_response.content.examples || []
})
```

### 2. QuizInteraction.vue 연동

#### API 연동 포인트
- **퀴즈 모드 활성화**: learningService.sendMessage()로 퀴즈 요청
- **답안 제출**: learningService.submitQuizAnswer()로 답안 전송

#### 백엔드 API 매핑
```javascript
// 퀴즈 요청
const messageData = {
  message: "다음 단계로 넘어가주세요",
  messageType: "user"
}
const quizResult = await learningService.sendMessage(sessionId, messageData)

// 답안 제출
const answerData = {
  answer: "2",
  questionId: 1
}
const submitResult = await learningService.submitQuizAnswer(sessionId, answerData)
```

#### 데이터 매핑 함수
```javascript
const mapQuizData = (apiResponse) => ({
  question: apiResponse.data.workflow_response.content.question,
  type: apiResponse.data.workflow_response.content.quiz_type,
  options: apiResponse.data.workflow_response.content.options?.map((option, index) => ({
    value: (index + 1).toString(),
    text: option
  })) || [],
  hint: apiResponse.data.workflow_response.content.hint || ''
})
```

### 3. ChatInteraction.vue 연동

#### API 연동 포인트
- **메시지 전송**: learningService.sendMessage()로 사용자 메시지 전송
- **대화 기록 로드**: learningService.getSessionConversations()로 히스토리 조회

#### 백엔드 API 매핑
```javascript
// 메시지 전송
const messageData = {
  message: "AI와 머신러닝의 차이가 뭐예요?",
  messageType: "user"
}
const response = await learningService.sendMessage(sessionId, messageData)

// 대화 기록 조회
const conversations = await learningService.getSessionConversations(sessionId)
```

## Data Models

### learningService.js 확장

기존 learningService.js를 백엔드 API 문서에 맞게 확장:

```javascript
// learningService.js에 추가할 메서드들

/**
 * 학습 세션 시작 (v2.0 API)
 * @param {number} chapterNumber - 챕터 번호
 * @param {number} sectionNumber - 섹션 번호
 * @param {string} userMessage - 시작 메시지
 */
async startLearningSession(chapterNumber, sectionNumber, userMessage) {
  try {
    const response = await apiClient.post('/learning/session/start', {
      chapter_number: chapterNumber,
      section_number: sectionNumber,
      user_message: userMessage
    })
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
 * 세션 메시지 전송 (v2.0 API)
 * @param {string} userMessage - 사용자 메시지
 * @param {string} messageType - 메시지 타입
 */
async sendSessionMessage(userMessage, messageType = 'user') {
  try {
    const response = await apiClient.post('/learning/session/message', {
      user_message: userMessage,
      message_type: messageType
    })
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
 * 퀴즈 답안 제출 (v2.0 API)
 * @param {string} userAnswer - 사용자 답안
 */
async submitQuizAnswerV2(userAnswer) {
  try {
    const response = await apiClient.post('/learning/quiz/submit', {
      user_answer: userAnswer
    })
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
```

### 데이터 변환 유틸리티

#### dataMappers.js
```javascript
// API 응답을 컴포넌트 데이터로 변환
export const mapApiResponseToComponent = (apiResponse, componentType) => {
  const { workflow_response } = apiResponse.data
  
  switch (componentType) {
    case 'theory':
      return mapTheoryContent(workflow_response)
    case 'quiz':
      return mapQuizData(workflow_response)
    case 'chat':
      return mapChatMessage(workflow_response)
    default:
      return workflow_response.content
  }
}

// 에러 응답 처리
export const handleApiError = (error, fallbackData) => {
  console.error('API 요청 실패:', error)
  return fallbackData
}
```

## Error Handling

### 에러 처리 전략

1. **네트워크 에러**: 더미데이터로 fallback
2. **API 응답 에러**: 에러 메시지 표시 후 더미데이터 사용
3. **데이터 형식 에러**: 기본값으로 대체
4. **인증 에러**: 로그인 페이지로 리다이렉트

### 에러 처리 구현

```javascript
// API 호출 래퍼 함수
const safeApiCall = async (apiFunction, fallbackData) => {
  try {
    const result = await apiFunction()
    return { success: true, data: result }
  } catch (error) {
    console.error('API 호출 실패:', error)
    return { success: false, data: fallbackData, error }
  }
}

// 컴포넌트에서 사용
const loadContent = async () => {
  const { success, data, error } = await safeApiCall(
    () => startLearningSession(2, 1, "시작"),
    dummyTheoryContent
  )
  
  if (success) {
    // API 데이터 사용
    updateMainContent(mapApiResponseToComponent(data, 'theory'))
  } else {
    // 더미데이터 사용
    updateMainContent(data)
    // 선택적으로 에러 알림 표시
    showErrorNotification('네트워크 연결을 확인해주세요.')
  }
}
```

## Testing Strategy

### ComponentTest.vue 활용

#### 테스트 시나리오
1. **MainContentArea 테스트**
   - API 연동 성공 시 실제 데이터 표시 확인
   - API 실패 시 더미데이터 fallback 확인
   - 에이전트 변경 시 컨텐츠 동적 로드 확인

2. **QuizInteraction 테스트**
   - 퀴즈 데이터 로드 확인
   - 답안 제출 및 평가 결과 수신 확인
   - 힌트 요청 기능 확인

3. **ChatInteraction 테스트**
   - 메시지 전송 및 AI 응답 수신 확인
   - 채팅 히스토리 업데이트 확인
   - 로딩 상태 표시 확인

#### 테스트 구현 방법
```javascript
// ComponentTest.vue에 API 테스트 버튼 추가
const testApiIntegration = async (componentType) => {
  console.log(`${componentType} API 연동 테스트 시작`)
  
  switch (componentType) {
    case 'MainContentArea':
      await testMainContentAreaApi()
      break
    case 'QuizInteraction':
      await testQuizInteractionApi()
      break
    case 'ChatInteraction':
      await testChatInteractionApi()
      break
  }
}
```

### 단위 테스트

#### API 서비스 테스트
```javascript
// learningApi.test.js
describe('Learning API', () => {
  test('세션 시작 API 호출', async () => {
    const result = await startLearningSession(2, 1, "시작")
    expect(result.success).toBe(true)
    expect(result.data.workflow_response).toBeDefined()
  })
  
  test('메시지 전송 API 호출', async () => {
    const result = await sendMessage("다음으로 넘어가주세요")
    expect(result.success).toBe(true)
  })
})
```

## Implementation Plan

### 단계별 구현 순서

#### 1단계: MainContentArea.vue 연동
- learningService.js에 v2.0 API 메서드 추가
- 데이터 매핑 함수 구현 (dataMappers.js)
- MainContentArea 컴포넌트 API 연동
- ComponentTest.vue에서 검증

#### 2단계: QuizInteraction.vue 연동
- learningService.js에 퀴즈 관련 메서드 확장
- 퀴즈 데이터 매핑 함수 구현
- QuizInteraction 컴포넌트 API 연동
- ComponentTest.vue에서 검증

#### 3단계: ChatInteraction.vue 연동
- learningService.js에 채팅 관련 메서드 확장
- 채팅 메시지 매핑 함수 구현
- ChatInteraction 컴포넌트 API 연동
- ComponentTest.vue에서 검증

### 기술적 고려사항

#### API 클라이언트 설정
```javascript
// api/client.js
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 요청 인터셉터 (JWT 토큰 추가)
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 응답 인터셉터 (에러 처리)
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 로그인 페이지로 리다이렉트
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

#### 환경 변수 설정
```javascript
// .env
VITE_API_BASE_URL=http://localhost:5000/api/v1
VITE_API_TIMEOUT=10000
VITE_ENABLE_API_MOCK=false
```

#### 개발/프로덕션 모드 분기
```javascript
// config/api.js
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1',
  timeout: import.meta.env.VITE_API_TIMEOUT || 10000,
  enableMock: import.meta.env.VITE_ENABLE_API_MOCK === 'true'
}
```

## Performance Considerations

### 최적화 전략 (MVP에서는 제외)

- API 응답 캐싱
- 요청 중복 방지 (debouncing)
- 페이지네이션
- 무한 스크롤

### 현재 구현에서는 기본 기능만 구현

- 단순한 API 호출
- 기본적인 에러 처리
- 더미데이터 fallback
- 로딩 상태 표시