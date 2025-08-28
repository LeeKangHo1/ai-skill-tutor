<!-- frontend/src/components/learning/QuizInteraction.vue -->
<template>
  <!-- 퀴즈 데이터가 있을 경우에만 전체 UI를 렌더링합니다. -->
  <div v-if="quizData" class="quiz-interaction active">
    
    <!-- 스크롤이 필요한 경우를 대비한 상호작용 컨텐츠 영역 -->
    <div class="interaction-content">
      <!-- 퀴즈 유형이 '객관식'일 때의 UI -->
      <div v-if="quizData.quiz_type === 'multiple_choice'" class="quiz-options">
        <!-- 객관식 옵션 헤더 -->
        <div class="options-header">
          <h4>답안을 선택해주세요</h4>
        </div>

        <!-- v-for 디렉티브를 사용해 Store의 quizData에 있는 선택지들을 반복 렌더링합니다. -->
        <div v-for="(option, index) in quizData.options" :key="index" class="quiz-option" 
             :class="{
               'selected': selectedAnswer === (index + 1).toString(),
               'disabled': isSubmitted
             }"
             @click="selectOption((index + 1).toString())">
          
          <!-- 선택 여부를 시각적으로 표시하는 인디케이터 -->
          <div class="option-indicator">
            {{ selectedAnswer === (index + 1).toString() ? '●' : '○' }}
          </div>
          <!-- 선택지 내용 -->
          <div class="option-content">
            <span class="option-number">{{ index + 1 }}.</span>
            <span class="option-text">{{ cleanOptionText(option) }}</span>
          </div>
        </div>
      </div>

      <!-- 퀴즈 유형이 '주관식'일 때의 UI -->
      <div v-else-if="quizData.quiz_type === 'subjective'" class="subjective-input-container">
        <div class="input-header">
          <h4>답안을 작성해주세요.</h4>
          <span class="input-guide">자세하고 구체적일수록 좋습니다.</span>
        </div>
        <!-- 주관식 답변을 입력받는 textarea -->
        <textarea v-model="subjectiveAnswer" ref="subjectiveInputRef" class="subjective-input"
          placeholder="답변을 입력해주세요... (최대 500자)" 
          :disabled="isSubmitted" 
          rows="4"></textarea>
      </div>
    </div>

    <!-- 힌트가 존재하고, 사용자가 힌트 보기를 클릭했을 때 표시되는 영역 -->
    <div v-if="showHint && quizData.hint" class="hint-container">
      <div class="hint-content">
        <div class="hint-icon">💡</div>
        <div class="hint-text">{{ quizData.hint }}</div>
      </div>
    </div>

    <!-- 하단 버튼 (힌트 보기, 정답 제출) 영역 -->
    <div class="quiz-actions">
      <!-- 힌트 보기/숨기기 버튼 -->
      <button class="btn btn-secondary hint-btn" @click="toggleHint" :disabled="isSubmitted" v-if="quizData.hint && !isSubmitted">
        {{ showHint ? '🔍 힌트 숨기기' : '💡 힌트 보기' }}
      </button>

      <!-- 정답 제출 버튼 (아직 제출하지 않았을 때만 보임) -->
      <button class="btn btn-primary submit-btn" @click="submitAnswer" :disabled="!canSubmit" v-if="!isSubmitted">
        정답 제출
      </button>

      <!-- 답변을 제출한 후에 표시되는 메시지 -->
      <div v-if="isSubmitted" class="post-submit-actions">
        <div class="submit-success">
          ✅ 답변이 제출되었습니다!
        </div>
        <div class="evaluation-loading-message">
          <span class="loading-text">평가를 기다려주세요</span>
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

  </div>

  <!-- 퀴즈 데이터가 없을 때 로딩 상태 표시 -->
  <div v-else class="quiz-loading">
    <div class="loading-spinner"></div>
    <p>퀴즈를 준비하고 있습니다...</p>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

// --- 스토어 연결 ---
const learningStore = useLearningStore()
// Store의 quizData 상태를 반응성을 유지한 채로 가져옵니다.
const { quizData } = storeToRefs(learningStore)

console.log('[QuizInteraction] 🟢 컴포넌트 초기화. Store와 연결되었습니다.')

// --- 로컬 상태 (컴포넌트 내 UI 제어용) ---
const selectedAnswer = ref('') // 객관식 선택 답안
const subjectiveAnswer = ref('') // 주관식 작성 답안
const showHint = ref(false) // 힌트 표시 여부
const isSubmitted = ref(false) // 사용자가 제출 버튼을 눌렀는지 여부 (UI 비활성화용)

