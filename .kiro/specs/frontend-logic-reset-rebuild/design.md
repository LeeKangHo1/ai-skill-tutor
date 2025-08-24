# 설계 문서

## 개요

프론트엔드 Vue 컴포넌트들의 디자인과 UI 구조는 완전히 보존하면서, learningService.js와 learningStore.js의 로직을 체계적으로 초기화하고 단계별로 재구현하는 시스템을 설계합니다. 기존 implementation_log_front.md에 기록된 모든 Vue 컴포넌트의 디자인, 스타일, 컴포넌트 구조는 그대로 유지하되, 백엔드 API와의 연동 로직만 새롭게 구축합니다.

## 아키텍처

### 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    프론트엔드 아키텍처                        │
├─────────────────────────────────────────────────────────────┤
│  Vue 컴포넌트 레이어 (디자인 보존)                           │
│  ├── LearningPage.vue (메인 컨테이너)                       │
│  ├── MainContentArea.vue (컨텐츠 표시)                      │
│  ├── TheoryContent.vue (이론 컨텐츠)                        │
│  ├── QuizContent.vue (퀴즈 컨텐츠)                          │
│  ├── FeedbackContent.vue (피드백 컨텐츠)                    │
│  ├── ChatInteraction.vue (채팅 인터랙션)                    │
│  └── QuizInteraction.vue (퀴즈 인터랙션)                    │
├─────────────────────────────────────────────────────────────┤
│  상태 관리 레이어 (로직 재구현)                              │
│  └── learningStore.js (Pinia Store - 완전 재구현)          │
├─────────────────────────────────────────────────────────────┤
│  서비스 레이어 (로직 재구현)                                 │
│  └── learningService.js (API 연동 - 완전 재구현)           │
├─────────────────────────────────────────────────────────────┤
│  백엔드 API 레이어                                          │
│  ├── POST /api/v1/learning/session/start                   │
│  ├── POST /api/v1/learning/session/message                 │
│  ├── POST /api/v1/learning/quiz/submit                     │
│  └── POST /api/v1/learning/session/complete                │
└─────────────────────────────────────────────────────────────┘
```

### 컴포넌트 간 데이터 흐름

```
LearningPage (컨테이너)
├── MainContentArea (컨텐츠 표시)
│   ├── TheoryContent (이론 표시)
│   ├── QuizContent (퀴즈 표시)
│   └── FeedbackContent (피드백 표시)
└── InteractionArea (사용자 인터랙션)
    ├── ChatInteraction (채팅 모드)
    └── QuizInteraction (퀴즈 모드)

데이터 흐름:
Props Down: 부모 → 자식 (컨텐츠 데이터 전달)
Events Up: 자식 → 부모 (사용자 액션 전달)
Store: 전역 상태 관리 (Pinia)
```

## 컴포넌트 및 인터페이스

### 1. Vue 컴포넌트 구조 (디자인 보존)

#### 1.1 LearningPage.vue (메인 컨테이너)
**보존할 요소:**
- 전체 레이아웃 구조 (헤더 + 메인 컨텐츠)
- 6:4 비율의 좌우 분할 레이아웃
- 헤더의 챕터/섹션 정보 표시
- 로딩 오버레이 모달

**수정할 요소:**
- script 섹션의 로직 (store 연동, API 호출)
- 이벤트 핸들러 메서드들

#### 1.2 MainContentArea.vue (컨텐츠 표시)
**보존할 요소:**
- 컨텐츠 헤더와 바디 구조
- 조건부 렌더링 구조 (v-if, v-else-if)
- 하위 컴포넌트들의 props 전달 구조

**수정할 요소:**
- 컨텐츠 데이터 처리 로직
- API 연동 부분

#### 1.3 TheoryContent.vue, QuizContent.vue, FeedbackContent.vue
**보존할 요소:**
- 전체 template 구조
- 모든 style 섹션
- props 정의 (필요시 확장만)

**수정할 요소:**
- 없음 (순수 표시 컴포넌트로 유지)

#### 1.4 ChatInteraction.vue, QuizInteraction.vue
**보존할 요소:**
- UI 레이아웃과 스타일
- 입력 폼 구조
- 메시지 표시 구조

**수정할 요소:**
- 이벤트 처리 로직
- 데이터 바인딩 부분

### 2. 상태 관리 구조 (완전 재구현)

#### 2.1 learningStore.js 새로운 구조

```javascript
// 기본 상태 변수들
const state = {
  // 세션 정보
  sessionInfo: {
    sessionId: null,
    chapterNumber: null,
    sectionNumber: null,
    chapterTitle: '',
    sectionTitle: ''
  },
  
  // 현재 상태
  currentAgent: 'theory_educator',
  uiMode: 'chat', // 'chat' | 'quiz'
  sessionProgressStage: 'session_start',
  
  // 컨텐츠 데이터
  contentData: {
    theory: null,
    quiz: null,
    feedback: null,
    qna: null
  },
  
  // 인터랙션 데이터
  chatHistory: [],
  quizData: null,
  
  // UI 상태
  isLoading: false,
  loadingMessage: '',
  errorMessage: ''
}

