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


        <!-- <p style="text-align: center; background: red; color: white;">[디버그] 현재 uiMode: {{ uiMode }}</p> -->

        
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
  </div>
</template>

<script setup>
import { onMounted, watch, ref } from 'vue' // ref를 import에 추가합니다.
import { useRouter } from 'vue-router'
import { useLearningStore } from '@/stores/learningStore'
// storeToRefs는 더 이상 uiMode를 위해 필요하지 않지만, 다른 상태를 위해 남겨둘 수 있습니다.
import { storeToRefs } from 'pinia'

// 자식 컴포넌트 임포트
import MainContentArea from '@/components/learning/MainContentArea.vue'
import ChatInteraction from '@/components/learning/ChatInteraction.vue'
import QuizInteraction from '@/components/learning/QuizInteraction.vue'

// --- 1. 스토어 및 라우터 설정 ---
const router = useRouter()
const learningStore = useLearningStore()

// --- 2. Store 상태 가져오기 ---
// [수정] uiMode를 임시로 'chat'으로 고정합니다.
const uiMode = ref('chat') 
// const { uiMode } = storeToRefs(learningStore) // 기존 코드는 주석 처리합니다.

console.log('[LearningPage] 🟢 컴포넌트 초기화 완료. Store와 연결되었습니다.')
console.log('[LearningPage] ⚠️ [임시 조치] uiMode를 "chat"으로 고정합니다.')


// --- 3. 이벤트 핸들러 (Store Action 호출) ---
const handleSendMessage = (message) => {
  console.log('[LearningPage] 📤 "send-message" 이벤트 수신. Store 액션을 호출합니다.', { message })
  learningStore.sendMessage(message)
}

const handleSubmitAnswer = (submitData) => {
  console.log('[LearningPage] 📥 "submit-answer" 이벤트 수신. Store 액션을 호출합니다.', { answer: submitData.answer })
  learningStore.sendMessage(submitData.answer)
}

const goToDashboard = () => {
  console.log('[LearningPage] 🚀 대시보드로 이동합니다.')
  router.push('/dashboard')
}

// --- 4. 라이프사이클 및 감시자 ---
onMounted(() => {
  console.log('[LearningPage] 🟢 컴포넌트가 마운트되었습니다. 새로운 세션 시작을 요청합니다.')
  learningStore.startNewSession()
})

// watch(uiMode, ... ) 부분은 uiMode가 고정되었으므로 잠시 무시됩니다.
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

.learning-header {
  background: $header-gradient;
  color: $white;
  padding: $spacing-md $spacing-lg;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.logo {
  font-size: $font-size-lg;
  font-weight: 600;
}

.learning-content {
  flex: 1;
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 0;
  overflow: hidden;
  min-height: 0;
}

.interaction-area {
  background: $gray-100;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

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
</style>