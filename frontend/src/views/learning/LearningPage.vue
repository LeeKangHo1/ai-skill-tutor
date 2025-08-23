<!-- frontend/src/views/learning/LearningPage.vue -->
<template>
  <div class="learning-page">
    <!-- 헤더 영역 -->
    <div class="learning-header">
      <div class="header-left">
        <div class="logo">🤖 AI 활용법 학습 튜터</div>
        <div class="current-session">
          {{ currentChapter }}챕터 {{ currentSection }}섹션: {{ sectionTitle }}
        </div>
      </div>
      <div class="header-right">
        <button class="btn btn-secondary" @click="goToDashboard">
          대시보드로
        </button>
      </div>
    </div>

    <!-- 진행 상태 표시 -->
    <div class="session-progress">
      <div class="progress-info">
        <div class="progress-steps">
          <div 
            class="progress-step"
            :class="getStepClass('theory')"
            id="theory-step"
          >
            <div class="step-indicator">이론</div>
          </div>
          <div 
            class="progress-step"
            :class="getStepClass('quiz')"
            id="quiz-step"
          >
            <div class="step-indicator">퀴즈</div>
          </div>
          <div 
            class="progress-step"
            :class="getStepClass('feedback')"
            id="feedback-step"
          >
            <div class="step-indicator">풀이</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 메인 컨텐츠 영역 -->
    <div class="learning-content">
      <!-- 왼쪽: 메인 컨텐츠 (60%) -->
      <MainContentArea 
        :current-agent="currentAgent"
        :content-data="contentData"
        :current-content-mode="currentContentMode"
        :completed-steps="completedSteps"
        @navigation-click="handleNavigationClick"
      />

      <!-- 오른쪽: 상호작용 영역 (50%) -->
      <div class="interaction-area">
        <div class="interaction-header">
          {{ uiMode === 'chat' ? '💬 채팅' : '📝 퀴즈' }}
        </div>
        
        <div class="interaction-body">
          <!-- 채팅 모드 -->
          <ChatInteraction 
            v-if="uiMode === 'chat'"
            :chat-history="chatHistory"
            :is-loading="isLoading || isApiLoading"
            @send-message="handleSendMessage"
          />

          <!-- 퀴즈 모드 -->
          <QuizInteraction 
            v-else-if="uiMode === 'quiz'"
            :quiz-data="quizData"
            :is-loading="isLoading || isApiLoading"
            @submit-answer="handleSubmitAnswer"
            @request-hint="handleRequestHint"
          />
        </div>
      </div>
    </div>

    <!-- 로딩 모달 -->
    <div v-if="isLoading || isApiLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>
    </div>

    <!-- 에러 표시 -->
    <div v-if="hasApiError" class="error-overlay">
      <div class="error-message">
        <h3>⚠️ 오류 발생</h3>
        <p>{{ learningStore.errorState.error_message }}</p>
        <button 
          v-if="learningStore.canRetry" 
          class="btn btn-primary"
          @click="learningStore.retryLastAction"
        >
          다시 시도
        </button>
        <button class="btn btn-secondary" @click="learningStore.clearErrors">
          닫기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// frontend/src/views/learning/LearningPage.vue
import { ref, computed, onMounted, onUnmounted, watch, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTutorStore } from '@/stores/tutorStore'
import { useLearningStore } from '@/stores/learningStore'
import MainContentArea from '@/components/learning/MainContentArea.vue'
import ChatInteraction from '@/components/learning/ChatInteraction.vue'
import QuizInteraction from '@/components/learning/QuizInteraction.vue'

// 라우터 및 스토어
const router = useRouter()
const route = useRoute()
const tutorStore = useTutorStore()
const learningStore = useLearningStore()

// ===== 반응형 상태 =====
const isLoading = ref(false)
const loadingMessage = ref('학습 내용을 준비하고 있습니다...')

// 컴포넌트별 데이터 (tutorStore에서 관리하므로 computed로 변경)
const contentData = computed(() => tutorStore.mainContent || {
  title: '',
  subtitle: '',
  content: '',
  type: 'theory'
})

// ===== 컴퓨티드 속성들 (tutorStore 기반) =====
const currentAgent = computed(() => tutorStore.currentAgent)
const uiMode = computed(() => tutorStore.currentUIMode)
const currentContentMode = computed(() => tutorStore.currentContentMode || 'current')
const completedSteps = computed(() => tutorStore.completedSteps || { theory: true, quiz: false, feedback: false })

