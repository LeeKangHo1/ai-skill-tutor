<!-- frontend/src/views/learning/LearningPage.vue -->
<template>
  <div class="learning-page">
    <!-- 헤더 영역 -->
    <div class="learning-header">
      <div class="header-left">
        <div class="logo">🤖 AI 활용법 학습 튜터</div>
      </div>
      <div class="header-right">
        <button class="btn btn-secondary" @click="goToDashboard">
          대시보드로
        </button>
      </div>
    </div>



    <!-- 메인 컨텐츠 영역 -->
    <div class="learning-content">
      <!-- 왼쪽: 메인 컨텐츠 (50%) -->
      <MainContentArea :current-agent="currentAgent" :content-data="contentData"
        :current-content-mode="currentContentMode" :completed-steps="learningStore.completedSteps"
        @navigation-click="handleNavigationClick" @content-loaded="handleContentLoaded" @api-error="handleApiError" />

      <!-- 오른쪽: 상호작용 영역 (50%) -->
      <div class="interaction-area">
        <div class="interaction-header">
          {{ uiMode === 'chat' ? '💬 채팅' : '📝 퀴즈' }}
        </div>

        <div class="interaction-body">
          <!-- 채팅 모드 -->
          <ChatInteraction v-if="uiMode === 'chat'" :chat-history="chatHistory" :is-loading="isLoading"
            @send-message="handleSendMessage" @session-complete="handleSessionComplete" />

          <!-- 퀴즈 모드 -->
          <QuizInteraction v-else-if="uiMode === 'quiz'" :quiz-data="quizData" :is-loading="isLoading"
            @submit-answer="handleSubmitAnswer" @request-hint="handleRequestHint" />
        </div>
      </div>
    </div>

    <!-- 로딩 모달 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useLearningStore } from '@/stores/learningStore'
import { learningService } from '@/services/learningService'
import MainContentArea from '@/components/learning/MainContentArea.vue'
import ChatInteraction from '@/components/learning/ChatInteraction.vue'
import QuizInteraction from '@/components/learning/QuizInteraction.vue'

// 라우터 및 스토어
const router = useRouter()
const learningStore = useLearningStore()

// 반응형 상태
const isLoading = ref(false)
const loadingMessage = ref('학습 내용을 준비하고 있습니다...')

// 컴포넌트별 데이터 - 캐시 없이 매번 새로 로드
const contentData = ref({
  title: '',
  subtitle: '',
  content: '',
  type: 'theory'
})

// 퀴즈 데이터는 store에서 가져오기 - 캐시 없이 실시간 데이터만 사용
const quizData = computed(() => learningStore.quizData)

// 채팅 히스토리 - 세션별로 새로 시작, 이전 대화 저장하지 않음
const chatHistory = ref([])

// 컴퓨티드 속성들
const currentAgent = computed(() => learningStore.currentAgent)
const uiMode = computed(() => learningStore.currentUIMode)
const currentContentMode = computed(() => learningStore.currentContentMode || 'current')





