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
          <div class="message-text" v-html="formatMessageContent(message)"></div>
        </div>
        <div class="message-timestamp">
          {{ formatTimestamp(message.timestamp) }}
        </div>
      </div>
      
      <!-- 로딩 메시지 -->
      <div v-if="isApiLoading" class="chat-message system-message loading-message">
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
          :disabled="isApiLoading"
        >
          ➡️ 다음 단계
        </button>
        <button 
          class="quick-action-btn"
          @click="sendQuickMessage('AI와 머신러닝의 차이가 뭐예요?')"
          :disabled="isApiLoading"
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
          :disabled="isApiLoading"
          class="message-input"
        />
        <button 
          @click="sendMessage"
          :disabled="isApiLoading || !currentMessage.trim()"
          class="send-button"
          :class="{ 'btn-disabled': isApiLoading || !currentMessage.trim() }"
        >
          <span v-if="isApiLoading" class="button-spinner"></span>
          <span v-else>전송</span>
        </button>
      </div>
      
      <!-- 에러 상태 및 재시도 -->
      <div v-if="learningStore.hasError" class="error-container">
        <div class="error-message">
          ⚠️ {{ learningStore.errorState.error_message }}
        </div>
        <button 
          v-if="learningStore.canRetry"
          @click="retryLastMessage"
          class="retry-button"
          :disabled="isApiLoading"
        >
          🔄 다시 시도
        </button>
      </div>
      
      <!-- 입력 힌트 -->
      <div class="input-hints" v-if="showInputHints && !learningStore.hasError">
        <div class="hint-item">
          💡 <strong>팁:</strong> "다음으로 넘어가주세요"라고 입력하면 퀴즈로 이동합니다.
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
import { useLearningStore } from '../../stores/learningStore.js'
import { useTutorStore } from '../../stores/tutorStore.js'

// Store 인스턴스
const learningStore = useLearningStore()
const tutorStore = useTutorStore()

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

// Emits 정의 (하위 호환성을 위해 유지)
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
    case 'theory':
      return `${baseClass} theory-message`
    case 'feedback':
      return `${baseClass} feedback-message`
    case 'evaluation':
      return `${baseClass} evaluation-message`
    default:
      return `${baseClass} system-message`
  }
}

// QnA 타입 메시지 포맷팅
const formatQnAMessage = (message) => {
  if (typeof message === 'string') {
    return message
  }
  
  // QnA 타입의 구조화된 응답 처리
  if (message.question && message.answer) {
    return `**Q: ${message.question}**\n\nA: ${message.answer}`
  }
  
  return message.content || message.message || '응답을 처리할 수 없습니다.'
}

