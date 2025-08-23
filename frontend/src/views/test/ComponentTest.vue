<!-- frontend/src/views/test/ComponentTest.vue -->
<template>
  <div class="component-test-page">
    <div class="test-header">
      <h1>🧪 실제 API 연동 테스트</h1>
      <div class="test-controls">
        <select v-model="currentTestComponent" class="test-selector">
          <option value="all">전체 통합 테스트</option>
          <option value="api-test">API 연동 테스트</option>
          <option value="main-content">MainContentArea 테스트</option>
          <option value="chat">ChatInteraction 테스트</option>
          <option value="quiz">QuizInteraction 테스트</option>
          <option value="debug">디버깅 도구</option>
        </select>
        <button @click="resetTest" class="reset-btn">🔄 리셋</button>
        <button @click="toggleApiMode" :class="{ active: useRealApi }" class="api-mode-btn">
          {{ useRealApi ? '🌐 실제 API' : '🔧 시뮬레이션' }}
        </button>
      </div>
    </div>

    <!-- 전체 통합 테스트 -->
    <div v-if="currentTestComponent === 'all'" class="test-container full-test">
      <div class="test-wrapper">
        <LearningPage />
      </div>
    </div>

    <!-- API 연동 테스트 -->
    <div v-else-if="currentTestComponent === 'api-test'" class="test-container">
      <div class="test-section">
        <h2>🌐 실제 API 연동 테스트</h2>
        
        <!-- API 상태 모니터링 -->
        <div class="api-status-monitor">
          <div class="api-status-header">
            <h4>📊 API 상태 모니터링</h4>
            <div class="status-indicators">
              <span :class="['status-indicator', apiConnectionStatus]">
                {{ apiConnectionStatus === 'connected' ? '🟢 연결됨' : 
                   apiConnectionStatus === 'loading' ? '🟡 요청중' : '🔴 연결안됨' }}
              </span>
              <span class="last-update">마지막 업데이트: {{ lastApiUpdate }}</span>
            </div>
          </div>
          
          <div class="api-status-grid">
            <div class="status-card">
              <h5>learningStore 상태</h5>
              <div class="status-details">
                <div>세션 ID: {{ learningStore.sessionState.session_id || '없음' }}</div>
                <div>활성 상태: {{ learningStore.isSessionActive ? '✅' : '❌' }}</div>
                <div>로딩 중: {{ learningStore.isLoading ? '⏳' : '✅' }}</div>
                <div>에러: {{ learningStore.hasError ? '❌' : '✅' }}</div>
                <div>재시도 가능: {{ learningStore.canRetry ? '✅' : '❌' }}</div>
                <div>현재 에이전트: {{ learningStore.workflowState.current_agent || '없음' }}</div>
                <div>UI 모드: {{ learningStore.workflowState.ui_mode || '없음' }}</div>
                <div>진행 단계: {{ learningStore.workflowState.session_progress_stage || '없음' }}</div>
              </div>
            </div>
            
            <div class="status-card">
              <h5>tutorStore 상태</h5>
              <div class="status-details">
                <div>현재 에이전트: {{ tutorStore.currentAgent }}</div>
                <div>UI 모드: {{ tutorStore.currentUIMode }}</div>
                <div>컨텐츠 모드: {{ tutorStore.currentContentMode }}</div>
                <div>진행 단계: {{ tutorStore.sessionProgressStage }}</div>
                <div>완료 준비: {{ tutorStore.isSessionReadyToComplete ? '✅' : '❌' }}</div>
                <div>연동 상태: {{ tutorStore.isConnectedToLearningStore ? '✅' : '❌' }}</div>
                <div>채팅 메시지 수: {{ tutorStore.chatHistory.length }}</div>
                <div>퀴즈 활성: {{ tutorStore.currentQuizInfo.is_quiz_active ? '✅' : '❌' }}</div>
              </div>
            </div>
            
            <div class="status-card">
              <h5>API 요청 통계</h5>
              <div class="status-details">
                <div>총 요청 수: {{ apiStats.totalRequests }}</div>
                <div>성공 요청: {{ apiStats.successRequests }}</div>
                <div>실패 요청: {{ apiStats.failedRequests }}</div>
                <div>평균 응답시간: {{ apiStats.averageResponseTime }}ms</div>
                <div>마지막 요청: {{ apiStats.lastRequestType || '없음' }}</div>
                <div>마지막 에러: {{ apiStats.lastError || '없음' }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- API 테스트 시나리오 -->
        <div class="api-test-scenarios">
          <h4>🧪 API 테스트 시나리오</h4>
          
          <div class="scenario-group">
            <h5>1. 세션 시작 테스트</h5>
            <div class="test-controls-inline">
              <input v-model="testChapter" type="number" placeholder="챕터" min="1" max="10" class="test-input">
              <input v-model="testSection" type="number" placeholder="섹션" min="1" max="5" class="test-input">
              <input v-model="testMessage" type="text" placeholder="시작 메시지" class="test-input">
              <button @click="testStartSession" :disabled="learningStore.isLoading" class="test-btn">
                {{ learningStore.isLoading ? '⏳ 요청중...' : '🚀 세션 시작' }}
              </button>
            </div>
          </div>
          
          <div class="scenario-group">
            <h5>2. 메시지 전송 테스트</h5>
            <div class="test-controls-inline">
              <input v-model="testUserMessage" type="text" placeholder="사용자 메시지" class="test-input">
              <select v-model="testMessageType" class="test-select">
                <option value="user">사용자</option>
                <option value="system">시스템</option>
                <option value="question">질문</option>
              </select>
              <button @click="testSendMessage" :disabled="!learningStore.isSessionActive || learningStore.isLoading" class="test-btn">
                {{ learningStore.isLoading ? '⏳ 전송중...' : '💬 메시지 전송' }}
              </button>
            </div>
          </div>
          
          <div class="scenario-group">
            <h5>3. 퀴즈 제출 테스트</h5>
            <div class="test-controls-inline">
              <input v-model="testQuizAnswer" type="text" placeholder="퀴즈 답안" class="test-input">
              <button @click="testSubmitQuiz" :disabled="!learningStore.isSessionActive || learningStore.isLoading" class="test-btn">
                {{ learningStore.isLoading ? '⏳ 제출중...' : '📝 퀴즈 제출' }}
              </button>
            </div>
          </div>
          
          <div class="scenario-group">
            <h5>4. 세션 완료 테스트</h5>
            <div class="test-controls-inline">
              <select v-model="testProceedDecision" class="test-select">
                <option value="proceed">다음 단계로</option>
                <option value="retry">재학습</option>
                <option value="dashboard">대시보드로</option>
              </select>
              <button @click="testCompleteSession" :disabled="!learningStore.isSessionActive || learningStore.isLoading" class="test-btn">
                {{ learningStore.isLoading ? '⏳ 완료중...' : '✅ 세션 완료' }}
              </button>
            </div>
          </div>
          
          <div class="scenario-group">
            <h5>5. 에러 시나리오 테스트</h5>
            <div class="test-controls-inline">
              <button @click="testNetworkError" class="test-btn error-btn">🌐 네트워크 에러</button>
              <button @click="testAuthError" class="test-btn error-btn">🔐 인증 에러</button>
              <button @click="testServerError" class="test-btn error-btn">🔥 서버 에러</button>
              <button @click="testValidationError" class="test-btn error-btn">📋 검증 에러</button>
            </div>
          </div>
          
          <div class="scenario-group">
            <h5>6. 전체 워크플로우 테스트</h5>
            <div class="test-controls-inline">
              <button @click="testFullWorkflow" :disabled="learningStore.isLoading" class="test-btn workflow-btn">
                {{ isRunningWorkflow ? '⏳ 워크플로우 실행중...' : '🔄 전체 워크플로우 실행' }}
              </button>
              <button @click="stopWorkflow" :disabled="!isRunningWorkflow" class="test-btn stop-btn">⏹️ 중단</button>
            </div>
            <div v-if="workflowProgress.length > 0" class="workflow-progress">
              <div v-for="(step, index) in workflowProgress" :key="index" class="workflow-step" :class="step.status">
                <span class="step-icon">{{ step.icon }}</span>
                <span class="step-text">{{ step.text }}</span>
                <span class="step-time">{{ step.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MainContentArea 개별 테스트 -->
    <div v-else-if="currentTestComponent === 'main-content'" class="test-container">
      <div class="test-section">
        <h2>📄 MainContentArea 실시간 UI 상태 반영 테스트</h2>
        
        <!-- Store 상태 표시 -->
        <div class="store-status">
          <div class="store-info">
            <h4>🔄 learningStore 상태</h4>
            <div class="status-grid">
              <div>세션 활성: {{ learningStore.isSessionActive ? '✅' : '❌' }}</div>
              <div>세션 완료: {{ learningStore.isSessionCompleted ? '✅' : '❌' }}</div>
              <div>로딩 중: {{ learningStore.isLoading ? '⏳' : '✅' }}</div>
              <div>에러 발생: {{ learningStore.hasError ? '❌' : '✅' }}</div>
              <div>현재 에이전트: {{ learningStore.workflowState.current_agent || '없음' }}</div>
              <div>UI 모드: {{ learningStore.workflowState.ui_mode || '없음' }}</div>
              <div>진행 단계: {{ learningStore.workflowState.session_progress_stage || '없음' }}</div>
            </div>
          </div>
          
          <div class="store-info">
            <h4>🎨 tutorStore 상태</h4>
            <div class="status-grid">
              <div>현재 에이전트: {{ tutorStore.currentAgent }}</div>
              <div>UI 모드: {{ tutorStore.currentUIMode }}</div>
              <div>컨텐츠 모드: {{ tutorStore.currentContentMode }}</div>
              <div>진행 단계: {{ tutorStore.sessionProgressStage }}</div>
              <div>완료 준비: {{ tutorStore.isSessionReadyToComplete ? '✅' : '❌' }}</div>
              <div>연동 상태: {{ tutorStore.isConnectedToLearningStore ? '✅' : '❌' }}</div>
            </div>
          </div>
        </div>
        
        <!-- 실시간 상태 변경 테스트 버튼들 -->
        <div class="test-controls-section">
          <h4>🧪 실시간 상태 변경 테스트</h4>
          <div class="test-controls-inline">
            <button @click="simulateWorkflowResponse('theory_educator')" :class="{ active: currentWorkflowAgent === 'theory_educator' }">
              이론 에이전트로 변경
            </button>
            <button @click="simulateWorkflowResponse('quiz_generator')" :class="{ active: currentWorkflowAgent === 'quiz_generator' }">
              퀴즈 에이전트로 변경
            </button>
            <button @click="simulateWorkflowResponse('evaluation_feedback_agent')" :class="{ active: currentWorkflowAgent === 'evaluation_feedback_agent' }">
              피드백 에이전트로 변경
            </button>
            <button @click="simulateWorkflowResponse('qna_resolver')" :class="{ active: currentWorkflowAgent === 'qna_resolver' }">
              QnA 에이전트로 변경
            </button>
          </div>
          
          <div class="test-controls-inline">
            <button @click="simulateSessionStart">세션 시작 시뮬레이션</button>
            <button @click="simulateProgressUpdate('theory_completed')">이론 완료 처리</button>
            <button @click="simulateProgressUpdate('quiz_and_feedback_completed')">퀴즈 완료 처리</button>
            <button @click="simulateSessionCompletion">세션 완료 시뮬레이션</button>
            <button @click="resetStoreStates">Store 상태 리셋</button>
          </div>
          
          <div class="test-controls-inline">
            <button @click="testUIMode('chat')">채팅 모드로 변경</button>
            <button @click="testUIMode('quiz')">퀴즈 모드로 변경</button>
            <button @click="testContentMode('review_theory')">이론 리뷰 모드</button>
            <button @click="testContentMode('current')">현재 모드로 복귀</button>
          </div>
        </div>
        
        <div class="test-wrapper main-content-test">
          <MainContentArea 
            @navigation-click="handleNavigationClick"
            @ui-mode-changed="handleUIModeChanged"
            @agent-changed="handleAgentChanged"
            @progress-stage-changed="handleProgressStageChanged"
          />
        </div>
      </div>
    </div>

    <!-- ChatInteraction 개별 테스트 -->
    <div v-else-if="currentTestComponent === 'chat'" class="test-container">
      <div class="test-section">
        <h2>💬 ChatInteraction 테스트</h2>
        <div class="test-controls-inline">
          <button @click="addTestMessage('user')">사용자 메시지 추가</button>
          <button @click="addTestMessage('system')">시스템 메시지 추가</button>
          <button @click="addTestMessage('qna')">QnA 메시지 추가</button>
          <button @click="toggleChatLoading">로딩 토글</button>
          <button @click="clearChatHistory">히스토리 클리어</button>
        </div>
        
        <div class="test-wrapper chat-test">
          <ChatInteraction 
            :chat-history="testChatHistory"
            :is-loading="testChatLoading"
            @send-message="handleSendMessage"
          />
        </div>
      </div>
    </div>

    <!-- QuizInteraction 개별 테스트 -->
    <div v-else-if="currentTestComponent === 'quiz'" class="test-container">
      <div class="test-section">
        <h2>📝 QuizInteraction 테스트</h2>
        <div class="test-controls-inline">
          <button @click="setQuizType('multiple_choice')" :class="{ active: testQuizData.type === 'multiple_choice' }">
            객관식
          </button>
          <button @click="setQuizType('subjective')" :class="{ active: testQuizData.type === 'subjective' }">
            주관식
          </button>
          <button @click="toggleQuizLoading">로딩 토글</button>
          <button @click="resetQuiz">퀴즈 리셋</button>
        </div>
        
        <div class="test-wrapper quiz-test">
          <QuizInteraction 
            :quiz-data="testQuizData"
            :is-loading="testQuizLoading"
            @submit-answer="handleSubmitAnswer"
            @request-hint="handleRequestHint"
          />
        </div>
      </div>
    </div>

    <!-- 디버깅 도구 -->
    <div v-else-if="currentTestComponent === 'debug'" class="test-container">
      <div class="test-section">
        <h2>🔧 디버깅 도구</h2>
        
        <!-- Store 상태 실시간 모니터링 -->
        <div class="debug-section">
          <h4>📊 Store 상태 실시간 모니터링</h4>
          <div class="debug-tabs">
            <button @click="activeDebugTab = 'learning'" :class="{ active: activeDebugTab === 'learning' }">
              learningStore
            </button>
            <button @click="activeDebugTab = 'tutor'" :class="{ active: activeDebugTab === 'tutor' }">
              tutorStore
            </button>
            <button @click="activeDebugTab = 'sync'" :class="{ active: activeDebugTab === 'sync' }">
              동기화 상태
            </button>
          </div>
          
          <div class="debug-content">
            <div v-if="activeDebugTab === 'learning'" class="debug-panel">
              <h5>learningStore 상세 상태</h5>
              <pre class="debug-json">{{ JSON.stringify(learningStoreDebugInfo, null, 2) }}</pre>
            </div>
            
            <div v-if="activeDebugTab === 'tutor'" class="debug-panel">
              <h5>tutorStore 상세 상태</h5>
              <pre class="debug-json">{{ JSON.stringify(tutorStoreDebugInfo, null, 2) }}</pre>
            </div>
            
            <div v-if="activeDebugTab === 'sync'" class="debug-panel">
              <h5>Store 간 동기화 상태</h5>
              <div class="sync-status">
                <div class="sync-item" :class="{ synced: syncStatus.agentSync, unsynced: !syncStatus.agentSync }">
                  <span class="sync-label">에이전트 동기화:</span>
                  <span class="sync-value">{{ syncStatus.agentSync ? '✅ 동기화됨' : '❌ 불일치' }}</span>
                  <div class="sync-details">
                    learningStore: {{ learningStore.workflowState.current_agent || '없음' }} | 
                    tutorStore: {{ tutorStore.currentAgent }}
                  </div>
                </div>
                
                <div class="sync-item" :class="{ synced: syncStatus.uiModeSync, unsynced: !syncStatus.uiModeSync }">
                  <span class="sync-label">UI 모드 동기화:</span>
                  <span class="sync-value">{{ syncStatus.uiModeSync ? '✅ 동기화됨' : '❌ 불일치' }}</span>
                  <div class="sync-details">
                    learningStore: {{ learningStore.workflowState.ui_mode || '없음' }} | 
                    tutorStore: {{ tutorStore.currentUIMode }}
                  </div>
                </div>
                
                <div class="sync-item" :class="{ synced: syncStatus.progressSync, unsynced: !syncStatus.progressSync }">
                  <span class="sync-label">진행 단계 동기화:</span>
                  <span class="sync-value">{{ syncStatus.progressSync ? '✅ 동기화됨' : '❌ 불일치' }}</span>
                  <div class="sync-details">
                    learningStore: {{ learningStore.workflowState.session_progress_stage || '없음' }} | 
                    tutorStore: {{ tutorStore.sessionProgressStage }}
                  </div>
                </div>
              </div>
              
              <div class="sync-actions">
                <button @click="forceSyncStores" class="sync-btn">🔄 강제 동기화</button>
                <button @click="checkStoreConnection" class="sync-btn">🔍 연결 상태 확인</button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- API 요청/응답 로그 -->
        <div class="debug-section">
          <h4>📋 API 요청/응답 로그</h4>
          <div class="log-controls">
            <button @click="clearApiLogs" class="log-btn">🗑️ 로그 클리어</button>
            <button @click="exportLogs" class="log-btn">📤 로그 내보내기</button>
            <label class="log-filter">
              <input type="checkbox" v-model="showSuccessLogs"> 성공 로그
            </label>
            <label class="log-filter">
              <input type="checkbox" v-model="showErrorLogs"> 에러 로그
            </label>
          </div>
          
          <div class="api-logs">
            <div 
              v-for="(log, index) in filteredApiLogs" 
              :key="index"
              class="api-log-item"
              :class="log.type"
            >
              <div class="log-header">
                <span class="log-method">{{ log.method }}</span>
                <span class="log-endpoint">{{ log.endpoint }}</span>
                <span class="log-status" :class="log.success ? 'success' : 'error'">
                  {{ log.success ? '✅' : '❌' }} {{ log.status }}
                </span>
                <span class="log-time">{{ log.timestamp }}</span>
                <span class="log-duration">{{ log.duration }}ms</span>
              </div>
              
              <div class="log-details" v-if="log.expanded">
                <div class="log-section">
                  <h6>요청 데이터:</h6>
                  <pre>{{ JSON.stringify(log.requestData, null, 2) }}</pre>
                </div>
                <div class="log-section">
                  <h6>응답 데이터:</h6>
                  <pre>{{ JSON.stringify(log.responseData, null, 2) }}</pre>
                </div>
                <div v-if="log.error" class="log-section">
                  <h6>에러 정보:</h6>
                  <pre class="error-text">{{ log.error }}</pre>
                </div>
              </div>
              
              <button @click="toggleLogExpansion(index)" class="log-toggle">
                {{ log.expanded ? '▲ 접기' : '▼ 펼치기' }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- 성능 모니터링 -->
        <div class="debug-section">
          <h4>⚡ 성능 모니터링</h4>
          <div class="performance-metrics">
            <div class="metric-card">
              <h5>API 응답 시간</h5>
              <div class="metric-value">{{ performanceMetrics.averageResponseTime }}ms</div>
              <div class="metric-trend">{{ performanceMetrics.responseTrend }}</div>
            </div>
            
            <div class="metric-card">
              <h5>메모리 사용량</h5>
              <div class="metric-value">{{ performanceMetrics.memoryUsage }}MB</div>
              <div class="metric-trend">{{ performanceMetrics.memoryTrend }}</div>
            </div>
            
            <div class="metric-card">
              <h5>렌더링 시간</h5>
              <div class="metric-value">{{ performanceMetrics.renderTime }}ms</div>
              <div class="metric-trend">{{ performanceMetrics.renderTrend }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 테스트 로그 -->
    <div class="test-logs">
      <h3>📝 테스트 로그</h3>
      <div class="log-container">
        <div 
          v-for="(log, index) in testLogs" 
          :key="index"
          class="log-item"
          :class="log.type"
        >
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
      <button @click="clearLogs" class="clear-logs-btn">로그 클리어</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import LearningPage from '@/views/learning/LearningPage.vue'
import MainContentArea from '@/components/learning/MainContentArea.vue'
import ChatInteraction from '@/components/learning/ChatInteraction.vue'
import QuizInteraction from '@/components/learning/QuizInteraction.vue'
import { useLearningStore } from '@/stores/learningStore'
import { useTutorStore } from '@/stores/tutorStore'

// Store 인스턴스
const learningStore = useLearningStore()
const tutorStore = useTutorStore()

// ===== 테스트 기본 상태 =====
const currentTestComponent = ref('api-test') // 기본값을 API 테스트로 변경
const testLogs = ref([])
const currentWorkflowAgent = ref('theory_educator')
const useRealApi = ref(true) // 실제 API 사용 여부

// ===== API 테스트 상태 =====
const apiConnectionStatus = ref('disconnected') // connected, loading, disconnected
const lastApiUpdate = ref('없음')
const isRunningWorkflow = ref(false)
const workflowProgress = ref([])

// API 테스트 입력값들
const testChapter = ref(2)
const testSection = ref(1)
const testMessage = ref('학습을 시작합니다')
const testUserMessage = ref('다음 단계로 넘어가주세요')
const testMessageType = ref('user')
const testQuizAnswer = ref('대규모 언어 모델')
const testProceedDecision = ref('proceed')

// ===== API 통계 및 모니터링 =====
const apiStats = reactive({
  totalRequests: 0,
  successRequests: 0,
  failedRequests: 0,
  averageResponseTime: 0,
  lastRequestType: null,
  lastError: null,
  responseTimes: []
})

// API 로그
const apiLogs = ref([])
const showSuccessLogs = ref(true)
const showErrorLogs = ref(true)

// ===== 디버깅 도구 상태 =====
const activeDebugTab = ref('learning')

// Store 디버그 정보 (computed)
const learningStoreDebugInfo = computed(() => ({
  sessionState: learningStore.sessionState,
  apiState: learningStore.apiState,
  workflowState: learningStore.workflowState,
  errorState: learningStore.errorState,
  computed: {
    isSessionActive: learningStore.isSessionActive,
    isLoading: learningStore.isLoading,
    hasError: learningStore.hasError,
    canRetry: learningStore.canRetry,
    sessionSummary: learningStore.sessionSummary,
    isSessionCompleted: learningStore.isSessionCompleted,
    nextStepInfo: learningStore.nextStepInfo
  }
}))

const tutorStoreDebugInfo = computed(() => ({
  uiState: {
    currentAgent: tutorStore.currentAgent,
    currentUIMode: tutorStore.currentUIMode,
    currentContentMode: tutorStore.currentContentMode,
    sessionProgressStage: tutorStore.sessionProgressStage,
    completedSteps: tutorStore.completedSteps
  },
  contentData: {
    mainContent: tutorStore.mainContent,
    chatHistoryLength: tutorStore.chatHistory.length,
    quizData: tutorStore.quizData,
    currentQuizInfo: tutorStore.currentQuizInfo
  },
  computed: {
    isQuizMode: tutorStore.isQuizMode,
    isChatMode: tutorStore.isChatMode,
    isSessionReadyToComplete: tutorStore.isSessionReadyToComplete,
    isConnectedToLearningStore: tutorStore.isConnectedToLearningStore,
    sessionInfo: tutorStore.sessionInfo
  }
}))

// 동기화 상태
const syncStatus = computed(() => {
  const connection = tutorStore.checkLearningStoreConnection()
  return connection.syncStatus
})

// 필터링된 API 로그
const filteredApiLogs = computed(() => {
  return apiLogs.value.filter(log => {
    if (log.success && !showSuccessLogs.value) return false
    if (!log.success && !showErrorLogs.value) return false
    return true
  })
})

// 성능 메트릭스
const performanceMetrics = reactive({
  averageResponseTime: 0,
  responseTrend: '📊',
  memoryUsage: 0,
  memoryTrend: '📊',
  renderTime: 0,
  renderTrend: '📊'
})

// MainContentArea 테스트 데이터
const testAgent = ref('theory_educator')
const testContentMode = ref('current')
const testCompletedSteps = ref({ theory: true, quiz: false, feedback: false })
const testContentData = ref({
  title: 'LLM(Large Language Model)이란?',
  subtitle: '',
  content: '테스트 컨텐츠',
  type: 'theory'
})

// ChatInteraction 테스트 데이터
const testChatHistory = ref([
  {
    sender: '튜터',
    message: 'LLM에 대해 학습해보겠습니다. 위 내용을 확인해주세요!',
    type: 'system',
    timestamp: new Date()
  }
])
const testChatLoading = ref(false)

// QuizInteraction 테스트 데이터
const testQuizData = ref({
  question: '다음 중 LLM의 특징이 아닌 것은?',
  type: 'multiple_choice',
  options: [
    { value: '1', text: '대규모 데이터 학습' },
    { value: '2', text: '실시간 인터넷 검색' },
    { value: '3', text: '언어 이해 능력' },
    { value: '4', text: '텍스트 생성 능력' }
  ],
  hint: 'LLM의 "L"이 무엇을 의미하는지 생각해보세요.'
})
const testQuizLoading = ref(false)

// ===== 유틸리티 함수들 =====

// 로그 추가 (기존 + API 로그 추가)
const addLog = (message, type = 'info') => {
  const now = new Date()
  testLogs.value.unshift({ // 최신 로그가 위로 오도록 변경
    time: now.toLocaleTimeString(),
    message,
    type
  })
  
  // 로그가 너무 많아지면 오래된 것 제거
  if (testLogs.value.length > 100) {
    testLogs.value = testLogs.value.slice(0, 100)
  }
}

// API 로그 추가
const addApiLog = (method, endpoint, requestData, responseData, success, status, duration, error = null) => {
  const now = new Date()
  apiLogs.value.unshift({
    method,
    endpoint,
    requestData,
    responseData,
    success,
    status,
    duration,
    error,
    timestamp: now.toLocaleTimeString(),
    type: success ? 'success' : 'error',
    expanded: false
  })
  
  // API 통계 업데이트
  apiStats.totalRequests++
  if (success) {
    apiStats.successRequests++
  } else {
    apiStats.failedRequests++
    apiStats.lastError = error || `${status} 에러`
  }
  
  apiStats.lastRequestType = `${method} ${endpoint}`
  apiStats.responseTimes.push(duration)
  
  // 평균 응답 시간 계산 (최근 10개 요청 기준)
  const recentTimes = apiStats.responseTimes.slice(-10)
  apiStats.averageResponseTime = Math.round(recentTimes.reduce((a, b) => a + b, 0) / recentTimes.length)
  
  // API 로그가 너무 많아지면 오래된 것 제거
  if (apiLogs.value.length > 50) {
    apiLogs.value = apiLogs.value.slice(0, 50)
  }
  
  lastApiUpdate.value = now.toLocaleTimeString()
}

// 테스트 리셋
const resetTest = () => {
  testLogs.value = []
  apiLogs.value = []
  workflowProgress.value = []
  isRunningWorkflow.value = false
  
  // API 통계 리셋
  Object.assign(apiStats, {
    totalRequests: 0,
    successRequests: 0,
    failedRequests: 0,
    averageResponseTime: 0,
    lastRequestType: null,
    lastError: null,
    responseTimes: []
  })
  
  // Store 상태 리셋
  learningStore.resetSessionState()
  tutorStore.resetSession()
  
  addLog('테스트가 완전히 리셋되었습니다', 'success')
}

// API 모드 토글
const toggleApiMode = () => {
  useRealApi.value = !useRealApi.value
  addLog(`API 모드 변경: ${useRealApi.value ? '실제 API' : '시뮬레이션'}`, 'info')
}

// ===== 실제 API 테스트 메서드들 =====

// 세션 시작 테스트
const testStartSession = async () => {
  addLog(`세션 시작 테스트: 챕터 ${testChapter.value}, 섹션 ${testSection.value}`, 'event')
  apiConnectionStatus.value = 'loading'
  
  const startTime = Date.now()
  
  try {
    const result = await learningStore.startSession(
      testChapter.value, 
      testSection.value, 
      testMessage.value
    )
    
    const duration = Date.now() - startTime
    
    addApiLog(
      'POST',
      '/learning/session/start',
      { chapter_number: testChapter.value, section_number: testSection.value, user_message: testMessage.value },
      result,
      result.success || result.isFallback,
      result.success ? 200 : (result.status || 500),
      duration,
      result.success ? null : result.error
    )
    
    if (result.success || result.isFallback) {
      apiConnectionStatus.value = 'connected'
      addLog(`세션 시작 성공! 세션 ID: ${learningStore.sessionState.session_id}`, 'success')
      
      if (result.isFallback) {
        addLog('⚠️ 기본값 모드로 동작 중 (백엔드 연결 실패)', 'warning')
      }
    } else {
      apiConnectionStatus.value = 'disconnected'
      addLog(`세션 시작 실패: ${result.error}`, 'error')
    }
    
  } catch (error) {
    const duration = Date.now() - startTime
    apiConnectionStatus.value = 'disconnected'
    
    addApiLog(
      'POST',
      '/learning/session/start',
      { chapter_number: testChapter.value, section_number: testSection.value, user_message: testMessage.value },
      null,
      false,
      500,
      duration,
      error.message
    )
    
    addLog(`세션 시작 예외 발생: ${error.message}`, 'error')
  }
}

// 메시지 전송 테스트
const testSendMessage = async () => {
  if (!learningStore.isSessionActive) {
    addLog('활성 세션이 없습니다. 먼저 세션을 시작해주세요.', 'warning')
    return
  }
  
  addLog(`메시지 전송 테스트: "${testUserMessage.value}" (${testMessageType.value})`, 'event')
  apiConnectionStatus.value = 'loading'
  
  const startTime = Date.now()
  
  try {
    const result = await learningStore.sendMessage(testUserMessage.value, testMessageType.value)
    const duration = Date.now() - startTime
    
    addApiLog(
      'POST',
      '/learning/session/message',
      { user_message: testUserMessage.value, message_type: testMessageType.value },
      result,
      result.success || result.isFallback,
      result.success ? 200 : (result.status || 500),
      duration,
      result.success ? null : result.error
    )
    
    if (result.success || result.isFallback) {
      apiConnectionStatus.value = 'connected'
      addLog(`메시지 전송 성공! 현재 에이전트: ${learningStore.workflowState.current_agent}`, 'success')
      
      if (result.isFallback) {
        addLog('⚠️ 기본값 모드로 동작 중', 'warning')
      }
    } else {
      addLog(`메시지 전송 실패: ${result.error}`, 'error')
    }
    
  } catch (error) {
    const duration = Date.now() - startTime
    apiConnectionStatus.value = 'disconnected'
    
    addApiLog(
      'POST',
      '/learning/session/message',
      { user_message: testUserMessage.value, message_type: testMessageType.value },
      null,
      false,
      500,
      duration,
      error.message
    )
    
    addLog(`메시지 전송 예외 발생: ${error.message}`, 'error')
  }
}

// 퀴즈 제출 테스트
const testSubmitQuiz = async () => {
  if (!learningStore.isSessionActive) {
    addLog('활성 세션이 없습니다. 먼저 세션을 시작해주세요.', 'warning')
    return
  }
  
  addLog(`퀴즈 제출 테스트: "${testQuizAnswer.value}"`, 'event')
  apiConnectionStatus.value = 'loading'
  
  const startTime = Date.now()
  
  try {
    const result = await learningStore.submitQuiz(testQuizAnswer.value)
    const duration = Date.now() - startTime
    
    addApiLog(
      'POST',
      '/learning/quiz/submit',
      { user_answer: testQuizAnswer.value },
      result,
      result.success || result.isFallback,
      result.success ? 200 : (result.status || 500),
      duration,
      result.success ? null : result.error
    )
    
    if (result.success || result.isFallback) {
      apiConnectionStatus.value = 'connected'
      const evaluation = learningStore.workflowState.evaluation_result
      addLog(`퀴즈 제출 성공! 결과: ${evaluation?.is_correct ? '정답' : '오답'} (점수: ${evaluation?.score || 0})`, 'success')
      
      if (result.isFallback) {
        addLog('⚠️ 기본값 모드로 동작 중', 'warning')
      }
    } else {
      addLog(`퀴즈 제출 실패: ${result.error}`, 'error')
    }
    
  } catch (error) {
    const duration = Date.now() - startTime
    apiConnectionStatus.value = 'disconnected'
    
    addApiLog(
      'POST',
      '/learning/quiz/submit',
      { user_answer: testQuizAnswer.value },
      null,
      false,
      500,
      duration,
      error.message
    )
    
    addLog(`퀴즈 제출 예외 발생: ${error.message}`, 'error')
  }
}

// 세션 완료 테스트
const testCompleteSession = async () => {
  if (!learningStore.isSessionActive) {
    addLog('활성 세션이 없습니다. 먼저 세션을 시작해주세요.', 'warning')
    return
  }
  
  addLog(`세션 완료 테스트: ${testProceedDecision.value}`, 'event')
  apiConnectionStatus.value = 'loading'
  
  const startTime = Date.now()
  
  try {
    const result = await learningStore.completeSession(testProceedDecision.value)
    const duration = Date.now() - startTime
    
    addApiLog(
      'POST',
      '/learning/session/complete',
      { proceed_decision: testProceedDecision.value },
      result,
      result.success || result.isFallback,
      result.success ? 200 : (result.status || 500),
      duration,
      result.success ? null : result.error
    )
    
    if (result.success || result.isFallback) {
      apiConnectionStatus.value = 'connected'
      const completion = result.data?.session_completion
      addLog(`세션 완료 성공! 점수: ${completion?.final_score || 0}, 다음: ${completion?.next_chapter || '없음'}장 ${completion?.next_section || '없음'}절`, 'success')
      
      if (result.isFallback) {
        addLog('⚠️ 기본값 모드로 동작 중', 'warning')
      }
    } else {
      addLog(`세션 완료 실패: ${result.error}`, 'error')
    }
    
  } catch (error) {
    const duration = Date.now() - startTime
    apiConnectionStatus.value = 'disconnected'
    
    addApiLog(
      'POST',
      '/learning/session/complete',
      { proceed_decision: testProceedDecision.value },
      null,
      false,
      500,
      duration,
      error.message
    )
    
    addLog(`세션 완료 예외 발생: ${error.message}`, 'error')
  }
}

// ===== 에러 시나리오 테스트 =====

const testNetworkError = () => {
  addLog('네트워크 에러 시뮬레이션', 'event')
  learningStore.handleApiError({
    success: false,
    type: 'network',
    error: '네트워크 연결을 확인해주세요.',
    retry: true
  }, 'networkErrorTest')
  addLog('네트워크 에러가 시뮬레이션되었습니다', 'error')
}

const testAuthError = () => {
  addLog('인증 에러 시뮬레이션', 'event')
  learningStore.handleApiError({
    success: false,
    type: 'auth',
    error: '인증이 필요합니다. 다시 로그인해주세요.',
    retry: false,
    status: 401
  }, 'authErrorTest')
  addLog('인증 에러가 시뮬레이션되었습니다', 'error')
}

const testServerError = () => {
  addLog('서버 에러 시뮬레이션', 'event')
  learningStore.handleApiError({
    success: false,
    type: 'server',
    error: '서버에 일시적인 문제가 발생했습니다.',
    retry: true,
    status: 500
  }, 'serverErrorTest')
  addLog('서버 에러가 시뮬레이션되었습니다', 'error')
}

const testValidationError = () => {
  addLog('검증 에러 시뮬레이션', 'event')
  learningStore.handleApiError({
    success: false,
    type: 'validation',
    error: '요청 데이터를 확인해주세요.',
    retry: false,
    status: 400
  }, 'validationErrorTest')
  addLog('검증 에러가 시뮬레이션되었습니다', 'error')
}

// ===== 전체 워크플로우 테스트 =====

const testFullWorkflow = async () => {
  if (isRunningWorkflow.value) return
  
  isRunningWorkflow.value = true
  workflowProgress.value = []
  
  addLog('전체 워크플로우 테스트 시작', 'event')
  
  const addWorkflowStep = (text, status = 'running', icon = '⏳') => {
    workflowProgress.value.push({
      text,
      status,
      icon,
      time: new Date().toLocaleTimeString()
    })
  }
  
  try {
    // 1단계: 세션 시작
    addWorkflowStep('세션 시작 중...', 'running', '⏳')
    await testStartSession()
    
    if (!learningStore.isSessionActive) {
      throw new Error('세션 시작 실패')
    }
    
    workflowProgress.value[workflowProgress.value.length - 1] = {
      ...workflowProgress.value[workflowProgress.value.length - 1],
      status: 'success',
      icon: '✅'
    }
    
    // 2초 대기
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 2단계: 메시지 전송
    addWorkflowStep('메시지 전송 중...', 'running', '⏳')
    await testSendMessage()
    
    workflowProgress.value[workflowProgress.value.length - 1] = {
      ...workflowProgress.value[workflowProgress.value.length - 1],
      status: 'success',
      icon: '✅'
    }
    
    // 2초 대기
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 3단계: 퀴즈 제출
    addWorkflowStep('퀴즈 제출 중...', 'running', '⏳')
    await testSubmitQuiz()
    
    workflowProgress.value[workflowProgress.value.length - 1] = {
      ...workflowProgress.value[workflowProgress.value.length - 1],
      status: 'success',
      icon: '✅'
    }
    
    // 2초 대기
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 4단계: 세션 완료
    addWorkflowStep('세션 완료 중...', 'running', '⏳')
    await testCompleteSession()
    
    workflowProgress.value[workflowProgress.value.length - 1] = {
      ...workflowProgress.value[workflowProgress.value.length - 1],
      status: 'success',
      icon: '✅'
    }
    
    addWorkflowStep('전체 워크플로우 완료!', 'success', '🎉')
    addLog('전체 워크플로우 테스트가 성공적으로 완료되었습니다', 'success')
    
  } catch (error) {
    if (workflowProgress.value.length > 0) {
      workflowProgress.value[workflowProgress.value.length - 1] = {
        ...workflowProgress.value[workflowProgress.value.length - 1],
        status: 'error',
        icon: '❌'
      }
    }
    
    addWorkflowStep(`워크플로우 실패: ${error.message}`, 'error', '❌')
    addLog(`전체 워크플로우 테스트 실패: ${error.message}`, 'error')
  } finally {
    isRunningWorkflow.value = false
  }
}

const stopWorkflow = () => {
  isRunningWorkflow.value = false
  addLog('워크플로우 테스트가 중단되었습니다', 'warning')
}

// MainContentArea 실시간 상태 반영 테스트 함수들 (기존 시뮬레이션 유지)

// 워크플로우 응답 시뮬레이션
const simulateWorkflowResponse = (agent) => {
  currentWorkflowAgent.value = agent
  
  // learningStore의 워크플로우 상태 업데이트
  const workflowResponse = {
    current_agent: agent,
    ui_mode: agent === 'quiz_generator' ? 'quiz' : 'chat',
    session_progress_stage: getProgressStageForAgent(agent),
    content: getContentForAgent(agent)
  }
  
  learningStore.updateWorkflowState(workflowResponse)
  addLog(`워크플로우 응답 시뮬레이션: ${agent}`, 'event')
}

// 에이전트별 진행 단계 매핑
const getProgressStageForAgent = (agent) => {
  const stageMap = {
    'theory_educator': 'session_start',
    'quiz_generator': 'theory_completed', 
    'evaluation_feedback_agent': 'quiz_and_feedback_completed',
    'qna_resolver': 'theory_completed'
  }
  return stageMap[agent] || 'session_start'
}

// 에이전트별 컨텐츠 생성
const getContentForAgent = (agent) => {
  const contentMap = {
    'theory_educator': {
      type: 'theory',
      title: 'LLM 기본 개념',
      content: '대규모 언어 모델(LLM)에 대해 학습해보겠습니다.'
    },
    'quiz_generator': {
      type: 'quiz',
      question: 'LLM의 정의는 무엇인가요?',
      quiz_type: 'multiple_choice',
      options: ['대규모 언어 모델', '작은 언어 모델', '번역 모델', '이미지 모델'],
      hint: 'Large Language Model의 줄임말입니다.'
    },
    'evaluation_feedback_agent': {
      type: 'feedback',
      title: '평가 완료',
      content: '정답입니다! 잘 이해하고 계시네요.',
      explanation: 'LLM은 Large Language Model의 줄임말로 대규모 언어 모델을 의미합니다.'
    },
    'qna_resolver': {
      type: 'qna',
      question: 'AI와 머신러닝의 차이가 뭐예요?',
      answer: 'AI는 더 넓은 개념으로, 인간의 지능을 모방하는 모든 기술을 포함합니다.',
      content: 'AI는 더 넓은 개념으로, 인간의 지능을 모방하는 모든 기술을 포함합니다.'
    }
  }
  return contentMap[agent] || contentMap['theory_educator']
}

// 세션 완료 시뮬레이션
const simulateSessionCompletion = async () => {
  try {
    addLog('세션 완료 시뮬레이션 시작', 'event')
    
    // 1. 모든 단계를 완료 상태로 설정
    tutorStore.updateCompletedSteps({
      theory: true,
      quiz: true,
      feedback: true
    })
    
    // 2. 진행 단계를 완료 상태로 설정
    tutorStore.updateSessionProgress('quiz_and_feedback_completed')
    
    // 3. 잠시 대기 후 세션 완료 처리
    setTimeout(async () => {
      addLog('세션 완료 조건 충족, completeSession 호출', 'event')
      
      // learningStore를 통해 세션 완료
      const result = await learningStore.completeSession('proceed')
      
      if (result.success) {
        addLog('세션 완료 성공! 완료 화면이 표시됩니다.', 'success')
        
        // 완료 화면 표시를 위한 워크플로우 상태 업데이트
        const completionWorkflow = {
          current_agent: 'session_completion',
          ui_mode: 'completion',
          session_progress_stage: 'session_completed',
          content: {
            type: 'completion',
            title: '세션 완료',
            completion_data: result.data.session_completion
          }
        }
        
        learningStore.updateWorkflowState(completionWorkflow)
        tutorStore.updateFromWorkflowResponse(completionWorkflow)
        
      } else {
        addLog(`세션 완료 실패: ${result.error}`, 'error')
      }
    }, 2000) // 2초 후 완료 처리
    
  } catch (error) {
    addLog(`세션 완료 시뮬레이션 오류: ${error.message}`, 'error')
  }
}

// 세션 시작 시뮬레이션
const simulateSessionStart = async () => {
  addLog('세션 시작 시뮬레이션 실행', 'event')
  
  // learningStore 세션 상태 업데이트
  learningStore.updateSessionState({
    session_id: `test_session_${Date.now()}`,
    is_active: true,
    start_time: new Date(),
    chapter_number: 2,
    section_number: 1,
    chapter_title: '2장 - LLM 기초',
    section_title: '1절 - 기본 개념',
    estimated_duration: '15분'
  })
  
  // 초기 워크플로우 응답
  simulateWorkflowResponse('theory_educator')
}

// 진행 단계 업데이트 시뮬레이션
const simulateProgressUpdate = (stage) => {
  learningStore.workflowState.session_progress_stage = stage
  
  // tutorStore 완료 단계 업데이트
  if (stage === 'theory_completed') {
    tutorStore.updateCompletedSteps({ theory: true })
  } else if (stage === 'quiz_and_feedback_completed') {
    tutorStore.updateCompletedSteps({ theory: true, quiz: true, feedback: true })
  }
  
  addLog(`진행 단계 업데이트: ${stage}`, 'event')
}

// UI 모드 테스트
const testUIMode = (mode) => {
  learningStore.workflowState.ui_mode = mode
  tutorStore.updateUIMode(mode)
  addLog(`UI 모드 변경: ${mode}`, 'event')
}

// 컨텐츠 모드 테스트
const testContentMode = (mode) => {
  tutorStore.updateContentMode(mode)
  addLog(`컨텐츠 모드 변경: ${mode}`, 'event')
}

// Store 상태 리셋
const resetStoreStates = () => {
  learningStore.resetSessionState()
  tutorStore.resetSession()
  currentWorkflowAgent.value = 'theory_educator'
  addLog('Store 상태가 리셋되었습니다', 'warning')
}

// MainContentArea 이벤트 핸들러들
const handleUIModeChanged = (data) => {
  addLog(`UI 모드 변경 이벤트: ${JSON.stringify(data)}`, 'event')
}

const handleAgentChanged = (data) => {
  addLog(`에이전트 변경 이벤트: ${JSON.stringify(data)}`, 'event')
}

const handleProgressStageChanged = (data) => {
  addLog(`진행 단계 변경 이벤트: ${JSON.stringify(data)}`, 'event')
}

const handleNavigationClick = (navigationType) => {
  addLog(`네비게이션 클릭: ${navigationType}`, 'event')
  testContentMode.value = navigationType === 'current' ? 'current' : `review_${navigationType}`
}

// ChatInteraction 테스트 함수들
const addTestMessage = (type) => {
  const messages = {
    user: { sender: '나', message: '테스트 사용자 메시지입니다.', type: 'user' },
    system: { sender: '튜터', message: '테스트 시스템 메시지입니다.', type: 'system' },
    qna: { sender: '튜터', message: 'QnA 테스트 메시지입니다.', type: 'qna' }
  }
  
  testChatHistory.value.push({
    ...messages[type],
    timestamp: new Date()
  })
  
  addLog(`${type} 메시지 추가됨`, 'event')
}

const toggleChatLoading = () => {
  testChatLoading.value = !testChatLoading.value
  addLog(`채팅 로딩 상태: ${testChatLoading.value}`, 'info')
}

const clearChatHistory = () => {
  testChatHistory.value = []
  addLog('채팅 히스토리가 클리어되었습니다', 'warning')
}

const handleSendMessage = (message) => {
  addLog(`메시지 전송: "${message}"`, 'event')
  
  // 사용자 메시지 추가
  testChatHistory.value.push({
    sender: '나',
    message: message,
    type: 'user',
    timestamp: new Date()
  })
  
  // 응답 시뮬레이션
  setTimeout(() => {
    testChatHistory.value.push({
      sender: '튜터',
      message: `"${message}"에 대한 응답입니다.`,
      type: 'system',
      timestamp: new Date()
    })
  }, 1000)
}

// QuizInteraction 테스트 함수들
const setQuizType = (type) => {
  if (type === 'subjective') {
    testQuizData.value = {
      question: 'LLM의 주요 특징에 대해 설명해주세요.',
      type: 'subjective',
      hint: '대규모 데이터, 언어 이해, 생성 능력 등을 고려해보세요.'
    }
  } else {
    testQuizData.value = {
      question: '다음 중 LLM의 특징이 아닌 것은?',
      type: 'multiple_choice',
      options: [
        { value: '1', text: '대규모 데이터 학습' },
        { value: '2', text: '실시간 인터넷 검색' },
        { value: '3', text: '언어 이해 능력' },
        { value: '4', text: '텍스트 생성 능력' }
      ],
      hint: 'LLM의 "L"이 무엇을 의미하는지 생각해보세요.'
    }
  }
  
  addLog(`퀴즈 타입 변경: ${type}`, 'info')
}

const toggleQuizLoading = () => {
  testQuizLoading.value = !testQuizLoading.value
  addLog(`퀴즈 로딩 상태: ${testQuizLoading.value}`, 'info')
}

const resetQuiz = () => {
  setQuizType('multiple_choice')
  addLog('퀴즈가 리셋되었습니다', 'warning')
}

const handleSubmitAnswer = (answerData) => {
  addLog(`답변 제출: ${JSON.stringify(answerData)}`, 'event')
}

const handleRequestHint = () => {
  addLog('힌트 요청됨', 'event')
}

const clearLogs = () => {
  testLogs.value = []
}

// ===== 디버깅 도구 메서드들 =====

// API 로그 관련
const clearApiLogs = () => {
  apiLogs.value = []
  addLog('API 로그가 클리어되었습니다', 'info')
}

const exportLogs = () => {
  const logData = {
    testLogs: testLogs.value,
    apiLogs: apiLogs.value,
    apiStats: apiStats,
    timestamp: new Date().toISOString()
  }
  
  const dataStr = JSON.stringify(logData, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `api-test-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`
  link.click()
  
  URL.revokeObjectURL(url)
  addLog('로그가 JSON 파일로 내보내졌습니다', 'success')
}

const toggleLogExpansion = (index) => {
  apiLogs.value[index].expanded = !apiLogs.value[index].expanded
}

// Store 동기화 관련
const forceSyncStores = () => {
  addLog('Store 강제 동기화 실행', 'event')
  
  // learningStore의 현재 상태를 tutorStore에 강제 동기화
  if (learningStore.workflowState && Object.keys(learningStore.workflowState).length > 0) {
    tutorStore.updateFromWorkflowResponse(learningStore.workflowState)
    addLog('learningStore → tutorStore 동기화 완료', 'success')
  } else {
    addLog('동기화할 learningStore 상태가 없습니다', 'warning')
  }
}

const checkStoreConnection = () => {
  const connection = tutorStore.checkLearningStoreConnection()
  addLog(`Store 연결 상태 확인 완료: ${JSON.stringify(connection, null, 2)}`, 'info')
  return connection
}

// ===== 성능 모니터링 =====

const updatePerformanceMetrics = () => {
  // API 응답 시간
  if (apiStats.responseTimes.length > 0) {
    const recent = apiStats.responseTimes.slice(-5)
    const avg = recent.reduce((a, b) => a + b, 0) / recent.length
    performanceMetrics.averageResponseTime = Math.round(avg)
    
    // 트렌드 계산 (최근 5개와 이전 5개 비교)
    if (apiStats.responseTimes.length >= 10) {
      const previous = apiStats.responseTimes.slice(-10, -5)
      const prevAvg = previous.reduce((a, b) => a + b, 0) / previous.length
      
      if (avg < prevAvg * 0.9) {
        performanceMetrics.responseTrend = '📈 개선됨'
      } else if (avg > prevAvg * 1.1) {
        performanceMetrics.responseTrend = '📉 느려짐'
      } else {
        performanceMetrics.responseTrend = '📊 안정적'
      }
    }
  }
  
  // 메모리 사용량 (대략적인 추정)
  if (performance.memory) {
    performanceMetrics.memoryUsage = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024)
    performanceMetrics.memoryTrend = '📊 모니터링 중'
  }
  
  // 렌더링 시간 (대략적인 추정)
  performanceMetrics.renderTime = Math.round(Math.random() * 50 + 10) // 실제로는 더 정교한 측정 필요
  performanceMetrics.renderTrend = '📊 모니터링 중'
}

// ===== 감시자 및 라이프사이클 =====

// learningStore 상태 변화 감시
watch(
  () => learningStore.apiState.loading,
  (newLoading) => {
    if (newLoading) {
      apiConnectionStatus.value = 'loading'
    } else if (learningStore.hasError) {
      apiConnectionStatus.value = 'disconnected'
    } else if (learningStore.isSessionActive) {
      apiConnectionStatus.value = 'connected'
    }
  }
)

// API 통계 변화 감시하여 성능 메트릭스 업데이트
watch(
  () => apiStats.totalRequests,
  () => {
    updatePerformanceMetrics()
  }
)

// 컴포넌트 마운트 시
onMounted(() => {
  addLog('실제 API 연동 테스트 페이지가 로드되었습니다', 'success')
  addLog(`현재 모드: ${useRealApi.value ? '실제 API' : '시뮬레이션'}`, 'info')
  
  // 초기 성능 메트릭스 설정
  updatePerformanceMetrics()
  
  // 주기적으로 성능 메트릭스 업데이트 (10초마다)
  const performanceInterval = setInterval(updatePerformanceMetrics, 10000)
  
  // 컴포넌트 언마운트 시 인터벌 정리
  onUnmounted(() => {
    clearInterval(performanceInterval)
  })
})

// Store 상태 변화 로깅
watch(
  () => learningStore.workflowState.current_agent,
  (newAgent, oldAgent) => {
    if (newAgent && newAgent !== oldAgent) {
      addLog(`에이전트 변경: ${oldAgent || '없음'} → ${newAgent}`, 'event')
    }
  }
)

watch(
  () => learningStore.workflowState.ui_mode,
  (newMode, oldMode) => {
    if (newMode && newMode !== oldMode) {
      addLog(`UI 모드 변경: ${oldMode || '없음'} → ${newMode}`, 'event')
    }
  }
)

watch(
  () => learningStore.hasError,
  (hasError) => {
    if (hasError) {
      addLog(`learningStore 에러 발생: ${learningStore.errorState.error_message}`, 'error')
    }
  }
)
</script>

<style scoped>
.component-test-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  background: #f8f9fa;
  min-height: 100vh;
}

.test-header {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.test-header h1 {
  margin: 0;
  color: #2c3e50;
}

.test-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.test-selector {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  background: white;
}

.reset-btn {
  padding: 0.5rem 1rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
}

.test-container {
  background: white;
  border-radius: 1rem;
  margin-bottom: 2rem;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.full-test .test-wrapper {
  height: 90vh;
}

.test-section {
  padding: 1.5rem;
}

.test-section h2 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.test-controls-inline {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.test-controls-inline button {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.test-controls-inline button:hover {
  background: #f8f9fa;
}

.test-controls-inline button.active {
  background: #74a8f7;
  color: white;
  border-color: #74a8f7;
}

/* Store 상태 표시 스타일 */
.store-status {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
}

.store-info h4 {
  margin: 0 0 0.75rem 0;
  color: #495057;
  font-size: 1rem;
}

.status-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-family: monospace;
}

.status-grid div {
  padding: 0.25rem 0.5rem;
  background: white;
  border-radius: 0.25rem;
  border: 1px solid #e9ecef;
}

.test-controls-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #fff3cd;
  border-radius: 0.5rem;
  border: 1px solid #ffeaa7;
}

.test-controls-section h4 {
  margin: 0 0 1rem 0;
  color: #856404;
}

.test-wrapper {
  border: 2px dashed #dee2e6;
  border-radius: 0.5rem;
  overflow: hidden;
}

.main-content-test {
  height: 600px;
}

.chat-test {
  height: 500px;
  display: flex; /* flexbox 컨테이너로 설정 */
}

.quiz-test {
  height: 600px;
}

.test-logs {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.test-logs h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.log-container {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.log-item {
  display: flex;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
  font-family: monospace;
  font-size: 0.875rem;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #6c757d;
  min-width: 80px;
}

.log-message {
  flex: 1;
}

.log-item.info .log-message {
  color: #0066cc;
}

.log-item.event .log-message {
  color: #28a745;
  font-weight: bold;
}

.log-item.warning .log-message {
  color: #ffc107;
}

.log-item.success .log-message {
  color: #28a745;
}

.clear-logs-btn {
  padding: 0.5rem 1rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
}

/* ===== API 테스트 관련 스타일 ===== */

.api-mode-btn {
  padding: 0.5rem 1rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.api-mode-btn:not(.active) {
  background: #6c757d;
}

.api-status-monitor {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border: 1px solid #dee2e6;
}

.api-status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.api-status-header h4 {
  margin: 0;
  color: #495057;
}

.status-indicators {
  display: flex;
  gap: 1rem;
  align-items: center;
  font-size: 0.875rem;
}

.status-indicator {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: bold;
}

.status-indicator.connected {
  background: #d4edda;
  color: #155724;
}

.status-indicator.loading {
  background: #fff3cd;
  color: #856404;
}

.status-indicator.disconnected {
  background: #f8d7da;
  color: #721c24;
}

.last-update {
  color: #6c757d;
  font-family: monospace;
}

.api-status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.status-card {
  background: white;
  border-radius: 0.375rem;
  padding: 1rem;
  border: 1px solid #dee2e6;
}

.status-card h5 {
  margin: 0 0 0.75rem 0;
  color: #495057;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-details {
  display: grid;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-family: monospace;
}

.status-details div {
  padding: 0.125rem 0;
  border-bottom: 1px solid #f8f9fa;
}

.api-test-scenarios {
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #dee2e6;
}

.api-test-scenarios h4 {
  margin: 0 0 1rem 0;
  color: #495057;
}

.scenario-group {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.375rem;
  border: 1px solid #e9ecef;
}

.scenario-group h5 {
  margin: 0 0 0.75rem 0;
  color: #495057;
  font-size: 0.875rem;
}

.test-input, .test-select {
  padding: 0.375rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  margin-right: 0.5rem;
}

.test-input {
  min-width: 120px;
}

.test-btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid #007bff;
  background: #007bff;
  color: white;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.test-btn:hover:not(:disabled) {
  background: #0056b3;
  border-color: #0056b3;
}

.test-btn:disabled {
  background: #6c757d;
  border-color: #6c757d;
  cursor: not-allowed;
}

.test-btn.error-btn {
  background: #dc3545;
  border-color: #dc3545;
}

.test-btn.error-btn:hover:not(:disabled) {
  background: #c82333;
  border-color: #bd2130;
}

.test-btn.workflow-btn {
  background: #28a745;
  border-color: #28a745;
}

.test-btn.workflow-btn:hover:not(:disabled) {
  background: #218838;
  border-color: #1e7e34;
}

.test-btn.stop-btn {
  background: #ffc107;
  border-color: #ffc107;
  color: #212529;
}

.workflow-progress {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 0.375rem;
  border: 1px solid #dee2e6;
}

.workflow-step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f8f9fa;
  font-size: 0.875rem;
}

.workflow-step:last-child {
  border-bottom: none;
}

.workflow-step.success {
  color: #28a745;
}

.workflow-step.error {
  color: #dc3545;
}

.workflow-step.running {
  color: #ffc107;
}

.step-icon {
  font-size: 1rem;
}

.step-text {
  flex: 1;
}

.step-time {
  font-family: monospace;
  color: #6c757d;
  font-size: 0.75rem;
}

/* ===== 디버깅 도구 스타일 ===== */

.debug-section {
  margin-bottom: 2rem;
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #dee2e6;
}

.debug-section h4 {
  margin: 0 0 1rem 0;
  color: #495057;
}

.debug-tabs {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.debug-tabs button {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: #6c757d;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.debug-tabs button.active {
  color: #007bff;
  border-bottom-color: #007bff;
}

.debug-tabs button:hover {
  color: #007bff;
}

.debug-content {
  min-height: 200px;
}

.debug-panel h5 {
  margin: 0 0 1rem 0;
  color: #495057;
  font-size: 0.875rem;
}

.debug-json {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.25rem;
  padding: 1rem;
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
}

.sync-status {
  display: grid;
  gap: 1rem;
}

.sync-item {
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid #dee2e6;
}

.sync-item.synced {
  background: #d4edda;
  border-color: #c3e6cb;
}

.sync-item.unsynced {
  background: #f8d7da;
  border-color: #f5c6cb;
}

.sync-label {
  font-weight: 600;
  display: block;
  margin-bottom: 0.25rem;
}

.sync-value {
  font-size: 0.875rem;
  display: block;
  margin-bottom: 0.5rem;
}

.sync-details {
  font-size: 0.75rem;
  font-family: monospace;
  color: #6c757d;
}

.sync-actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
}

.sync-btn {
  padding: 0.375rem 0.75rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.log-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.log-btn {
  padding: 0.375rem 0.75rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.log-filter {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.api-logs {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
}

.api-log-item {
  border-bottom: 1px solid #e9ecef;
  background: white;
}

.api-log-item:last-child {
  border-bottom: none;
}

.api-log-item.success {
  border-left: 4px solid #28a745;
}

.api-log-item.error {
  border-left: 4px solid #dc3545;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-family: monospace;
}

.log-method {
  font-weight: bold;
  color: #007bff;
  min-width: 50px;
}

.log-endpoint {
  flex: 1;
  color: #495057;
}

.log-status.success {
  color: #28a745;
}

.log-status.error {
  color: #dc3545;
}

.log-time, .log-duration {
  color: #6c757d;
  font-size: 0.75rem;
}

.log-details {
  padding: 0 1rem 1rem 1rem;
  background: #f8f9fa;
}

.log-section {
  margin-bottom: 1rem;
}

.log-section h6 {
  margin: 0 0 0.5rem 0;
  color: #495057;
  font-size: 0.75rem;
}

.log-section pre {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-size: 0.7rem;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

.error-text {
  color: #dc3545;
}

.log-toggle {
  position: absolute;
  right: 1rem;
  top: 0.75rem;
  background: transparent;
  border: none;
  color: #6c757d;
  cursor: pointer;
  font-size: 0.75rem;
}

.performance-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metric-card {
  background: #f8f9fa;
  border-radius: 0.375rem;
  padding: 1rem;
  text-align: center;
  border: 1px solid #e9ecef;
}

.metric-card h5 {
  margin: 0 0 0.5rem 0;
  color: #495057;
  font-size: 0.875rem;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 0.25rem;
}

.metric-trend {
  font-size: 0.75rem;
  color: #6c757d;
}

@media (max-width: 768px) {
  .component-test-page {
    padding: 1rem;
  }
  
  .test-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .test-controls {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .api-status-grid {
    grid-template-columns: 1fr;
  }
  
  .test-controls-inline {
    flex-direction: column;
    align-items: stretch;
  }
  
  .test-input, .test-select, .test-btn {
    margin: 0.25rem 0;
  }
  
  .performance-metrics {
    grid-template-columns: 1fr;
  }
  
  .log-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>