// 이벤트 핸들러들
const handleSendMessage = async (message) => {
  try {
    isLoading.value = true
    loadingMessage.value = '메시지를 처리하고 있습니다...'

    // 사용자 메시지를 채팅 히스토리에 추가
    chatHistory.value.push({
      sender: '나',
      message: message,
      type: 'user',
      timestamp: new Date()
    })

    // 실제 백엔드 API 호출
    await sendMessageToAPI(message)

  } catch (error) {
    console.error('메시지 전송 오류:', error)
    chatHistory.value.push({
      sender: '시스템',
      message: '오류가 발생했습니다. 다시 시도해주세요.',
      type: 'system',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
  }
}

const handleSubmitAnswer = async (submitData) => {
  try {
    isLoading.value = true
    loadingMessage.value = '평가를 진행하고 있습니다...'

    console.log('퀴즈 답안 제출 처리:', submitData)

    // API 결과가 있으면 처리, 없으면 시뮬레이션
    if (submitData.apiResult) {
      // 실제 API 응답 처리
      const { apiResult } = submitData
      
      // 피드백 데이터를 store에 저장 (채팅에 추가하지 않음)
      console.log('🔍 API 결과 상세 분석:', {
        apiResult: apiResult,
        feedback: apiResult.feedback,
        explanation: apiResult.explanation,
        nextStep: apiResult.nextStep
      })
      
      learningStore.updateFeedbackData({
        scoreText: apiResult.feedback,
        explanation: apiResult.explanation,
        nextStep: apiResult.nextStep || '다음 단계로 진행하세요.'
      })

      // UI 모드를 채팅 모드로 전환 (피드백 표시를 위해)
      learningStore.updateUIMode('chat')
      
      // 에이전트를 evaluation_feedback으로 변경
      console.log('🔄 퀴즈 제출 후 에이전트를 evaluation_feedback으로 변경')
      learningStore.updateAgent('evaluation_feedback')
      
      console.log('🔍 현재 상태 확인:', {
        currentAgent: learningStore.currentAgent,
        currentUIMode: learningStore.currentUIMode,
        feedbackData: learningStore.feedbackData
      })
      
    } else {
      // 백엔드 API 호출 시뮬레이션 (fallback)
      await simulateQuizSubmission()
    }

  } catch (error) {
    console.error('퀴즈 제출 오류:', error)
  } finally {
    isLoading.value = false
  }
}

const handleRequestHint = (hintData) => {
  // 힌트 요청 처리 - 하드코딩된 메시지 제거
  console.log('힌트 요청:', hintData)
  // 필요시 여기에 힌트 관련 로직 추가
}

const handleNavigationClick = (navigationType) => {
  // 네비게이션 버튼 클릭 처리
  if (navigationType === 'theory') {
    updateContentMode('review_theory')
  } else if (navigationType === 'quiz') {
    updateContentMode('review_quiz')
  } else if (navigationType === 'current') {
    updateContentMode('current')
  }
}

const handleContentLoaded = (eventData) => {
  const { type, data } = eventData

  // 자연스러운 데이터 전환 (초기화 최소화)
  if (type === 'quiz' && data) {
    learningStore.updateUIMode('quiz')
    // 새 데이터로 업데이트 (기존 데이터 초기화하지 않음)
    updateQuizData(data)
  } else if (type === 'theory') {
    learningStore.updateUIMode('chat')
    // 컨텐츠 타입만 업데이트
    contentData.value.type = 'theory'
  } else if (type === 'feedback') {
    learningStore.updateUIMode('chat')
    // 컨텐츠 타입만 업데이트
    contentData.value.type = 'feedback'
  }
}

const handleApiError = (errorData) => {
  const { message, fallback } = errorData
  console.warn(`API 오류: ${message} ${fallback ? '(더미데이터 사용)' : ''}`)

  // 에러 발생 시 fallback 데이터 사용 (초기화하지 않음)
  if (fallback) {
    // 더미데이터로 업데이트 (기존 데이터 유지)
    updateQuizData()
  }
}

const goToDashboard = () => {
  router.push('/dashboard')
}

// 세션 완료 처리 (새로운 학습 세션 시작)
const handleSessionComplete = (sessionData) => {
  console.log('새로운 학습 세션 시작:', sessionData)
  
  // 모든 상태 초기화
  learningStore.initializeNewSession()
  contentData.value = { title: '', subtitle: '', content: '', type: 'theory' }
  chatHistory.value = []
  
  // 초기 컨텐츠 설정
  updateContentData('theory')
  
  // 초기 상태 설정
  learningStore.updateAgent('theory_educator')
  learningStore.updateUIMode('chat')
  
  // 새 세션 시작 메시지 추가
  chatHistory.value.push({
    sender: '튜터',
    message: '새로운 학습 세션을 시작합니다. 왼쪽 내용을 확인해주세요!',
    type: 'system',
    timestamp: new Date()
  })
}

// 실제 API 호출 함수 - Store 중심 구조
const sendMessageToAPI = async (message) => {
  try {
    // v2.0 API 사용: POST /learning/session/message
    const result = await learningService.sendSessionMessage(message, 'user')
    
    if (result.success && result.data) {
      const apiResponse = result.data
      console.log('API 응답 수신:', apiResponse)
      
      // 1. API 응답을 store에 저장 (가장 먼저)
      learningStore.updateCurrentApiResponse(apiResponse)
      
      // 2. API 응답 구조 확인 및 처리
      console.log('📦 전체 API 응답 구조:', apiResponse)
      
      // data.workflow_response 구조 확인
      if (apiResponse.data?.workflow_response) {
        const workflowResponse = apiResponse.data.workflow_response
        console.log('🔄 워크플로우 응답 (data.workflow_response):', workflowResponse)
        
        // Store에 워크플로우 응답 저장
        learningStore.updateWorkflowResponse(workflowResponse)
        
        // 퀴즈 데이터 확인 및 저장
        const content = workflowResponse.content
        console.log('📋 컨텐츠 확인:', content)
        
        if (content) {
          console.log('🔍 컨텐츠 속성 상세:', {
            quiz_type: content.quiz_type,
            question: content.question,
            options: content.options,
            current_agent: workflowResponse.current_agent,
            hasOptions: Array.isArray(content.options),
            optionsLength: content.options?.length
          })
          
          // 퀴즈 데이터 조건 확인 - 더 관대한 조건으로 설정
          if (workflowResponse.current_agent === 'quiz_generator' || 
              content.quiz_type || 
              content.question || 
              (content.options && content.options.length > 0)) {
            console.log('🎯 퀴즈 데이터 조건 만족 - setQuizDataFromAPI 호출')
            
            // API 응답을 올바른 구조로 전달
            const formattedResponse = {
              workflow_response: workflowResponse
            }
            learningStore.setQuizDataFromAPI(formattedResponse)
          } else {
            console.log('❌ 퀴즈 데이터 조건 불만족')
          }
        }
        
        // 채팅 메시지 처리 (퀴즈 생성 시에는 채팅에 추가하지 않음)
        if (content && content.refined_content && workflowResponse.current_agent !== 'quiz_generator') {
          chatHistory.value.push({
            sender: '튜터',
            message: content.refined_content,
            type: 'system',
            timestamp: new Date()
          })
        }
      }
      // 직접 workflow_response가 있는 경우 (이전 구조)
      else if (apiResponse.workflow_response) {
        console.log('🔄 워크플로우 응답 (직접):', apiResponse.workflow_response)
        learningStore.updateWorkflowResponse(apiResponse.workflow_response)
        
        const content = apiResponse.workflow_response.content
        if (content && (content.quiz_type || content.question || content.options)) {
          console.log('🎯 직접 구조에서 퀴즈 데이터 발견')
          learningStore.setQuizDataFromAPI(apiResponse)
        }
        
        // 채팅 메시지 처리 (퀴즈 생성 시에는 채팅에 추가하지 않음)
        if (content && content.refined_content && apiResponse.workflow_response.current_agent !== 'quiz_generator') {
          chatHistory.value.push({
            sender: '튜터',
            message: content.refined_content,
            type: 'system',
            timestamp: new Date()
          })
        }
      } else {
        console.log('⚠️ workflow_response를 찾을 수 없습니다:', apiResponse)
        
        // API 응답에 직접 메시지가 있는 경우
        if (apiResponse.message) {
          chatHistory.value.push({
            sender: '튜터',
            message: apiResponse.message,
            type: 'system',
            timestamp: new Date()
          })
        }
      }
      
    } else {
      // API 호출 실패 시 fallback
      console.warn('API 호출 실패, 시뮬레이션으로 대체:', result.error)
      await simulateAPICall(message)
    }
    
  } catch (error) {
    console.error('API 호출 중 오류 발생:', error)
    // 오류 발생 시 시뮬레이션으로 fallback
    await simulateAPICall(message)
  }
}

// 유틸리티 함수들 (fallback용)
const simulateAPICall = async (message) => {
  if (message.includes('다음') || message.includes('퀴즈')) {
    // 퀴즈 모드로 전환
    learningStore.updateAgent('quiz_generator')
    learningStore.updateUIMode('quiz')

    chatHistory.value.push({
      sender: '튜터',
      message: '퀴즈를 생성하고 있습니다. 잠시만 기다려주세요...',
      type: 'system',
      timestamp: new Date()
    })

    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 2000))

    // API 응답 생성
    const mockApiResponse = {
      success: true,
      data: {
        workflow_response: {
          current_agent: "quiz_generator",
          session_progress_stage: "theory_completed",
          ui_mode: "quiz",
          content: {
            type: "quiz",
            quiz_type: "multiple_choice",
            question: "다음 중 LLM의 특징이 아닌 것은?",
            options: [
              "대규모 데이터 학습",
              "실시간 인터넷 검색",
              "언어 이해 능력",
              "텍스트 생성 능력"
            ],
            hint: "LLM의 'L'이 무엇을 의미하는지 생각해보세요."
          }
        }
      },
      message: "퀴즈가 준비되었습니다."
    }

    // 퀴즈 데이터를 store에 저장
    learningStore.setQuizDataFromAPI(mockApiResponse.data)

    chatHistory.value.push({
      sender: '튜터',
      message: '퀴즈를 준비했습니다. 오른쪽에서 답변해주세요.',
      type: 'system',
      timestamp: new Date()
    })
  } else {
    await new Promise(resolve => setTimeout(resolve, 500))

    chatHistory.value.push({
      sender: '튜터',
      message: '무엇을 도와드릴까요? "다음으로 넘어가주세요" 또는 질문을 해주세요.',
      type: 'system',
      timestamp: new Date()
    })
  }
}

