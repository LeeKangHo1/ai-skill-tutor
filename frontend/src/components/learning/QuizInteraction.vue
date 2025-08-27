<!-- frontend/src/components/learning/QuizInteraction.vue -->
<template>
  <div v-if="quizData" class="quiz-interaction active">
    
    <div class="interaction-content">
      <div v-if="quizData.type === 'multiple_choice'" class="quiz-options">
        <div class="options-header">
          <h4>답안을 선택해주세요</h4>
          <span class="options-count">{{ quizData.options?.length || 0 }}개 선택지</span>
        </div>

        <div v-for="(option, index) in quizData.options" :key="index" class="quiz-option" :class="{
          'selected': selectedAnswer === (index + 1).toString(),
          'disabled': isContentLoading || isSubmitted
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

      <div v-else-if="quizData.type === 'subjective'" class="subjective-input-container">
        <div class="input-header">
          <h4>답안을 작성해주세요</h4>
          <span class="input-guide">자세하고 구체적으로 작성해주세요</span>
        </div>
        <textarea v-model="subjectiveAnswer" ref="subjectiveInputRef" class="subjective-input"
          placeholder="답변을 입력해주세요... (최대 500자)" :disabled="isContentLoading || isSubmitted" rows="4"></textarea>
      </div>
    </div>

    <div v-if="showHint && quizData.hint" class="hint-container">
      <div class="hint-content">
        <div class="hint-icon">💡</div>
        <div class="hint-text">{{ quizData.hint }}</div>
      </div>
    </div>

    <div class="quiz-actions">
      <button class="btn btn-secondary hint-btn" @click="toggleHint" :disabled="isContentLoading || isSubmitted" v-if="quizData.hint">
        {{ showHint ? '🔍 힌트 숨기기' : '💡 힌트 보기' }}
      </button>

      <button class="btn btn-primary submit-btn" @click="submitAnswer" :disabled="!canSubmit || isContentLoading" v-if="!isSubmitted">
        <span v-if="isContentLoading" class="button-spinner"></span>
        <span v-else>정답 제출</span>
      </button>

      <div v-if="isSubmitted" class="post-submit-actions">
        <div class="submit-success">
          ✅ 답변이 제출되었습니다! 평가를 기다려주세요...
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

// [리팩토링] props와 emits를 모두 제거하고, 모든 데이터와 액션은 store를 통해 관리합니다.

// --- 1. 스토어 연결 ---
const learningStore = useLearningStore()
const { quizData, isContentLoading } = storeToRefs(learningStore)

console.log('[QuizInteraction] 🟢 컴포넌트 초기화. Store와 연결되었습니다.')

// --- 2. 로컬 상태 (컴포넌트 내 UI 제어용) ---
const selectedAnswer = ref('')
const subjectiveAnswer = ref('')
const showHint = ref(false)
const isSubmitted = ref(false) // 사용자가 제출 버튼을 눌렀는지 여부

// --- 3. 컴퓨티드 속성 ---

// 제출 버튼 활성화 여부를 결정합니다.
const canSubmit = computed(() => {
  if (isContentLoading.value || isSubmitted.value) return false
  if (!quizData.value) return false

  if (quizData.value.type === 'multiple_choice') {
    return selectedAnswer.value !== ''
  } else if (quizData.value.type === 'subjective') {
    return subjectiveAnswer.value.trim().length > 0
  }
  return false
})

// --- 4. 메서드 ---

const selectOption = (value) => {
  if (isContentLoading.value || isSubmitted.value) return
  selectedAnswer.value = value
}

const toggleHint = () => {
  if (isContentLoading.value || isSubmitted.value) return
  showHint.value = !showHint.value
}

// [리팩토링] API 호출 로직을 제거하고 Store 액션만 호출하도록 변경
const submitAnswer = () => {
  if (!canSubmit.value) return

  const answer = quizData.value.type === 'multiple_choice'
    ? selectedAnswer.value
    : subjectiveAnswer.value.trim()

  console.log('[QuizInteraction] 📥 답안 제출. Store 액션을 호출합니다.', { answer })
  isSubmitted.value = true // 제출 상태로 변경하여 UI를 잠급니다.
  learningStore.sendMessage(answer)
}

// --- 5. 유틸리티 ---

const cleanOptionText = (option, index) => {
  let text = typeof option === 'string' ? option : (option.text || String(option))
  const numberPattern = new RegExp(`^${index + 1}\\.\\s*`)
  return text.replace(numberPattern, '').trim()
}

// --- 6. 감시자 ---

// Store의 quizData가 변경되면 (새로운 퀴즈가 출제되면) 로컬 상태를 초기화합니다.
watch(quizData, (newQuizData) => {
  if (newQuizData) {
    console.log('[QuizInteraction] 🔄 새로운 퀴즈 데이터를 Store로부터 받았습니다.', newQuizData)
    selectedAnswer.value = ''
    subjectiveAnswer.value = ''
    showHint.value = false
    isSubmitted.value = false // 제출 상태도 초기화
  }
}, { deep: true, immediate: true })
</script>