// 액션 메서드들 (단계별 구현)
const actions = {
  // 1단계: 기본 상태 관리
  updateSessionInfo(),
  updateCurrentAgent(),
  updateUIMode(),
  
  // 2단계: 컨텐츠 관리
  updateContentData(),
  clearContentData(),
  
  // 3단계: 인터랙션 관리
  addChatMessage(),
  updateQuizData(),
  
  // 4단계: API 연동
  startLearningSession(),
  sendMessage(),
  submitQuizAnswer(),
  
  // 5단계: 고급 기능
  handleWorkflowResponse(),
  syncWithBackend()
}
```

#### 2.2 상태 동기화 시스템

```javascript
// 백엔드 응답과 프론트엔드 상태 동기화
const syncWorkflowResponse = (workflowResponse) => {
  // 에이전트 상태 동기화
  if (workflowResponse.current_agent) {
    updateCurrentAgent(workflowResponse.current_agent)
  }
  
  // UI 모드 동기화
  if (workflowResponse.ui_mode) {
    updateUIMode(workflowResponse.ui_mode)
  }
  
  // 세션 진행 단계 동기화
  if (workflowResponse.session_progress_stage) {
    updateSessionProgressStage(workflowResponse.session_progress_stage)
  }
  
  // 컨텐츠 데이터 동기화
  if (workflowResponse.content) {
    updateContentData(workflowResponse.content)
  }
}
```

### 3. API 서비스 구조 (완전 재구현)

#### 3.1 learningService.js 새로운 구조

```javascript
// 기본 API 클라이언트 설정
const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// API 메서드들 (단계별 구현)
const learningService = {
  // 1단계: 기본 API 호출
  async startSession(chapterNumber, sectionNumber, userMessage),
  async sendMessage(userMessage, messageType),
  async submitQuizAnswer(userAnswer),
  async completeSession(proceedDecision),
  
  // 2단계: 응답 처리
  async handleApiResponse(response),
  async handleApiError(error),
  
  // 3단계: 상태 동기화
  async syncWithStore(response),
  
  // 4단계: 고급 기능
  async retryFailedRequest(requestConfig),
  async validateResponse(response)
}
```

#### 3.2 API 응답 처리 시스템

```javascript
// 통일된 API 응답 처리
const handleApiResponse = async (response) => {
  if (response.data.success) {
    // 성공 응답 처리
    const workflowResponse = response.data.data.workflow_response
    await syncWorkflowResponse(workflowResponse)
    return { success: true, data: response.data.data }
  } else {
    // 실패 응답 처리
    throw new Error(response.data.error.message)
  }
}

// 에러 처리 시스템
const handleApiError = (error) => {
  const errorMessage = error.response?.data?.error?.message || error.message
  store.setErrorMessage(errorMessage)
  return { success: false, error: errorMessage }
}
```

## 데이터 모델

### 1. 세션 정보 모델

```typescript
interface SessionInfo {
  sessionId: number | null
  chapterNumber: number
  sectionNumber: number
  chapterTitle: string
  sectionTitle: string
  userType: string
}
```

### 2. 컨텐츠 데이터 모델

```typescript
interface ContentData {
  theory: TheoryContent | null
  quiz: QuizContent | null
  feedback: FeedbackContent | null
  qna: QnAContent | null
}

