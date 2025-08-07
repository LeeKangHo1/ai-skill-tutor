<!-- frontend/src/components/diagnosis/DiagnosisQuestion.vue -->
<template>
  <div class="diagnosis-question">
    <!-- 질문 헤더 -->
    <div class="question-header">
      <div class="question-number">
        질문 {{ currentQuestionIndex + 1 }} / {{ totalQuestions }}
      </div>
      <div class="question-category" v-if="question.category">
        {{ question.category }}
      </div>
    </div>

    <!-- 질문 내용 -->
    <div class="question-content">
      <h3 class="question-title">{{ question.title }}</h3>
      <p v-if="question.description" class="question-description">
        {{ question.description }}
      </p>
    </div>

    <!-- 답변 옵션 -->
    <div class="answer-options">
      <div
        v-for="(option, index) in question.options"
        :key="index"
        class="option-item"
        :class="{ 
          'selected': selectedAnswer === option.value,
          'disabled': isLoading 
        }"
        @click="handleOptionSelect(option.value)"
      >
        <!-- 라디오 버튼 -->
        <div class="option-radio">
          <input
            :id="`option-${index}`"
            v-model="selectedAnswer"
            :value="option.value"
            type="radio"
            :name="`question-${currentQuestionIndex}`"
            :disabled="isLoading"
            class="radio-input"
          />
          <div class="radio-custom"></div>
        </div>

        <!-- 옵션 내용 -->
        <label :for="`option-${index}`" class="option-content">
          <div class="option-text">{{ option.text }}</div>
          <div v-if="option.description" class="option-description">
            {{ option.description }}
          </div>
        </label>
      </div>
    </div>

    <!-- 추가 입력 필드 (선택적) -->
    <div v-if="question.allowCustomInput && selectedAnswer === 'custom'" class="custom-input">
      <label for="customAnswer" class="custom-label">직접 입력:</label>
      <textarea
        id="customAnswer"
        v-model="customAnswer"
        class="custom-textarea"
        :placeholder="question.customInputPlaceholder || '자세한 내용을 입력해주세요'"
        :disabled="isLoading"
        rows="3"
      ></textarea>
    </div>

    <!-- 네비게이션 버튼 -->
    <div class="question-navigation">
      <button
        v-if="currentQuestionIndex > 0"
        @click="handlePrevious"
        class="nav-btn prev-btn"
        :disabled="isLoading"
      >
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        </svg>
        이전
      </button>

      <button
        @click="handleNext"
        class="nav-btn next-btn"
        :disabled="!canProceed || isLoading"
      >
        {{ isLastQuestion ? '완료' : '다음' }}
        <svg v-if="!isLastQuestion" viewBox="0 0 24 24" fill="currentColor">
          <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
      </button>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span class="loading-text">처리 중...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// Props 정의
const props = defineProps({
  // 현재 질문 데이터
  question: {
    type: Object,
    required: true,
    validator: (question) => {
      return question.title && question.options && Array.isArray(question.options)
    }
  },
  // 현재 질문 인덱스
  currentQuestionIndex: {
    type: Number,
    required: true
  },
  // 전체 질문 수
  totalQuestions: {
    type: Number,
    required: true
  },
  // 초기 선택된 답변
  initialAnswer: {
    type: [String, Number],
    default: null
  },
  // 로딩 상태
  isLoading: {
    type: Boolean,
    default: false
  }
})

// 이벤트 정의
const emit = defineEmits(['answer-change', 'next', 'previous', 'complete'])

// 반응형 데이터
const selectedAnswer = ref(props.initialAnswer)
const customAnswer = ref('')

// 계산된 속성
const isLastQuestion = computed(() => {
  return props.currentQuestionIndex === props.totalQuestions - 1
})

const canProceed = computed(() => {
  if (!selectedAnswer.value) return false
  
  // 커스텀 입력이 필요한 경우 추가 검증
  if (selectedAnswer.value === 'custom' && props.question.allowCustomInput) {
    return customAnswer.value.trim().length > 0
  }
  
  return true
})

// 옵션 선택 처리
const handleOptionSelect = (value) => {
  if (props.isLoading) return
  
  selectedAnswer.value = value
  
  // 커스텀 입력이 아닌 경우 커스텀 답변 초기화
  if (value !== 'custom') {
    customAnswer.value = ''
  }
}

// 다음 버튼 클릭 처리
const handleNext = () => {
  if (!canProceed.value || props.isLoading) return

  const answerData = {
    questionIndex: props.currentQuestionIndex,
    answer: selectedAnswer.value,
    customAnswer: selectedAnswer.value === 'custom' ? customAnswer.value : null,
    question: props.question
  }

  if (isLastQuestion.value) {
    emit('complete', answerData)
  } else {
    emit('next', answerData)
  }
}

// 이전 버튼 클릭 처리
const handlePrevious = () => {
  if (props.isLoading) return

  const answerData = {
    questionIndex: props.currentQuestionIndex,
    answer: selectedAnswer.value,
    customAnswer: selectedAnswer.value === 'custom' ? customAnswer.value : null,
    question: props.question
  }

  emit('previous', answerData)
}

