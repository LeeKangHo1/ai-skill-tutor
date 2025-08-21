<!-- frontend/src/views/test/ComponentTest.vue -->
<template>
  <div class="component-test-page">
    <div class="test-header">
      <h1>🧪 LearningPage 컴포넌트 테스트</h1>
      <div class="test-controls">
        <select v-model="currentTestComponent" class="test-selector">
          <option value="all">전체 통합 테스트</option>
          <option value="main-content">MainContentArea 테스트</option>
          <option value="chat">ChatInteraction 테스트</option>
          <option value="quiz">QuizInteraction 테스트</option>
        </select>
        <button @click="resetTest" class="reset-btn">🔄 리셋</button>
      </div>
    </div>

    <!-- 전체 통합 테스트 -->
    <div v-if="currentTestComponent === 'all'" class="test-container full-test">
      <div class="test-wrapper">
        <LearningPage />
      </div>
    </div>

    <!-- MainContentArea 개별 테스트 -->
    <div v-else-if="currentTestComponent === 'main-content'" class="test-container">
      <div class="test-section">
        <h2>📄 MainContentArea 테스트</h2>
        <div class="test-controls-inline">
          <button @click="changeAgent('theory_educator')" :class="{ active: testAgent === 'theory_educator' }">
            이론 모드
          </button>
          <button @click="changeAgent('quiz_generator')" :class="{ active: testAgent === 'quiz_generator' }">
            퀴즈 모드
          </button>
          <button @click="changeAgent('evaluation_feedback')" :class="{ active: testAgent === 'evaluation_feedback' }">
            피드백 모드
          </button>
          <button @click="changeAgent('qna_resolver')" :class="{ active: testAgent === 'qna_resolver' }">
            QnA 모드
          </button>
        </div>
        
        <div class="test-wrapper main-content-test">
          <MainContentArea 
            :current-agent="testAgent"
            :content-data="testContentData"
            :current-content-mode="testContentMode"
            :completed-steps="testCompletedSteps"
            @navigation-click="handleNavigationClick"
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
import { ref, reactive } from 'vue'
import LearningPage from '@/views/learning/LearningPage.vue'
import MainContentArea from '@/components/learning/MainContentArea.vue'
import ChatInteraction from '@/components/learning/ChatInteraction.vue'
import QuizInteraction from '@/components/learning/QuizInteraction.vue'

// 테스트 상태
const currentTestComponent = ref('all')
const testLogs = ref([])

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

// 유틸리티 함수들
const addLog = (message, type = 'info') => {
  const now = new Date()
  testLogs.value.push({
    time: now.toLocaleTimeString(),
    message,
    type
  })
}

const resetTest = () => {
  testLogs.value = []
  testAgent.value = 'theory_educator'
  testContentMode.value = 'current'
  testChatLoading.value = false
  testQuizLoading.value = false
  addLog('테스트가 리셋되었습니다', 'success')
}

// MainContentArea 테스트 함수들
const changeAgent = (agent) => {
  testAgent.value = agent
  addLog(`에이전트 변경: ${agent}`, 'info')
  
  // 에이전트별 컨텐츠 데이터 업데이트
  switch (agent) {
    case 'quiz_generator':
      testCompletedSteps.value.quiz = true
      break
    case 'evaluation_feedback':
      testCompletedSteps.value.feedback = true
      break
  }
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

// 초기 로그
addLog('컴포넌트 테스트 페이지가 로드되었습니다', 'success')
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
  }
}
</style>