// 세션 정보 (learningStore 우선, tutorStore 폴백)
const currentChapter = computed(() => {
  return learningStore.sessionState?.chapter_number || 
         tutorStore.sessionInfo?.chapter_number || 2
})

const currentSection = computed(() => {
  return learningStore.sessionState?.section_number || 
         tutorStore.sessionInfo?.section_number || 1
})

const sectionTitle = computed(() => {
  return learningStore.sessionState?.section_title || 
         tutorStore.sessionInfo?.section_title || 'LLM이란 무엇인가'
})

// tutorStore에서 UI 데이터 가져오기
const chatHistory = computed(() => tutorStore.chatHistory || [])
const quizData = computed(() => tutorStore.quizData || {
  question: '',
  options: [],
  type: 'multiple_choice',
  hint: ''
})

// learningStore 상태 반영
const isApiLoading = computed(() => learningStore.isLoading)
const hasApiError = computed(() => learningStore.hasError)

// 진행 단계 클래스 계산
const getStepClass = (stepType) => {
  const agent = currentAgent.value
  
  if (stepType === 'theory') {
    if (agent === 'theory_educator' || agent === 'qna_resolver') {
      return 'step-active'
    }
    return completedSteps.value.theory ? 'step-completed' : 'step-pending'
  }
  
  if (stepType === 'quiz') {
    if (agent === 'quiz_generator') {
      return 'step-active'
    }
    return completedSteps.value.quiz ? 'step-completed' : 'step-pending'
  }
  
  if (stepType === 'feedback') {
    if (agent === 'evaluation_feedback') {
      return 'step-active'
    }
    return completedSteps.value.feedback ? 'step-completed' : 'step-pending'
  }
  
  return 'step-pending'
}

// ===== learningStore와 tutorStore 연동 함수들 =====

// 세션 시작 함수 - learningStore.startSession 호출 및 결과를 tutorStore에 반영
const startLearning = async (chapterNumber, sectionNumber, initialMessage = '학습을 시작합니다') => {
  try {
    console.log(`학습 세션 시작: 챕터 ${chapterNumber}, 섹션 ${sectionNumber}`)
    
    isLoading.value = true
    loadingMessage.value = '학습 세션을 시작하고 있습니다...'
    
    // learningStore를 통해 세션 시작
    const result = await learningStore.startSession(chapterNumber, sectionNumber, initialMessage)
    
    if (result.success && result.data.workflow_response) {
      // API 응답의 workflow_response를 tutorStore에 반영
      tutorStore.updateFromWorkflowResponse(result.data.workflow_response)
      
      console.log('세션 시작 성공, UI 상태 업데이트 완료')
    } else {
      console.error('세션 시작 실패:', result.error)
      // 에러 상황에서도 tutorStore에 에러 상태 반영
      tutorStore.setError?.(result.error || '세션 시작에 실패했습니다.')
    }
  } catch (error) {
    console.error('세션 시작 중 오류 발생:', error)
    tutorStore.setError?.('세션 시작 중 오류가 발생했습니다.')
  } finally {
    isLoading.value = false
  }
}

// 메시지 전송 함수 - learningStore를 통한 API 호출 및 tutorStore 업데이트
const sendMessage = async (message, messageType = 'user') => {
  try {
    console.log('메시지 전송:', message)
    
    isLoading.value = true
    loadingMessage.value = '메시지를 처리하고 있습니다...'
    
    // learningStore를 통해 메시지 전송
    const result = await learningStore.sendMessage(message, messageType)
    
    if (result.success && result.data.workflow_response) {
      // API 응답의 workflow_response를 tutorStore에 반영
      tutorStore.updateFromWorkflowResponse(result.data.workflow_response)
      
      console.log('메시지 전송 성공, UI 상태 업데이트 완료')
    } else {
      console.error('메시지 전송 실패:', result.error)
      tutorStore.setError?.(result.error || '메시지 전송에 실패했습니다.')
    }
  } catch (error) {
    console.error('메시지 전송 중 오류 발생:', error)
    tutorStore.setError?.('메시지 전송 중 오류가 발생했습니다.')
  } finally {
    isLoading.value = false
  }
}

