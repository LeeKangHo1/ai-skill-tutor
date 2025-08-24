<!-- frontend/src/components/learning/QuizContent.vue -->
<template>
  <div class="quiz-content"
    :class="{ 'content-active': isVisible, 'content-hidden': !isVisible }">
    <h3>📝 퀴즈 문제</h3>
    <div class="quiz-question-display">
      <p><strong>{{ quizData.question }}</strong></p>
      <div class="quiz-description">
        <p>💡 오른쪽 상호작용 영역에서 답변을 선택해주세요.</p>
        <p>⚠️ 답변을 제출하기 전까지는 다른 내용을 볼 수 없습니다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

// Props 정의
const props = defineProps({
  quizData: {
    type: Object,
    required: true,
    default: () => ({
      question: '',
      type: 'multiple_choice',
      options: [],
      hint: ''
    })
  },
  isVisible: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.quiz-content {
  background: linear-gradient(135deg, #fff3e0, #fce4ec);
  border-left: 4px solid #ff9800;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.quiz-question-display p {
  margin-bottom: 1rem;
}

.quiz-description {
  background: rgba(255, 255, 255, 0.7);
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.quiz-description p {
  margin-bottom: 0.5rem;
}

.quiz-description p:last-child {
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

/* 반응형 */
@media (max-width: 768px) {
  .quiz-content {
    padding: 1rem;
  }
}
</style>