// --- 컴퓨티드 속성 ---

// 제출 버튼 활성화 여부를 결정합니다.
const canSubmit = computed(() => {
  // 이미 제출했다면 비활성화
  if (isSubmitted.value) return false
  // 퀴즈 데이터가 없으면 비활성화
  if (!quizData.value) return false

  // 퀴즈 유형에 따라 제출 가능 조건을 다르게 설정합니다.
  if (quizData.value.quiz_type === 'multiple_choice') {
    return selectedAnswer.value !== '' // 객관식은 답을 선택해야만 활성화
  } else if (quizData.value.quiz_type === 'subjective') {
    return subjectiveAnswer.value.trim().length > 0 // 주관식은 내용을 입력해야만 활성화
  }
  return false
})

// --- 메서드 ---

// 객관식 옵션을 선택했을 때 호출되는 함수
const selectOption = (value) => {
  if (isSubmitted.value) return // 제출 후에는 동작하지 않음
  selectedAnswer.value = value
}

// 힌트 보기/숨기기 버튼을 클릭했을 때 호출되는 함수
const toggleHint = () => {
  if (isSubmitted.value) return
  showHint.value = !showHint.value
}

// 정답 제출 시 Store의 액션을 호출합니다.
const submitAnswer = () => {
  if (!canSubmit.value) return // 제출 불가능 상태면 함수 종료

  // 퀴즈 유형에 맞는 답안을 결정합니다.
  const answer = quizData.value.quiz_type === 'multiple_choice'
    ? selectedAnswer.value
    : subjectiveAnswer.value.trim()

  console.log('[QuizInteraction] 📥 답안 제출. Store 액션을 호출합니다.', { answer })
  isSubmitted.value = true // 제출 상태로 변경하여 UI를 잠급니다.
  learningStore.sendMessage(answer) // Store의 sendMessage 액션을 호출하여 답안을 서버로 전송
}

// --- 유틸리티 함수 ---

// API에서 받은 선택지 텍스트에서 '1.', 'A.', 'a.' 등 불필요한 번호를 모두 제거합니다.
const cleanOptionText = (option) => {
  const text = typeof option === 'string' ? option : (option.text || String(option));
  // ex) '1. A. 단어' 또는 ' a. 단어' 같은 패턴을 제거하는 정규식
  const pattern = /^(\s*(\d+\.|[A-Za-z]\.)\s*)+/;
  return text.replace(pattern, '').trim();
}

// --- 감시자 ---

// Store의 quizData가 변경되면 (새로운 퀴즈가 출제되면) 로컬 상태를 초기화합니다.
watch(quizData, (newQuizData) => {
  if (newQuizData) {
    console.log('[QuizInteraction] 🔄 새로운 퀴즈 데이터를 Store로부터 받았습니다.', newQuizData)
    // 모든 로컬 상태를 초기값으로 리셋합니다.
    selectedAnswer.value = ''
    subjectiveAnswer.value = ''
    showHint.value = false
    isSubmitted.value = false 
  }
}, { deep: true, immediate: true })
</script>

<style lang="scss" scoped>
/* --- Layout --- */
.quiz-interaction {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  height: 100%;
  padding: $spacing-md;
  background: $white;
  border: 1px solid $gray-300;
  border-radius: $border-radius-lg;
  transition: opacity 0.3s ease;
  overflow: hidden;
}

.quiz-interaction.active {
  opacity: 1;
}

.interaction-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  overflow-y: auto;
  min-height: 0;
  padding-right: $spacing-sm;

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: $gray-100;
    border-radius: 3px;
  }
  &::-webkit-scrollbar-thumb {
    background: $gray-400;
    border-radius: 3px;
  }
  &::-webkit-scrollbar-thumb:hover {
    background: $gray-500;
  }
}

/* --- Loading --- */
.quiz-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: $spacing-lg;
  flex: 1;
  padding: $spacing-lg * 2 1rem;
  text-align: center;
  color: $secondary;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid $gray-200;
  border-top: 4px solid $primary;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.quiz-loading p {
  margin: 0;
  font-size: $font-size-base;
  font-weight: 500;
  color: $gray-700;
}

/* --- Headers --- */
.options-header,
.input-header {
  padding-bottom: $spacing-sm;
  border-bottom: 1px solid $gray-200;
  margin-bottom: $spacing-sm;
}

