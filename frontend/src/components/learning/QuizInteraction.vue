<!-- frontend/src/components/learning/QuizInteraction.vue -->
<template>
  <div class="quiz-interaction" :class="{ active: !isLoading }">
    <!-- 퀴즈 진행률 (선택적) -->
    <div class="quiz-header" v-if="showProgress">
      <div class="quiz-progress">
        <span class="progress-text">{{ progressText }}</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- 퀴즈 상호작용 영역 -->
    <div class="interaction-content">
      <!-- 객관식 옵션 -->
      <div v-if="hasValidQuizData && actualQuizData.type === 'multiple_choice'" class="quiz-options">
        <div class="options-header">
          <h4>답안을 선택해주세요</h4>
          <span class="options-count">{{ actualQuizData.options?.length || 0 }}개 선택지</span>
        </div>

        <div v-for="(option, index) in actualQuizData.options" :key="index" class="quiz-option" :class="{
          'selected': selectedAnswer === (index + 1).toString(),
          'disabled': isLoading || isSubmitted
        }" @click="selectOption((index + 1).toString())">
          <div class="option-indicator">
            {{ selectedAnswer === (index + 1).toString() ? '●' : '○' }}
          </div>
          <div class="option-content">
            <span class="option-number">{{ index + 1 }}.</span>
            <span class="option-text">{{ cleanOptionText(option, index) }}</span>
          </div>
        </div>
      </div>

      <!-- 주관식 입력 -->
      <div v-else-if="hasValidQuizData && actualQuizData.type === 'subjective'" class="subjective-input-container">
        <div class="input-header">
          <h4>답안을 작성해주세요</h4>
          <span class="input-guide">자세하고 구체적으로 작성해주세요</span>
        </div>

        <textarea v-model="subjectiveAnswer" ref="subjectiveInputRef" class="subjective-input"
          :placeholder="subjectivePlaceholder" :disabled="isLoading || isSubmitted" rows="4" maxlength="500"></textarea>
        <div class="character-count">
          {{ subjectiveAnswer.length }}/500
        </div>
      </div>

      <!-- 퀴즈 데이터가 없는 경우 - 로딩 인디케이터 -->
      <div v-else-if="!hasValidQuizData" class="quiz-loading">
        <div class="loading-spinner"></div>
        <p v-if="!actualQuizData.question">퀴즈를 로드 중입니다...</p>
        <p v-else>퀴즈를 로드 중입니다...</p>
        <div class="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>

    <!-- 힌트 표시 -->
    <div v-if="hasValidQuizData && showHint && currentHint" class="hint-container">
      <div class="hint-content">
        <div class="hint-icon">💡</div>
        <div class="hint-text">{{ currentHint }}</div>
      </div>
    </div>

    <!-- 액션 버튼들 -->
    <div v-if="hasValidQuizData" class="quiz-actions">
      <button class="btn btn-secondary hint-btn" @click="toggleHint" :disabled="isLoading"
        v-if="!isSubmitted && actualQuizData.hint">
        <span v-if="isLoading">⏳ 로딩중...</span>
        <span v-else-if="showHint">🔍 힌트 숨기기</span>
        <span v-else>💡 힌트 보기</span>
      </button>

      <button class="btn btn-primary submit-btn" @click="submitAnswer" :disabled="!canSubmit || isLoading"
        v-if="!isSubmitted">
        <span v-if="isLoading" class="button-spinner"></span>
        <span v-else>{{ submitButtonText }}</span>
      </button>

      <!-- 제출 후 버튼 -->
      <div v-if="isSubmitted" class="post-submit-actions">
        <div class="submit-success">
          ✅ 답변이 제출되었습니다!
        </div>
        <button class="btn btn-outline" @click="resetQuiz" v-if="allowRetry">
          🔄 다시 풀기
        </button>
      </div>
    </div>

    <!-- 추가 정보 -->
    <div class="quiz-footer" v-if="showFooter">
      <div class="quiz-tips">
        <div class="tip-item" v-if="actualQuizData.type === 'subjective'">
          <span class="tip-icon">📝</span>
          <span class="tip-text">자세하고 구체적으로 작성해주세요.</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, defineProps, defineEmits } from 'vue'
