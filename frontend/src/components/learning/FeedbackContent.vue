<!-- frontend/src/components/learning/FeedbackContent.vue -->
<template>
  <div v-if="feedbackData" class="feedback-content content-active">
    <h3>{{ parsedFeedback.title }}</h3>

    <div v-if="parsedFeedback.answerInfo" class="answer-info-section">
      <h4>📋 답변 정보</h4>
      <div class="details-text" v-html="parsedFeedback.answerInfo"></div>
    </div>

    <div v-if="parsedFeedback.feedbackContent" class="feedback-content-section">
      <h4>💬 상세 피드백</h4>
      <div class="details-text" v-html="parsedFeedback.feedbackContent"></div>
    </div>

    <div v-if="parsedFeedback.nextStepInfo" class="next-step-section">
      <h4>🎯 다음 단계 안내</h4>
      <div class="details-text" v-html="parsedFeedback.nextStepInfo"></div>
    </div>
  </div>

  <!-- 피드백 데이터가 없을 때 로딩 상태 표시 -->
  <div v-else class="loading-state">
    <div class="loading-content">
      <div class="loading-icon">💬</div>
      <h3>피드백을 생성하고 있습니다...</h3>
      <p>답변을 평가 중입니다. 잠시만 기다려주세요.</p>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

// --- Store 직접 연결 ---
const learningStore = useLearningStore()
// Store에서 feedbackData를 직접 가져옵니다.
const { feedbackData } = storeToRefs(learningStore)

console.log('[FeedbackContent] 🟢 컴포넌트 초기화. Store의 feedbackData와 연결되었습니다.')

const parsedFeedback = computed(() => {
  // feedbackData 또는 필수 필드가 없으면 즉시 종료
  if (!feedbackData.value || !feedbackData.value.feedback_content) {
    return {}
  }

  const feedbackSource = feedbackData.value;

  // 답변 정보 텍스트 생성
  let answerInfoText = ''
  if (feedbackSource.answer_info) {
    if (feedbackSource.answer_info.correct_answer) {
      answerInfoText += `• 정답: ${feedbackSource.answer_info.correct_answer}<br>`
    }
    if (feedbackSource.answer_info.user_answer) {
      answerInfoText += `• 사용자 답변: ${feedbackSource.answer_info.user_answer}`
    }
  }

  const result = {
    title: feedbackSource.title || '✅ 평가 결과',
    answerInfo: answerInfoText,
    feedbackContent: (feedbackSource.feedback_content || '').replace(/\n/g, '<br>'),
    explanation: (feedbackSource.explanation || '').replace(/\n/g, '<br>'),
    nextStepInfo: (feedbackSource.next_step_guidance || '').replace(/\n/g, '<br>')
  }

  console.log('[FeedbackContent v2.2] 🟢 파싱 완료. 수정된 경로로 데이터를 사용합니다.', result);

  return result
})

// 디버깅용 감시자
watch(feedbackData, (newData) => {
  if (newData) {
    console.log('[FeedbackContent] 💬 피드백 데이터가 변경되어 화면을 다시 그립니다.', newData)
  } else {
    console.log('[FeedbackContent] ⏳ 피드백 데이터가 없어 로딩 상태를 표시합니다.')
  }
}, { deep: true, immediate: true })
</script>

<style lang="scss" scoped>
.feedback-content {
  background: linear-gradient(135deg, lighten($success, 55%), lighten($success, 50%));
  border-left: 4px solid $success;
  padding: $spacing-lg;
  border-radius: $border-radius-lg;
  margin-bottom: $spacing-md;
}
.answer-info-section,
.feedback-content-section,
.next-step-section {
  background: rgba($white, 0.8);
  border: 1px solid rgba($success, 0.3);
  border-radius: $border-radius-lg;
  padding: $spacing-md;
}

.answer-info-section,
.feedback-content-section {
    margin-bottom: $spacing-lg;
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

/* 로딩 상태 스타일 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  background: linear-gradient(135deg, lighten($success, 60%), lighten($success, 55%));
  border: 1px solid rgba($success, 0.2);
  border-radius: $border-radius-lg;
  padding: $spacing-lg * 2;
}

.loading-content {
  text-align: center;
  color: darken($success, 15%);
}

.loading-icon {
  font-size: 3rem;
  margin-bottom: $spacing-md;
  animation: pulse 2s infinite;
}

.loading-state h3 {
  margin: 0 0 $spacing-sm 0;
  font-size: $font-size-lg;
  color: darken($success, 20%);
}

.loading-state p {
  margin: 0;
  font-size: $font-size-base;
  color: darken($success, 15%);
  opacity: 0.8;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.7; }
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