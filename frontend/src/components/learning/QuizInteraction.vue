<!-- frontend/src/components/learning/QuizInteraction.vue -->
<template>
  <div class="quiz-mode" :class="{ active: !isLoading }">
    <!-- 퀴즈 헤더 -->
    <div class="quiz-header">
      <div class="quiz-progress" v-if="showProgress">
        <span class="progress-text">{{ progressText }}</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- 퀴즈 질문 -->
    <div class="quiz-question-container">
      <div class="quiz-question">
        {{ quizData.question || '퀴즈를 준비하고 있습니다...' }}
      </div>
      
      <!-- 퀴즈 타입별 설명 -->
      <div class="quiz-type-info" v-if="quizData.type">
        <span class="quiz-type-badge" :class="quizTypeBadgeClass">
          {{ quizTypeText }}
        </span>
        <span class="quiz-instruction">{{ quizInstruction }}</span>
      </div>
    </div>
    
    <!-- 객관식 옵션 -->
    <div 
      v-if="quizData.type === 'multiple_choice' && quizData.options?.length"
      class="quiz-options"
    >
      <div 
        v-for="(option, index) in quizData.options" 
        :key="option.value"
        class="quiz-option"
        :class="{ 
          'selected': selectedAnswer === option.value,
          'disabled': isOverallLoading || isSubmitted
        }"
        @click="selectOption(option.value)"
      >
        <div class="option-indicator">
          {{ selectedAnswer === option.value ? '●' : '○' }}
        </div>
        <div class="option-content">
          <span class="option-number">{{ option.value }}.</span>
          <span class="option-text">{{ option.text }}</span>
        </div>
      </div>
    </div>

    <!-- 주관식 입력 -->
    <div 
      v-else-if="quizData.type === 'subjective'"
      class="subjective-input-container"
    >
      <textarea
        v-model="subjectiveAnswer"
        ref="subjectiveInputRef"
        class="subjective-input"
        :placeholder="subjectivePlaceholder"
        :disabled="isOverallLoading || isSubmitted"
        rows="4"
        maxlength="500"
      ></textarea>
      <div class="character-count">
        {{ subjectiveAnswer.length }}/500
      </div>
    </div>

    <!-- 힌트 표시 -->
    <div v-if="showHint && currentHint" class="hint-container">
      <div class="hint-content">
        <div class="hint-icon">💡</div>
        <div class="hint-text">{{ currentHint }}</div>
      </div>
    </div>
    
    <!-- 액션 버튼들 -->
    <div class="quiz-actions">
      <button 
        class="btn btn-secondary hint-btn"
        @click="requestHint"
        :disabled="isOverallLoading || hintUsed"
        v-if="!isSubmitted"
      >
        <span v-if="hintUsed">✅ 힌트 사용됨</span>
        <span v-else-if="isOverallLoading">⏳ 로딩중...</span>
        <span v-else>💡 힌트</span>
      </button>
      
      <button 
        class="btn btn-primary submit-btn"
        @click="submitAnswer"
        :disabled="!canSubmit || isOverallLoading"
        v-if="!isSubmitted"
      >
        <span v-if="isOverallLoading" class="button-spinner"></span>
        <span v-else>{{ submitButtonText }}</span>
      </button>

      <!-- 제출 후 버튼 -->
      <div v-if="isSubmitted" class="post-submit-actions">
        <div class="submit-success">
          ✅ 답변이 제출되었습니다!
        </div>
        <button 
          class="btn btn-outline"
          @click="resetQuiz"
          v-if="allowRetry && !showEvaluationResult"
        >
          🔄 다시 풀기
        </button>
      </div>
    </div>

    <!-- 평가 결과 표시 -->
    <div v-if="showEvaluationResult && evaluationResult" class="evaluation-result">
      <div class="result-header">
        <div class="result-status" :class="{ 'correct': evaluationResult.is_correct, 'incorrect': !evaluationResult.is_correct }">
          <span class="result-icon">
            {{ evaluationResult.is_correct ? '✅' : '❌' }}
          </span>
          <span class="result-text">
            {{ evaluationResult.is_correct ? '정답입니다!' : '틀렸습니다.' }}
          </span>
          <span class="result-score" v-if="evaluationResult.score !== undefined">
            ({{ evaluationResult.score }}점)
          </span>
        </div>
      </div>
      
      <div class="result-content">
        <div v-if="evaluationResult.feedback" class="result-feedback">
          <div class="feedback-label">피드백</div>
          <div class="feedback-text">{{ evaluationResult.feedback }}</div>
        </div>
        
        <div v-if="evaluationResult.explanation" class="result-explanation">
          <div class="explanation-label">해설</div>
          <div class="explanation-text">{{ evaluationResult.explanation }}</div>
        </div>
      </div>
      
      <div class="result-actions">
        <button 
          class="btn btn-outline"
          @click="resetQuiz"
          v-if="allowRetry"
        >
          🔄 다시 풀기
        </button>
      </div>
    </div>

    <!-- 추가 정보 -->
    <div class="quiz-footer" v-if="showFooter && !showEvaluationResult">
      <div class="quiz-tips">
        <div class="tip-item">
          <span class="tip-icon">⚠️</span>
          <span class="tip-text">신중하게 답변을 선택한 후 제출해주세요.</span>
        </div>
        <div class="tip-item" v-if="quizData.type === 'subjective'">
          <span class="tip-icon">📝</span>
          <span class="tip-text">자세하고 구체적으로 작성해주세요.</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, defineProps, defineEmits } from 'vue'
