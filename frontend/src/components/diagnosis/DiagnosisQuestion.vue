<!-- frontend/src/components/diagnosis/DiagnosisQuestion.vue -->
<!-- 진단 문항 표시 및 답변 수집 컴포넌트 -->

<template>
  <div class="diagnosis-question">
    <div class="question-content">
      <h3>{{ question.question_text }}</h3>
    </div>
    
    <div class="answer-options">
      <div 
        v-if="question.question_type === 'single_choice'"
        class="single-choice-options"
      >
        <div 
          v-for="option in question.options" 
          :key="option.value"
          class="option-item"
          :class="{ 'selected': selectedAnswer === option.value }"
          @click="selectAnswer(option.value)"
        >
          <div class="option-radio">
            <input 
              type="radio" 
              :id="`option-${option.value}`"
              :value="option.value"
              v-model="selectedAnswer"
              @change="selectAnswer(option.value)"
            />
            <label :for="`option-${option.value}`"></label>
          </div>
          <div class="option-text">
            {{ option.text }}
          </div>
        </div>
      </div>
    </div>
    
    <div class="navigation-buttons">
      <button 
        class="btn btn-secondary"
        @click="$emit('previous')"
        :disabled="isFirstQuestion"
      >
        이전
      </button>
      
      <button 
        class="btn btn-primary"
        @click="handleNext"
        :disabled="!hasAnswer"
      >
        {{ isLastQuestion ? '답변 완료' : '다음' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DiagnosisQuestion',
  
  props: {
    // 문항 데이터
    question: {
      type: Object,
      required: true
    },
    
    // 기존 답변 (수정 시)
    existingAnswer: {
      type: String,
      default: null
    },
    
    // 첫 번째 문항 여부
    isFirstQuestion: {
      type: Boolean,
      default: false
    },
    
    // 마지막 문항 여부
    isLastQuestion: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['answer', 'next', 'previous', 'complete'],
  
  data() {
    return {
      selectedAnswer: null
    }
  },
  
  computed: {
    // 답변 여부 확인
    hasAnswer() {
      return this.selectedAnswer !== null
    }
  },
  
  watch: {
    // 문항 변경 시 답변 상태 초기화 후 기존 답변 로드
    question: {
      immediate: true,
      handler() {
        this.selectedAnswer = null
        this.loadExistingAnswer()
      }
    },
    
    existingAnswer: {
      immediate: true,
      handler() {
        this.loadExistingAnswer()
      }
    }
  },
  
  methods: {
    /**
     * 기존 답변 로드
     */
    loadExistingAnswer() {
      if (this.existingAnswer) {
        this.selectedAnswer = this.existingAnswer
      }
    },
    
    /**
     * 단일 선택 답변 선택
     */
    selectAnswer(value) {
      this.selectedAnswer = value
      // 마지막 문항이 아닌 경우에만 즉시 답변 저장
      if (!this.isLastQuestion) {
        this.$emit('answer', this.question.question_id, value)
      }
    },
    
    /**
     * 다음 버튼 클릭 처리
     */
    handleNext() {
      if (!this.hasAnswer) return
      
      // 현재 답변 저장
      this.$emit('answer', this.question.question_id, this.selectedAnswer)
      
      // 마지막 문항인 경우 바로 진단 완료 처리
      if (this.isLastQuestion) {
        this.$emit('complete')
      } else {
        this.$emit('next')
      }
    }
  }
}
</script>

<style scoped lang="scss">
.diagnosis-question {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  
  .question-content {
    margin-bottom: 2rem;
    text-align: center;
    
    h3 {
      font-size: 1.3rem;
      font-weight: 600;
      color: $gray-900;
      line-height: 1.4;
      margin: 0;
    }
  }
  
  .answer-options {
    margin-bottom: 2rem;
    
    .option-item {
      display: flex;
      align-items: center;
      padding: 1rem;
      margin-bottom: 0.5rem;
      border: 2px solid $gray-200;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: $primary;
        background-color: $gray-100;
      }
      
      &.selected {
        border-color: $primary;
        background-color: lighten($primary, 35%);
      }
      
      .option-radio {
        margin-right: 1rem;
        position: relative;
        
        input {
          opacity: 0;
          position: absolute;
        }
        
        label {
          display: block;
          width: 20px;
          height: 20px;
          border: 2px solid $gray-300;
          border-radius: 50%;
          position: relative;
          cursor: pointer;
          
          &::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: $primary;
            opacity: 0;
            transition: opacity 0.3s ease;
          }
        }
        
        input:checked + label::after {
          opacity: 1;
        }
      }
      
      .option-text {
        flex: 1;
        font-size: 1rem;
        color: $gray-700;
      }
    }
  }
  
  .navigation-buttons {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    
    .btn {
      padding: 0.75rem 2rem;
      border-radius: 8px;
      border: none;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &.btn-secondary {
        background-color: $secondary;
        color: $white;
        
        &:hover:not(:disabled) {
          background-color: darken($secondary, 10%);
        }
      }
      
      &.btn-primary {
        background-color: $primary;
        color: $white;
        
        &:hover:not(:disabled) {
          background-color: darken($primary, 10%);
        }
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}
</style>