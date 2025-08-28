<!-- frontend/src/components/learning/ChatInteraction.vue -->
<template>
  <div class="chat-mode" :class="{ active: true }">
    <div class="chat-history" ref="chatHistoryRef">
      <div v-for="(message, index) in chatHistory" :key="index" class="chat-message"
        :class="getMessageClass(message.type)">
        <div class="message-content">
          <strong class="message-sender">{{ message.sender }}:</strong>
          <span class="message-text">{{ message.message }}</span>
        </div>
        <div class="message-timestamp">
          {{ formatTimestamp(message.timestamp) }}
        </div>
      </div>
    </div>

    <div class="chat-input-container">

      <div class="quick-actions" v-if="showQuickActions">
        <button class="quick-action-btn" @click="handleRetryLearning" :disabled="!isFeedbackComplete">
          🔄 재학습
        </button>
        <button class="quick-action-btn" @click="handleProceedLearning" :disabled="!isFeedbackComplete">
          ➡️ 다음 학습
        </button>
      </div>

      <div class="input-hints">
        <div class="hint-item" v-if="showInputHints">
          💡 <strong>팁:</strong> "다음"이라고 입력하면 퀴즈로 이동합니다.
        </div>
        <div class="hint-item">
          🤔 <strong>질문:</strong> 학습 내용에 대해 궁금한 점을 자유롭게 물어보세요.
        </div>
      </div>


      <div class="chat-input">
        <input type="text" v-model="currentMessage" ref="messageInputRef"
          placeholder="메시지를 입력하세요" @keypress="handleKeyPress" @input="handleInput"
          class="message-input" />
        <button 
          @click="sendMessage" 
          :disabled="!currentMessage.trim() || sessionProgressStage === 'session_start'" 
          class="send-button">
          전송
        </button>
      </div>

    </div>

    <div v-if="showCompletionModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>학습 세션 완료</h3>
          <button class="modal-close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <p>학습 세션이 완료되었습니다. 다음 단계를 선택해주세요.</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn dashboard-btn" @click="goToDashboard" :disabled="isDashboardLoading">
            <span v-if="isDashboardLoading" class="button-spinner"></span>
            <span v-else>📊</span>
            {{ isDashboardLoading ? '이동 중...' : '대시보드' }}
          </button>
          <button class="modal-btn start-learning-btn" @click="startNewLearning" :disabled="isProcessing">
            <span v-if="isProcessing" class="button-spinner"></span>
            <span v-else>🚀</span>
            {{ isProcessing ? '학습 준비 중...' : '학습 시작' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

// --- 스토어 및 라우터 설정 ---
const router = useRouter()
const learningStore = useLearningStore()
// 필요한 모든 상태를 반응형으로 가져옵니다.
const { chatHistory, completedSteps, sessionCompleted, sessionProgressStage } = storeToRefs(learningStore)

console.log('[ChatInteraction] 🟢 컴포넌트 초기화. Store와 연결되었습니다.')

// --- 로컬 상태 (컴포넌트 내 UI 제어용) ---
const currentMessage = ref('')
const chatHistoryRef = ref(null)
const messageInputRef = ref(null)
const isProcessing = ref(false)
const isDashboardLoading = ref(false)

// --- 컴퓨티드 속성 (Store 상태를 기반으로 UI 표시 여부 결정) ---

// 피드백 단계가 완료되었는지 여부
const isFeedbackComplete = computed(() => completedSteps.value.feedback)

// 빠른 액션 버튼 표시 여부
const showQuickActions = computed(() => isFeedbackComplete.value)

// 입력 힌트 표시 여부 (이론 학습이 완료되었을 때만)
const showInputHints = computed(() => {
  return sessionProgressStage.value === 'theory_completed'
})

// 완료 모달 표시 여부
const showCompletionModal = computed(() => sessionCompleted.value)

// --- 메서드 (Store 액션 호출 또는 로컬 UI 제어) ---

const sendMessage = () => {
  const message = currentMessage.value.trim()
  if (!message) return
  console.log('[ChatInteraction] 📤 메시지 전송. Store 액션을 호출합니다.')
  learningStore.sendMessage(message)
  currentMessage.value = ''
  nextTick(() => messageInputRef.value?.focus())
}

const handleRetryLearning = () => {
  console.log('[ChatInteraction] 🔄 재학습 요청. Store 액션을 호출합니다.')
  learningStore.completeSession('retry')
}

const handleProceedLearning = () => {
  console.log('[ChatInteraction] ➡️ 다음 학습 요청. Store 액션을 호출합니다.')
  learningStore.completeSession('proceed')
}

// 모달 관련 로직
const closeModal = () => {
  console.log('[ChatInteraction] 모달 닫기.')
  learningStore.sessionCompleted = false
}

const goToDashboard = () => {
  closeModal()
  router.push('/dashboard')
}

const startNewLearning = () => {
  closeModal()
  learningStore.startNewSession()
}

// --- 유틸리티 및 라이프사이클 훅 (원본과 동일) ---
const handleKeyPress = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const handleInput = (event) => {
  const target = event.target
  target.style.height = 'auto'
  target.style.height = target.scrollHeight + 'px'
}

const getMessageClass = (messageType) => {
  const baseClass = 'chat-message'
  switch (messageType) {
    case 'user': return `${baseClass} user-message`
    case 'system': return `${baseClass} system-message`
    case 'qna': return `${baseClass} qna-message`
    default: return `${baseClass} system-message`
  }
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '방금 전'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    chatHistoryRef.value?.scrollTo({ top: chatHistoryRef.value.scrollHeight, behavior: 'smooth' })
  })
}

watch(chatHistory, () => scrollToBottom(), { deep: true })

