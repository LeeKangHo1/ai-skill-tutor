<!-- frontend/src/components/learning/QuizContent.vue -->
<template>
  <div v-if="quizData" class="quiz-content content-active">
    <div class="quiz-header">
      <h3>📝 퀴즈 문제</h3>
      <div class="quiz-type-badge">{{ quizData.type === 'multiple_choice' ? '객관식' : '주관식' }}</div>
    </div>
    <div class="quiz-question-display">
      <p class="question-text"><strong>{{ quizData.question }}</strong></p>
      <div class="quiz-description">
        <p>💡 오른쪽 상호작용 영역에서 답변을 선택해주세요.</p>
      </div>
    </div>
  </div>
  <div v-else class="loading-state">
    <div class="loading-spinner"></div>
    <p>퀴즈를 생성하고 있습니다...</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

// [리팩토링] props 정의를 모두 제거합니다.

const learningStore = useLearningStore()
// Store에서 quizData를 직접 가져옵니다.
const { quizData } = storeToRefs(learningStore)

console.log('[QuizContent] 🟢 컴포넌트 초기화. Store와 연결되었습니다.')
</script>

<style lang="scss" scoped>
/* 스타일은 원본과 동일하게 유지합니다. */
.quiz-content { background: linear-gradient(135deg, lighten($warning, 40%), lighten($danger, 45%)); border-left: 4px solid $warning; padding: $spacing-lg; border-radius: $border-radius-lg; margin-bottom: $spacing-md; }
.quiz-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-md; padding-bottom: $spacing-md * 0.75; border-bottom: 1px solid rgba($warning, 0.2); }
.quiz-header h3 { margin: 0; color: darken($warning, 30%); font-size: $font-size-lg; }
.quiz-type-badge { padding: $spacing-xs $spacing-md * 0.75; border-radius: $border-radius-pill; font-weight: 500; background: lighten($primary, 40%); color: darken($primary, 10%); }
.quiz-question-display { display: flex; flex-direction: column; gap: $spacing-md; }
.question-text { font-size: $font-size-base * 1.1; line-height: 1.6; color: $text-dark; margin: 0; padding: $spacing-md; background: rgba($white, 0.8); border-radius: $border-radius-lg; }
.quiz-description { background: rgba($white, 0.7); padding: $spacing-md; border-radius: $border-radius; }
.quiz-description p { margin: 0; font-size: $font-size-sm; }
.loading-state { display: flex; flex-direction: column; align-items: center; gap: $spacing-md; padding: $spacing-lg * 2; }
.loading-spinner { width: 32px; height: 32px; border: 3px solid $gray-100; border-top: 3px solid $warning; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.content-active { display: block; animation: fadeIn 0.3s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>



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