// 메시지 내용 포맷팅 (타입별 처리)
const formatMessageContent = (message) => {
  if (!message) return ''
  
  switch (message.type) {
    case 'qna':
      return formatQnAMessage(message.message)
    case 'theory':
      return message.message || message.content || ''
    case 'feedback':
      return message.message || message.content || ''
    case 'evaluation':
      // 평가 결과 포맷팅
      if (message.metadata) {
        const { is_correct, score, explanation } = message.metadata
        let formatted = message.message || ''
        if (explanation) {
          formatted += `\n\n💡 **설명:** ${explanation}`
        }
        if (typeof score === 'number') {
          formatted += `\n\n📊 **점수:** ${score}점`
        }
        return formatted
      }
      return message.message || ''
    default:
      return message.message || message.content || ''
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

// learningStore 로딩 상태 확인 (props.isLoading과 통합)
const isApiLoading = computed(() => {
  return props.isLoading || learningStore.isLoading
})

// 메시지 전송 처리 (learningStore API 연동)
const sendMessage = async () => {
  const message = currentMessage.value.trim()
  if (!message || isApiLoading.value) return
  
  console.log('ChatInteraction: 메시지 전송 시작:', message)
  
  try {
    // 사용자 메시지를 즉시 채팅 히스토리에 추가
    tutorStore.addChatMessage({
      sender: '사용자',
      message: message,
      type: 'user',
      timestamp: new Date()
    })
    
    // 입력창 초기화 (사용자 경험 개선)
    currentMessage.value = ''
    
    // learningStore를 통한 API 호출
    const result = await learningStore.sendMessage(message, 'user')
    
    if (result.success) {
      console.log('ChatInteraction: 메시지 전송 성공:', result.data)
      
      // API 응답의 workflow_response는 learningStore에서 자동으로 처리되고
      // tutorStore의 watch를 통해 UI가 업데이트됨
      
      // 하위 호환성을 위해 부모 컴포넌트에도 이벤트 전송
      emit('send-message', message)
      
    } else {
      console.error('ChatInteraction: 메시지 전송 실패:', result.error)
      
      // 에러 메시지를 채팅에 추가
      tutorStore.addChatMessage({
        sender: '시스템',
        message: `메시지 전송에 실패했습니다: ${result.error}`,
        type: 'system',
        timestamp: new Date()
      })
    }
    
  } catch (error) {
    console.error('ChatInteraction: 메시지 전송 중 예외 발생:', error)
    
    // 예외 상황 메시지 추가
    tutorStore.addChatMessage({
      sender: '시스템',
      message: '메시지 전송 중 오류가 발생했습니다. 다시 시도해주세요.',
      type: 'system',
      timestamp: new Date()
    })
  }
  
  // 입력창에 포커스
  nextTick(() => {
    if (messageInputRef.value) {
      messageInputRef.value.focus()
    }
  })
}

// 에러 재시도 처리
const retryLastMessage = async () => {
  if (!learningStore.canRetry) {
    console.warn('ChatInteraction: 재시도 불가능한 상태')
    return
  }
  
  console.log('ChatInteraction: 마지막 메시지 재시도 시도')
  
  try {
    const result = await learningStore.retryLastAction('sendMessage', currentMessage.value)
    
    if (result.success) {
      console.log('ChatInteraction: 재시도 성공')
      tutorStore.addChatMessage({
        sender: '시스템',
        message: '✅ 메시지가 성공적으로 전송되었습니다.',
        type: 'system',
        timestamp: new Date()
      })
    } else {
      console.error('ChatInteraction: 재시도 실패:', result.error)
    }
  } catch (error) {
    console.error('ChatInteraction: 재시도 중 예외:', error)
  }
}

// 세션 상태 확인
const checkSessionStatus = () => {
  if (!learningStore.isSessionActive) {
    tutorStore.addChatMessage({
      sender: '시스템',
      message: '⚠️ 활성 세션이 없습니다. 학습을 시작해주세요.',
      type: 'system',
      timestamp: new Date()
    })
    return false
  }
  return true
}

// 디버그 정보 표시 (개발용)
const showDebugInfo = () => {
  const debugInfo = {
    learningStore: {
      isSessionActive: learningStore.isSessionActive,
      isLoading: learningStore.isLoading,
      hasError: learningStore.hasError,
      currentAgent: learningStore.workflowState.current_agent,
      sessionId: learningStore.sessionState.session_id
    },
    tutorStore: {
      currentAgent: tutorStore.currentAgent,
      currentUIMode: tutorStore.currentUIMode,
      chatHistoryLength: tutorStore.chatHistory.length,
      isConnected: tutorStore.isConnectedToLearningStore
    }
  }
  
  console.log('ChatInteraction 디버그 정보:', debugInfo)
  return debugInfo
}

const sendQuickMessage = async (message) => {
  if (isApiLoading.value) return
  
  currentMessage.value = message
  await sendMessage()
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

// learningStore 로딩 상태 감시
watch(() => learningStore.isLoading, (newValue) => {
  if (newValue) {
    scrollToBottom()
  }
})

// tutorStore 채팅 히스토리 변화 감시 (실시간 UI 업데이트)
watch(() => tutorStore.chatHistory, () => {
  scrollToBottom()
}, { deep: true })

// learningStore 에러 상태 감시
watch(() => learningStore.hasError, (hasError) => {
  if (hasError && learningStore.errorState.error_message) {
    console.warn('ChatInteraction: learningStore 에러 감지:', learningStore.errorState.error_message)
    
    // 에러 메시지를 채팅에 표시
    tutorStore.addChatMessage({
      sender: '시스템',
      message: `⚠️ ${learningStore.errorState.error_message}`,
      type: 'system',
      timestamp: new Date()
    })
  }
})

// 세션 상태 변화 감시
watch(() => learningStore.isSessionActive, (isActive) => {
  if (!isActive) {
    console.log('ChatInteraction: 세션이 비활성화됨')
    // 세션이 종료되면 입력 비활성화 등의 처리 가능
  }
})

// 라이프사이클 훅
onMounted(() => {
  console.log('ChatInteraction 마운트됨')
  
  // 초기 상태 확인
  console.log('초기 상태:', {
    learningStoreActive: learningStore.isSessionActive,
    tutorStoreAgent: tutorStore.currentAgent,
    tutorStoreUIMode: tutorStore.currentUIMode,
    chatHistoryLength: tutorStore.chatHistory.length
  })
  
  scrollToBottom()
  
  // 입력창에 포커스
  if (messageInputRef.value) {
    messageInputRef.value.focus()
  }
  
  // learningStore 연동 상태 확인
  if (learningStore.isSessionActive) {
    console.log('ChatInteraction: 활성 세션 감지됨, 세션 정보:', learningStore.sessionSummary)
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

.theory-message {
  background: #e8f5e8;
  border-left: 3px solid #4caf50;
  margin-right: 2rem;
  margin-left: 0;
  align-self: flex-start;
}

.feedback-message {
  background: #fff3e0;
  border-left: 3px solid #ff9800;
  margin-right: 2rem;
  margin-left: 0;
  align-self: flex-start;
}

.evaluation-message {
  background: #e3f2fd;
  border-left: 3px solid #2196f3;
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
  white-space: pre-wrap; /* 줄바꿈 문자 처리 */
}

/* QnA 메시지 내 강조 텍스트 스타일 */
.message-text strong {
  color: #333;
  font-weight: 600;
}

/* 메시지 내 이모지 및 아이콘 스타일 */
.message-text .emoji {
  font-size: 1.1em;
  margin-right: 0.25rem;
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

/* 에러 컨테이너 */
.error-container {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 0.375rem;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.error-message {
  flex: 1;
  font-size: 0.875rem;
  color: #c53030;
  line-height: 1.4;
}

.retry-button {
  padding: 0.5rem 0.75rem;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  white-space: nowrap;
}

.retry-button:hover:not(:disabled) {
  background: #c53030;
}

.retry-button:disabled {
  background: #a0aec0;
  cursor: not-allowed;
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
  .qna-message,
  .theory-message,
  .feedback-message,
  .evaluation-message {
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
  
  .error-container {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .retry-button {
    width: 100%;
  }
}
</style>