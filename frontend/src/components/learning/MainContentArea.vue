<!-- frontend/src/components/learning/MainContentArea.vue -->
<template>
  <div class="main-content-area">
    <div class="content-header">
      <h2 class="content-title">{{ chapterTitle }}</h2>
      <p class="content-subtitle">{{ sectionTitle }}</p>
    </div>

    <div class="content-body">
      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>컨텐츠를 불러오는 중...</p>
      </div>

      <!-- 이론 설명 컨텐츠 -->
      <div 
        v-else-if="shouldShowContent('theory')"
        class="theory-content content-active"
        :class="{ 'content-hidden': !isContentVisible('theory') }"
      >
        <h3>🧠 {{ theoryContent.title || 'LLM(Large Language Model)이란?' }}</h3>
        <div class="theory-body">
          <!-- API 응답 텍스트를 그대로 표시 (포맷팅 유지) -->
          <div class="theory-description" v-html="formatText(theoryContent.description)"></div>
          
          <!-- 핵심 포인트가 별도로 있는 경우만 표시 -->
          <div v-if="theoryContent.keyPoints && theoryContent.keyPoints.length > 0 && !isKeyPointsInDescription" class="key-points">
            <p><strong>💡 핵심 포인트:</strong></p>
            <ul>
              <li v-for="point in theoryContent.keyPoints" :key="point">{{ point }}</li>
            </ul>
          </div>
          
          <!-- 예시가 별도로 있는 경우만 표시 -->
          <div v-if="theoryContent.examples && theoryContent.examples.length > 0 && !isExamplesInDescription" class="examples">
            <p><strong>📋 대표 예시:</strong></p>
            <ul>
              <li v-for="example in theoryContent.examples" :key="example">{{ example }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 퀴즈 컨텐츠 -->
      <div 
        v-else-if="shouldShowContent('quiz')"
        class="quiz-content"
        :class="{ 'content-active': isContentVisible('quiz'), 'content-hidden': !isContentVisible('quiz') }"
      >
        <h3>📝 퀴즈 문제</h3>
        <div class="quiz-question-display">
          <p><strong>{{ quizContent.question }}</strong></p>
          <div class="quiz-description">
            <p>💡 오른쪽 상호작용 영역에서 답변을 선택해주세요.</p>
            <p>⚠️ 답변을 제출하기 전까지는 다른 내용을 볼 수 없습니다.</p>
          </div>
        </div>
      </div>

      <!-- 피드백 컨텐츠 -->
      <div 
        v-else-if="shouldShowContent('feedback')"
        class="feedback-content"
        :class="{ 'content-active': isContentVisible('feedback'), 'content-hidden': !isContentVisible('feedback') }"
      >
        <h3>✅ 평가 결과</h3>
        <div class="feedback-score">
          <p><strong>{{ feedbackContent.scoreText }}</strong></p>
        </div>
        <div class="feedback-explanation">
          <p><strong>📝 상세 피드백:</strong></p>
          <p>{{ feedbackContent.explanation }}</p>
        </div>
        <div class="feedback-next-steps">
          <p><strong>🎯 다음 단계 결정:</strong></p>
          <p>{{ feedbackContent.nextStep }}</p>
        </div>
      </div>

      <!-- QnA 컨텐츠 (이론 유지하면서 질답 추가) -->
      <div 
        v-else-if="shouldShowContent('qna')"
        class="qna-content"
        :class="{ 'content-active': isContentVisible('qna'), 'content-hidden': !isContentVisible('qna') }"
      >
        <h4>❓ 질문 답변</h4>
        <div class="qna-item">
          <p><strong>질문:</strong> {{ qnaContent.question }}</p>
          <p><strong>답변:</strong> {{ qnaContent.answer }}</p>
        </div>
        <div v-if="qnaContent.relatedInfo" class="qna-related">
          <p><strong>🔗 관련 학습:</strong></p>
          <p>{{ qnaContent.relatedInfo }}</p>
        </div>
      </div>
    </div>

    <!-- 이전 컨텐츠 접근 버튼 -->
    <div class="content-navigation">
      <button 
        v-if="canShowNavigationButton('theory')"
        class="btn btn-outline"
        @click="handleNavigationClick('theory')"
      >
        📖 이론 다시 보기
      </button>
      <button 
        v-if="canShowNavigationButton('quiz')"
        class="btn btn-outline"
        @click="handleNavigationClick('quiz')"
      >
        📝 퀴즈 다시 보기
      </button>
      <button 
        v-if="canShowNavigationButton('current')"
        class="btn btn-outline"
        @click="handleNavigationClick('current')"
      >
        ← 현재 단계로
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
const emit = defineEmits(['navigation-click', 'content-loaded', 'api-error'])

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

// 텍스트 포맷팅 함수
const formatText = (text) => {
  if (!text) return ''
  
  return text
    .replace(/\n\n/g, '<br><br>') // 이중 줄바꿈을 <br><br>로
    .replace(/\n/g, '<br>') // 단일 줄바꿈을 <br>로
    .replace(/### /g, '<h4>') // ### 헤더 처리
    .replace(/\n/g, '</h4>') // 헤더 닫기 (간단한 처리)
}

// 핵심 포인트가 이미 description에 포함되어 있는지 확인
const isKeyPointsInDescription = computed(() => {
  return theoryContent.value.description?.includes('💡 핵심 포인트') || 
         theoryContent.value.description?.includes('핵심 포인트')
})

// 예시가 이미 description에 포함되어 있는지 확인
const isExamplesInDescription = computed(() => {
  return theoryContent.value.description?.includes('📋 대표 예시') || 
         theoryContent.value.description?.includes('대표 예시')
})

// 에이전트별 컨텐츠 매핑
const agentContentMap = {
  theory_educator: 'theory',
  quiz_generator: 'quiz',
  evaluation_feedback: 'feedback',
  qna_resolver: 'qna'
}

// 컴퓨티드 속성들
const chapterTitle = computed(() => `${currentChapterNumber.value}챕터 ${currentSectionNumber.value}섹션`)
const sectionTitle = computed(() => 'LLM이란 무엇인가')

// 더미 데이터 (fallback용)
const dummyTheoryContent = {
  title: 'LLM(Large Language Model)이란?',
  description: 'LLM은 대규모 언어 모델로, 방대한 텍스트 데이터를 학습하여 인간과 유사한 언어 이해와 생성 능력을 가진 AI 모델입니다.',
  keyPoints: [
    '대규모 데이터 학습',
    '언어 이해 및 생성',
    '문맥 파악 능력'
  ],
  examples: [
    'ChatGPT (OpenAI)',
    'Claude (Anthropic)',
    'Bard (Google)'
  ]
}

const dummyQuizContent = {
  question: '다음 중 LLM의 특징이 아닌 것은?'
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

// API 데이터와 더미 데이터를 결합한 컨텐츠 데이터
const theoryContent = computed(() => {
  // 1. 현재 컴포넌트의 API 데이터 확인
  if (apiContentData.value?.theory) {
    return apiContentData.value.theory
  }
  
  // 2. 스토어의 캐시된 데이터 확인
  const cachedTheory = learningStore.getApiContentCache('theory')
  if (cachedTheory) {
    return cachedTheory
  }
  
  // 3. 더미데이터 사용
  return dummyTheoryContent
})

const quizContent = computed(() => {
  if (apiContentData.value?.quiz) {
    return apiContentData.value.quiz
  }
  const cachedQuiz = learningStore.getApiContentCache('quiz')
  if (cachedQuiz) {
    return cachedQuiz
  }
  return dummyQuizContent
})

const feedbackContent = computed(() => {
  if (apiContentData.value?.feedback) {
    return apiContentData.value.feedback
  }
  const cachedFeedback = learningStore.getApiContentCache('feedback')
  if (cachedFeedback) {
    return cachedFeedback
  }
  return dummyFeedbackContent
})

const qnaContent = computed(() => {
  if (apiContentData.value?.qna) {
    return apiContentData.value.qna
  }
  const cachedQna = learningStore.getApiContentCache('qna')
  if (cachedQna) {
    return cachedQna
  }
  return dummyQnaContent
})

// 컨텐츠 표시/숨김 로직
const shouldShowContent = (contentType) => {
  // 현재 에이전트의 컨텐츠이거나, 리뷰 모드인 경우
  const currentContentType = agentContentMap[props.currentAgent]
  
  if (props.currentContentMode === 'current') {
    return contentType === currentContentType
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
  if (buttonType === 'theory') {
    // 피드백 단계에서 이론이 완료된 경우만
    return props.currentAgent === 'evaluation_feedback' && 
           props.currentContentMode === 'current' && 
           props.completedSteps.theory
  }
  
  if (buttonType === 'quiz') {
    // 피드백 단계에서 퀴즈가 완료된 경우만
    return props.currentAgent === 'evaluation_feedback' && 
           props.currentContentMode === 'current' && 
           props.completedSteps.quiz
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
        // 스토어에도 캐시 저장
        learningStore.updateApiContentCache('theory', mappedContent)
        emit('content-loaded', { type: 'theory', data: mappedContent, source: 'api' })
        console.log('MainContentArea: API 데이터 로드 성공', mappedContent)
      } else {
        throw new Error('API 응답 매핑 실패')
      }
    } else {
      // 더미데이터 fallback
      apiContentData.value = { theory: dummyTheoryContent }
      // 스토어에도 더미데이터 저장 (일관성 유지)
      learningStore.updateApiContentCache('theory', dummyTheoryContent)
      emit('content-loaded', { type: 'theory', data: dummyTheoryContent, source: 'fallback' })
      emit('api-error', { message: error || 'API 호출 실패', fallback: true })
      console.warn('MainContentArea: 더미데이터로 fallback', error)
    }
  } catch (error) {
    // 에러 발생 시 더미데이터 사용
    apiContentData.value = { theory: dummyTheoryContent }
    // 스토어에도 더미데이터 저장
    learningStore.updateApiContentCache('theory', dummyTheoryContent)
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
        // 스토어에도 캐시 저장
        learningStore.updateApiContentCache(contentType, mappedContent)
        emit('content-loaded', { type: contentType, data: mappedContent, source: 'api' })
        lastApiCall.value = agent
        console.log(`MainContentArea: ${agent} API 데이터 로드 성공`, mappedContent)
      } else {
        throw new Error('API 응답 매핑 실패')
      }
    } else {
      // 더미데이터 fallback
      if (!apiContentData.value) apiContentData.value = {}
      apiContentData.value[contentType] = fallbackData
      // 스토어에도 더미데이터 저장
      learningStore.updateApiContentCache(contentType, fallbackData)
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
    // 스토어에도 더미데이터 저장
    learningStore.updateApiContentCache(contentType, fallbackData)
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
  
  // 스토어에 캐시된 데이터가 있는지 먼저 확인
  const cachedTheory = learningStore.getApiContentCache('theory')
  if (cachedTheory) {
    console.log('MainContentArea: 캐시된 이론 데이터 발견', cachedTheory)
    apiContentData.value = { theory: cachedTheory }
    emit('content-loaded', { type: 'theory', data: cachedTheory, source: 'cache' })
  } else {
    // 캐시된 데이터가 없으면 API 호출
    loadInitialContent()
  }
})

// 에이전트 변경 감지
watch(() => props.currentAgent, (newAgent, oldAgent) => {
  if (newAgent !== oldAgent) {
    console.log(`MainContentArea: 에이전트 변경 감지 - ${oldAgent} → ${newAgent}`)
    loadAgentContent(newAgent)
  }
}, { immediate: false })

// 이벤트 핸들러
const handleNavigationClick = (navigationType) => {
  emit('navigation-click', navigationType)
}
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

.content-subtitle {
  color: #6c757d;
  font-size: 1rem;
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 에이전트별 컨텐츠 스타일 */
.theory-content {
  background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
  border-left: 4px solid #2196f3;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.theory-body {
  line-height: 1.6;
}

.key-points ul,
.examples ul {
  padding-left: 1.5rem;
  margin-top: 0.5rem;
}

.key-points li,
.examples li {
  margin-bottom: 0.25rem;
}

.quiz-content {
  background: linear-gradient(135deg, #fff3e0, #fce4ec);
  border-left: 4px solid #ff9800;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.quiz-question-display p {
  margin-bottom: 1rem;
}

.quiz-description {
  background: rgba(255, 255, 255, 0.7);
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.quiz-description p {
  margin-bottom: 0.5rem;
}

.quiz-description p:last-child {
  margin-bottom: 0;
}

.feedback-content {
  background: linear-gradient(135deg, #e8f5e8, #f1f8e9);
  border-left: 4px solid #4caf50;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.feedback-score {
  margin-bottom: 1.5rem;
}

.feedback-score p {
  font-size: 1.2rem;
  color: #2e7d32;
}

.feedback-explanation,
.feedback-next-steps {
  margin-bottom: 1rem;
}

.feedback-explanation p:last-child,
.feedback-next-steps p:last-child {
  margin-top: 0.5rem;
  line-height: 1.6;
}

.qna-content {
  background: linear-gradient(135deg, #f3e5f5, #fce4ec);
  border-left: 4px solid #9c27b0;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.qna-item {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.qna-item p {
  margin-bottom: 0.75rem;
}

.qna-related {
  background: rgba(255, 255, 255, 0.7);
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(156, 39, 176, 0.3);
}

.qna-related p {
  margin-bottom: 0.5rem;
}

.qna-related p:last-child {
  margin-bottom: 0;
}

/* 컨텐츠 표시/숨김 */
.content-active {
  display: block;
  animation: fadeIn 0.3s ease-in;
}

.content-hidden {
  display: none;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

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

/* 반응형 */
@media (max-width: 768px) {
  .main-content-area {
    padding: 1rem;
  }
  
  .content-title {
    font-size: 1.25rem;
  }
  
  .theory-content,
  .quiz-content,
  .feedback-content,
  .qna-content {
    padding: 1rem;
  }
  
  .content-navigation {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>