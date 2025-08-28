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
          <ChatInteraction v-if="uiMode === 'chat'" @send-message="handleSendMessage" />
          <QuizInteraction v-else-if="uiMode === 'quiz'" @submit-answer="handleSubmitAnswer" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

import MainContentArea from '@/components/learning/MainContentArea.vue'
import ChatInteraction from '@/components/learning/ChatInteraction.vue'
import QuizInteraction from '@/components/learning/QuizInteraction.vue'

const router = useRouter()
const learningStore = useLearningStore()
// isContentLoading 제거 - 더 이상 전역 로딩 상태를 사용하지 않음
const { currentUIMode: uiMode } = storeToRefs(learningStore)

const handleSendMessage = (message) => {
  learningStore.sendMessage(message)
}

const handleSubmitAnswer = (submitData) => {
  learningStore.sendMessage(submitData.answer)
}

const goToDashboard = () => {
  router.push('/dashboard')
}

onMounted(() => {
  learningStore.startNewSession()
})

watch(uiMode, (newMode, oldMode) => {
  console.log(`[LearningPage] 🔄 UI 모드 변경 감지: ${oldMode} -> ${newMode}`)
})
</script>

<style lang="scss" scoped>
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