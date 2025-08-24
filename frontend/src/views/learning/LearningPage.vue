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



    <!-- 메인 컨텐츠 영역 -->
    <div class="learning-content">
      <!-- 왼쪽: 메인 컨텐츠 (50%) -->
      <MainContentArea :current-agent="currentAgent" :content-data="contentData"
        :current-content-mode="currentContentMode" @navigation-click="handleNavigationClick"
        @content-loaded="handleContentLoaded" @api-error="handleApiError" />

      <!-- 오른쪽: 상호작용 영역 (50%) -->
      <div class="interaction-area">
        <div class="interaction-header">
          {{ uiMode === 'chat' ? '💬 채팅' : '📝 퀴즈' }}
        </div>

        <div class="interaction-body">
          <!-- 채팅 모드 -->
          <ChatInteraction v-if="uiMode === 'chat'" :chat-history="chatHistory" :is-loading="isLoading"
            @send-message="handleSendMessage" />

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

// 세션 정보
const currentChapter = computed(() => learningStore.sessionInfo?.chapter_number || 2)
const currentSection = computed(() => learningStore.sessionInfo?.section_number || 1)
const sectionTitle = computed(() => learningStore.sessionInfo?.section_title || 'LLM이란 무엇인가')



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

    // 백엔드 API 호출 시뮬레이션
    await simulateAPICall(message)

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

const handleSubmitAnswer = async (answer) => {
  try {
    isLoading.value = true
    loadingMessage.value = '새로운 평가를 진행하고 있습니다...'

    // 답변 제출 시 기존 데이터 초기화
    learningStore.clearQuizData()

    // 백엔드 API 호출 시뮬레이션 (매번 새로운 평가)
    await simulateQuizSubmission()

  } catch (error) {
    console.error('퀴즈 제출 오류:', error)
  } finally {
    isLoading.value = false
  }
}

const handleRequestHint = () => {
  chatHistory.value.push({
    sender: '튜터',
    message: '힌트: LLM의 "L"이 무엇을 의미하는지 생각해보세요.',
    type: 'system',
    timestamp: new Date()
  })
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

  // 캐시 없이 매번 새로운 데이터로 UI 업데이트
  if (type === 'quiz' && data) {
    learningStore.updateUIMode('quiz')
    // 기존 퀴즈 데이터 완전 초기화 후 새 데이터 설정
    learningStore.clearQuizData()
    updateQuizData(data)
  } else if (type === 'theory') {
    learningStore.updateUIMode('chat')
    // 기존 컨텐츠 데이터 초기화
    contentData.value = { title: '', subtitle: '', content: '', type: 'theory' }
  } else if (type === 'feedback') {
    learningStore.updateUIMode('chat')
    // 기존 컨텐츠 데이터 초기화
    contentData.value = { title: '', subtitle: '', content: '', type: 'feedback' }
  }
}

const handleApiError = (errorData) => {
  const { message, fallback } = errorData
  console.warn(`API 오류: ${message} ${fallback ? '(더미데이터 사용)' : ''}`)

  // 에러 발생 시 모든 데이터 초기화 후 새로 로드
  if (fallback) {
    // 캐시된 데이터 사용하지 않고 새로운 더미데이터 생성
    learningStore.clearQuizData()
    updateQuizData()
  }
}

const goToDashboard = () => {
  router.push('/dashboard')
}

// 유틸리티 함수들
const simulateAPICall = async (message) => {
  if (message.includes('다음') || message.includes('퀴즈')) {
    // 1. 모든 기존 데이터 초기화 후 퀴즈 모드로 전환
    learningStore.clearAllData()
    learningStore.updateAgent('quiz_generator')
    learningStore.updateUIMode('quiz')

    // 2. 컨텐츠 데이터 완전 초기화
    contentData.value = { title: '', subtitle: '', content: '', type: 'quiz' }

    chatHistory.value.push({
      sender: '튜터',
      message: '새로운 퀴즈를 생성하고 있습니다. 잠시만 기다려주세요...',
      type: 'system',
      timestamp: new Date()
    })

    // 3. API 호출 시뮬레이션 (매번 새로운 데이터 생성)
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 4. 매번 새로운 API 응답 생성 (캐시 사용하지 않음)
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
      message: "새로운 퀴즈가 준비되었습니다."
    }

    // 5. 새로운 퀴즈 데이터를 store에 저장 (기존 데이터 완전 대체)
    learningStore.setQuizDataFromAPI(mockApiResponse.data)

    chatHistory.value.push({
      sender: '튜터',
      message: '새로운 퀴즈를 준비했습니다. 오른쪽에서 답변해주세요.',
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

  // 퀴즈 제출 시 기존 데이터 모두 초기화 후 새로운 피드백 생성
  learningStore.clearAllData()
  learningStore.updateAgent('evaluation_feedback')
  learningStore.updateUIMode('chat')

  // 컨텐츠 데이터 완전 초기화 후 새로운 피드백 데이터 설정
  contentData.value = { title: '', subtitle: '', content: '', type: 'feedback' }
  updateContentData('feedback')

  chatHistory.value.push({
    sender: '튜터',
    message: '정답입니다! 새로운 피드백을 확인해주세요.',
    type: 'system',
    timestamp: new Date()
  })
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
  // 기존 퀴즈 데이터 완전 초기화
  learningStore.clearQuizData()

  if (apiQuizData) {
    // 새로운 API 응답 데이터를 store에 저장 (캐시 사용하지 않음)
    learningStore.updateQuizData({
      question: apiQuizData.question || '',
      options: apiQuizData.options || [],
      type: apiQuizData.type || 'multiple_choice',
      hint: apiQuizData.hint || ''
    })
  } else {
    // 매번 새로운 로딩 상태 데이터 생성
    learningStore.updateQuizData({
      question: '새로운 퀴즈를 로드 중입니다...',
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

// 라이프사이클 훅 - 캐시 없이 매번 새로운 세션 시작
onMounted(async () => {
  try {
    isLoading.value = true
    loadingMessage.value = '새로운 학습 세션을 시작하고 있습니다...'

    // 모든 기존 데이터 완전 초기화
    learningStore.clearAllData()
    contentData.value = { title: '', subtitle: '', content: '', type: 'theory' }
    chatHistory.value = []

    // 새로운 초기 컨텐츠 설정
    updateContentData('theory')

    // 새로운 세션 시작 (실제로는 API 호출)
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 새로운 초기 상태 설정
    learningStore.updateAgent('theory_educator')
    learningStore.updateUIMode('chat')

    // 새로운 세션 시작 메시지 추가
    chatHistory.value.push({
      sender: '튜터',
      message: 'LLM에 대해 새로운 학습을 시작합니다. 왼쪽 내용을 확인해주세요!',
      type: 'system',
      timestamp: new Date()
    })

  } catch (error) {
    console.error('세션 초기화 오류:', error)
  } finally {
    isLoading.value = false
  }
})

// 감시자 - 상태 변경 시 캐시 초기화
watch(currentAgent, (newAgent) => {
  console.log('에이전트 변경:', newAgent)
  // 에이전트 변경 시 관련 캐시 데이터 초기화
  if (newAgent === 'quiz_generator') {
    learningStore.clearQuizData()
  }
})

watch(uiMode, (newMode) => {
  console.log('UI 모드 변경:', newMode)
  // UI 모드 변경 시 이전 모드의 데이터 초기화
  if (newMode === 'quiz') {
    chatHistory.value = []
  } else if (newMode === 'chat') {
    learningStore.clearQuizData()
  }
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