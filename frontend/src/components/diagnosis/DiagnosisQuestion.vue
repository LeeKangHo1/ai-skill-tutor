<!-- frontend/src/components/diagnosis/DiagnosisQuestion.vue -->
<!-- 진단 문항 표시 및 답변 수집 컴포넌트 -->

<template>
  <div class="diagnosis-question">
    <!-- 문항 번호 -->
    <div class="question-number">
      질문 {{ questionNumber }}/{{ totalQuestions }}
    </div>
    
    <!-- 문항 내용 -->
    <div class="question-content">
      <h3>{{ question.question_text }}</h3>
    </div>
    
    <!-- 답변 선택 영역 -->
    <div class="answer-options">
      <!-- 단일 선택 문항 -->
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
      
      <!-- 다중 선택 문항 (향후 확장용) -->
      <div 
        v-else-if="question.question_type === 'multiple_choice'"
        class="multiple-choice-options"
      >
        <div 
          v-for="option in question.options" 
          :key="option.value"
          class="option-item"
          :class="{ 'selected': isMultipleSelected(option.value) }"
          @click="toggleMultipleAnswer(option.value)"
        >
          <div class="option-checkbox">
            <input 
              type="checkbox" 
              :id="`option-${option.value}`"
              :value="option.value"
              v-model="multipleSelectedAnswers"
            />
            <label :for="`option-${option.value}`"></label>
          </div>
          <div class="option-text">
            {{ option.text }}
          </div>
        </div>
      </div>
      
      <!-- 텍스트 입력 문항 (향후 확장용) -->
      <div 
        v-else-if="question.question_type === 'text_input'"
        class="text-input-option"
      >
        <textarea
          v-model="textAnswer"
          :placeholder="question.placeholder || '답변을 입력해주세요'"
          @input="handleTextInput"
        ></textarea>
      </div>
    </div>
    
    <!-- 네비게이션 버튼 -->
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
    
    // 문항 번호
    questionNumber: {
      type: Number,
      required: true
    },
    
    // 전체 문항 수
    totalQuestions: {
      type: Number,
      required: true
    },
    
    // 기존 답변 (수정 시)
    existingAnswer: {
      type: [String, Array],
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
  
  emits: ['answer', 'next', 'previous'],
  
  data() {
    return {
      selectedAnswer: null,
      multipleSelectedAnswers: [],
      textAnswer: ''
    }
  },
  
  computed: {
    // 답변 여부 확인
    hasAnswer() {
      switch (this.question.question_type) {
        case 'single_choice':
          return this.selectedAnswer !== null
        case 'multiple_choice':
          return this.multipleSelectedAnswers.length > 0
        case 'text_input':
          return this.textAnswer.trim().length > 0
        default:
          return false
      }
    }
  },
  
  watch: {
    // 문항 변경 시 답변 상태 초기화 후 기존 답변 로드
    question: {
      immediate: true,
      handler() {
        this.resetAnswerState()
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
     * 답변 상태 초기화
     */
    resetAnswerState() {
      this.selectedAnswer = null
      this.multipleSelectedAnswers = []
      this.textAnswer = ''
    },
    
    /**
     * 기존 답변 로드
     */
    loadExistingAnswer() {
      if (!this.existingAnswer) return
      
      switch (this.question.question_type) {
        case 'single_choice':
          this.selectedAnswer = this.existingAnswer
          break
        case 'multiple_choice':
          this.multipleSelectedAnswers = Array.isArray(this.existingAnswer) 
            ? [...this.existingAnswer] 
            : [this.existingAnswer]
          break
        case 'text_input':
          this.textAnswer = this.existingAnswer
          break
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
     * 다중 선택 답변 토글
     */
    toggleMultipleAnswer(value) {
      const index = this.multipleSelectedAnswers.indexOf(value)
      if (index > -1) {
        this.multipleSelectedAnswers.splice(index, 1)
      } else {
        this.multipleSelectedAnswers.push(value)
      }
      // 마지막 문항이 아닌 경우에만 즉시 답변 저장
      if (!this.isLastQuestion) {
        this.$emit('answer', this.question.question_id, [...this.multipleSelectedAnswers])
      }
    },
    
    /**
     * 다중 선택 선택 여부 확인
     */
    isMultipleSelected(value) {
      return this.multipleSelectedAnswers.includes(value)
    },
    
    /**
     * 텍스트 입력 처리
     */
    handleTextInput() {
      // 마지막 문항이 아닌 경우에만 즉시 답변 저장
      if (!this.isLastQuestion) {
        this.$emit('answer', this.question.question_id, this.textAnswer.trim())
      }
    },
    
    /**
     * 다음 버튼 클릭 처리
     */
    handleNext() {
      if (!this.hasAnswer) return
      
      // 현재 답변 저장 (모든 문항에서 버튼 클릭 시에만 저장)
      let answer
      switch (this.question.question_type) {
        case 'single_choice':
          answer = this.selectedAnswer
          break
        case 'multiple_choice':
          answer = [...this.multipleSelectedAnswers]
          break
        case 'text_input':
          answer = this.textAnswer.trim()
          break
      }
      
      this.$emit('answer', this.question.question_id, answer)
      
      // 마지막 문항이 아닌 경우에만 다음으로 이동
      if (!this.isLastQuestion) {
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
  
  .question-number {
    font-size: 0.9rem;
    color: #6c757d;
    margin-bottom: 1rem;
    text-align: center;
  }
  
  .question-content {
    margin-bottom: 2rem;
    text-align: center;
    
    h3 {
      font-size: 1.3rem;
      font-weight: 600;
      color: #212529;
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
      border: 2px solid #e9ecef;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: #007bff;
        background-color: #f8f9fa;
      }
      
      &.selected {
        border-color: #007bff;
        background-color: #e3f2fd;
      }
      
      .option-radio,
      .option-checkbox {
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
          border: 2px solid #dee2e6;
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
            background-color: #007bff;
            opacity: 0;
            transition: opacity 0.3s ease;
          }
        }
        
        input:checked + label::after {
          opacity: 1;
        }
      }
      
      .option-checkbox label {
        border-radius: 3px;
        
        &::after {
          width: 6px;
          height: 10px;
          border: 2px solid #007bff;
          border-top: 0;
          border-left: 0;
          transform: translate(-50%, -60%) rotate(45deg);
          border-radius: 0;
          background-color: transparent;
        }
      }
      
      .option-text {
        flex: 1;
        font-size: 1rem;
        color: #495057;
      }
    }
    
    .text-input-option {
      textarea {
        width: 100%;
        min-height: 120px;
        padding: 1rem;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        font-size: 1rem;
        resize: vertical;
        
        &:focus {
          outline: none;
          border-color: #007bff;
        }
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
        background-color: #6c757d;
        color: white;
        
        &:hover:not(:disabled) {
          background-color: #5a6268;
        }
      }
      
      &.btn-primary {
        background-color: #007bff;
        color: white;
        
        &:hover:not(:disabled) {
          background-color: #0056b3;
        }
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

// 반응형 디자인
@media (max-width: 768px) {
  .diagnosis-question {
    padding: 1rem;
    
    .question-content h3 {
      font-size: 1.1rem;
    }
    
    .navigation-buttons {
      .btn {
        padding: 0.6rem 1.5rem;
        font-size: 0.9rem;
      }
    }
  }
}
</style>