import { learningService } from '@/services/learningService.js'
import { useLearningStore } from '@/stores/learningStore'

// Store 사용 (캐시 없이 실시간 데이터만 사용)
const learningStore = useLearningStore()

// Props 정의
const props = defineProps({
  quizData: {
    type: Object,
    required: false,
    default: () => ({
      question: '',
      type: 'multiple_choice', // 'multiple_choice' | 'subjective'
      options: [],
      hint: ''
    })
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  allowRetry: {
    type: Boolean,
    default: false
  },
  currentQuestionNumber: {
    type: Number,
    default: 1
  },
  totalQuestions: {
    type: Number,
    default: 1
  }
})

// Emits 정의
const emit = defineEmits(['submit-answer', 'request-hint', 'quiz-reset', 'api-error'])

// store에서 퀴즈 데이터 가져오기 (캐시 없이 현재 데이터만 사용)
const storeQuizData = computed(() => learningStore.quizData)
const actualQuizData = computed(() => {
  // 캐시된 데이터 사용하지 않고 현재 store 데이터만 사용
  if (storeQuizData.value && storeQuizData.value.question && !storeQuizData.value.question.includes('로드 중입니다')) {
    console.log('QuizInteraction - store에서 퀴즈 데이터 사용:', storeQuizData.value)
    return storeQuizData.value
  }
  console.log('QuizInteraction - props에서 퀴즈 데이터 사용:', props.quizData)
  return props.quizData
})

// 반응형 상태
const selectedAnswer = ref('')
const subjectiveAnswer = ref('')
const showHint = ref(false)
const currentHint = ref('')
const hintUsed = ref(false)
const isSubmitted = ref(false)
const subjectiveInputRef = ref(null)

// 컴퓨티드 속성들
const progressText = computed(() =>
  `${props.currentQuestionNumber}/${props.totalQuestions}`
)

const progressPercentage = computed(() =>
  (props.currentQuestionNumber / props.totalQuestions) * 100
)



const subjectivePlaceholder = computed(() =>
  '답변을 입력해주세요... (최대 500자)'
)

const canSubmit = computed(() => {
  if (props.isLoading || isSubmitted.value) return false

  if (actualQuizData.value.type === 'multiple_choice') {
    return selectedAnswer.value !== ''
  } else if (actualQuizData.value.type === 'subjective') {
    return subjectiveAnswer.value.trim().length > 0
  }

  return false
})

const submitButtonText = computed(() => {
  if (actualQuizData.value.type === 'subjective') {
    return '답안 제출'
  }
  return '정답 제출'
})

// 퀴즈 데이터가 유효한지 확인
const hasValidQuizData = computed(() => {
  // 로딩 중인 더미 데이터는 유효하지 않은 것으로 처리
  if (actualQuizData.value.question && actualQuizData.value.question.includes('로드 중입니다')) {
    console.log('QuizInteraction - 로딩 중인 데이터 감지')
    return false
  }

  const isValid = actualQuizData.value.question &&
    actualQuizData.value.question !== '' &&
    actualQuizData.value.type &&
    actualQuizData.value.type !== '' &&
    ((actualQuizData.value.type === 'multiple_choice' && actualQuizData.value.options?.length > 0) ||
      actualQuizData.value.type === 'subjective')
  
  console.log('QuizInteraction - 퀴즈 데이터 유효성 검사:', {
    isValid,
    question: actualQuizData.value.question,
    type: actualQuizData.value.type,
    optionsLength: actualQuizData.value.options?.length,
    actualData: actualQuizData.value
  })
  
  return isValid
})

// 유틸리티 함수들
const cleanOptionText = (option, index) => {
  let text = typeof option === 'string' ? option : (option.text || option)
  
  // 텍스트 앞의 번호 패턴 제거 (예: "1.", "2.", "1. ", "2. " 등)
  const numberPattern = new RegExp(`^${index + 1}\\.\\s*`)
  text = text.replace(numberPattern, '')
  
  // 다른 번호 패턴도 제거 (예: "1)", "(1)", "[1]" 등)
  text = text.replace(/^\d+[\.\)\]]\s*/, '')
  text = text.replace(/^\[\d+\]\s*/, '')
  text = text.replace(/^\(\d+\)\s*/, '')
  
  return text.trim()
}

