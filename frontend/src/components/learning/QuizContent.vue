<!-- frontend/src/components/learning/QuizContent.vue -->
<template>
  <div class="quiz-content"
    :class="{ 'content-active': isVisible, 'content-hidden': !isVisible }">
    <!-- 퀴즈 헤더 -->
    <div class="quiz-header">
      <h3>📝 퀴즈 문제</h3>
      <div class="quiz-type-badge" :class="quizTypeBadgeClass" v-if="actualQuizData.type">
        {{ quizTypeText }}
      </div>
    </div>
    
    <!-- 퀴즈 문제 내용 -->
    <div class="quiz-question-display">
      <div class="question-content">
        <p class="question-text"><strong>{{ actualQuizData.question || '퀴즈를 로드 중입니다...' }}</strong></p>
        
        <!-- 퀴즈 타입별 안내 -->
        <div class="quiz-instruction" v-if="actualQuizData.type">
          <span class="instruction-icon">{{ instructionIcon }}</span>
          <span class="instruction-text">{{ instructionText }}</span>
        </div>
      </div>
      
      <!-- 안내 메시지 -->
      <div class="quiz-description">
        <p>💡 오른쪽 상호작용 영역에서 답변을 선택해주세요.</p>
        <p>⚠️ 답변을 제출하기 전까지는 다른 내용을 볼 수 없습니다.</p>
      </div>
      
      <!-- 로딩 상태 표시 -->
      <div v-if="isLoading || isQuizLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>퀴즈를 로드 중입니다...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'
import { useLearningStore } from '@/stores/learningStore'

// Store 사용
const learningStore = useLearningStore()

// Props 정의
const props = defineProps({
  quizData: {
    type: Object,
    required: false,
    default: () => ({
      question: '',
      type: 'multiple_choice',
      options: [],
      hint: ''
    })
  },
  isVisible: {
    type: Boolean,
    default: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

// store에서 퀴즈 데이터 가져오기 (props보다 우선)
const storeQuizData = computed(() => learningStore.quizData)
const actualQuizData = computed(() => {
  // store에 퀴즈 데이터가 있으면 store 데이터 사용, 없으면 props 사용
  if (storeQuizData.value && storeQuizData.value.question) {
    return storeQuizData.value
  }
  return props.quizData
})

// 퀴즈 데이터가 로딩 중인지 확인
const isQuizLoading = computed(() => {
  return !actualQuizData.value.question || 
         actualQuizData.value.question === '' ||
         actualQuizData.value.question.includes('로드 중입니다')
})

// 컴퓨티드 속성들
const quizTypeText = computed(() => {
  switch (actualQuizData.value.type) {
    case 'multiple_choice':
      return '객관식'
    case 'subjective':
      return '주관식'
    default:
      return '문제'
  }
})

const quizTypeBadgeClass = computed(() => {
  switch (actualQuizData.value.type) {
    case 'multiple_choice':
      return 'badge-multiple'
    case 'subjective':
      return 'badge-subjective'
    default:
      return 'badge-default'
  }
})

const instructionIcon = computed(() => {
  switch (actualQuizData.value.type) {
    case 'multiple_choice':
      return '🔘'
    case 'subjective':
      return '✏️'
    default:
      return '❓'
  }
})

const instructionText = computed(() => {
  switch (actualQuizData.value.type) {
    case 'multiple_choice':
      return '하나의 정답을 선택해주세요.'
    case 'subjective':
      return '자유롭게 답변을 작성해주세요.'
    default:
      return '문제를 확인해주세요.'
  }
})
</script>

<style scoped>
.quiz-content {
  background: linear-gradient(135deg, #fff3e0, #fce4ec);
  border-left: 4px solid #ff9800;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

/* 퀴즈 헤더 */
.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 152, 0, 0.2);
}

.quiz-header h3 {
  margin: 0;
  color: #e65100;
  font-size: 1.25rem;
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

/* 퀴즈 문제 표시 */
.quiz-question-display {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.question-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.question-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #2c3e50;
  margin: 0;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 152, 0, 0.2);
}

.quiz-instruction {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6c757d;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 0.375rem;
}

.instruction-icon {
  font-size: 1rem;
}

.instruction-text {
  font-weight: 500;
}

/* 안내 메시지 */
.quiz-description {
  background: rgba(255, 255, 255, 0.7);
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.quiz-description p {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  line-height: 1.4;
}

.quiz-description p:last-child {
  margin-bottom: 0;
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 152, 0, 0.2);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #ff9800;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  margin: 0;
  color: #6c757d;
  font-size: 0.875rem;
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
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 반응형 */
@media (max-width: 768px) {
  .quiz-content {
    padding: 1rem;
  }
  
  .quiz-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .question-text {
    font-size: 1rem;
    padding: 0.75rem;
  }
  
  .quiz-instruction {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>