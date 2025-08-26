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

// store에서 퀴즈 데이터 가져오기 (캐시 없이 현재 데이터만 사용)
const storeQuizData = computed(() => learningStore.quizData)
const actualQuizData = computed(() => {
  // 캐시된 데이터 사용하지 않고 현재 store 데이터만 사용
  if (storeQuizData.value && storeQuizData.value.question && !storeQuizData.value.question.includes('로드 중입니다')) {
    console.log('QuizContent - store에서 퀴즈 데이터 사용:', storeQuizData.value)
    return storeQuizData.value
  }
  console.log('QuizContent - props에서 퀴즈 데이터 사용:', props.quizData)
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

<style lang="scss" scoped>
.quiz-content {
  background: linear-gradient(135deg, lighten($warning, 40%), lighten($danger, 45%));
  border-left: 4px solid $warning;
  padding: $spacing-lg;
  border-radius: $border-radius-lg;
  margin-bottom: $spacing-md;
}

/* 퀴즈 헤더 */
.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
  padding-bottom: $spacing-md * 0.75;
  border-bottom: 1px solid rgba($warning, 0.2);
}

.quiz-header h3 {
  margin: 0;
  color: darken($warning, 30%);
  font-size: $font-size-lg;
}

.quiz-type-badge {
  padding: $spacing-xs $spacing-md * 0.75;
  border-radius: $border-radius-pill;
  font-weight: 500;
  font-size: $font-size-sm * 0.85; // 0.75rem
}

.badge-multiple {
  background: lighten($primary, 40%);
  color: darken($primary, 10%);
}

.badge-subjective {
  background: lighten($brand-purple, 40%);
  color: darken($brand-purple, 5%);
}

.badge-default {
  background: $gray-100;
  color: $gray-700;
}

/* 퀴즈 문제 표시 */
.quiz-question-display {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.question-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-md * 0.75;
}

.question-text {
  font-size: $font-size-base * 1.1;
  line-height: 1.6;
  color: $text-dark;
  margin: 0;
  padding: $spacing-md;
  background: rgba($white, 0.8);
  border-radius: $border-radius-lg;
  border: 1px solid rgba($warning, 0.2);
}

.quiz-instruction {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: $font-size-sm;
  color: $secondary;
  padding: $spacing-sm $spacing-md;
  background: rgba($white, 0.6);
  border-radius: $border-radius;
}

.instruction-icon {
  font-size: $font-size-base;
}

.instruction-text {
  font-weight: 500;
}

/* 안내 메시지 */
.quiz-description {
  background: rgba($white, 0.7);
  padding: $spacing-md;
  border-radius: $border-radius;
  border: 1px solid rgba($warning, 0.3);
}

.quiz-description p {
  margin-bottom: $spacing-sm;
  font-size: $font-size-sm;
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
  gap: $spacing-md * 0.75;
  padding: $spacing-lg * 1.33; // 2rem
  background: rgba($white, 0.8);
  border-radius: $border-radius-lg;
  border: 1px solid rgba($warning, 0.2);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid $gray-100;
  border-top: 3px solid $warning;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  margin: 0;
  color: $secondary;
  font-size: $font-size-sm;
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
</style>