// 퀴즈 제출 함수 - learningStore를 통한 API 호출 및 tutorStore 업데이트
const submitQuiz = async (answer) => {
  try {
    console.log('퀴즈 답안 제출:', answer)
    
    isLoading.value = true
    loadingMessage.value = '답변을 평가하고 있습니다...'
    
    // learningStore를 통해 퀴즈 제출
    const result = await learningStore.submitQuiz(answer)
    
    if (result.success && result.data.workflow_response) {
      // API 응답의 workflow_response를 tutorStore에 반영
      tutorStore.updateFromWorkflowResponse(result.data.workflow_response)
      
      console.log('퀴즈 제출 성공, UI 상태 업데이트 완료')
    } else {
      console.error('퀴즈 제출 실패:', result.error)
      tutorStore.setError?.(result.error || '퀴즈 제출에 실패했습니다.')
    }
  } catch (error) {
    console.error('퀴즈 제출 중 오류 발생:', error)
    tutorStore.setError?.('퀴즈 제출 중 오류가 발생했습니다.')
  } finally {
    isLoading.value = false
  }
}

// 세션 완료 함수 - learningStore를 통한 API 호출 및 tutorStore 업데이트
const completeSession = async (proceedDecision = 'proceed') => {
  try {
    console.log('세션 완료 처리:', proceedDecision)
    
    isLoading.value = true
    loadingMessage.value = '세션을 완료하고 있습니다...'
    
    // learningStore를 통해 세션 완료
    const result = await learningStore.completeSession(proceedDecision)
    
    if (result.success) {
      // 세션 완료 후 tutorStore 상태 업데이트
      if (result.data.workflow_response) {
        tutorStore.updateFromWorkflowResponse(result.data.workflow_response)
      }
      
      console.log('세션 완료 성공')
    } else {
      console.error('세션 완료 실패:', result.error)
      tutorStore.setError?.(result.error || '세션 완료에 실패했습니다.')
    }
  } catch (error) {
    console.error('세션 완료 중 오류 발생:', error)
    tutorStore.setError?.('세션 완료 중 오류가 발생했습니다.')
  } finally {
    isLoading.value = false
  }
}

// ===== 컴포넌트 이벤트 핸들러들 =====

// 이벤트 핸들러들
const handleSendMessage = async (message) => {
  try {
    // 사용자 메시지를 채팅 히스토리에 추가 (UI 즉시 반영)
    tutorStore.addChatMessage({
      sender: '나',
      message: message,
      type: 'user',
      timestamp: new Date()
    })
    
    // learningStore를 통한 실제 API 호출
    await sendMessage(message, 'user')
    
  } catch (error) {
    console.error('메시지 전송 오류:', error)
    tutorStore.addChatMessage({
      sender: '시스템',
      message: '오류가 발생했습니다. 다시 시도해주세요.',
      type: 'system',
      timestamp: new Date()
    })
  }
}

const handleSubmitAnswer = async (answerData) => {
  try {
    // answerData에서 실제 답안 추출
    const answer = answerData.answer || answerData
    
    // learningStore를 통한 실제 API 호출
    await submitQuiz(answer)
    
  } catch (error) {
    console.error('퀴즈 제출 오류:', error)
  }
}

const handleRequestHint = () => {
  // 힌트 요청을 채팅 히스토리에 추가
  tutorStore.addChatMessage({
    sender: '튜터',
    message: '힌트: LLM의 "L"이 무엇을 의미하는지 생각해보세요.',
    type: 'system',
    timestamp: new Date()
  })
}

const handleNavigationClick = (navigationType) => {
  // 네비게이션 버튼 클릭 처리
  if (navigationType === 'theory') {
    tutorStore.updateContentMode('review_theory')
  } else if (navigationType === 'quiz') {
    tutorStore.updateContentMode('review_quiz')
  } else if (navigationType === 'current') {
    tutorStore.updateContentMode('current')
  }
}

const goToDashboard = () => {
  router.push('/dashboard')
}

// ===== 유틸리티 함수들 =====

// 디버그용 함수들
const debugStoreStates = () => {
  console.log('=== Store 상태 디버그 ===')
  console.log('learningStore 상태:', {
    isSessionActive: learningStore.isSessionActive,
    isLoading: learningStore.isLoading,
    hasError: learningStore.hasError,
    sessionState: learningStore.sessionState,
    workflowState: learningStore.workflowState
  })
  console.log('tutorStore 상태:', tutorStore.getStateInfo())
  console.log('연동 상태:', tutorStore.checkLearningStoreConnection())
}

// ===== 하위 컴포넌트에서 사용할 수 있도록 함수들을 provide =====
provide('learningActions', {
  startLearning,
  sendMessage,
  submitQuiz,
  completeSession
})