import { useLearningStore } from '../../stores/learningStore.js'
import { useTutorStore } from '../../stores/tutorStore.js'
import { useErrorHandler } from '../../composables/useErrorHandler.js'

// Store 인스턴스
const learningStore = useLearningStore()
const tutorStore = useTutorStore()

// 에러 핸들러 컴포저블
const { executeWithErrorHandling } = useErrorHandler()

// Props 정의
const props = defineProps({
  quizData: {
    type: Object,
    required: true,
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
    default: true
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
const emit = defineEmits(['submit-answer', 'request-hint', 'quiz-reset', 'evaluation-complete'])

// 반응형 상태
const selectedAnswer = ref('')
const subjectiveAnswer = ref('')
const showHint = ref(false)
const currentHint = ref('')
const hintUsed = ref(false)
const isSubmitted = ref(false)
const subjectiveInputRef = ref(null)

// API 연동 상태
const isSubmitting = ref(false)
const evaluationResult = ref(null)
const showEvaluationResult = ref(false)

// 컴퓨티드 속성들
const progressText = computed(() => 
  `${props.currentQuestionNumber}/${props.totalQuestions}`
)

const progressPercentage = computed(() => 
  (props.currentQuestionNumber / props.totalQuestions) * 100
)

const quizTypeText = computed(() => {
  switch (props.quizData.type) {
    case 'multiple_choice':
      return '객관식'
    case 'subjective':
      return '주관식'
    default:
      return '문제'
  }
})

const quizTypeBadgeClass = computed(() => {
  switch (props.quizData.type) {
    case 'multiple_choice':
      return 'badge-multiple'
    case 'subjective':
      return 'badge-subjective'
    default:
      return 'badge-default'
  }
})

const quizInstruction = computed(() => {
  switch (props.quizData.type) {
    case 'multiple_choice':
      return '하나의 정답을 선택해주세요.'
    case 'subjective':
      return '자유롭게 답변을 작성해주세요.'
    default:
      return ''
  }
})

const subjectivePlaceholder = computed(() => 
  '답변을 입력해주세요... (최대 500자)'
)

const canSubmit = computed(() => {
  if (props.isLoading || isSubmitted.value || isSubmitting.value || learningStore.isLoading) return false
  
  if (props.quizData.type === 'multiple_choice') {
    return selectedAnswer.value !== ''
  } else if (props.quizData.type === 'subjective') {
    return subjectiveAnswer.value.trim().length > 0
  }
  
  return false
})

const submitButtonText = computed(() => {
  if (isSubmitting.value || learningStore.isLoading) {
    return '제출 중...'
  }
  
  if (props.quizData.type === 'subjective') {
    return '답안 제출'
  }
  return '정답 제출'
})

// 전체 로딩 상태 (props와 store 상태 통합)
const isOverallLoading = computed(() => {
  return props.isLoading || learningStore.isLoading || isSubmitting.value
})

// 이벤트 핸들러들
const selectOption = (value) => {
  if (isOverallLoading.value || isSubmitted.value) return
  
  selectedAnswer.value = selectedAnswer.value === value ? '' : value
}

const requestHint = () => {
  if (props.isLoading || hintUsed.value || learningStore.isLoading) return
  
  console.log('힌트 요청')
  hintUsed.value = true
  
  if (props.quizData.hint) {
    currentHint.value = props.quizData.hint
    showHint.value = true
    
    // 힌트 사용을 tutorStore를 통해 채팅에 기록
    tutorStore.addChatMessage({
      sender: '튜터',
      message: `💡 힌트: ${props.quizData.hint}`,
      type: 'hint',
      timestamp: new Date()
    })
  }
  
  emit('request-hint', {
    hint: props.quizData.hint,
    questionNumber: props.currentQuestionNumber
  })
}

const submitAnswer = async () => {
  if (!canSubmit.value) return
  
  const answer = props.quizData.type === 'multiple_choice' 
    ? selectedAnswer.value 
    : subjectiveAnswer.value.trim()
  
  if (!answer) return
  
  console.log('퀴즈 답안 제출 시작:', { answer, type: props.quizData.type })
  
  // 제출 상태 설정
  isSubmitting.value = true
  isSubmitted.value = true
  
  try {
    // 에러 핸들링이 통합된 API 호출
    const result = await executeWithErrorHandling(
      learningStore.submitQuiz,
      'submitQuiz',
      answer
    )
    
    if (result.success) {
      console.log('퀴즈 제출 성공:', result.data)
      
      // 평가 결과 처리
      if (result.data.evaluation_result) {
        evaluationResult.value = result.data.evaluation_result
        showEvaluationResult.value = true
        
        // 평가 결과를 tutorStore에 전달하여 채팅에 피드백 메시지 추가
        tutorStore.processEvaluationResult(result.data.evaluation_result)
        
        console.log('평가 결과 처리 완료:', evaluationResult.value)
      }
      
      // 워크플로우 응답이 있으면 tutorStore에 전달
      if (result.data.workflow_response) {
        tutorStore.updateFromWorkflowResponse(result.data.workflow_response)
      }
      
      // 부모 컴포넌트에 평가 완료 알림
      emit('evaluation-complete', {
        answer: answer,
        type: props.quizData.type,
        hintUsed: hintUsed.value,
        questionNumber: props.currentQuestionNumber,
        evaluationResult: evaluationResult.value
      })
      
      // 기존 emit도 유지 (하위 호환성)
      emit('submit-answer', {
        answer: answer,
        type: props.quizData.type,
        hintUsed: hintUsed.value,
        questionNumber: props.currentQuestionNumber,
        evaluationResult: evaluationResult.value
      })
      
    } else {
      console.error('퀴즈 제출 실패:', result.error)
      
      // 에러 발생 시 제출 상태 되돌리기
      isSubmitted.value = false
      
      // 에러는 ErrorAlert 컴포넌트에서 표시되므로 여기서는 간단한 시스템 메시지만 추가
      tutorStore.addChatMessage({
        sender: '시스템',
        message: '⚠️ 퀴즈 제출에 실패했습니다. 상단의 에러 알림을 확인해주세요.',
        type: 'error',
        timestamp: new Date()
      })
    }
    
  } catch (error) {
    console.error('퀴즈 제출 중 예외 발생:', error)
    
    // 에러 발생 시 제출 상태 되돌리기
    isSubmitted.value = false
    
    // 예외 상황 메시지 추가
    tutorStore.addChatMessage({
      sender: '시스템',
      message: '⚠️ 퀴즈 제출 중 예상치 못한 오류가 발생했습니다.',
      type: 'error',
      timestamp: new Date()
    })
    
  } finally {
    isSubmitting.value = false
  }
}

const resetQuiz = () => {
  selectedAnswer.value = ''
  subjectiveAnswer.value = ''
  showHint.value = false
  currentHint.value = ''
  hintUsed.value = false
  isSubmitted.value = false
  isSubmitting.value = false
  evaluationResult.value = null
  showEvaluationResult.value = false
  
  emit('quiz-reset')
}

// 감시자들
watch(() => props.quizData, (newQuizData) => {
  // 새로운 퀴즈 데이터가 들어오면 상태 리셋
  if (newQuizData) {
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

// learningStore의 에러 상태 감시
watch(() => learningStore.hasError, (hasError) => {
  if (hasError && learningStore.errorState.error_message) {
    console.log('learningStore 에러 감지:', learningStore.errorState)
    
    // 제출 중이었다면 상태 되돌리기
    if (isSubmitting.value) {
      isSubmitted.value = false
      isSubmitting.value = false
    }
    
    // 에러 메시지를 tutorStore를 통해 채팅에 표시
    tutorStore.addChatMessage({
      sender: '시스템',
      message: learningStore.errorState.error_message,
      type: 'error',
      timestamp: new Date()
    })
  }
})

// learningStore의 워크플로우 상태 변화 감시 (평가 결과 처리)
watch(() => learningStore.workflowState.evaluation_result, (newEvaluationResult) => {
  if (newEvaluationResult && isSubmitted.value) {
    console.log('워크플로우에서 평가 결과 감지:', newEvaluationResult)
    evaluationResult.value = newEvaluationResult
    showEvaluationResult.value = true
  }
})
</script>

<style scoped>
.quiz-mode {
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
}

.quiz-mode.active {
  opacity: 1;
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

/* 객관식 옵션들 */
.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
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
  gap: 0.5rem;
  flex: 1;
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

/* 평가 결과 표시 */
.evaluation-result {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 1rem;
  animation: resultSlideIn 0.4s ease-out;
}

@keyframes resultSlideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result-header {
  margin-bottom: 1rem;
}

.result-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-weight: 500;
}

.result-status.correct {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.result-status.incorrect {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.result-icon {
  font-size: 1.25rem;
}

.result-text {
  font-size: 1rem;
}

.result-score {
  font-size: 0.875rem;
  opacity: 0.8;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-feedback,
.result-explanation {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 0.375rem;
  padding: 0.75rem;
}

.feedback-label,
.explanation-label {
  font-weight: 500;
  color: #495057;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.feedback-text,
.explanation-text {
  line-height: 1.5;
  color: #212529;
}

.result-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
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

/* 반응형 */
@media (max-width: 768px) {
  .quiz-mode {
    padding: 0.75rem;
  }
  
  .quiz-question {
    font-size: 1rem;
    padding: 0.75rem;
  }
  
  .quiz-option {
    padding: 0.75rem;
  }
  
  .option-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .quiz-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .btn {
    width: 100%;
  }
  
  .subjective-input {
    font-size: 16px; /* iOS에서 줌 방지 */
  }
  
  .quiz-type-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

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