const simulateQuizSubmission = async () => {
  await new Promise(resolve => setTimeout(resolve, 1500))

  // 피드백 모드로 전환
  learningStore.updateAgent('evaluation_feedback')
  learningStore.updateUIMode('chat')

  // 피드백 데이터를 store에 저장 (채팅에 추가하지 않음)
  learningStore.updateFeedbackData({
    scoreText: '정답입니다! (100점)',
    explanation: '훌륭합니다! 정확한 답변을 선택하셨습니다.',
    nextStep: '다음 단계로 진행하세요.'
  })

  // 피드백 컨텐츠 설정
  updateContentData('feedback')
}

const updateContentData = (type) => {
  switch (type) {
    case 'theory':
      contentData.value = {
        title: '🧠 LLM(Large Language Model)이란?',
        subtitle: '',
        content: 'LLM은 대규모 언어 모델로, 방대한 텍스트 데이터를 학습하여 인간과 유사한 언어 이해와 생성 능력을 가진 AI 모델입니다.',
        type: 'theory'
      }
      break
    case 'quiz':
      contentData.value = {
        title: '📝 퀴즈 문제',
        subtitle: '',
        content: '다음 중 LLM의 특징이 아닌 것은?',
        type: 'quiz'
      }
      break
    case 'feedback':
      contentData.value = {
        title: '✅ 평가 결과',
        subtitle: '',
        content: '정답입니다! (100점)',
        type: 'feedback'
      }
      break

  }
}