provide('learningStore', learningStore)
provide('tutorStore', tutorStore)

// ===== 라이프사이클 훅 =====
onMounted(async () => {
  try {
    // 라우트 파라미터에서 챕터/섹션 정보 가져오기
    const chapterNumber = parseInt(route.params.chapter) || 2
    const sectionNumber = parseInt(route.params.section) || 1
    
    console.log('LearningPage 마운트:', { chapterNumber, sectionNumber })
    
    // learningStore와 tutorStore를 통한 세션 시작
    await startLearning(chapterNumber, sectionNumber, '학습을 시작합니다')
    
  } catch (error) {
    console.error('세션 초기화 오류:', error)
  }
})

// 컴포넌트 언마운트 시 상태 정리
onUnmounted(() => {
  console.log('LearningPage 언마운트')
  // 필요시 세션 정리 로직 추가
})

// ===== 감시자 =====
watch(currentAgent, (newAgent) => {
  console.log('에이전트 변경:', newAgent)
})

watch(uiMode, (newMode) => {
  console.log('UI 모드 변경:', newMode)
})

// learningStore 상태 변화 감시
watch(() => learningStore.isLoading, (newLoading) => {
  isLoading.value = newLoading
})

watch(() => learningStore.hasError, (hasError) => {
  if (hasError) {
    console.error('learningStore 에러:', learningStore.errorState)
  }
})

// tutorStore와 learningStore 연동 상태 감시
watch(() => tutorStore.isConnectedToLearningStore, (isConnected) => {
  console.log('tutorStore-learningStore 연동 상태:', isConnected)
})
</script>

<style scoped>
.learning-page {
  max-width: 1400px;
  margin: 0 auto;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: 90vh;
  display: flex;
  flex-direction: column;
}

/* 헤더 영역 */
.learning-header {
  background: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  font-size: 1.2rem;
  font-weight: bold;
}

.current-session {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.9rem;
}

/* 진행 상태 표시 */
.session-progress {
  background: #f8f9fa;
  padding: 1rem 2rem;
  border-bottom: 1px solid #dee2e6;
}

.progress-info {
  display: flex;
  justify-content: center;
  align-items: center;
}

.progress-steps {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.4rem;
  font-weight: 700;
  position: relative;
}

.step-indicator {
  width: 80px;
  height: 40px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.75rem;
  transition: all 0.3s ease;
  text-align: center;
  line-height: 1.2;
}

.step-active .step-indicator {
  background: #74a8f7;
  color: white;
  box-shadow: 0 0 0 3px rgba(116, 168, 247, 0.25);
}

.step-completed .step-indicator {
  background: #6bb26b;
  color: white;
}

.step-pending .step-indicator {
  background: #e9ecef;
  color: #6c757d;
  border: 2px solid #dee2e6;
}

.step-active {
  color: #74a8f7;
}

.step-completed {
  color: #6bb26b;
}

.step-pending {
  color: #6c757d;
}

/* 메인 컨텐츠 영역 - 6:4 비율 */
.learning-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  overflow: hidden;
  min-height: 0; /* flexbox 오버플로우 활성화 */
}

/* 오른쪽: 상호작용 영역 (50%) */
.interaction-area {
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  min-height: 0; /* flexbox 오버플로우 활성화 */
}

.interaction-header {
  background: #495057;
  color: white;
  padding: 1rem;
  text-align: center;
  font-weight: 500;
  flex-shrink: 0; /* 헤더 크기 고정 */
}

.interaction-body {
  flex: 1;
  padding: 1rem;
  overflow: hidden; /* 자식 컴포넌트에서 스크롤 처리하도록 */
  min-height: 0; /* flexbox 오버플로우 활성화 */
}

/* 로딩 오버레이 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #74a8f7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 에러 오버레이 */
.error-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
}

.error-message {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 400px;
}

.error-message h3 {
  color: #dc3545;
  margin-bottom: 1rem;
}

.error-message p {
  margin-bottom: 1.5rem;
  color: #6c757d;
}

.error-message .btn {
  margin: 0 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
}

.error-message .btn-primary {
  background: #74a8f7;
  color: white;
}

.error-message .btn-secondary {
  background: #6c757d;
  color: white;
}

/* 반응형 */
@media (max-width: 768px) {
  .learning-content {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto;
  }
  
  .interaction-area {
    max-height: 300px;
  }
}
</style>