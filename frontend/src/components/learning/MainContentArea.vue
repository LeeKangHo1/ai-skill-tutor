<!-- frontend/src/components/learning/MainContentArea.vue -->
<template>
  <div class="main-content-area">
    <div class="content-header">
      <h2 class="content-title">{{ chapterTitle }}</h2>
    </div>

    <div class="content-body">
      <div v-if="isContentLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>콘텐츠를 불러오는 중...</p>
      </div>

      <div v-else-if="apiError" class="error-container">
        <h3>😥 오류가 발생했습니다</h3>
        <p>{{ apiError.message }}</p>
        <span>채팅창에 메시지를 입력하여 다시 시도해주세요.</span>
      </div>

      <template v-else>
        <TheoryContent v-if="shouldShowContent('theory')" />
        <QuizContent v-else-if="shouldShowContent('quiz')" />
        <FeedbackContent v-else-if="shouldShowContent('feedback')" />

        <template v-else-if="shouldShowContent('qna')">
          <TheoryContent v-if="hasFeedbackCompleted" />
          <FeedbackContent v-if="hasFeedbackCompleted" />
          <TheoryContent v-else />
        </template>
      </template>
    </div>

    <div class="content-navigation">
      <button v-if="canShowNavigationButton('theory')" class="btn btn-outline" @click="handleNavigationClick('review_theory')">
        📖 이론 다시 보기
      </button>
      <button v-if="canShowNavigationButton('quiz')" class="btn btn-outline" @click="handleNavigationClick('review_quiz')">
        📝 퀴즈 다시 보기
      </button>
      <button v-if="canShowNavigationButton('current')" class="btn btn-outline" @click="handleNavigationClick('current')">
        ← 현재 학습으로 돌아가기
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'
import TheoryContent from './TheoryContent.vue'
import QuizContent from './QuizContent.vue'
import FeedbackContent from './FeedbackContent.vue'

// --- Store 직접 연결 ---
const learningStore = useLearningStore()
const {
  isContentLoading,
  apiError,
  sessionInfo,
  currentAgent,
  // [기능 복원] store에서 새로운 상태들을 가져옵니다.
  contentMode,
  completedSteps,
} = storeToRefs(learningStore)

console.log('[MainContentArea] 🟢 컴포넌트 초기화. Store와 직접 연결되었습니다.')

// --- Store 상태 기반 Computed 속성 ---

const chapterTitle = computed(() =>
  `${sessionInfo.value.chapter_number}챕터 ${sessionInfo.value.section_number}섹션`
)

const agentContentType = computed(() => {
  const agentMap = {
    theory_educator: 'theory',
    quiz_generator: 'quiz',
    evaluation_feedback: 'feedback',
    qna_resolver: 'qna',
  }
  return agentMap[currentAgent.value] || 'theory'
})

// [기능 복원] 피드백을 완료했는지 여부
const hasFeedbackCompleted = computed(() => completedSteps.value.feedback)

// [기능 복원] 어떤 컨텐츠를 보여줄지 결정하는 로직
const shouldShowContent = (contentType) => {
  if (contentMode.value === 'current') {
    return contentType === agentContentType.value
  } else if (contentMode.value === 'review_theory') {
    return contentType === 'theory'
  } else if (contentMode.value === 'review_quiz') {
    return contentType === 'quiz'
  }
  return false
}

// [기능 복원] 네비게이션 버튼 표시 여부 결정 로직
const canShowNavigationButton = (buttonType) => {
  const isAfterQuiz = completedSteps.value.quiz
  const isCurrentMode = contentMode.value === 'current'

  if (buttonType === 'theory' || buttonType === 'quiz') {
    return isAfterQuiz && isCurrentMode && (currentAgent.value === 'evaluation_feedback' || currentAgent.value === 'qna_resolver')
  }
  if (buttonType === 'current') {
    return !isCurrentMode
  }
  return false
}

// [기능 복원] 네비게이션 버튼 클릭 핸들러
const handleNavigationClick = (mode) => {
  console.log(`[MainContentArea] 🖱️ 네비게이션 클릭: ${mode} 모드로 변경`)
  // store의 액션을 호출하여 contentMode를 변경합니다.
  learningStore.setContentMode(mode)
}
</script>

<style lang="scss" scoped>
/* 스타일은 기존과 동일하게 유지합니다. */
.main-content-area {
  background: $white;
  padding: $spacing-lg * 1.33; /* 2rem */
  overflow-y: auto;
  border-right: 1px solid $gray-300;
  height: 100%;
}
.content-header { margin-bottom: $spacing-lg; }
.content-title {
  font-size: $font-size-lg * 1.2; /* 1.5rem */
  color: $text-dark;
  margin-bottom: $spacing-sm;
}
.content-body { min-height: 400px; }
.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: $secondary;
  background-color: $gray-100;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  text-align: center;
}
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid $gray-200;
  border-top: 4px solid $primary;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: $spacing-md;
}
.error-container {
  border-left: 4px solid $danger;
  background-color: lighten($danger, 45%);
  color: darken($danger, 20%);
}
.error-container h3 { margin-top: 0; margin-bottom: $spacing-sm; }
.error-container p { margin-bottom: $spacing-md; }
.error-container span { font-size: $font-size-sm; color: $gray-600; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* [기능 복원] 이전 컨텐츠 접근 버튼 스타일 */
.content-navigation {
  margin-top: $spacing-lg * 1.33; // 2rem
  padding-top: $spacing-md;
  border-top: 1px solid $gray-300;
  display: flex;
  gap: $spacing-md;
  flex-wrap: wrap;
}
.btn {
  padding: 0.75rem $spacing-md;
  border: none;
  border-radius: $border-radius;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}
.btn-outline {
  background: $white;
  color: $secondary;
  border: 1px solid $secondary;
}
.btn-outline:hover {
  background: $gray-100;
  border-color: $gray-700;
  color: $gray-700;
  transform: translateY(-1px);
}
</style>