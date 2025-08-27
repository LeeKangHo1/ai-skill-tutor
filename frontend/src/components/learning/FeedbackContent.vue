<!-- frontend/src/components/learning/FeedbackContent.vue -->
<template>
  <div v-if="feedbackData" class="feedback-content content-active">
    <h3>✅ 평가 결과</h3>
    <div class="feedback-details" v-html="formattedFeedback"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

const learningStore = useLearningStore()
// [수정] mainContent와 preservedFeedback 상태를 가져옵니다.
const { mainContent, preservedFeedback } = storeToRefs(learningStore)

const feedbackData = computed(() => {
  // 현재 컨텐츠 타입이 'feedback'이면 mainContent.data를 사용하고,
  // 그 외의 경우(예: QnA)에는 보존된 피드백(preservedFeedback)을 사용합니다.
  if (mainContent.value.type === 'feedback') {
    return mainContent.value.data
  }
  return preservedFeedback.value
})

// feedbackData의 내용을 HTML로 변환합니다.
const formattedFeedback = computed(() => {
  if (!feedbackData.value) return ''
  // API 응답의 content 필드를 사용하도록 수정
  return (feedbackData.value.content || '').replace(/\n/g, '<br>')
})
</script>

<style lang="scss" scoped>
/* 스타일은 원본과 동일하게 유지합니다. */
.feedback-content { background: linear-gradient(135deg, lighten($success, 55%), lighten($success, 50%)); border-left: 4px solid $success; padding: $spacing-lg; border-radius: $border-radius-lg; }
.feedback-details { line-height: 1.6; color: darken($success, 20%); background: rgba($white, 0.8); padding: $spacing-md; border-radius: $border-radius; }
.content-active { display: block; animation: fadeIn 0.3s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>



<style lang="scss" scoped>
.feedback-content {
  background: linear-gradient(135deg, lighten($success, 55%), lighten($success, 50%));
  border-left: 4px solid $success;
  padding: $spacing-lg;
  border-radius: $border-radius-lg;
  margin-bottom: $spacing-md;
}

/* 답변 정보 섹션 */
.answer-info-section {
  background: rgba($white, 0.8);
  border: 1px solid rgba($success, 0.3);
  border-radius: $border-radius-lg;
  padding: $spacing-md;
  margin-bottom: $spacing-md;
}

.answer-details {
  line-height: 1.6;
  color: darken($success, 20%);
}

/* 피드백 내용 섹션 */
.feedback-content-section {
  background: rgba($white, 0.8);
  border: 1px solid rgba($success, 0.3);
  border-radius: $border-radius-lg;
  padding: $spacing-md;
  margin-bottom: $spacing-md;
}

.feedback-content-section h4 {
  margin: 0 0 $spacing-md * 0.75 0;
  color: darken($success, 20%);
  font-size: $font-size-base;
  font-weight: 600;
}

.feedback-details {
  line-height: 1.6;
  color: darken($success, 20%);
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