// 이벤트 핸들러들
const selectOption = (value) => {
  if (props.isLoading || isSubmitted.value) return

  selectedAnswer.value = selectedAnswer.value === value ? '' : value
}

const toggleHint = () => {
  if (props.isLoading) return

  if (showHint.value) {
    // 힌트 숨기기
    showHint.value = false
    currentHint.value = ''
  } else {
    // 힌트 보이기
    if (actualQuizData.value.hint) {
      currentHint.value = actualQuizData.value.hint
      showHint.value = true
      hintUsed.value = true // 힌트를 한 번이라도 본 경우 기록
    }
  }

  emit('request-hint', {
    action: showHint.value ? 'show' : 'hide',
    hintUsed: hintUsed.value
  })
}

const submitAnswer = async () => {
  if (!canSubmit.value) return

  const answer = actualQuizData.value.type === 'multiple_choice'
    ? selectedAnswer.value
    : subjectiveAnswer.value.trim()

  if (!answer) return

  // 로딩 상태 시작
  isSubmitted.value = true

  try {
    // 백엔드 API 호출 (v2.0 API 사용)
    const result = await learningService.submitQuizAnswerV2(answer)

    if (result.success) {
      // API 성공 시 응답 데이터를 기존 구조로 매핑
      const mappedResult = mapApiResponseToQuizResult(result.data)

      // store에 사용자 답변 저장 (API 성공 후에만)
      learningStore.updateUserAnswer(answer)

      emit('submit-answer', {
        answer: answer,
        type: actualQuizData.value.type,
        hintUsed: hintUsed.value,
        questionNumber: props.currentQuestionNumber,
        apiResult: mappedResult,
        success: true
      })
    } else {
      // API 실패 시 더미데이터로 fallback
      console.warn('퀴즈 답안 제출 API 실패:', result.error)

      const fallbackResult = createFallbackQuizResult(answer)

      emit('submit-answer', {
        answer: answer,
        type: actualQuizData.value.type,
        hintUsed: hintUsed.value,
        questionNumber: props.currentQuestionNumber,
        apiResult: fallbackResult,
        success: false,
        error: result.error
      })

      // 에러 이벤트 발생
      emit('api-error', {
        type: 'quiz-submit',
        error: result.error,
        fallbackUsed: true
      })
    }
  } catch (error) {
    // 예외 발생 시 더미데이터로 fallback
    console.error('퀴즈 답안 제출 중 오류:', error)

    const fallbackResult = createFallbackQuizResult(answer)

    emit('submit-answer', {
      answer: answer,
      type: actualQuizData.value.type,
      hintUsed: hintUsed.value,
      questionNumber: props.currentQuestionNumber,
      apiResult: fallbackResult,
      success: false,
      error: error.message
    })

    // 에러 이벤트 발생
    emit('api-error', {
      type: 'quiz-submit',
      error: error.message,
      fallbackUsed: true
    })
  }
}

// API 응답을 기존 퀴즈 결과 구조로 매핑하는 함수
const mapApiResponseToQuizResult = (apiResponse) => {
  console.log('🔍 mapApiResponseToQuizResult 호출됨:', apiResponse)
  
  // 실제 API 응답 구조 확인
  if (apiResponse && apiResponse.feedback && apiResponse.explanation) {
    // 직접적인 피드백 구조인 경우
    console.log('📋 직접 피드백 구조 감지:', apiResponse)
    return {
      isCorrect: true, // 임시로 true 설정
      correctAnswer: '',
      explanation: apiResponse.explanation || '설명이 없습니다.',
      feedback: apiResponse.feedback || '피드백이 없습니다.',
      score: 100, // 임시로 100점 설정
      nextStep: apiResponse.nextStep || 'continue'
    }
  }
  
  // workflow_response 구조인 경우
  if (apiResponse && apiResponse.data && apiResponse.data.workflow_response) {
    console.log('📋 workflow_response 구조 감지:', apiResponse.data.workflow_response)
    const workflow_response = apiResponse.data.workflow_response
    const evaluationResult = workflow_response.evaluation_result || {}
    const feedback = evaluationResult.feedback || {}

    return {
      isCorrect: evaluationResult.is_answer_correct || false,
      correctAnswer: '',
      explanation: feedback.explanation || '설명이 없습니다.',
      feedback: feedback.content || feedback.title || '피드백이 없습니다.',
      score: evaluationResult.score || 0,
      nextStep: feedback.next_step_decision || 'continue'
    }
  }
  
  // 다른 구조들 확인
  console.log('⚠️ 알 수 없는 API 응답 구조:', apiResponse)
  
  return {
    isCorrect: false,
    correctAnswer: '',
    explanation: 'API 응답 구조가 올바르지 않습니다.',
    feedback: '응답을 처리할 수 없습니다.',
    score: 0,
    nextStep: 'continue'
  }
}

