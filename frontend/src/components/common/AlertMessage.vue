<!-- frontend/src/components/common/AlertMessage.vue -->
<template>
  <transition name="alert-fade">
    <div 
      v-if="isVisible" 
      class="alert-message" 
      :class="[
        `alert-${type}`,
        { 'alert-dismissible': dismissible }
      ]"
      role="alert"
    >
      <!-- 아이콘 -->
      <div class="alert-icon">
        <svg v-if="type === 'success'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
        <svg v-else-if="type === 'error'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
        <svg v-else-if="type === 'warning'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
        </svg>
        <svg v-else-if="type === 'info'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
        </svg>
      </div>

      <!-- 메시지 내용 -->
      <div class="alert-content">
        <div v-if="title" class="alert-title">{{ title }}</div>
        <div class="alert-message-text">{{ message }}</div>
        
        <!-- 추가 액션 버튼들 (선택적) -->
        <div v-if="actions && actions.length > 0" class="alert-actions">
          <button
            v-for="action in actions"
            :key="action.label"
            @click="handleActionClick(action)"
            class="alert-action-btn"
            :class="action.style || 'primary'"
          >
            {{ action.label }}
          </button>
        </div>
      </div>

      <!-- 닫기 버튼 -->
      <button 
        v-if="dismissible" 
        @click="handleClose"
        class="alert-close-btn"
        aria-label="알림 닫기"
      >
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
      </button>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Props 정의
const props = defineProps({
  // 알림 타입
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  // 알림 제목
  title: {
    type: String,
    default: ''
  },
  // 알림 메시지
  message: {
    type: String,
    required: true
  },
  // 표시 여부
  visible: {
    type: Boolean,
    default: true
  },
  // 닫기 버튼 표시 여부
  dismissible: {
    type: Boolean,
    default: true
  },
  // 자동 닫기 시간 (밀리초, 0이면 자동 닫기 안함)
  autoClose: {
    type: Number,
    default: 5000
  },
  // 액션 버튼들
  actions: {
    type: Array,
    default: () => []
  }
})

// 이벤트 정의
const emit = defineEmits(['close', 'action'])

// 반응형 데이터
const isVisible = ref(props.visible)
let autoCloseTimer = null

// 계산된 속성
const shouldAutoClose = computed(() => props.autoClose > 0)

// 자동 닫기 타이머 설정
const setupAutoClose = () => {
  if (shouldAutoClose.value && isVisible.value) {
    autoCloseTimer = setTimeout(() => {
      handleClose()
    }, props.autoClose)
  }
}

// 타이머 정리
const clearAutoCloseTimer = () => {
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer)
    autoCloseTimer = null
  }
}

// 닫기 처리
const handleClose = () => {
  isVisible.value = false
  clearAutoCloseTimer()
  emit('close')
}

// 액션 버튼 클릭 처리
const handleActionClick = (action) => {
  emit('action', action)
  if (action.closeOnClick !== false) {
    handleClose()
  }
}

// 라이프사이클 훅
onMounted(() => {
  setupAutoClose()
})

onUnmounted(() => {
  clearAutoCloseTimer()
})

// props.visible 변경 감지
const unwatchVisible = computed(() => {
  isVisible.value = props.visible
  if (props.visible) {
    setupAutoClose()
  } else {
    clearAutoCloseTimer()
  }
})
</script>

<style lang="scss" scoped>
.alert-message {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
  position: relative;

  // 타입별 스타일
  &.alert-success {
    background-color: #f0f9ff;
    border-left-color: #10b981;
    color: #065f46;

    .alert-icon {
      color: #10b981;
    }
  }

  &.alert-error {
    background-color: #fef2f2;
    border-left-color: #ef4444;
    color: #991b1b;

    .alert-icon {
      color: #ef4444;
    }
  }

  &.alert-warning {
    background-color: #fffbeb;
    border-left-color: #f59e0b;
    color: #92400e;

    .alert-icon {
      color: #f59e0b;
    }
  }

  &.alert-info {
    background-color: #eff6ff;
    border-left-color: #3b82f6;
    color: #1e40af;

    .alert-icon {
      color: #3b82f6;
    }
  }
}

.alert-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  margin-right: 0.75rem;
  margin-top: 0.125rem;

  svg {
    width: 100%;
    height: 100%;
  }
}

.alert-content {
  flex: 1;
  min-width: 0;

  .alert-title {
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 0.25rem;
  }

  .alert-message-text {
    font-size: 0.875rem;
    line-height: 1.4;
    word-break: break-word;
  }

  .alert-actions {
    margin-top: 0.75rem;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;

    .alert-action-btn {
      padding: 0.375rem 0.75rem;
      border-radius: 4px;
      border: none;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;

      &.primary {
        background-color: var(--primary-color);
        color: white;

        &:hover {
          background-color: var(--primary-color-dark);
        }
      }

      &.secondary {
        background-color: transparent;
        color: currentColor;
        border: 1px solid currentColor;

        &:hover {
          background-color: rgba(0, 0, 0, 0.05);
        }
      }

      &.danger {
        background-color: #ef4444;
        color: white;

        &:hover {
          background-color: #dc2626;
        }
      }
    }
  }
}

.alert-close-btn {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  background: none;
  border: none;
  color: currentColor;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s ease;
  margin-left: 0.5rem;

  &:hover {
    opacity: 1;
  }

  svg {
    width: 100%;
    height: 100%;
  }
}

// 애니메이션
.alert-fade-enter-active,
.alert-fade-leave-active {
  transition: all 0.3s ease;
}

.alert-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.alert-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

// 반응형 디자인
@media (max-width: 480px) {
  .alert-message {
    padding: 0.75rem;

    .alert-content {
      .alert-actions {
        .alert-action-btn {
          padding: 0.25rem 0.5rem;
          font-size: 0.8125rem;
        }
      }
    }
  }
}
</style>