// 답변 변경 감지
watch([selectedAnswer, customAnswer], () => {
  const answerData = {
    questionIndex: props.currentQuestionIndex,
    answer: selectedAnswer.value,
    customAnswer: selectedAnswer.value === 'custom' ? customAnswer.value : null,
    question: props.question
  }

  emit('answer-change', answerData)
}, { deep: true })

// 초기 답변 변경 감지
watch(() => props.initialAnswer, (newAnswer) => {
  selectedAnswer.value = newAnswer
}, { immediate: true })
</script>

<style lang="scss" scoped>
.diagnosis-question {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: relative;

  .question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border-light);

    .question-number {
      font-size: 0.875rem;
      font-weight: 600;
      color: var(--primary-color);
      background: rgba(var(--primary-color-rgb), 0.1);
      padding: 0.5rem 1rem;
      border-radius: 20px;
    }

    .question-category {
      font-size: 0.875rem;
      color: var(--text-secondary);
      background: var(--bg-light);
      padding: 0.5rem 1rem;
      border-radius: 20px;
    }
  }

  .question-content {
    margin-bottom: 2rem;

    .question-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0 0 1rem 0;
      line-height: 1.4;
    }

    .question-description {
      font-size: 1rem;
      color: var(--text-secondary);
      line-height: 1.6;
      margin: 0;
    }
  }

  .answer-options {
    margin-bottom: 2rem;

    .option-item {
      display: flex;
      align-items: flex-start;
      padding: 1rem;
      border: 2px solid var(--border-color);
      border-radius: 12px;
      margin-bottom: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover:not(.disabled) {
        border-color: var(--primary-color);
        background-color: rgba(var(--primary-color-rgb), 0.02);
      }

      &.selected {
        border-color: var(--primary-color);
        background-color: rgba(var(--primary-color-rgb), 0.05);

        .radio-custom {
          border-color: var(--primary-color);
          background-color: var(--primary-color);

          &::after {
            opacity: 1;
          }
        }
      }

      &.disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      .option-radio {
        margin-right: 1rem;
        margin-top: 0.125rem;

        .radio-input {
          display: none;
        }

        .radio-custom {
          width: 20px;
          height: 20px;
          border: 2px solid var(--border-color);
          border-radius: 50%;
          position: relative;
          transition: all 0.2s ease;

          &::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 8px;
            height: 8px;
            background-color: white;
            border-radius: 50%;
            opacity: 0;
            transition: opacity 0.2s ease;
          }
        }
      }

      .option-content {
        flex: 1;
        cursor: pointer;

        .option-text {
          font-size: 1rem;
          font-weight: 500;
          color: var(--text-primary);
          margin-bottom: 0.25rem;
        }

        .option-description {
          font-size: 0.875rem;
          color: var(--text-secondary);
          line-height: 1.4;
        }
      }
    }
  }

  .custom-input {
    margin-bottom: 2rem;

    .custom-label {
      display: block;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 0.5rem;
    }

    .custom-textarea {
      width: 100%;
      padding: 0.75rem;
      border: 2px solid var(--border-color);
      border-radius: 8px;
      font-size: 1rem;
      font-family: inherit;
      resize: vertical;
      min-height: 80px;
      transition: all 0.2s ease;

      &:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.1);
      }

      &:disabled {
        background-color: var(--bg-disabled);
        cursor: not-allowed;
      }
    }
  }

  .question-navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;

    .nav-btn {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;

      svg {
        width: 20px;
        height: 20px;
      }

      &.prev-btn {
        background-color: var(--bg-light);
        color: var(--text-secondary);

        &:hover:not(:disabled) {
          background-color: var(--border-color);
          color: var(--text-primary);
        }
      }

      &.next-btn {
        background-color: var(--primary-color);
        color: white;
        margin-left: auto;

        &:hover:not(:disabled) {
          background-color: var(--primary-color-dark);
          transform: translateY(-1px);
        }
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
      }
    }
  }

  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    z-index: 10;

    .loading-spinner {
      width: 32px;
      height: 32px;
      border: 3px solid #f3f3f3;
      border-top: 3px solid var(--primary-color);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }

    .loading-text {
      color: var(--text-secondary);
      font-weight: 500;
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 반응형 디자인
@media (max-width: 768px) {
  .diagnosis-question {
    padding: 1.5rem;
    margin: 1rem;

    .question-header {
      flex-direction: column;
      gap: 0.5rem;
      align-items: flex-start;
    }

    .question-content {
      .question-title {
        font-size: 1.25rem;
      }
    }

    .answer-options {
      .option-item {
        padding: 0.75rem;

        .option-radio {
          margin-right: 0.75rem;
        }
      }
    }

    .question-navigation {
      .nav-btn {
        padding: 0.625rem 1.25rem;
        font-size: 0.9rem;

        svg {
          width: 18px;
          height: 18px;
        }
      }
    }
  }
}
</style>