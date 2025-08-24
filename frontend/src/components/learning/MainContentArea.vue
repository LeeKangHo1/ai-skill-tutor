<!-- frontend/src/components/learning/MainContentArea.vue -->
<template>
  <div class="main-content-area">
    <div class="content-header">
      <h2 class="content-title">{{ chapterTitle }}</h2>
    </div>

    <div class="content-body">
      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>컨텐츠를 불러오는 중...</p>
      </div>

      <!-- 이론 설명 컨텐츠 -->
      <TheoryContent v-else-if="shouldShowContent('theory')" :theory-data="theoryContent"
        :is-visible="isContentVisible('theory')" />

      <!-- 퀴즈 컨텐츠 -->
      <QuizContent v-else-if="shouldShowContent('quiz')" :quiz-data="quizContent" :is-visible="isContentVisible('quiz')"
        :is-loading="isLoading" />

      <!-- 피드백 컨텐츠 -->
      <FeedbackContent v-else-if="shouldShowContent('feedback')" :feedback-data="feedbackContent" :qna-data="qnaContent"
        :should-show-qna="shouldShowContent('qna')" :is-visible="isContentVisible('feedback')" />

      <!-- QnA 컨텐츠 (이론과 함께 표시) -->
      <template v-else-if="shouldShowContent('qna')">
        <TheoryContent :theory-data="theoryContent" :is-visible="true" />
        <FeedbackContent :feedback-data="{ scoreText: '', explanation: '', nextStep: '' }" :qna-data="qnaContent"
          :should-show-qna="true" :is-visible="true" />
      </template>
    </div>

    <!-- 이전 컨텐츠 접근 버튼 -->
    <div class="content-navigation">
      <button v-if="canShowNavigationButton('theory')" class="btn btn-outline" @click="handleNavigationClick('theory')">
        📖 이론 다시 보기
      </button>
      <button v-if="canShowNavigationButton('quiz')" class="btn btn-outline" @click="handleNavigationClick('quiz')">
        📝 퀴즈 다시 보기
      </button>
      <button v-if="canShowNavigationButton('current')" class="btn btn-outline"
        @click="handleNavigationClick('current')">
        ← 돌아가기
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits, ref, onMounted, watch } from 'vue'
import { learningService } from '@/services/learningService.js'
import { mapApiResponseToComponent, safeApiCall } from '@/utils/dataMappers.js'
import { useAuthStore } from '@/stores/authStore.js'
import { useLearningStore } from '@/stores/learningStore.js'
import TheoryContent from './TheoryContent.vue'
import QuizContent from './QuizContent.vue'
import FeedbackContent from './FeedbackContent.vue'

// Props 정의
const props = defineProps({
  currentAgent: {
    type: String,
    required: true,
    default: 'theory_educator'
  },
  contentData: {
    type: Object,
    required: true,
    default: () => ({
      title: '',
      subtitle: '',
      content: '',
      type: 'theory'
    })
  },
  currentContentMode: {
    type: String,
    default: 'current' // 'current', 'review_theory', 'review_quiz'
  },
  completedSteps: {
    type: Object,
    default: () => ({ theory: true, quiz: false, feedback: false })
  }
})

// Emits 정의
const emit = defineEmits(['navigation-click', 'content-loaded', 'api-error', 'qna-response'])

// 스토어
const authStore = useAuthStore()
const learningStore = useLearningStore()

// 반응형 상태
const isLoading = ref(false)
const apiContentData = ref(null)
const lastApiCall = ref(null)

// 사용자의 현재 챕터/섹션 정보
const currentChapterNumber = computed(() => authStore.currentChapter || 1)
const currentSectionNumber = computed(() => authStore.currentSection || 1)





// 에이전트별 컨텐츠 매핑
const agentContentMap = {
  theory_educator: 'theory',
  quiz_generator: 'quiz',
  evaluation_feedback: 'feedback',
  qna_resolver: 'qna'
}