onMounted(() => {
  scrollToBottom()
  messageInputRef.value?.focus()
})
</script>

<style lang="scss" scoped>
/* 원본의 모든 스타일을 그대로 유지합니다. */
.chat-mode { display: flex; flex-direction: column; gap: $spacing-md; height: 100%; transition: opacity 0.3s ease; min-height: 0; }
.chat-mode.active { opacity: 1; }
.chat-history { flex: 1; overflow-y: auto; background: $white; border-radius: $border-radius-lg; padding: $spacing-md; border: 1px solid $gray-300; scroll-behavior: smooth; display: flex; flex-direction: column; min-height: 0; }
.chat-history::-webkit-scrollbar { width: 6px; }
.chat-history::-webkit-scrollbar-track { background: $gray-100; border-radius: 3px; }
.chat-history::-webkit-scrollbar-thumb { background: $gray-400; border-radius: 3px; }
.chat-history::-webkit-scrollbar-thumb:hover { background: $gray-500; }
.chat-message { margin-bottom: $spacing-md; padding: $spacing-md * 0.75; border-radius: $border-radius-lg; animation: messageSlideIn 0.3s ease-out; max-width: 85%; width: fit-content; }
@keyframes messageSlideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.user-message { background: lighten($primary, 40%); margin-left: auto; margin-right: 0; border-bottom-right-radius: $border-radius-sm; align-self: flex-end; }
.system-message { background: lighten($warning, 38%); margin-right: auto; margin-left: 0; border-bottom-left-radius: $border-radius-sm; align-self: flex-start; }
.qna-message { background: lighten($brand-purple, 40%); border-left: 3px solid $brand-purple; margin-right: auto; margin-left: 0; align-self: flex-start; }
.message-content { display: flex; flex-direction: column; gap: $spacing-xs; }
.message-sender { font-size: $font-size-sm; color: $gray-700; }
.message-text { line-height: 1.5; word-wrap: break-word; }
.message-timestamp { font-size: $font-size-sm * 0.85; color: $secondary; text-align: right; margin-top: $spacing-xs; }
.chat-input-container { display: flex; flex-direction: column; gap: $spacing-md * 0.75; flex-shrink: 0; }
.input-hints { background: $gray-100; border: 1px solid $gray-300; border-radius: $border-radius; padding: $spacing-md * 0.75; font-size: $font-size-sm; }
.hint-item { margin-bottom: $spacing-sm; line-height: 1.4; color: $gray-700; }
.hint-item:last-child { margin-bottom: 0; }
.chat-input { display: flex; gap: $spacing-sm; align-items: flex-end; }
.message-input { flex: 1; padding: $spacing-md * 0.75; border: 1px solid $gray-300; border-radius: $border-radius; font-size: $font-size-sm; line-height: 1.5; resize: none; min-height: 44px; max-height: 120px; transition: border-color 0.2s ease; }
.message-input:focus { outline: none; border-color: $primary; box-shadow: 0 0 0 2px rgba($primary, 0.25); }
.message-input:disabled { background: $gray-100; opacity: 0.7; }
.send-button { padding: $spacing-md * 0.75 $spacing-md; background: $primary; color: $white; border: none; border-radius: $border-radius; cursor: pointer; font-weight: 500; transition: all 0.2s ease; min-width: 60px; display: flex; align-items: center; justify-content: center; }
.send-button:hover:not(:disabled) { background: darken($primary, 10%); transform: translateY(-1px); }
.send-button:disabled, .send-button.btn-disabled { background: $gray-500; cursor: not-allowed; transform: none; }
.quick-actions { display: flex; gap: $spacing-sm; flex-wrap: wrap; }
.quick-action-btn { padding: $spacing-sm $spacing-md * 0.75; background: $gray-100; border: 1px solid $gray-300; border-radius: $border-radius-pill; font-size: $font-size-sm; cursor: pointer; transition: all 0.2s ease; white-space: nowrap; }
.quick-action-btn:hover:not(:disabled) { background: $gray-200; border-color: $gray-500; transform: translateY(-1px); }
.quick-action-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.button-spinner { width: 16px; height: 16px; border: 2px solid transparent; border-top: 2px solid $white; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba($black, 0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.modal-content { background: $white; border-radius: $border-radius-lg * 1.5; box-shadow: 0 10px 25px rgba($black, 0.15); max-width: 500px; width: 90%; max-height: 90vh; overflow-y: auto; animation: slideUp 0.3s ease; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: $spacing-lg; border-bottom: 1px solid $gray-300; }
.modal-header h3 { margin: 0; font-size: $font-size-lg; font-weight: 600; color: $gray-900; }
.modal-close-btn { background: none; border: none; font-size: $font-size-lg * 1.2; color: $secondary; cursor: pointer; padding: 0; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border-radius: 50%; transition: all 0.2s ease; }
.modal-close-btn:hover { background: $gray-100; color: $gray-700; }
.modal-body { padding: $spacing-lg; color: $gray-700; line-height: 1.6; }
.modal-footer { display: flex; gap: $spacing-md * 0.75; padding: $spacing-lg; border-top: 1px solid $gray-300; justify-content: flex-end; }
.modal-btn { padding: $spacing-md * 0.75 $spacing-lg; border: none; border-radius: $border-radius-lg; font-weight: 500; cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; gap: $spacing-sm; font-size: $font-size-sm; }
.dashboard-btn { background: $secondary; color: $white; }
.dashboard-btn:hover { background: darken($secondary, 10%); transform: translateY(-1px); }
.start-learning-btn { background: $primary; color: $white; }
.start-learning-btn:hover { background: darken($primary, 10%); transform: translateY(-1px); }
</style>