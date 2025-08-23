# Design Document

## Overview

프론트엔드 학습 시스템의 실제 백엔드 API 연동을 위한 설계 문서입니다. 현재 더미 데이터 기반으로 구현된 시스템을 API 문서 v2.0에 정의된 4가지 핵심 학습 세션 API와 완전히 통합합니다. 새로운 learningStore.js 생성과 기존 learningService.js 개편을 통해 견고하고 확장 가능한 구조를 구축합니다.

## Architecture

### 전체 아키텍처 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    Vue 3 Frontend                           │
├─────────────────────────────────────────────────────────────┤
│  Components Layer                                           │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  LearningPage   │  │ MainContentArea │                  │
│  │                 │  │                 │                  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │                  │
│  │ │ChatInteract │ │  │ │QuizInteract │ │                  │
│  │ └─────────────┘ │  │ └─────────────┘ │                  │
│  └─────────────────┘  └─────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│  State Management Layer (Pinia)                            │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  tutorStore.js  │  │learningStore.js │                  │
│  │  (UI 상태 관리)   │  │ (API 상태 관리) │                  │
│  └─────────────────┘  └─────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│  Service Layer                                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │learningService  │  │    api.js       │                  │
│  │ (HTTP API 호출) │  │ (Axios 설정)    │                  │
│  └─────────────────┘  └─────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│                    HTTP Layer                               │
│              POST /learning/session/*                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend API (Flask)                         │
│           LangGraph Workflow System                         │
└─────────────────────────────────────────────────────────────┘
```

### 데이터 흐름 설계

```
사용자 액션 → Component → learningStore → learningService → Backend API
                ↓              ↓              ↓              ↓
            UI 업데이트 ← tutorStore ← API 응답 처리 ← HTTP 응답
```

## Components and Interfaces

### 1. learningStore.js (새로 생성)

학습 세션 전용 Pinia store로 API 호출과 관련된 모든 상태를 관리합니다.

#### State 구조

```javascript
// 세션 관리 상태
const sessionState = ref({
  session_id: null,
  is_active: false,
  start_time: null,
  chapter_number: null,
  section_number: null
})

// API 호출 상태
const apiState = ref({
  loading: false,
  error: null,
  last_request: null,
  retry_count: 0
})

// 워크플로우 응답 상태
const workflowState = ref({
  current_agent: null,
  session_progress_stage: null,
  ui_mode: null,
  content: null,
  evaluation_result: null
})

// 에러 처리 상태
const errorState = ref({
  network_error: false,
  auth_error: false,
  server_error: false,
  error_message: ''
})
```

#### 핵심 Actions

```javascript
// 세션 시작
async startSession(chapterNumber, sectionNumber, userMessage)

// 메시지 전송
async sendMessage(userMessage, messageType = 'user')

// 퀴즈 답안 제출
async submitQuiz(userAnswer)

// 세션 완료
async completeSession(proceedDecision = 'proceed')

// 에러 처리
handleApiError(error)

// 상태 초기화
resetSessionState()
```

### 2. learningService.js (완전 개편)

기존 더미 데이터 기반 구조를 실제 HTTP API 호출 구조로 완전히 교체합니다.

#### 기존 구조 vs 새로운 구조

**기존 (제거할 메서드들):**
- `startSession()` - 더미 데이터 반환
- `sendMessage()` - 시뮬레이션 기반
- `submitQuizAnswer()` - 가짜 채점
- `completeSession()` - 로컬 상태만 변경

**새로운 구조:**

```javascript
class LearningService {
  constructor() {
    this.baseURL = '/api/v1/learning'
    this.defaultTimeout = 10000
  }

  // POST /learning/session/start
  async startLearningSession(chapterNumber, sectionNumber, userMessage) {
    const payload = {
      chapter_number: chapterNumber,
      section_number: sectionNumber,
      user_message: userMessage
    }
    return await this.makeRequest('POST', '/session/start', payload)
  }

  // POST /learning/session/message
  async sendSessionMessage(userMessage, messageType = 'user') {
    const payload = {
      user_message: userMessage,
      message_type: messageType
    }
    return await this.makeRequest('POST', '/session/message', payload)
  }

  // POST /learning/quiz/submit
  async submitQuizAnswer(userAnswer) {
    const payload = {
      user_answer: userAnswer
    }
    return await this.makeRequest('POST', '/quiz/submit', payload)
  }

  // POST /learning/session/complete
  async completeSession(proceedDecision = 'proceed') {
    const payload = {
      proceed_decision: proceedDecision
    }
    return await this.makeRequest('POST', '/session/complete', payload)
  }

  // 공통 HTTP 요청 처리
  async makeRequest(method, endpoint, data = null) {
    // JWT 토큰 인증, 에러 처리, 응답 파싱 로직
  }
}
```

### 3. tutorStore.js (기존 수정)

UI 상태 관리에 집중하고 API 관련 상태는 learningStore로 이관합니다.

#### 역할 분담

**tutorStore (유지할 상태):**
- `currentAgent`, `currentUIMode`, `currentContentMode`
- `chatHistory`, `quizData`, `completedSteps`
- UI 관련 computed 속성들
- UI 업데이트 액션들

**learningStore로 이관할 상태:**
- 세션 관리 관련 상태
- API 호출 상태
- 에러 처리 상태

### 4. Component 연동 구조

#### LearningPage.vue
```javascript
// learningStore와 tutorStore 모두 사용
const learningStore = useLearningStore()
const tutorStore = useTutorStore()

// 세션 시작 시
const startLearning = async (chapter, section) => {
  const result = await learningStore.startSession(chapter, section, '학습을 시작합니다')
  if (result.success) {
    tutorStore.updateWorkflowResponse(result.data.workflow_response)
  }
}
```

#### MainContentArea.vue
```javascript
// tutorStore의 UI 상태를 기반으로 컴포넌트 전환
const currentComponent = computed(() => {
  return tutorStore.isQuizMode ? 'QuizInteraction' : 'ChatInteraction'
})
```

#### ChatInteraction.vue
```javascript
// 메시지 전송 시 learningStore 사용
const sendMessage = async (message) => {
  const result = await learningStore.sendMessage(message)
  if (result.success) {
    tutorStore.updateWorkflowResponse(result.data.workflow_response)
  }
}
```

#### QuizInteraction.vue
```javascript
// 퀴즈 제출 시 learningStore 사용
const submitAnswer = async (answer) => {
  const result = await learningStore.submitQuiz(answer)
  if (result.success) {
    tutorStore.updateWorkflowResponse(result.data.workflow_response)
  }
}
```

## Data Models

### API 요청/응답 모델

#### 1. 세션 시작 요청/응답
```typescript
// 요청
interface SessionStartRequest {
  chapter_number: number
  section_number: number
  user_message: string
}

// 응답
interface SessionStartResponse {
  success: boolean
  data: {
    session_info: {
      chapter_number: number
      section_number: number
      chapter_title: string
      estimated_duration: string
    }
    workflow_response: WorkflowResponse
  }
  message: string
}
```

#### 2. 워크플로우 응답 모델
```typescript
interface WorkflowResponse {
  current_agent: 'theory_educator' | 'quiz_generator' | 'evaluation_feedback_agent' | 'qna_resolver'
  session_progress_stage: 'session_start' | 'theory_completed' | 'quiz_and_feedback_completed'
  ui_mode: 'chat' | 'quiz'
  content: TheoryContent | QuizContent | FeedbackContent | QnAContent
}

interface TheoryContent {
  type: 'theory'
  title: string
  content: string
  key_points: string[]
  examples: string[]
}

interface QuizContent {
  type: 'quiz'
  quiz_type: 'multiple_choice' | 'subjective'
  question: string
  options?: string[]
  hint: string
}

interface FeedbackContent {
  type: 'feedback'
  title: string
  content: string
  explanation: string
  next_step_decision: 'proceed' | 'retry'
}
```

### Store 상태 모델

#### learningStore 상태
```typescript
interface LearningStoreState {
  sessionState: {
    session_id: string | null
    is_active: boolean
    start_time: Date | null
    chapter_number: number | null
    section_number: number | null
  }
  apiState: {
    loading: boolean
    error: string | null
    last_request: string | null
    retry_count: number
  }
  workflowState: {
    current_agent: string | null
    session_progress_stage: string | null
    ui_mode: string | null
    content: any | null
    evaluation_result: any | null
  }
  errorState: {
    network_error: boolean
    auth_error: boolean
    server_error: boolean
    error_message: string
  }
}
```

## Error Handling

### 에러 분류 및 처리 전략

#### 1. 네트워크 에러
```javascript
// 연결 실패, 타임아웃 등
if (error.code === 'NETWORK_ERROR') {
  return {
    success: false,
    error: '네트워크 연결을 확인해주세요.',
    type: 'network',
    retry: true
  }
}
```

#### 2. 인증 에러
```javascript
// 토큰 만료, 인증 실패
if (error.status === 401) {
  // 자동 토큰 갱신 시도
  const refreshResult = await authService.refreshToken()
  if (refreshResult.success) {
    // 원래 요청 재시도
    return await this.retryRequest(originalRequest)
  }
}
```

#### 3. 서버 에러
```javascript
// 500, 503 등 서버 오류
if (error.status >= 500) {
  return {
    success: false,
    error: '서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.',
    type: 'server',
    retry: true
  }
}
```

#### 4. 데이터 검증 에러
```javascript
// API 응답 구조 검증
const validateWorkflowResponse = (response) => {
  const required = ['current_agent', 'session_progress_stage', 'ui_mode', 'content']
  for (const field of required) {
    if (!response[field]) {
      console.warn(`Missing required field: ${field}`)
      return false
    }
  }
  return true
}
```

## Testing Strategy

### 1. 단위 테스트

#### learningService 테스트
```javascript
// HTTP 요청 모킹
describe('LearningService', () => {
  test('startLearningSession should call correct API endpoint', async () => {
    const mockResponse = { success: true, data: { session_info: {} } }
    axios.post.mockResolvedValue({ data: mockResponse })
    
    const result = await learningService.startLearningSession(2, 1, 'test message')
    
    expect(axios.post).toHaveBeenCalledWith('/api/v1/learning/session/start', {
      chapter_number: 2,
      section_number: 1,
      user_message: 'test message'
    })
    expect(result.success).toBe(true)
  })
})
```

#### learningStore 테스트
```javascript
describe('LearningStore', () => {
  test('startSession should update session state', async () => {
    const store = useLearningStore()
    
    await store.startSession(2, 1, 'test')
    
    expect(store.sessionState.chapter_number).toBe(2)
    expect(store.sessionState.section_number).toBe(1)
    expect(store.sessionState.is_active).toBe(true)
  })
})
```

### 2. 통합 테스트

#### Component-Store 연동 테스트
```javascript
describe('LearningPage Integration', () => {
  test('should handle complete learning workflow', async () => {
    const wrapper = mount(LearningPage)
    
    // 세션 시작
    await wrapper.vm.startLearning(2, 1)
    expect(wrapper.vm.tutorStore.currentAgent).toBe('theory_educator')
    
    // 메시지 전송
    await wrapper.vm.sendMessage('다음 단계로 넘어가주세요')
    expect(wrapper.vm.tutorStore.currentUIMode).toBe('quiz')
    
    // 퀴즈 제출
    await wrapper.vm.submitQuiz('2')
    expect(wrapper.vm.tutorStore.currentAgent).toBe('evaluation_feedback_agent')
  })
})
```

### 3. API 모킹 전략

#### MSW (Mock Service Worker) 사용
```javascript
// API 응답 모킹
const handlers = [
  rest.post('/api/v1/learning/session/start', (req, res, ctx) => {
    return res(
      ctx.json({
        success: true,
        data: {
          session_info: { chapter_number: 2, section_number: 1 },
          workflow_response: {
            current_agent: 'theory_educator',
            ui_mode: 'chat',
            content: { type: 'theory', title: 'Test Theory' }
          }
        }
      })
    )
  })
]
```

## Implementation Phases

### Phase 1: learningStore.js 생성
1. 기본 상태 구조 정의
2. 핵심 액션 메서드 구현
3. 에러 처리 로직 구현
4. 단위 테스트 작성

### Phase 2: learningService.js 개편
1. 기존 더미 데이터 메서드 제거
2. HTTP API 호출 메서드 구현
3. 공통 요청 처리 로직 구현
4. 에러 처리 및 재시도 로직 구현

### Phase 3: tutorStore.js 리팩토링
1. API 관련 상태를 learningStore로 이관
2. UI 상태 관리에 집중하도록 정리
3. learningStore와의 연동 로직 구현

### Phase 4: Component 연동
1. LearningPage에서 두 store 연동
2. ChatInteraction과 QuizInteraction에서 API 호출 연동
3. MainContentArea에서 UI 상태 반영 로직 구현

### Phase 5: 통합 테스트 및 최적화
1. 전체 워크플로우 통합 테스트
2. 에러 시나리오 테스트
3. 성능 최적화 및 코드 정리