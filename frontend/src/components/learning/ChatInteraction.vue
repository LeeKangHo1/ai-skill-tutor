<!-- frontend/src/components/learning/ChatInteraction.vue -->
<template>
  <div class="chat-mode" :class="{ active: !isLoading }">
    <!-- 채팅 히스토리 -->
    <div class="chat-history" ref="chatHistoryRef">
      <div 
        v-for="(message, index) in chatHistory" 
        :key="index"
        class="chat-message"
        :class="getMessageClass(message.type)"
      >
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
        <button 
          class="quick-action-btn"
          @click="sendQuickMessage('다음으로 넘어가주세요')"
          :disabled="isLoading"
        >
          ➡️ 다음 단계
        </button>
        <button 
          class="quick-action-btn"
          @click="sendQuickMessage('AI와 머신러닝의 차이가 뭐예요?')"
          :disabled="isLoading"
        >
          ❓ 질문하기
        </button>
      </div>
      
      <div class="chat-input">
        <input 
          type="text" 
          v-model="currentMessage"
          ref="messageInputRef"
          placeholder="메시지를 입력하세요... (예: 다음으로 넘어가주세요, AI와 머신러닝 차이는?)"
          @keypress="handleKeyPress"
          @input="handleInput"
          :disabled="isLoading"
          class="message-input"
        />
        <button 
          @click="sendMessage"
          :disabled="isLoading || !currentMessage.trim()"
          class="send-button"
          :class="{ 'btn-disabled': isLoading || !currentMessage.trim() }"
        >
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
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted, defineProps, defineEmits } from 'vue'

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
const emit = defineEmits(['send-message'])

// 반응형 상태
const currentMessage = ref('')
const chatHistoryRef = ref(null)
const messageInputRef = ref(null)

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

const sendQuickMessage = (message) => {
  if (props.isLoading) return
  
  currentMessage.value = message
  sendMessage()
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

<style scoped>
.chat-mode {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
  opacity: 0.7;
  transition: opacity 0.3s ease;
  min-height: 0; /* flexbox 부모에서 overflow가 작동하도록 */
}

.chat-mode.active {
  opacity: 1;
}

/* 채팅 히스토리 영역 */
.chat-history {
  flex: 1;
  overflow-y: auto;
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #dee2e6;
  scroll-behavior: smooth;
  display: flex;
  flex-direction: column;
  min-height: 0; /* flexbox 자식에서 overflow가 작동하도록 */
}

.chat-message {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
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
  background: #e3f2fd;
  margin-left: 2rem;
  margin-right: 0;
  border-bottom-right-radius: 0.25rem;
  align-self: flex-end;
}

.user-message .message-content {
  text-align: right;
}

.user-message .message-timestamp {
  text-align: left;
}

.system-message {
  background: #f1f8e9;
  margin-right: 2rem;
  margin-left: 0;
  border-bottom-left-radius: 0.25rem;
  align-self: flex-start;
}

.qna-message {
  background: #f3e5f5;
  border-left: 3px solid #9c27b0;
  margin-right: 2rem;
  margin-left: 0;
  align-self: flex-start;
}

.loading-message {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  margin-right: 2rem;
  margin-left: 0;
  align-self: flex-start;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.message-sender {
  font-size: 0.875rem;
  color: #495057;
}

.message-text {
  line-height: 1.5;
  word-wrap: break-word;
}

.message-timestamp {
  font-size: 0.75rem;
  color: #6c757d;
  text-align: right;
  margin-top: 0.25rem;
}

/* 타이핑 인디케이터 */
.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6c757d;
  animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typingBounce {
  0%, 80%, 100% {
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
  gap: 0.75rem;
  flex-shrink: 0; /* 입력 영역은 크기가 고정되도록 */
}

.quick-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.quick-action-btn {
  padding: 0.5rem 0.75rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.quick-action-btn:hover:not(:disabled) {
  background: #e9ecef;
  border-color: #adb5bd;
  transform: translateY(-1px);
}

.quick-action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chat-input {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  line-height: 1.5;
  resize: none;
  min-height: 44px;
  max-height: 120px;
  transition: border-color 0.2s ease;
}

.message-input:focus {
  outline: none;
  border-color: #74a8f7;
  box-shadow: 0 0 0 2px rgba(116, 168, 247, 0.25);
}

.message-input:disabled {
  background: #f8f9fa;
  opacity: 0.7;
}

.send-button {
  padding: 0.75rem 1rem;
  background: #74a8f7;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:hover:not(:disabled) {
  background: #5a94f5;
  transform: translateY(-1px);
}

.send-button:disabled,
.btn-disabled {
  background: #adb5bd;
  cursor: not-allowed;
  transform: none;
}

.button-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 입력 힌트 */
.input-hints {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  padding: 0.75rem;
  font-size: 0.875rem;
}

.hint-item {
  margin-bottom: 0.5rem;
  line-height: 1.4;
  color: #495057;
}

.hint-item:last-child {
  margin-bottom: 0;
}

/* 스크롤바 스타일링 */
.chat-history::-webkit-scrollbar {
  width: 6px;
}

.chat-history::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 반응형 */
@media (max-width: 768px) {
  .chat-message {
    padding: 0.5rem;
    margin-left: 0;
    margin-right: 0;
  }
  
  .user-message {
    margin-left: 1rem;
  }
  
  .system-message,
  .qna-message {
    margin-right: 1rem;
  }
  
  .quick-actions {
    flex-direction: column;
  }
  
  .quick-action-btn {
    width: 100%;
  }
  
  .message-input {
    font-size: 16px; /* iOS에서 줌 방지 */
  }
}
</style>