// 더미데이터 fallback 결과 생성 함수
const createFallbackQuizResult = (userAnswer) => {
  // 간단한 더미 평가 로직 (실제로는 백엔드에서 처리)
  const isCorrect = Math.random() > 0.5 // 임시로 랜덤 결과

  return {
    isCorrect: isCorrect,
    correctAnswer: actualQuizData.value.options?.[0] || '1',
    explanation: '네트워크 연결 문제로 임시 결과입니다.',
    feedback: isCorrect ? '정답입니다!' : '다시 한번 생각해보세요.',
    score: isCorrect ? 100 : 0,
    nextStep: 'continue'
  }
}

const resetQuiz = () => {
  // 모든 상태 완전 초기화 (캐시 데이터 사용하지 않음)
  selectedAnswer.value = ''
  subjectiveAnswer.value = ''
  showHint.value = false
  currentHint.value = ''
  hintUsed.value = false
  isSubmitted.value = false

  console.log('퀴즈 상태 완전 초기화됨')
  emit('quiz-reset')
}

// 감시자들 - 캐시 없이 새로운 데이터마다 완전 리셋
watch(() => actualQuizData.value, (newQuizData, oldQuizData) => {
  // 새로운 퀴즈 데이터가 들어오면 이전 상태 완전 초기화
  if (newQuizData && newQuizData.question && newQuizData !== oldQuizData) {
    console.log('새로운 퀴즈 데이터 감지 - 상태 완전 리셋')
    resetQuiz()
  }
}, { deep: true })

watch(subjectiveAnswer, () => {
  // 주관식 입력창 자동 높이 조절
  nextTick(() => {
    if (subjectiveInputRef.value) {
      subjectiveInputRef.value.style.height = 'auto'
      subjectiveInputRef.value.style.height = subjectiveInputRef.value.scrollHeight + 'px'
    }
  })
})
</script>

<style scoped>
.quiz-interaction {
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #dee2e6;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  opacity: 0.7;
  transition: opacity 0.3s ease;
  overflow: hidden;
  /* 전체 컨테이너 오버플로우 제어 */
}

.quiz-interaction.active {
  opacity: 1;
}

/* 상호작용 컨텐츠 */
.interaction-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
  /* 세로 스크롤 추가 */
  min-height: 0;
  /* flex 아이템이 축소될 수 있도록 */
  padding-right: 0.5rem;
  /* 스크롤바 공간 확보 */
}

/* 스크롤바 스타일링 */
.interaction-content::-webkit-scrollbar {
  width: 6px;
}

.interaction-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.interaction-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.interaction-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 퀴즈 헤더 */
.quiz-header {
  border-bottom: 1px solid #eee;
  padding-bottom: 0.75rem;
}

.quiz-progress {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-text {
  font-size: 0.875rem;
  color: #6c757d;
  text-align: center;
}

.progress-bar {
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #74a8f7, #5a94f5);
  transition: width 0.3s ease;
}

/* 퀴즈 질문 */
.quiz-question-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.quiz-question {
  font-weight: 500;
  font-size: 1.1rem;
  line-height: 1.5;
  color: #2c3e50;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  border-left: 4px solid #74a8f7;
}

.quiz-type-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
}

.quiz-type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-weight: 500;
  font-size: 0.75rem;
}

.badge-multiple {
  background: #e3f2fd;
  color: #1976d2;
}

.badge-subjective {
  background: #f3e5f5;
  color: #7b1fa2;
}

.badge-default {
  background: #f5f5f5;
  color: #666;
}

