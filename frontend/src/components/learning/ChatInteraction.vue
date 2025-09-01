<!-- frontend/src/components/learning/ChatInteraction.vue -->
<template>
  <div class="chat-mode" :class="{ active: true }">
    <div class="chat-history" ref="chatHistoryRef">
      <div v-for="message in chatHistory" :key="message.id || message.timestamp" class="chat-message"
        :class="getMessageClass(message)">
        <div class="message-content">
          <strong class="message-sender">{{ message.sender }}:</strong>
          
          <div v-if="message.type === 'loading' || (message.type === 'qna-streaming' && !message.message)" class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
          
          <span v-else class="message-text">{{ formatMessage(message.message) }}</span>
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
          placeholder="메시지를 입력하거나 질문해보세요..." @keypress.enter.prevent="handleSendMessage"
          :disabled="isTutorReplying"
          class="message-input" />
        <button 
          @click="handleSendMessage" 
          :disabled="!currentMessage.trim() || isTutorReplying" 
          class="send-button">
          {{ isTutorReplying ? '응답 중...' : '전송' }}
        </button>
      </div>
    </div>
    
    <div v-if="showCompletionModal" class="modal-overlay" @click="closeModal">
      </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useLearningStore } from '@/stores/learningStore';
import { storeToRefs } from 'pinia';

// 스토어 연결
const router = useRouter();
const learningStore = useLearningStore();
const { 
  chatHistory, 
  completedSteps, 
  sessionCompleted, 
  sessionProgressStage,
  isTutorReplying
} = storeToRefs(learningStore);

console.log('[ChatInteraction] 🟢 컴포넌트 초기화 완료.');

const currentMessage = ref('');
const chatHistoryRef = ref(null);
const messageInputRef = ref(null);

// computed 속성
const isFeedbackComplete = computed(() => completedSteps.value.feedback);
const showQuickActions = computed(() => isFeedbackComplete.value);
const showInputHints = computed(() => sessionProgressStage.value === 'theory_completed');
const showCompletionModal = computed(() => sessionCompleted.value);

const handleSendMessage = () => {
  const message = currentMessage.value.trim();
  if (!message || isTutorReplying.value) return;
  
  console.log(`[ChatInteraction] 📤 메시지 전송: "${message}"`);
  learningStore.sendMessage(message);
  
  currentMessage.value = '';
  nextTick(() => messageInputRef.value?.focus());
};

// 재학습/다음학습 핸들러
const handleRetryLearning = () => learningStore.completeSession('retry');
const handleProceedLearning = () => learningStore.completeSession('proceed');
const closeModal = () => learningStore.sessionCompleted = false;
const goToDashboard = () => { closeModal(); router.push('/dashboard'); };
const startNewLearning = () => { closeModal(); learningStore.startNewSession(); };

// 메시지 포맷 및 스타일링
const formatMessage = (text) => text ? text.replace(/##\s?/g, '').replace(/\*\*/g, '') : '';

const getMessageClass = (message) => {
  const baseClass = 'chat-message';
  switch (message.type) {
    case 'user': return `${baseClass} user-message`;
    case 'system': return `${baseClass} system-message`;
    case 'qna': return `${baseClass} qna-message`;
    case 'loading': return `${baseClass} system-message loading-message`;
    case 'qna-streaming': return `${baseClass} qna-message`; // 🚀 [핵심 수정] 스트리밍 메시지는 기본 qna 스타일만 적용
    default: return `${baseClass} system-message`;
  }
};

const formatTimestamp = (ts) => new Date(ts).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });

// 스크롤 처리
const scrollToBottom = () => {
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight;
    }
  });
};

watch(chatHistory, () => scrollToBottom(), { deep: true });
onMounted(() => {
  scrollToBottom();
  messageInputRef.value?.focus();
});
</script>

<style lang="scss" scoped>
/* style 태그의 내용은 이전과 완전히 동일합니다. */
.chat-mode {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  height: 100%;
  transition: opacity 0.3s ease;
  min-height: 0;
}

.chat-mode.active {
  opacity: 1;
}

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
  min-height: 0;
}

.chat-history::-webkit-scrollbar {
  width: 6px;
}

.chat-history::-webkit-scrollbar-track {
  background: $gray-100;
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb {
  background: $gray-400;
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb:hover {
  background: $gray-500;
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
  margin-left: auto;
  margin-right: 0;
  border-bottom-right-radius: $border-radius-sm;
  align-self: flex-end;
}

.system-message {
  background: lighten($warning, 38%);
  margin-right: auto;
  margin-left: 0;
  border-bottom-left-radius: $border-radius-sm;
  align-self: flex-start;
}

.qna-message {
  background: lighten($brand-purple, 40%);
  border-left: 3px solid $brand-purple;
  margin-right: auto;
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
  white-space: pre-wrap;
}

.message-timestamp {
  font-size: $font-size-sm * 0.85;
  color: $secondary;
  text-align: right;
  margin-top: $spacing-xs;
}

.chat-input-container {
  display: flex;
  flex-direction: column;
  gap: $spacing-md * 0.75;
  flex-shrink: 0;
}

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
}

.hint-item:last-child {
  margin-bottom: 0;
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
}

.message-input:focus {
  outline: none;
  border-color: $primary;
  box-shadow: 0 0 0 2px rgba($primary, 0.25);
}

.message-input:disabled {
  background: $gray-100;
  opacity: 0.7;
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
}

.send-button:hover:not(:disabled) {
  background: darken($primary, 10%);
  transform: translateY(-1px);
}

.send-button:disabled,
.send-button.btn-disabled {
  background: $gray-500;
  cursor: not-allowed;
  transform: none;
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
}

.quick-action-btn:hover:not(:disabled) {
  background: $gray-200;
  border-color: $gray-500;
  transform: translateY(-1px);
}

.quick-action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  border-radius: $border-radius-lg * 1.5;
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
}

.modal-header h3 {
  margin: 0;
  font-size: $font-size-lg;
  font-weight: 600;
  color: $gray-900;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: $font-size-lg * 1.2;
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
}

.modal-close-btn:hover {
  background: $gray-100;
  color: $gray-700;
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
}

.dashboard-btn:hover {
  background: darken($secondary, 10%);
  transform: translateY(-1px);
}

.start-learning-btn {
  background: $primary;
  color: $white;
}

.start-learning-btn:hover {
  background: darken($primary, 10%);
  transform: translateY(-1px);
}

/* --- 타이핑 애니메이션 스타일 --- */
.loading-message {
  padding-bottom: 1.1rem;
}

.typing-indicator {
  span {
    height: 10px;
    width: 10px;
    background-color: $gray-600;
    border-radius: 50%;
    display: inline-block;
    margin: 0 2px;
    animation: bounce 1.4s infinite both;
  }
  span:nth-child(1) {
    animation-delay: -0.32s;
  }
  span:nth-child(2) {
    animation-delay: -0.16s;
  }
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1.0);
  }
}
</style>