interface TheoryContent {
  type: 'theory'
  title: string
  content: string
  keyPoints: string[]
  examples: string[]
}

interface QuizContent {
  type: 'quiz'
  quizType: 'multiple_choice' | 'subjective'
  question: string
  options: string[]
  hint: string
  correctAnswer?: string | number
}

interface FeedbackContent {
  type: 'feedback'
  title: string
  content: string
  explanation: string
  nextStep: string
  score?: number
}

interface QnAContent {
  type: 'qna'
  question: string
  answer: string
}
```

### 3. 워크플로우 응답 모델

```typescript
interface WorkflowResponse {
  current_agent: string
  session_progress_stage: string
  ui_mode: 'chat' | 'quiz'
  content: TheoryContent | QuizContent | FeedbackContent | QnAContent
  metadata?: {
    [key: string]: any
  }
}
```

## 오류 처리

### 1. API 오류 처리 시스템

```javascript
// 오류 타입별 처리
const errorHandlers = {
  // 네트워크 오류
  NETWORK_ERROR: (error) => {
    store.setErrorMessage('네트워크 연결을 확인해주세요.')
    return { retry: true, delay: 3000 }
  },
  
  // 인증 오류
  AUTH_ERROR: (error) => {
    store.setErrorMessage('로그인이 필요합니다.')
    router.push('/auth/login')
    return { retry: false }
  },
  
  // 서버 오류
  SERVER_ERROR: (error) => {
    store.setErrorMessage('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
    return { retry: true, delay: 5000 }
  },
  
  // 워크플로우 오류
  WORKFLOW_ERROR: (error) => {
    store.setErrorMessage('AI 처리 중 오류가 발생했습니다.')
    return { retry: true, delay: 2000 }
  }
}
```

### 2. 사용자 피드백 시스템

```javascript
// 로딩 상태 관리
const loadingStates = {
  'session_start': '학습 세션을 시작하는 중...',
  'sending_message': '메시지를 전송하는 중...',
  'generating_quiz': '퀴즈를 생성하는 중...',
  'evaluating_answer': '답안을 평가하는 중...',
  'completing_session': '세션을 완료하는 중...'
}

// 에러 메시지 표시
const showErrorMessage = (message, duration = 5000) => {
  store.setErrorMessage(message)
  setTimeout(() => {
    store.clearErrorMessage()
  }, duration)
}
```

## 테스트 전략

### 1. 단위 테스트

```javascript
// learningStore.js 테스트
describe('learningStore', () => {
  test('세션 정보 업데이트', () => {
    const store = useLearningStore()
    store.updateSessionInfo({ chapterNumber: 2, sectionNumber: 1 })
    expect(store.sessionInfo.chapterNumber).toBe(2)
  })
  
  test('컨텐츠 데이터 업데이트', () => {
    const store = useLearningStore()
    const theoryData = { type: 'theory', title: 'Test', content: 'Test content' }
    store.updateContentData('theory', theoryData)
    expect(store.contentData.theory).toEqual(theoryData)
  })
})

// learningService.js 테스트
describe('learningService', () => {
  test('세션 시작 API 호출', async () => {
    const mockResponse = { data: { success: true, data: {} } }
    axios.post.mockResolvedValue(mockResponse)
    
    const result = await learningService.startSession(2, 1, 'test message')
    expect(result.success).toBe(true)
  })
})
```

### 2. 통합 테스트

```javascript
// 컴포넌트 통합 테스트
describe('LearningPage Integration', () => {
  test('세션 시작부터 완료까지 전체 플로우', async () => {
    const wrapper = mount(LearningPage)
    
    // 1. 세션 시작
    await wrapper.vm.startSession(2, 1)
    expect(wrapper.vm.currentAgent).toBe('theory_educator')
    
    // 2. 다음 단계 진행
    await wrapper.vm.handleSendMessage('다음 단계로 넘어가주세요')
    expect(wrapper.vm.currentAgent).toBe('quiz_generator')
    expect(wrapper.vm.uiMode).toBe('quiz')
    
    // 3. 퀴즈 답안 제출
    await wrapper.vm.handleSubmitAnswer('2')
    expect(wrapper.vm.currentAgent).toBe('evaluation_feedback_agent')
    expect(wrapper.vm.uiMode).toBe('chat')
  })
})
```

### 3. E2E 테스트

```javascript
// Cypress E2E 테스트
describe('Learning Flow E2E', () => {
  it('전체 학습 세션 완료', () => {
    cy.visit('/learning')
    
    // 세션 시작 확인
    cy.contains('2챕터 1섹션').should('be.visible')
    
    // 이론 컨텐츠 확인
    cy.get('.theory-content').should('be.visible')
    
    // 다음 단계 진행
    cy.get('.chat-input').type('다음 단계로 넘어가주세요')
    cy.get('.send-button').click()
    
    // 퀴즈 모드 전환 확인
    cy.get('.quiz-content').should('be.visible')
    cy.get('.quiz-options').should('be.visible')
    
    // 퀴즈 답안 선택 및 제출
    cy.get('.quiz-option[data-option="2"]').click()
    cy.get('.submit-answer-button').click()
    
    // 피드백 확인
    cy.get('.feedback-content').should('be.visible')
    cy.contains('정답입니다').should('be.visible')
  })
})
```

## 성능 최적화

### 1. 컴포넌트 최적화

```javascript
// 메모이제이션 활용
const TheoryContent = defineComponent({
  props: ['theoryData', 'isVisible'],
  setup(props) {
    // 컨텐츠 데이터 메모이제이션
    const processedContent = computed(() => {
      if (!props.theoryData) return null
      return processContentData(props.theoryData)
    })
    
    return { processedContent }
  }
})

// 지연 로딩
const QuizInteraction = defineAsyncComponent(() => 
  import('./QuizInteraction.vue')
)
```

### 2. API 최적화

```javascript
// 요청 중복 방지
const requestCache = new Map()

const cachedApiCall = async (key, apiCall) => {
  if (requestCache.has(key)) {
    return requestCache.get(key)
  }
  
  const promise = apiCall()
  requestCache.set(key, promise)
  
  try {
    const result = await promise
    return result
  } finally {
    requestCache.delete(key)
  }
}

// 요청 취소
const abortController = new AbortController()

const cancelableApiCall = async (url, data) => {
  return axios.post(url, data, {
    signal: abortController.signal
  })
}
```

### 3. 상태 관리 최적화

```javascript
// 불필요한 리렌더링 방지
const learningStore = defineStore('learning', () => {
  const state = reactive({
    sessionInfo: {},
    contentData: {},
    // ...
  })
  
  // 깊은 비교를 통한 업데이트 최적화
  const updateContentData = (type, data) => {
    if (!isEqual(state.contentData[type], data)) {
      state.contentData[type] = data
    }
  }
  
  return { state, updateContentData }
})
```

## 보안 고려사항

### 1. API 보안

```javascript
// JWT 토큰 자동 첨부
apiClient.interceptors.request.use((config) => {
  const token = tokenManager.getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 토큰 만료 처리
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await tokenManager.refreshToken()
      return apiClient.request(error.config)
    }
    return Promise.reject(error)
  }
)
```

### 2. 입력 검증

```javascript
// 사용자 입력 검증
const validateUserMessage = (message) => {
  if (!message || typeof message !== 'string') {
    throw new Error('메시지는 문자열이어야 합니다.')
  }
  
  if (message.length > 1000) {
    throw new Error('메시지는 1000자를 초과할 수 없습니다.')
  }
  
  // XSS 방지
  return DOMPurify.sanitize(message)
}
```

### 3. 데이터 보호

```javascript
// 민감한 데이터 마스킹
const maskSensitiveData = (data) => {
  const masked = { ...data }
  if (masked.sessionId) {
    masked.sessionId = '***'
  }
  return masked
}

// 로그에서 민감한 정보 제거
const safeLog = (message, data) => {
  console.log(message, maskSensitiveData(data))
}
```