const updateQuizData = (apiQuizData = null) => {
  if (apiQuizData) {
    // API 응답 데이터를 store에 저장
    learningStore.updateQuizData({
      question: apiQuizData.question || '',
      options: apiQuizData.options || [],
      type: apiQuizData.type || 'multiple_choice',
      hint: apiQuizData.hint || ''
    })
  } else {
    // 로딩 상태 데이터
    learningStore.updateQuizData({
      question: '퀴즈를 로드 중입니다...',
      options: [
        '로드 중입니다...',
        '로드 중입니다...',
        '로드 중입니다...',
        '로드 중입니다...'
      ],
      type: 'multiple_choice',
      hint: '잠시만 기다려주세요.'
    })
  }
}

const updateContentMode = (mode) => {
  learningStore.updateContentMode(mode)
}

// 라이프사이클 훅 - 학습 세션 시작 (POST /learning/session/start 호출)
onMounted(async () => {
  try {
    isLoading.value = true
    loadingMessage.value = '학습 세션을 시작하고 있습니다...'

    // 새로운 세션 시작 시에만 초기화 (POST /learning/session/start)
    learningStore.initializeNewSession()
    contentData.value = { title: '', subtitle: '', content: '', type: 'theory' }
    chatHistory.value = []

    // 초기 컨텐츠 설정
    updateContentData('theory')

    // 세션 시작 API 호출 시뮬레이션 (실제로는 POST /learning/session/start)
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 초기 상태 설정
    learningStore.updateAgent('theory_educator')
    learningStore.updateUIMode('chat')

    // 세션 시작 메시지 추가
    chatHistory.value.push({
      sender: '튜터',
      message: '학습을 시작합니다. 왼쪽 내용을 확인해주세요!',
      type: 'system',
      timestamp: new Date()
    })

  } catch (error) {
    console.error('세션 초기화 오류:', error)
  } finally {
    isLoading.value = false
  }
})

