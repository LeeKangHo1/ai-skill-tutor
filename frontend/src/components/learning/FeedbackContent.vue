<!-- frontend/src/components/learning/FeedbackContent.vue -->
<template>
  <!-- v-if 조건을 feedbackData가 아닌, 파싱된 결과가 실제로 있는지 여부로 변경하여 안정성을 높입니다. -->
  <div v-if="feedbackData && (parsedFeedback.answerInfo || parsedFeedback.feedbackContent)" class="feedback-content content-active">
    <h3>{{ parsedFeedback.title }}</h3>

    <div v-if="parsedFeedback.answerInfo" class="answer-info-section">
      <h4>📋 답변 정보</h4>
      <div class="details-text" v-html="parsedFeedback.answerInfo"></div>
    </div>

    <div v-if="parsedFeedback.feedbackContent" class="feedback-content-section">
      <h4>💬 상세 피드백</h4>
      <div class="details-text" v-html="parsedFeedback.feedbackContent"></div>
    </div>
    
    <div v-if="parsedFeedback.explanation" class="explanation-section">
        <h4>🧠 추가 설명</h4>
        <div class="details-text" v-html="parsedFeedback.explanation"></div>
    </div>

    <div v-if="parsedFeedback.nextStepInfo" class="next-step-section">
      <h4>🎯 다음 단계 안내</h4>
      <div class="details-text" v-html="parsedFeedback.nextStepInfo"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

const learningStore = useLearningStore()
const { feedbackData } = storeToRefs(learningStore)

const parsedFeedback = computed(() => {
  // feedbackData가 없으면 즉시 종료
  if (!feedbackData.value || !feedbackData.value.content) {
    return {}
  }

  const result = {
    title: feedbackData.value.title || '✅ 평가 결과',
    answerInfo: '',
    feedbackContent: '',
    nextStepInfo: '',
    explanation: (feedbackData.value.explanation || '').replace(/\n/g, '<br>')
  }

  let content = feedbackData.value.content
  
  const nextStepDelimiter = '🎯 **다음 단계 안내**'
  const answerInfoDelimiter = '📋 **답변 정보**'

  // 1. '다음 단계 안내' 섹션을 분리
  const nextStepIndex = content.indexOf(nextStepDelimiter)
  if (nextStepIndex !== -1) {
    result.nextStepInfo = content.substring(nextStepIndex + nextStepDelimiter.length).trim().replace(/\n/g, '<br>')
    content = content.substring(0, nextStepIndex).trim()
  }

  // 2. 남은 content에서 '답변 정보' 섹션을 분리
  const answerInfoIndex = content.indexOf(answerInfoDelimiter)
  if (answerInfoIndex !== -1) {
    result.answerInfo = content.substring(answerInfoIndex + answerInfoDelimiter.length).trim().replace(/\n/g, '<br>')
    content = content.substring(0, answerInfoIndex).trim()
  }
  
  // 3. 최종적으로 남은 content가 '상세 피드백'
  result.feedbackContent = content.replace(/^[🎉💪]\s*/, '').trim().replace(/\n/g, '<br>')

  // [요청사항] 파싱 결과 로그 출력
  console.log('[FeedbackContent 파싱 결과]', {
    answerInfo: result.answerInfo,
    feedbackContent: result.feedbackContent,
    nextStepInfo: result.nextStepInfo
  });

  return result
})

// [추가] feedbackData 변경을 감지하여 디버깅 로그를 남깁니다.
watch(feedbackData, (newData) => {
  if (newData) {
    console.log('[FeedbackContent] Store로부터 새로운 feedbackData를 받았습니다:', newData);
  }
}, { deep: true, immediate: true });
</script>


<style lang="scss" scoped>
/* style 부분은 이전과 동일하게 유지합니다. */
.feedback-content {
  background: linear-gradient(135deg, lighten($success, 55%), lighten($success, 50%));
  border-left: 4px solid $success;
  padding: $spacing-lg;
  border-radius: $border-radius-lg;
  margin-bottom: $spacing-md;
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}
.answer-info-section,
.feedback-content-section,
.explanation-section,
.next-step-section {
  background: rgba($white, 0.8);
  border: 1px solid rgba($success, 0.3);
  border-radius: $border-radius-lg;
  padding: $spacing-md;
}
h4 {
  margin: 0 0 $spacing-md * 0.75 0;
  color: darken($success, 20%);
  font-size: $font-size-base;
  font-weight: 600;
}
.details-text {
  line-height: 1.6;
  color: darken($success, 20%);
}
.content-active {
  display: block;
  animation: fadeIn 0.3s ease-in;
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