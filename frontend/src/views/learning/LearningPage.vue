<!-- frontend/src/views/learning/LearningPage.vue -->
<template>
  <div class="learning-page">
    <div class="learning-header">
      <div class="header-left">
        <div class="logo">🤖 AI 활용법 학습 튜터</div>
      </div>
      <div class="header-right">
        <button class="btn btn-secondary" @click="goToDashboard">
          대시보드로
        </button>
      </div>
    </div>

    <div class="learning-content">
      <MainContentArea />

      <div class="interaction-area">
        <div class="interaction-header">
          {{ uiMode === 'chat' ? '💬 채팅' : '📝 퀴즈' }}
        </div>

        <div class="interaction-body">
          <ChatInteraction
            v-if="uiMode === 'chat'"
            @send-message="handleSendMessage"
          />

          <QuizInteraction
            v-else-if="uiMode === 'quiz'"
            @submit-answer="handleSubmitAnswer"
          />
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

// 자식 컴포넌트 임포트
import MainContentArea from '@/components/learning/MainContentArea.vue'
import ChatInteraction from '@/components/learning/ChatInteraction.vue'
import QuizInteraction from '@/components/learning/QuizInteraction.vue'

// --- 1. 스토어 및 라우터 설정 ---
const router = useRouter()
const learningStore = useLearningStore()

// --- 2. Store 상태와 게터를 반응형으로 가져오기 ---
// storeToRefs를 사용하면 구조 분해 할당 시 반응성을 유지할 수 있습니다.
const { isLoading, loadingMessage, uiMode } = storeToRefs(learningStore)

console.log('[LearningPage] 🟢 컴포넌트 초기화 완료. Store와 연결되었습니다.')

// --- 3. 이벤트 핸들러 (Store Action 호출) ---

/**
 * ChatInteraction 컴포넌트에서 받은 메시지를 Store로 전달합니다.
 * @param {string} message - 사용자가 입력한 메시지
 */
const handleSendMessage = (message) => {
  console.log('[LearningPage] 📤 "send-message" 이벤트 수신. Store 액션을 호출합니다.', { message })
  learningStore.sendMessage(message)
}

/**
 * QuizInteraction 컴포넌트에서 받은 퀴즈 답변을 Store로 전달합니다.
 * @param {object} submitData - 퀴즈 제출 데이터 객체
 */
const handleSubmitAnswer = (submitData) => {
  console.log('[LearningPage] 📥 "submit-answer" 이벤트 수신. Store 액션을 호출합니다.', { answer: submitData.answer })
  // v2.0 API에서는 주관식/객관식 모두 동일한 message API를 사용하므로, 답변 텍스트만 넘겨줍니다.
  learningStore.sendMessage(submitData.answer)
}

/**
 * 대시보드 페이지로 이동합니다.
 */
const goToDashboard = () => {
  console.log('[LearningPage] 🚀 대시보드로 이동합니다.')
  router.push('/dashboard')
}

// --- 4. 라이프사이클 및 감시자 (디버깅용) ---

onMounted(() => {
  console.log('[LearningPage] 🟢 컴포넌트가 마운트되었습니다.')
  // 페이지 첫 로딩(세션 시작)은 이제 HeaderComponent에서 트리거하므로
  // 이 페이지는 로딩이 완료된 후 보여지게 됩니다.
  // 만약 URL로 직접 접근하는 경우를 대비한 로직이 필요하다면 여기에 추가할 수 있습니다.
})

// UI 모드 변경을 감지하여 로그를 남깁니다 (디버깅에 유용).
watch(uiMode, (newMode, oldMode) => {
  console.log(`[LearningPage] 🔄 UI 모드 변경 감지: ${oldMode} -> ${newMode}`)
})
</script>

<style lang="scss" scoped>
/* 스타일은 변경되지 않았으므로 그대로 유지합니다. */
.learning-page {
  max-width: 1400px;
  margin: 0 auto;
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: 0 20px 40px rgba($black, 0.1);
  overflow: hidden;
  height: 90vh;
  display: flex;
  flex-direction: column;
}

/* Header Area */
.learning-header {
  background: $header-gradient;
  color: $white;
  padding: $spacing-md $spacing-lg;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;

  .header-left {
    display: flex;
    align-items: center;
    gap: $spacing-md;
  }

  .logo {
    font-size: $font-size-lg;
    font-weight: 600;
  }
}

/* Main Content Area */
.learning-content {
  flex: 1;
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 0;
  overflow: hidden;
  min-height: 0;
}

/* Interaction Area */
.interaction-area {
  background: $gray-100;
  display: flex;
  flex-direction: column;
  min-height: 0;

  .interaction-header {
    background: $gray-700;
    color: $white;
    padding: $spacing-md;
    text-align: center;
    font-weight: 500;
    flex-shrink: 0;
  }

  .interaction-body {
    flex: 1;
    padding: $spacing-md;
    overflow: hidden;
    min-height: 0;
  }
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba($black, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;

  .loading-spinner {
    background: $white;
    padding: $spacing-lg;
    border-radius: $border-radius-lg;
    text-align: center;
    box-shadow: 0 10px 30px rgba($black, 0.2);

    p {
      margin-top: $spacing-md;
      font-weight: 500;
      color: $gray-700;
    }
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid $gray-200;
    border-top-color: $primary;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>