<template>
  <div class="main-content-area">
    <div class="content-header">
      <h2 class="content-title">{{ chapterTitle }}</h2>
    </div>

    <div class="content-body">
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>콘텐츠를 불러오는 중...</p>
      </div>

      <div v-else-if="apiError" class="error-container">
        <h3>😥 오류가 발생했습니다</h3>
        <p>{{ apiError.message }}</p>
        <span>채팅창에 메시지를 입력하여 다시 시도해주세요.</span>
      </div>

      <template v-else>
        <TheoryContent
          v-if="effectiveContentType === 'theory' && theoryContent"
          :theory-data="theoryContent"
        />
        <QuizContent
          v-else-if="effectiveContentType === 'quiz'"
          :is-visible="true"
        />
        <FeedbackContent
          v-else-if="effectiveContentType === 'feedback'"
          :is-visible="true"
        />
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, watch } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

// 자식 컨텐츠 컴포넌트들
import TheoryContent from './TheoryContent.vue'
import QuizContent from './QuizContent.vue'
import FeedbackContent from './FeedbackContent.vue'

// --- 1. [임시 브릿지] 기존 props 정의를 유지합니다. ---
// 이 코드는 하위 호환성을 위해 남겨두며, 최종 단계에서 삭제됩니다.
const props = defineProps({
  currentAgent: {
    type: String,
    default: ''
  },
  contentData: {
    type: Object,
    default: () => ({})
  },
})

// --- 2. Store 연결 ---
const learningStore = useLearningStore()
const { 
  isLoading, 
  apiError,
  mainContent, 
  sessionInfo,
  currentAgent: agentFromStore,
} = storeToRefs(learningStore)

console.log('[MainContentArea] 🟢 컴포넌트 초기화. Store와 연결되었습니다.')

// --- 3. '임시 브릿지' Computed 속성 생성 ---

// props로 받은 currentAgent가 있으면 그것을 사용하고, 없으면 store의 currentAgent를 사용합니다.
const effectiveAgent = computed(() => {
  const agent = props.currentAgent || agentFromStore.value
  console.log(`[MainContentArea] 🕵️‍♂️ 유효 에이전트 결정: ${agent}`)
  return agent
})

// 에이전트에 따라 현재 보여줘야 할 컨텐츠 타입을 결정합니다.
const effectiveContentType = computed(() => {
  const typeMap = {
    theory_educator: 'theory',
    quiz_generator: 'quiz',
    evaluation_feedback: 'feedback',
    qna_resolver: 'theory', // QnA 상황에서는 이론 컨텐츠를 배경으로 표시
    session_manager: 'theory',
  }
  const type = typeMap[effectiveAgent.value] || 'theory'
  console.log(`[MainContentArea] 📄 유효 컨텐츠 타입 결정: ${type}`)
  return type
})

// Store에서 가져온 sessionInfo를 기반으로 제목을 생성합니다.
const chapterTitle = computed(() => 
  `${sessionInfo.value.chapter_number}챕터 ${sessionInfo.value.section_number}섹션`
)

// 이론 컨텐츠는 store의 mainContent.data를 사용합니다.
const theoryContent = computed(() => {
  // mainContent의 타입이 'theory' 또는 'feedback'일 때 그 데이터를 사용합니다.
  if (mainContent.value.type === 'theory' || mainContent.value.type === 'feedback') {
    return mainContent.value.data
  }
  // 퀴즈나 다른 상황에서는 null을 반환하여 TheoryContent가 렌더링되지 않도록 합니다.
  return null
})

// --- 4. 디버깅용 감시자 ---
watch(effectiveAgent, (newAgent) => {
  console.log(`[MainContentArea] 🔄 에이전트 변경 감지: ${newAgent}`)
})

watch(apiError, (newError) => {
  if (newError) {
    console.error('[MainContentArea] 🔴 API 오류 상태 감지:', newError)
  }
})

watch(isLoading, (newLoading) => {
  console.log(`[MainContentArea] ⏳ 로딩 상태 변경: ${newLoading}`)
})

</script>

<style lang="scss" scoped>
/* 스타일은 변경되지 않았으므로 그대로 유지합니다. */
.main-content-area {
  background: $white;
  padding: $spacing-lg * 1.33; /* 2rem */
  overflow-y: auto;
  border-right: 1px solid $gray-300;
  height: 100%;
}

.content-header {
  margin-bottom: $spacing-lg;
}

.content-title {
  font-size: $font-size-lg * 1.2; /* 1.5rem */
  color: $text-dark;
  margin-bottom: $spacing-sm;
}

.content-body {
  min-height: 400px;
}

/* 로딩 및 오류 컨테이너 스타일 */
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
  
  h3 {
    margin-top: 0;
    margin-bottom: $spacing-sm;
  }

  p {
    margin-bottom: $spacing-md;
  }

  span {
    font-size: $font-size-sm;
    color: $gray-600;
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>