// 컴퓨티드 속성들
const chapterTitle = computed(() => `${currentChapterNumber.value}챕터 ${currentSectionNumber.value}섹션`)

// 더미 데이터 (fallback용) - 새로운 JSON 구조
const dummyTheoryContent = {
  chapter_info: "📚 1챕터 1섹션",
  title: "AI는 어떻게 우리 삶에 들어와 있을까? 🤖",
  sections: [
    {
      type: "introduction",
      content: "안녕하세요! 오늘은 인공지능(AI)가 어떻게 우리의 일상에 스며들어 있는지에 대해 이야기해보려고 해요."
    },
    {
      type: "definition",
      title: "1. AI란 무엇인가요? 🤔",
      content: "AI는 기계를 사람처럼 똑똑하게 만들어 상황에 맞게 판단하고 행동하도록 하는 기술이에요.",
      analogy: {
        concept: "AI",
        comparison: "스스로 레시피를 배우고 개발하는 요리사",
        details: ["데이터 = 식재료", "알고리즘 = 조리법"]
      }
    },
    {
      type: "examples",
      title: "2. AI가 우리 일상에 스며든 방법들 🌍",
      items: [
        {
          category: "음성 비서 📱",
          description: "헤이 시리, 안녕 빅스비로 날씨나 전화 걸기",
          benefit: "음성 인식과 자연어 처리"
        },
        {
          category: "추천 시스템 🎬",
          description: "넷플릭스, 유튜브 맞춤 추천",
          benefit: "개인 취향 분석"
        }
      ]
    }
  ]
}

const dummyQuizContent = {
  question: '퀴즈를 로드 중입니다...',
  type: 'multiple_choice',
  options: [
    '로드 중입니다...',
    '로드 중입니다...',
    '로드 중입니다...',
    '로드 중입니다...'
  ],
  hint: '잠시만 기다려주세요.'
}

const dummyFeedbackContent = {
  scoreText: '정답입니다! (100점)',
  explanation: '훌륭합니다! LLM의 핵심 특징을 정확히 이해하고 계시네요. 실시간 인터넷 검색은 LLM의 기본 기능이 아닙니다. LLM은 학습된 데이터를 바탕으로 응답을 생성합니다.',
  nextStep: '점수가 우수하므로 다음 섹션으로 진행하는 것을 권장합니다.'
}

const dummyQnaContent = {
  question: 'AI와 머신러닝의 차이가 뭐예요?',
  answer: 'AI는 더 넓은 개념으로, 인간의 지능을 모방하는 모든 기술을 포함합니다. 머신러닝은 AI의 한 분야로, 데이터를 통해 학습하는 방법론입니다. LLM은 머신러닝의 딥러닝 분야에 속하는 특화된 모델입니다.',
  relatedInfo: '3챕터에서 AI의 역사와 발전 과정을 더 자세히 다룹니다.'
}

// API 데이터와 더미 데이터
const theoryContent = computed(() => {
  if (apiContentData.value?.theory) {
    return apiContentData.value.theory
  }
  return dummyTheoryContent
})

const quizContent = computed(() => {
  if (apiContentData.value?.quiz) {
    return apiContentData.value.quiz
  }
  return dummyQuizContent
})

const feedbackContent = computed(() => {
  // Store에서 피드백 데이터를 우선적으로 사용
  if (learningStore.feedbackData && learningStore.feedbackData.scoreText) {
    console.log('🔍 MainContentArea: feedbackContent computed - store 데이터 사용:', learningStore.feedbackData)
    return learningStore.feedbackData
  }
  if (apiContentData.value?.feedback) {
    console.log('🔍 MainContentArea: feedbackContent computed - API 데이터 사용:', apiContentData.value.feedback)
    return apiContentData.value.feedback
  }
  console.log('🔍 MainContentArea: feedbackContent computed - 더미 데이터 사용:', dummyFeedbackContent)
  return dummyFeedbackContent
})

