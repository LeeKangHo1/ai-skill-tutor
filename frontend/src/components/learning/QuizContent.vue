<!-- frontend/src/components/learning/QuizContent.vue -->
<template>
  <div v-if="quizData" class="quiz-content content-active">
    <div class="quiz-header">
      <h3>📝 퀴즈 문제</h3>
      <div class="quiz-type-badge">{{ quizData.quiz_type === 'multiple_choice' ? '객관식' : '주관식' }}</div>
    </div>
    <div class="quiz-question-display">
      <p class="question-text"><strong>{{ quizData.question }}</strong></p>
      <div class="quiz-description">
        <p>💡 오른쪽 상호작용 영역에서 답변을 선택해주세요.</p>
        <p>⚠️ 답변을 제출하기 전까지는 다른 내용을 볼 수 없습니다.</p>
      </div>
    </div>
  </div>

  <!-- 퀴즈 데이터가 없을 때 로딩 상태 표시 -->
  <div v-else class="loading-state">
    <div class="loading-content">
      <div class="loading-icon">📝</div>
      <h3>퀴즈를 준비하고 있습니다...</h3>
      <p>잠시만 기다려주세요.</p>
    </div>
  </div>
</template>

<script setup>
import { watch } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

// --- Store 직접 연결 ---
const learningStore = useLearningStore()
// Store에서 quizData를 직접 가져옵니다.
const { quizData } = storeToRefs(learningStore)

console.log('[QuizContent] 🟢 컴포넌트 초기화. Store와 연결되었습니다.')

// 디버깅용 감시자
watch(quizData, (newData) => {
  if (newData) {
    console.log('[QuizContent] 📝 퀴즈 데이터가 변경되어 화면을 다시 그립니다.', newData)
  } else {
    console.log('[QuizContent] ⏳ 퀴즈 데이터가 없어 로딩 상태를 표시합니다.')
  }
}, { immediate: true })
</script>

<style lang="scss" scoped>
/* 퀴즈 컨텐츠 스타일 */
.quiz-content { 
  background: linear-gradient(135deg, lighten($warning, 40%), lighten($danger, 45%)); 
  border-left: 4px solid $warning; 
  padding: $spacing-lg; 
  border-radius: $border-radius-lg; 
  margin-bottom: $spacing-md; 
}

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
  background: lighten($primary, 45%); 
  color: darken($primary, 10%); 
}

.quiz-question-display { 
  display: flex; 
  flex-direction: column; 
  gap: $spacing-md; 
}

.question-text { 
  font-size: $font-size-base * 1.1; 
  line-height: 1.6; 
  color: $text-dark; 
  margin: 0; 
  padding: $spacing-md; 
  background: rgba($white, 0.8); 
  border-radius: $border-radius-lg; 
}

.quiz-description { 
  background: rgba($white, 0.7); 
  padding: $spacing-md; 
  border-radius: $border-radius; 
}

.quiz-description p { 
  margin: 0; 
  font-size: $font-size-sm; 
}

/* 로딩 상태 스타일 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  background: linear-gradient(135deg, lighten($warning, 50%), lighten($danger, 55%));
  border: 1px solid rgba($warning, 0.2);
  border-radius: $border-radius-lg;
  padding: $spacing-lg * 2;
}

.loading-content {
  text-align: center;
  color: darken($warning, 20%);
}

.loading-icon {
  font-size: 3rem;
  margin-bottom: $spacing-md;
  animation: pulse 2s infinite;
}

.loading-state h3 {
  margin: 0 0 $spacing-sm 0;
  font-size: $font-size-lg;
  color: darken($warning, 25%);
}

.loading-state p {
  margin: 0;
  font-size: $font-size-base;
  color: darken($warning, 15%);
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
  from { opacity: 0; } 
  to { opacity: 1; } 
}
</style>