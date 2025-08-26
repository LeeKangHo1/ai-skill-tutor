<!-- frontend/src/components/learning/ChatInteraction.vue -->
<template>
  <div class="chat-mode" :class="{ active: !isLoading }">
    <!-- 채팅 히스토리 -->
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

      <!-- 로딩 메시지 -->
      <div v-if="isLoading" class="chat-message system-message loading-message">
        <div class="message-content">
          <strong class="message-sender">튜터:</strong>
          <span class="typing-indicator">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </span>
        </div>
      </div>
    </div>

    <!-- 메시지 입력 영역 -->
    <div class="chat-input-container">
      <div class="quick-actions" v-if="showQuickActions">
        <button class="quick-action-btn" @click="handleRetryLearning" :disabled="isLoading || !isFeedbackComplete">
          🔄 재학습
        </button>
        <button class="quick-action-btn" @click="handleProceedLearning" :disabled="isLoading || !isFeedbackComplete">
          ➡️ 다음 학습
        </button>
      </div>

      <div class="chat-input">
        <input type="text" v-model="currentMessage" ref="messageInputRef"
          placeholder="메시지를 입력하세요 (예: 퀴즈, AI와 머신러닝 차이는?)" @keypress="handleKeyPress" @input="handleInput"
          :disabled="isLoading" class="message-input" />
        <button @click="sendMessage" :disabled="isLoading || !currentMessage.trim()" class="send-button"
          :class="{ 'btn-disabled': isLoading || !currentMessage.trim() }">
          <span v-if="isLoading" class="button-spinner"></span>
          <span v-else>전송</span>
        </button>
      </div>

      <!-- 입력 힌트 -->
      <div class="input-hints" v-if="showInputHints">
        <div class="hint-item">
          💡 <strong>팁:</strong> "다음"이라고 입력하면 퀴즈로 이동합니다.
        </div>
        <div class="hint-item">
          🤔 <strong>질문:</strong> 학습 내용에 대해 궁금한 점을 자유롭게 물어보세요.
        </div>
      </div>
    </div>

    <!-- 학습 완료 모달 -->
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
import { ref, nextTick, watch, onMounted, defineProps, defineEmits, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import tokenManager from '@/utils/tokenManager'
import { useAuthStore } from '@/stores/authStore'
import { useLearningStore } from '@/stores/learningStore'

// Props 정의
const props = defineProps({
  chatHistory: {
    type: Array,
    required: true,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  showQuickActions: {
    type: Boolean,
    default: true
  },
  showInputHints: {
    type: Boolean,
    default: true
  }
})

// Emits 정의
const emit = defineEmits(['send-message', 'session-complete'])

// 라우터 및 스토어 사용
const router = useRouter()
const authStore = useAuthStore()
const learningStore = useLearningStore()

const isFeedbackComplete = computed(() => learningStore.completedSteps.feedback)

// 반응형 상태
const currentMessage = ref('')
const chatHistoryRef = ref(null)
const messageInputRef = ref(null)
const showCompletionModal = ref(false)
const isProcessing = ref(false)
const isDashboardLoading = ref(false)

// 메시지 클래스 결정
const getMessageClass = (messageType) => {
  const baseClass = 'chat-message'
  switch (messageType) {
    case 'user':
      return `${baseClass} user-message`
    case 'system':
      return `${baseClass} system-message`
    case 'qna':
      return `${baseClass} qna-message`
    default:
      return `${baseClass} system-message`
  }
}

// 타임스탬프 포맷팅
const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  const now = new Date()
  const diffInMinutes = Math.floor((now - date) / (1000 * 60))

  if (diffInMinutes < 1) {
    return '방금 전'
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}분 전`
  } else {
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

// 이벤트 핸들러들
const handleKeyPress = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const handleInput = (event) => {
  // 자동 높이 조절 (선택사항)
  const target = event.target
  target.style.height = 'auto'
  target.style.height = target.scrollHeight + 'px'
}

const sendMessage = () => {
  const message = currentMessage.value.trim()
  if (!message || props.isLoading) return

  // 부모 컴포넌트로 메시지 전송
  emit('send-message', message)

  // 입력창 초기화
  currentMessage.value = ''

  // 입력창에 포커스
  nextTick(() => {
    if (messageInputRef.value) {
      messageInputRef.value.focus()
    }
  })
}



// 재학습 처리
const handleRetryLearning = async () => {
  if (isProcessing.value) return

  try {
    isProcessing.value = true

    const response = await axios.post('/api/v1/learning/session/complete', {
      proceed_decision: 'retry'
    }, {
      headers: {
        'Authorization': `Bearer ${tokenManager.getAccessToken()}`
      }
    })

    if (response.data.success) {
      // 응답에서 새로운 토큰이나 사용자 정보가 있다면 업데이트
      if (response.data.data?.access_token) {
        authStore.updateUserFromToken(response.data.data.access_token)
      }

      // 사용자 정보 업데이트 (진행 상태 등)
      if (response.data.data?.user_info) {
        authStore.user = { ...authStore.user, ...response.data.data.user_info }
        tokenManager.setUserInfo(authStore.user)
      }

      showCompletionModal.value = true
    }
  } catch (error) {
    console.error('재학습 요청 실패:', error)
    alert('재학습 요청에 실패했습니다. 다시 시도해주세요.')
  } finally {
    isProcessing.value = false
  }
}

// 다음 학습 처리
const handleProceedLearning = async () => {
  if (isProcessing.value) return

  try {
    isProcessing.value = true

    const response = await axios.post('/api/v1/learning/session/complete', {
      proceed_decision: 'proceed'
    }, {
      headers: {
        'Authorization': `Bearer ${tokenManager.getAccessToken()}`
      }
    })

    if (response.data.success) {
      console.log('다음 학습 응답 데이터:', response.data)

      // 서버에서 최신 사용자 정보 강제 조회하여 authStore 갱신
      try {
        await authStore.updateUserInfo()
        console.log('사용자 정보 갱신 완료:', authStore.user)
      } catch (updateError) {
        console.warn('사용자 정보 갱신 실패:', updateError)
      }

      showCompletionModal.value = true
    }
  } catch (error) {
    console.error('다음 학습 요청 실패:', error)
    alert('다음 학습 요청에 실패했습니다. 다시 시도해주세요.')
  } finally {
    isProcessing.value = false
  }
}

// 모달 닫기
const closeModal = () => {
  showCompletionModal.value = false
}

// 대시보드로 이동
const goToDashboard = async () => {
  if (isDashboardLoading.value) return

  try {
    isDashboardLoading.value = true

    // 대시보드 이동 전 사용자 정보 갱신
    await authStore.updateUserInfo()
    console.log('대시보드 이동 전 사용자 정보 갱신 완료:', authStore.user)

    closeModal()
    router.push('/dashboard')
  } catch (error) {
    console.error('대시보드 이동 중 사용자 정보 갱신 실패:', error)
    // 갱신 실패해도 대시보드로 이동 시도 (라우터 가드에서 처리)
    closeModal()
    router.push('/dashboard')
  } finally {
    isDashboardLoading.value = false
  }
}

// 새로운 학습 시작
const startNewLearning = async () => {
  try {
    // 로딩 상태 시작
    isProcessing.value = true

    console.log('새 학습 세션으로 이동 중...')

    // start 요청은 LearningPage에서 처리하도록 하고, 여기서는 바로 페이지 이동
    // 약간의 딜레이를 주어 사용자가 로딩을 인지할 수 있도록 함
    setTimeout(() => {
      window.location.href = '/learning'
    }, 500)

  } catch (error) {
    console.error('새 학습 세션 이동 실패:', error)
    alert('새 학습 세션 이동에 실패했습니다. 다시 시도해주세요.')
    isProcessing.value = false
  }
}

// 채팅 히스토리 스크롤 자동 이동
const scrollToBottom = () => {
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
    }
  })
}

// 감시자
watch(() => props.chatHistory, () => {
  scrollToBottom()
}, { deep: true })

watch(() => props.isLoading, (newValue) => {
  if (newValue) {
    scrollToBottom()
  }
})

// 라이프사이클 훅
onMounted(() => {
  scrollToBottom()

  // 입력창에 포커스
  if (messageInputRef.value) {
    messageInputRef.value.focus()
  }
})
</script>

<style lang="scss" scoped>
.chat-mode {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  height: 100%;
  opacity: 0.7;
  transition: opacity 0.3s ease;
  min-height: 0; // flexbox 부모에서 overflow가 작동하도록
}

.chat-mode.active {
  opacity: 1;
}

/* 채팅 히스토리 영역 */
.chat-history {
  flex: 1;
  overflow-y: auto;
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-md;
  border: 1px solid $gray-300;
  scroll-behavior: smooth;
  display: flex;
  flex-direction: column;
  min-height: 0; // flexbox 자식에서 overflow가 작동하도록

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: $gray-100;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: $gray-400;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: $gray-500;
  }
}

.chat-message {
  margin-bottom: $spacing-md;
  padding: $spacing-md * 0.75;
  border-radius: $border-radius-lg;
  animation: messageSlideIn 0.3s ease-out;
  max-width: 85%;
  width: fit-content;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  background: lighten($primary, 40%);
  margin-left: $spacing-lg * 1.33; // 2rem
  margin-right: 0;
  border-bottom-right-radius: $border-radius-sm;
  align-self: flex-end;

  .message-content {
    text-align: right;
  }

  .message-timestamp {
    text-align: left;
  }
}

.system-message {
  background: lighten($warning, 38%);
  margin-right: $spacing-lg * 1.33; // 2rem
  margin-left: 0;
  border-bottom-left-radius: $border-radius-sm;
  align-self: flex-start;
}

.qna-message {
  background: lighten($brand-purple, 40%);
  border-left: 3px solid $brand-purple;
  margin-right: $spacing-lg * 1.33; // 2rem
  margin-left: 0;
  align-self: flex-start;
}

.loading-message {
  background: lighten($warning, 35%);
  border: 1px solid lighten($warning, 30%);
  margin-right: $spacing-lg * 1.33; // 2rem
  margin-left: 0;
  align-self: flex-start;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.message-sender {
  font-size: $font-size-sm;
  color: $gray-700;
}

.message-text {
  line-height: 1.5;
  word-wrap: break-word;
}

.message-timestamp {
  font-size: $font-size-sm * 0.85; // 0.75rem
  color: $secondary;
  text-align: right;
  margin-top: $spacing-xs;
}

/* 타이핑 인디케이터 */
.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: $secondary;
  animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typingBounce {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 입력 영역 */
.chat-input-container {
  display: flex;
  flex-direction: column;
  gap: $spacing-md * 0.75;
  flex-shrink: 0;
}

.quick-actions {
  display: flex;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

.quick-action-btn {
  padding: $spacing-sm $spacing-md * 0.75;
  background: $gray-100;
  border: 1px solid $gray-300;
  border-radius: $border-radius-pill;
  font-size: $font-size-sm;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;

  &:hover:not(:disabled) {
    background: $gray-200;
    border-color: $gray-500;
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.chat-input {
  display: flex;
  gap: $spacing-sm;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: $spacing-md * 0.75;
  border: 1px solid $gray-300;
  border-radius: $border-radius;
  font-size: $font-size-sm;
  line-height: 1.5;
  resize: none;
  min-height: 44px;
  max-height: 120px;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: $primary;
    box-shadow: 0 0 0 2px rgba($primary, 0.25);
  }

  &:disabled {
    background: $gray-100;
    opacity: 0.7;
  }
}

.send-button {
  padding: $spacing-md * 0.75 $spacing-md;
  background: $primary;
  color: $white;
  border: none;
  border-radius: $border-radius;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover:not(:disabled) {
    background: darken($primary, 10%);
    transform: translateY(-1px);
  }

  &:disabled,
  &.btn-disabled {
    background: $gray-500;
    cursor: not-allowed;
    transform: none;
  }
}

.button-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid $white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 입력 힌트 */
.input-hints {
  background: $gray-100;
  border: 1px solid $gray-300;
  border-radius: $border-radius;
  padding: $spacing-md * 0.75;
  font-size: $font-size-sm;
}

.hint-item {
  margin-bottom: $spacing-sm;
  line-height: 1.4;
  color: $gray-700;

  &:last-child {
    margin-bottom: 0;
  }
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba($black, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: $white;
  border-radius: $border-radius-lg * 1.5; // 0.75rem
  box-shadow: 0 10px 25px rgba($black, 0.15);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
  border-bottom: 1px solid $gray-300;

  h3 {
    margin: 0;
    font-size: $font-size-lg;
    font-weight: 600;
    color: $gray-900;
  }
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: $font-size-lg * 1.2; // 1.5rem
  color: $secondary;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;

  &:hover {
    background: $gray-100;
    color: $gray-700;
  }
}

.modal-body {
  padding: $spacing-lg;
  color: $gray-700;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  gap: $spacing-md * 0.75;
  padding: $spacing-lg;
  border-top: 1px solid $gray-300;
  justify-content: flex-end;
}

.modal-btn {
  padding: $spacing-md * 0.75 $spacing-lg;
  border: none;
  border-radius: $border-radius-lg;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: $font-size-sm;
}

.dashboard-btn {
  background: $secondary;
  color: $white;

  &:hover {
    background: darken($secondary, 10%);
    transform: translateY(-1px);
  }
}

.start-learning-btn {
  background: $primary;
  color: $white;

  &:hover {
    background: darken($primary, 10%);
    transform: translateY(-1px);
  }
}
</style>