const qnaContent = computed(() => {
  if (apiContentData.value?.qna) {
    return apiContentData.value.qna
  }
  return dummyQnaContent
})

// 컨텐츠 표시/숨김 로직
const shouldShowContent = (contentType) => {
  // 현재 에이전트의 컨텐츠이거나, 리뷰 모드인 경우
  const currentContentType = agentContentMap[props.currentAgent]

  // 디버깅용 로그
  console.log(`shouldShowContent 체크: contentType=${contentType}, currentAgent=${props.currentAgent}, currentContentType=${currentContentType}, currentContentMode=${props.currentContentMode}`)

  if (props.currentContentMode === 'current') {
    const result = contentType === currentContentType
    console.log(`shouldShowContent 결과: ${contentType} === ${currentContentType} = ${result}`)
    return result
  } else if (props.currentContentMode === 'review_theory') {
    return contentType === 'theory'
  } else if (props.currentContentMode === 'review_quiz') {
    return contentType === 'quiz'
  }

  // QnA의 경우 이론도 함께 표시
  if (currentContentType === 'qna') {
    return contentType === 'qna' || contentType === 'theory'
  }

  return contentType === currentContentType
}

const isContentVisible = (contentType) => {
  return shouldShowContent(contentType)
}

// 네비게이션 버튼 표시 로직
const canShowNavigationButton = (buttonType) => {
  // store에서 직접 completedSteps 가져오기
  const completedSteps = learningStore.completedSteps

  if (buttonType === 'theory') {
    // 피드백 단계에서 이론이 완료된 경우만
    return props.currentAgent === 'evaluation_feedback' &&
      props.currentContentMode === 'current' &&
      completedSteps.theory
  }

  if (buttonType === 'quiz') {
    // 피드백 단계에서 퀴즈가 완료된 경우만
    console.log('🔍 퀴즈 다시 보기 버튼 조건 확인:', {
      currentAgent: props.currentAgent,
      currentContentMode: props.currentContentMode,
      completedStepsQuiz: completedSteps.quiz,
      shouldShow: props.currentAgent === 'evaluation_feedback' &&
        props.currentContentMode === 'current' &&
        completedSteps.quiz
    })

    return props.currentAgent === 'evaluation_feedback' &&
      props.currentContentMode === 'current' &&
      completedSteps.quiz
  }

  if (buttonType === 'current') {
    // 리뷰 모드일 때만
    return props.currentContentMode !== 'current'
  }

  return false
}

// API 호출 함수들
const loadInitialContent = async () => {
  console.log('MainContentArea: 초기 컨텐츠 로드 시작')
  isLoading.value = true

  try {
    // 학습 세션 시작 API 호출 - 사용자의 현재 챕터/섹션 사용
    const { success, data, error } = await safeApiCall(
      () => learningService.startLearningSession(
        currentChapterNumber.value,
        currentSectionNumber.value,
        "학습을 시작합니다"
      ),
      dummyTheoryContent
    )

    if (success && data) {
      // API 응답을 컴포넌트 데이터로 변환
      const mappedContent = mapApiResponseToComponent(data, 'theory')
      if (mappedContent) {
        apiContentData.value = { theory: mappedContent }
        learningStore.updateCurrentApiResponse(data)
        emit('content-loaded', { type: 'theory', data: mappedContent, source: 'api' })
        console.log('MainContentArea: API 데이터 로드 성공', mappedContent)
      } else {
        throw new Error('API 응답 매핑 실패')
      }
    } else {
      // 더미데이터 fallback
      apiContentData.value = { theory: dummyTheoryContent }
      emit('content-loaded', { type: 'theory', data: dummyTheoryContent, source: 'fallback' })
      emit('api-error', { message: error || 'API 호출 실패', fallback: true })
      console.warn('MainContentArea: 더미데이터로 fallback', error)
    }
  } catch (error) {
    // 에러 발생 시 더미데이터 사용
    apiContentData.value = { theory: dummyTheoryContent }
    emit('content-loaded', { type: 'theory', data: dummyTheoryContent, source: 'fallback' })
    emit('api-error', { message: error.message, fallback: true })
    console.error('MainContentArea: 컨텐츠 로드 에러', error)
  } finally {
    isLoading.value = false
  }
}