<style lang="scss" scoped>
/* 원본의 모든 스타일을 그대로 유지합니다. */
.quiz-interaction { background: $white; border-radius: $border-radius-lg; padding: $spacing-md; border: 1px solid $gray-300; height: 100%; display: flex; flex-direction: column; gap: $spacing-md; opacity: 0.7; transition: opacity 0.3s ease; overflow: hidden; }
.quiz-interaction.active { opacity: 1; }
.interaction-content { flex: 1; display: flex; flex-direction: column; gap: $spacing-md; overflow-y: auto; min-height: 0; padding-right: $spacing-sm; }
.interaction-content::-webkit-scrollbar { width: 6px; }
.interaction-content::-webkit-scrollbar-track { background: $gray-100; border-radius: 3px; }
.interaction-content::-webkit-scrollbar-thumb { background: $gray-400; border-radius: 3px; }
.interaction-content::-webkit-scrollbar-thumb:hover { background: $gray-500; }
.options-header, .input-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-md; padding-bottom: $spacing-sm; border-bottom: 1px solid $gray-200; }
.options-header h4, .input-header h4 { margin: 0; font-size: $font-size-base; color: $text-dark; font-weight: 600; }
.quiz-options { display: flex; flex-direction: column; gap: $spacing-md * 0.75; flex: 1; min-height: 0; }
.quiz-option { display: flex; align-items: center; gap: $spacing-md * 0.75; padding: $spacing-md; border: 1px solid $gray-300; border-radius: $border-radius-lg; cursor: pointer; transition: all 0.2s ease; background: $white; }
.quiz-option:hover:not(.disabled) { background: $gray-100; border-color: $primary; transform: translateY(-1px); box-shadow: 0 2px 8px rgba($primary, 0.15); }
.quiz-option.selected { background: lighten($primary, 40%); border-color: $primary; box-shadow: 0 0 0 2px rgba($primary, 0.25); }
.quiz-option.disabled { opacity: 0.6; cursor: not-allowed; }
.option-indicator { font-size: $font-size-lg; color: $primary; font-weight: bold; min-width: 20px; }
.option-content { display: flex; align-items: center; gap: $spacing-sm; flex: 1; }
.option-number { font-weight: 500; color: $gray-700; }
.option-text { line-height: 1.4; }
.subjective-input-container { display: flex; flex-direction: column; gap: $spacing-md * 0.75; flex: 1; min-height: 0; }
.quiz-loading { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: $spacing-lg; padding: $spacing-lg * 2 1rem; text-align: center; color: $secondary; flex: 1; }
.loading-spinner { width: 48px; height: 48px; border: 4px solid $gray-200; border-top: 4px solid $primary; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.quiz-loading p { margin: 0; font-size: $font-size-base; font-weight: 500; color: $gray-700; }
.subjective-input { width: 100%; padding: $spacing-md; border: 1px solid $gray-300; border-radius: $border-radius-lg; font-size: $font-size-sm; line-height: 1.5; resize: vertical; min-height: 120px; max-height: 200px; transition: border-color 0.2s ease; }
.subjective-input:focus { outline: none; border-color: $primary; box-shadow: 0 0 0 2px rgba($primary, 0.25); }
.subjective-input:disabled { background: $gray-100; opacity: 0.7; }
.hint-container { background: lighten($warning, 35%); border: 1px solid lighten($warning, 30%); border-radius: $border-radius-lg; padding: $spacing-md; animation: hintSlideIn 0.3s ease-out; flex-shrink: 0; }
@keyframes hintSlideIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.hint-content { display: flex; align-items: flex-start; gap: $spacing-md * 0.75; }
.hint-icon { font-size: $font-size-lg; }
.hint-text { line-height: 1.5; color: darken($warning, 40%); font-weight: 500; }
.quiz-actions { display: flex; justify-content: space-between; gap: $spacing-md * 0.75; align-items: center; flex-wrap: wrap; flex-shrink: 0; border-top: 1px solid $gray-200; padding-top: $spacing-md; margin-top: auto; }
.btn { padding: $spacing-md * 0.75 $spacing-md; border: none; border-radius: $border-radius; cursor: pointer; font-weight: 500; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; min-width: 80px; }
.btn-primary { background: $primary; color: $white; }
.btn-primary:hover:not(:disabled) { background: darken($primary, 10%); transform: translateY(-1px); }
.btn-secondary { background: $secondary; color: $white; }
.btn-secondary:hover:not(:disabled) { background: darken($secondary, 10%); transform: translateY(-1px); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
.hint-btn { flex: 0 0 auto; }
.submit-btn { flex: 1; max-width: 150px; }
.button-spinner { width: 16px; height: 16px; border: 2px solid transparent; border-top: 2px solid $white; border-radius: 50%; animation: spin 1s linear infinite; }
.post-submit-actions { display: flex; flex-direction: column; gap: $spacing-md * 0.75; align-items: center; width: 100%; }
.submit-success { color: $success; font-weight: 500; padding: $spacing-sm $spacing-md; background: lighten($success, 45%); border: 1px solid lighten($success, 40%); border-radius: $border-radius; text-align: center; width: 100%; }
</style>