.quiz-instruction {
  color: #6c757d;
}

/* 옵션 헤더 */
.options-header,
.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.options-header h4,
.input-header h4 {
  margin: 0;
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 600;
}

.options-count,
.input-guide {
  font-size: 0.875rem;
  color: #6c757d;
}

/* 객관식 옵션들 */
.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
  min-height: 0;
  /* flex 아이템이 축소될 수 있도록 */
}

.quiz-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.quiz-option:hover:not(.disabled) {
  background: #f8f9fa;
  border-color: #74a8f7;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(116, 168, 247, 0.15);
}

.quiz-option.selected {
  background: #e3f2fd;
  border-color: #74a8f7;
  box-shadow: 0 0 0 2px rgba(116, 168, 247, 0.25);
}

.quiz-option.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.option-indicator {
  font-size: 1.25rem;
  color: #74a8f7;
  font-weight: bold;
  min-width: 20px;
}

.option-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.option-number {
  font-weight: 500;
  color: #495057;
}

.option-text {
  line-height: 1.4;
}

/* 주관식 입력 */
.subjective-input-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
  min-height: 0;
  /* flex 아이템이 축소될 수 있도록 */
}

/* 퀴즈 로딩 상태 */
.quiz-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 3rem 1rem;
  text-align: center;
  color: #6c757d;
  flex: 1;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #74a8f7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.quiz-loading p {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
  color: #495057;
}

/* 로딩 점들 애니메이션 */
.loading-dots {
  display: flex;
  gap: 0.5rem;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: #74a8f7;
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {

  0%,
  80%,
  100% {
    transform: scale(0);
  }

  40% {
    transform: scale(1);
  }
}

.subjective-input {
  width: 100%;
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  line-height: 1.5;
  resize: vertical;
  min-height: 120px;
  max-height: 200px;
  transition: border-color 0.2s ease;
}

.subjective-input:focus {
  outline: none;
  border-color: #74a8f7;
  box-shadow: 0 0 0 2px rgba(116, 168, 247, 0.25);
}

.subjective-input:disabled {
  background: #f8f9fa;
  opacity: 0.7;
}

.character-count {
  text-align: right;
  font-size: 0.75rem;
  color: #6c757d;
}

/* 힌트 컨테이너 */
.hint-container {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 0.5rem;
  padding: 1rem;
  animation: hintSlideIn 0.3s ease-out;
  flex-shrink: 0;
  /* 힌트 영역이 축소되지 않도록 */
}

@keyframes hintSlideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hint-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.hint-icon {
  font-size: 1.25rem;
}

.hint-text {
  line-height: 1.5;
  color: #856404;
  font-weight: 500;
}

/* 액션 버튼들 */
.quiz-actions {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
  flex-shrink: 0;
  /* 버튼 영역이 축소되지 않도록 */
  border-top: 1px solid #eee;
  padding-top: 1rem;
  margin-top: auto;
  /* 하단에 고정 */
}

.btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 80px;
}

.btn-primary {
  background: #74a8f7;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a94f5;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
  transform: translateY(-1px);
}

.btn-outline {
  background: white;
  color: #6c757d;
  border: 1px solid #6c757d;
}

.btn-outline:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #495057;
  color: #495057;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.hint-btn {
  flex: 0 0 auto;
}

.submit-btn {
  flex: 1;
  max-width: 150px;
}

.button-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 제출 후 액션 */
.post-submit-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: center;
  width: 100%;
}

.submit-success {
  color: #28a745;
  font-weight: 500;
  padding: 0.5rem 1rem;
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 0.375rem;
  text-align: center;
  width: 100%;
}

/* 퀴즈 푸터 */
.quiz-footer {
  border-top: 1px solid #eee;
  padding-top: 0.75rem;
}

.quiz-tips {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.tip-icon {
  font-size: 1rem;
}

.tip-text {
  line-height: 1.4;
}

/* 데스크톱 전용 - 모바일/태블릿 대응 제거 */

/* 접근성 개선 */
@media (prefers-reduced-motion: reduce) {

  .quiz-option,
  .btn,
  .hint-container {
    transition: none;
  }

  .button-spinner {
    animation: none;
  }
}
</style>