const loadAgentContent = async (agent) => {
  console.log(`MainContentArea: 에이전트 컨텐츠 로드 시작 - ${agent}`)

  // 이미 같은 에이전트로 API 호출한 경우 스킵
  if (lastApiCall.value === agent && apiContentData.value?.[agentContentMap[agent]]) {
    console.log(`MainContentArea: ${agent} 컨텐츠 이미 로드됨`)
    return
  }

  isLoading.value = true

  try {
    let apiResult
    let contentType = agentContentMap[agent]
    let fallbackData

    // 에이전트별 API 호출 및 fallback 데이터 설정
    switch (agent) {
      case 'theory_educator':
        apiResult = await safeApiCall(
          () => learningService.sendSessionMessage("이론 설명을 해주세요", "user"),
          dummyTheoryContent
        )
        fallbackData = dummyTheoryContent
        break

      case 'quiz_generator':
        apiResult = await safeApiCall(
          () => learningService.sendSessionMessage("퀴즈를 출제해주세요", "user"),
          dummyQuizContent
        )
        fallbackData = dummyQuizContent
        break

      case 'evaluation_feedback':
        apiResult = await safeApiCall(
          () => learningService.sendSessionMessage("평가 결과를 알려주세요", "user"),
          dummyFeedbackContent
        )
        fallbackData = dummyFeedbackContent
        break

      case 'qna_resolver':
        apiResult = await safeApiCall(
          () => learningService.sendSessionMessage("질문에 답변해주세요", "user"),
          dummyQnaContent
        )
        fallbackData = dummyQnaContent
        break

      default:
        console.warn(`MainContentArea: 알 수 없는 에이전트 - ${agent}`)
        return
    }

    if (apiResult.success && apiResult.data) {
      // API 응답을 컴포넌트 데이터로 변환
      const mappedContent = mapApiResponseToComponent(apiResult.data, contentType)
      if (mappedContent) {
        if (!apiContentData.value) apiContentData.value = {}
        apiContentData.value[contentType] = mappedContent
        learningStore.updateCurrentApiResponse(apiResult.data)
        emit('content-loaded', { type: contentType, data: mappedContent, source: 'api' })
        lastApiCall.value = agent
        console.log(`MainContentArea: ${agent} API 데이터 로드 성공`, mappedContent)
        
        // QnA 응답인 경우 채팅 히스토리에 추가하기 위해 이벤트 전달
        if (agent === 'qna_resolver' && mappedContent.answer) {
          console.log('🔄 MainContentArea에서 QnA 응답 감지 - 채팅 이벤트 전달')
          emit('qna-response', {
            message: mappedContent.answer,
            type: 'qna',
            timestamp: new Date()
          })
        }
      } else {
        throw new Error('API 응답 매핑 실패')
      }
    } else {
      // 더미데이터 fallback
      if (!apiContentData.value) apiContentData.value = {}
      apiContentData.value[contentType] = fallbackData
      emit('content-loaded', { type: contentType, data: fallbackData, source: 'fallback' })
      emit('api-error', { message: apiResult.error || 'API 호출 실패', fallback: true })
      console.warn(`MainContentArea: ${agent} 더미데이터로 fallback`, apiResult.error)
    }
  } catch (error) {
    // 에러 발생 시 더미데이터 사용
    const contentType = agentContentMap[agent]
    const fallbackData = {
      theory: dummyTheoryContent,
      quiz: dummyQuizContent,
      feedback: dummyFeedbackContent,
      qna: dummyQnaContent
    }[contentType]

    if (!apiContentData.value) apiContentData.value = {}
    apiContentData.value[contentType] = fallbackData
    emit('content-loaded', { type: contentType, data: fallbackData, source: 'fallback' })
    emit('api-error', { message: error.message, fallback: true })
    console.error(`MainContentArea: ${agent} 컨텐츠 로드 에러`, error)
  } finally {
    isLoading.value = false
  }
}