.options-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: $spacing-xs;
}

.options-header h4,
.input-header h4 {
  margin: 0;
  font-size: $font-size-base;
  font-weight: 600;
  color: $text-dark;
}

.input-guide {
  font-size: $font-size-sm;
  color: $secondary;
}

/* --- Multiple Choice --- */
.quiz-options {
  display: flex;
  flex-direction: column;
  gap: $spacing-md * 0.75;
  flex: 1;
  min-height: 0;
}

.quiz-option {
  display: flex;
  align-items: center;
  gap: $spacing-md * 0.75;
  padding: $spacing-md;
  border: 1px solid $gray-300;
  border-radius: $border-radius-lg;
  background: $white;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(.disabled) {
    background: $gray-100;
    border-color: $primary;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba($primary, 0.15);
  }

  &.selected {
    background: lighten($primary, 40%);
    border-color: $primary;
    box-shadow: 0 0 0 2px rgba($primary, 0.25);
  }

  &.disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.option-indicator {
  min-width: 20px;
  font-size: $font-size-lg;
  font-weight: bold;
  color: $primary;
}

.option-content {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  flex: 1;
}

.option-number {
  font-weight: 500;
  color: $gray-700;
}

.option-text {
  line-height: 1.4;
}

/* --- Subjective (Short-answer) --- */
.subjective-input-container {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
  height: 100%;
}

.subjective-input {
  flex-grow: 1;
  width: 100%;
  min-height: 150px;
  padding: $spacing-md;
  border: 1px solid $gray-300;
  border-radius: $border-radius-lg;
  font-size: $font-size-sm;
  line-height: 1.6;
  color: $text-dark;
  resize: vertical;
  transition: all 0.2s ease-in-out;

  &:focus {
    outline: none;
    border-color: $primary;
    box-shadow: 0 0 0 3px rgba($primary, 0.15);
  }

  &:disabled {
    background-color: $gray-100;
    cursor: not-allowed;
  }
}

/* --- Hint --- */
.hint-container {
  padding: $spacing-md;
  background: lighten($warning, 35%);
  border: 1px solid lighten($warning, 30%);
  border-radius: $border-radius-lg;
  animation: hintSlideIn 0.3s ease-out;
  flex-shrink: 0;
}

.hint-content {
  display: flex;
  align-items: flex-start;
  gap: $spacing-md * 0.75;
}

.hint-icon {
  font-size: $font-size-lg;
}

.hint-text {
  font-weight: 500;
  line-height: 1.5;
  color: darken($warning, 40%);
}

/* --- Actions & Buttons --- */
.quiz-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: $spacing-md * 0.75;
  padding-top: $spacing-md;
  border-top: 1px solid $gray-200;
  margin-top: auto; /* Pushes actions to the bottom */
  flex-shrink: 0;
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 80px;
  padding: $spacing-md * 0.75 $spacing-md;
  border: none;
  border-radius: $border-radius;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: $primary;
  color: $white;
  &:hover:not(:disabled) {
    background: darken($primary, 10%);
    transform: translateY(-1px);
  }
}

.btn-secondary {
  background: $secondary;
  color: $white;
  &:hover:not(:disabled) {
    background: darken($secondary, 10%);
    transform: translateY(-1px);
  }
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

/* --- Post-Submission --- */
.post-submit-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-sm;
  width: 100%;
}

.submit-success {
  width: 100%;
  padding: $spacing-sm $spacing-md;
  background: lighten($success, 45%);
  border: 1px solid lighten($success, 40%);
  border-radius: $border-radius;
  color: $success;
  font-weight: 500;
  text-align: center;
}

.evaluation-loading-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  width: 100%;
  padding: $spacing-sm $spacing-md;
  background: $gray-100;
  border: 1px solid $gray-200;
  border-radius: $border-radius;
  color: $gray-700;
  font-size: $font-size-sm;
  font-weight: 500;
}

.loading-text {
  line-height: 1.5;
  color: $gray-700;
}

/* --- Animations --- */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
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

.typing-indicator {
  display: flex;
  align-items: center;
  height: 1.2rem;

  span {
    height: 8px;
    width: 8px;
    margin: 0 2px;
    background-color: $gray-600;
    border-radius: 50%;
    display: inline-block;
    animation: bounce 1.4s infinite both;
  }

  span:nth-child(1) {
    animation-delay: -0.32s;
  }
  span:nth-child(2) {
    animation-delay: -0.16s;
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1.0);
  }
}
</style>