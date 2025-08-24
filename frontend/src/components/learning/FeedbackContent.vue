<!-- frontend/src/components/learning/FeedbackContent.vue -->
<template>
  <div class="feedback-content"
    :class="{ 'content-active': isVisible, 'content-hidden': !isVisible }">
    <h3>✅ 평가 결과</h3>
    <div class="feedback-score">
      <p><strong>{{ feedbackData.scoreText }}</strong></p>
    </div>
    <div class="feedback-explanation">
      <p><strong>📝 상세 피드백:</strong></p>
      <p class="feedback-text">{{ feedbackData.explanation }}</p>
    </div>
    <div class="feedback-next-steps">
      <p><strong>🎯 다음 단계 결정:</strong></p>
      <p class="feedback-text">{{ feedbackData.nextStep }}</p>
    </div>

    <!-- QnA 컨텐츠 (이론 유지하면서 질답 추가) -->
    <div v-if="qnaData && shouldShowQna" class="qna-section">
      <h4>❓ 질문 답변</h4>
      <div class="qna-item">
        <p><strong>질문:</strong> {{ qnaData.question }}</p>
        <div><strong>답변:</strong></div>
        <p class="qna-answer">{{ qnaData.answer }}</p>
      </div>
      <div v-if="qnaData.relatedInfo" class="qna-related">
        <p><strong>🔗 관련 학습:</strong></p>
        <p class="qna-related-text">{{ qnaData.relatedInfo }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

// Props 정의
const props = defineProps({
  feedbackData: {
    type: Object,
    required: true,
    default: () => ({
      scoreText: '',
      explanation: '',
      nextStep: ''
    })
  },
  qnaData: {
    type: Object,
    default: null
  },
  shouldShowQna: {
    type: Boolean,
    default: false
  },
  isVisible: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.feedback-content {
  background: linear-gradient(135deg, #e8f5e8, #f1f8e9);
  border-left: 4px solid #4caf50;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.feedback-score {
  margin-bottom: 1.5rem;
}

.feedback-score p {
  font-size: 1.2rem;
  color: #2e7d32;
}

.feedback-explanation,
.feedback-next-steps {
  margin-bottom: 1rem;
}

.feedback-text {
  line-height: 1.6;
  color: #2e7d32;
  margin-top: 0.5rem;
}

/* QnA 섹션 스타일 */
.qna-section {
  background: linear-gradient(135deg, #f3e5f5, #fce4ec);
  border-left: 4px solid #9c27b0;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1.5rem;
}

.qna-item {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.qna-item p {
  margin-bottom: 0.75rem;
}

.qna-related {
  background: rgba(255, 255, 255, 0.7);
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(156, 39, 176, 0.3);
}

.qna-related p {
  margin-bottom: 0.5rem;
}

.qna-answer {
  line-height: 1.6;
  color: #495057;
  margin-top: 0.5rem;
}

.qna-related-text {
  line-height: 1.6;
  color: #6c757d;
  margin-top: 0.5rem;
  margin-bottom: 0;
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

/* 데스크톱 전용 - 모바일/태블릿 대응 제거 */
</style>