// 감시자 - Store 상태 변화 감지하여 UI 자동 업데이트
watch(currentAgent, (newAgent, oldAgent) => {
  console.log(`🔄 에이전트 변경 감지: ${oldAgent} → ${newAgent}`)
  
  // 에이전트별 컨텐츠 데이터 업데이트
  if (newAgent === 'quiz_generator') {
    updateContentData('quiz')
  } else if (newAgent === 'evaluation_feedback') {
    updateContentData('feedback')
  } else if (newAgent === 'theory_educator') {
    updateContentData('theory')
  }
})

watch(uiMode, (newMode, oldMode) => {
  console.log(`🔄 UI 모드 변경 감지: ${oldMode} → ${newMode}`)
  
  // UI 모드 변경 시 추가 처리
  if (newMode === 'quiz') {
    console.log('퀴즈 모드로 전환됨 - 퀴즈 데이터 확인:', learningStore.quizData)
  } else if (newMode === 'chat') {
    console.log('채팅 모드로 전환됨')
  }
})

// 퀴즈 데이터 변화 감지
watch(() => learningStore.quizData, (newQuizData, oldQuizData) => {
  if (newQuizData && newQuizData.question && newQuizData.question !== oldQuizData?.question) {
    console.log('🔄 퀴즈 데이터 변경 감지:', newQuizData)
    
    // 퀴즈 데이터가 업데이트되면 자동으로 퀴즈 모드로 전환
    if (learningStore.currentUIMode !== 'quiz') {
      console.log('퀴즈 데이터 감지로 인한 UI 모드 자동 전환')
      learningStore.updateUIMode('quiz')
    }
  }
}, { deep: true })
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





/* 메인 컨텐츠 영역 - 6:4 비율 */
.learning-content {
  flex: 1;
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 0;
  overflow: hidden;
  min-height: 0;
  /* flexbox 오버플로우 활성화 */
}

/* 오른쪽: 상호작용 영역 (50%) */
.interaction-area {
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  min-height: 0;
  /* flexbox 오버플로우 활성화 */
}

.interaction-header {
  background: #495057;
  color: white;
  padding: 1rem;
  text-align: center;
  font-weight: 500;
  flex-shrink: 0;
  /* 헤더 크기 고정 */
}

.interaction-body {
  flex: 1;
  padding: 1rem;
  overflow: hidden;
  /* 자식 컴포넌트에서 스크롤 처리하도록 */
  min-height: 0;
  /* flexbox 오버플로우 활성화 */
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
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 데스크톱 전용 - 모바일/태블릿 대응 제거 */
</style>