// 라이프사이클 훅
onMounted(() => {
  console.log('MainContentArea: 컴포넌트 마운트됨')
  loadInitialContent()
})

// 에이전트 변경 감지 (quiz_generator와 evaluation_feedback은 별도 처리)
watch(() => props.currentAgent, (newAgent, oldAgent) => {
  if (newAgent !== oldAgent) {
    console.log(`MainContentArea: 에이전트 변경 감지 - ${oldAgent} → ${newAgent}`)

    // quiz_generator는 UI에 직접적인 영향을 주지 않으므로 API 호출하지 않음
    if (newAgent === 'quiz_generator') {
      console.log('MainContentArea: quiz_generator는 UI 업데이트 스킵')
      return
    }

    // qna_resolver는 채팅에서만 처리되므로 MainContentArea에서는 API 호출하지 않음
    if (newAgent === 'qna_resolver') {
      console.log('MainContentArea: qna_resolver는 채팅 전용 - API 호출 스킵')
      // 이론 컨텐츠를 유지하기 위해 아무것도 하지 않음
      return
    }

    // evaluation_feedback은 이미 store에 피드백 데이터가 있으므로 별도 API 호출하지 않음
    if (newAgent === 'evaluation_feedback') {
      console.log('MainContentArea: evaluation_feedback - store 피드백 데이터 사용')
      // 피드백 데이터가 store에 있는지 확인
      if (learningStore.feedbackData && learningStore.feedbackData.scoreText) {
        console.log('MainContentArea: evaluation_feedback API 데이터 로드 성공', learningStore.feedbackData)
        emit('content-loaded', { type: 'feedback', data: learningStore.feedbackData, source: 'store' })
      } else {
        console.log('MainContentArea: evaluation_feedback - store에 피드백 데이터 없음, API 호출')
        loadAgentContent(newAgent)
      }
      return
    }

    loadAgentContent(newAgent)
  }
}, { immediate: false })

// 이벤트 핸들러
const handleNavigationClick = (navigationType) => {
  emit('navigation-click', navigationType)
}

// 피드백 데이터 변화 감지
watch(() => learningStore.feedbackData, (newFeedbackData) => {
  if (newFeedbackData && newFeedbackData.scoreText) {
    console.log('🔍 MainContentArea: 피드백 데이터 변화 감지:', newFeedbackData)
    console.log('🔍 MainContentArea: 현재 에이전트:', props.currentAgent)
    console.log('🔍 MainContentArea: shouldShowContent(feedback):', shouldShowContent('feedback'))
  }
}, { deep: true })
</script>

<style scoped>
.main-content-area {
  background: white;
  padding: 2rem;
  overflow-y: auto;
  border-right: 1px solid #dee2e6;
  height: 100%;
}

.content-header {
  margin-bottom: 1.5rem;
}

.content-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}



.content-body {
  min-height: 400px;
}

/* 로딩 상태 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #6c757d;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #74a8f7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 컨테이너 스타일만 유지 */

/* 이전 컨텐츠 접근 버튼 */
.content-navigation {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-outline {
  background: white;
  color: #6c757d;
  border: 1px solid #6c757d;
}

.btn-outline:hover {
  background: #f8f9fa;
  border-color: #495057;
  color: #495057;
  transform: translateY(-1px);
}



/* 데스크톱 전용 - 모바일/태블릿 대응 제거 */
</style>