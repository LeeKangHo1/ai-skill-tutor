<!-- frontend/src/components/common/LoadingModal.vue -->
<template>
  <teleport to="body">
    <div v-if="isVisible" class="loading-modal-overlay" @click="handleOverlayClick">
      <div class="loading-modal" :class="{ 'modal-large': size === 'large' }">
        <!-- 로딩 스피너 -->
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
        </div>

        <!-- 로딩 메시지 -->
        <div class="loading-content">
          <h3 class="loading-title">{{ title }}</h3>
          <p v-if="message" class="loading-message">{{ message }}</p>
          
          <!-- 진행률 표시 (선택적) -->
          <div v-if="showProgress && progress !== null" class="progress-container">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: `${progress}%` }"
              ></div>
            </div>
            <span class="progress-text">{{ progress }}%</span>
          </div>
        </div>

        <!-- 취소 버튼 (선택적) -->
        <button 
          v-if="showCancelButton" 
          @click="handleCancel"
          class="cancel-button"
        >
          취소
        </button>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { computed } from 'vue'

// Props 정의
const props = defineProps({
  // 모달 표시 여부
  visible: {
    type: Boolean,
    default: false
  },
  // 로딩 제목
  title: {
    type: String,
    default: '처리 중...'
  },
  // 로딩 메시지
  message: {
    type: String,
    default: ''
  },
  // 모달 크기
  size: {
    type: String,
    default: 'normal', // 'normal' | 'large'
    validator: (value) => ['normal', 'large'].includes(value)
  },
  // 진행률 표시 여부
  showProgress: {
    type: Boolean,
    default: false
  },
  // 진행률 값 (0-100)
  progress: {
    type: Number,
    default: null,
    validator: (value) => value === null || (value >= 0 && value <= 100)
  },
  // 취소 버튼 표시 여부
  showCancelButton: {
    type: Boolean,
    default: false
  },
  // 오버레이 클릭으로 닫기 허용 여부
  closeOnOverlay: {
    type: Boolean,
    default: false
  }
})

// 이벤트 정의
const emit = defineEmits(['cancel', 'close'])

// 계산된 속성
const isVisible = computed(() => props.visible)

// 오버레이 클릭 처리
const handleOverlayClick = (event) => {
  if (props.closeOnOverlay && event.target === event.currentTarget) {
    emit('close')
  }
}

// 취소 버튼 클릭 처리
const handleCancel = () => {
  emit('cancel')
}
</script>

<style lang="scss" scoped>
.loading-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
}

.loading-modal {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  text-align: center;
  min-width: 300px;
  max-width: 90vw;
  animation: modalFadeIn 0.3s ease-out;

  &.modal-large {
    min-width: 400px;
    padding: 3rem;
  }
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.loading-spinner {
  margin-bottom: 1.5rem;

  .spinner-ring {
    width: 48px;
    height: 48px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-content {
  .loading-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
  }

  .loading-message {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin: 0 0 1rem 0;
    line-height: 1.4;
  }
}

.progress-container {
  margin-top: 1.5rem;

  .progress-bar {
    width: 100%;
    height: 8px;
    background-color: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
      border-radius: 4px;
      transition: width 0.3s ease;
      animation: progressShimmer 2s infinite;
    }
  }

  .progress-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-secondary);
  }
}

@keyframes progressShimmer {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.cancel-button {
  margin-top: 1.5rem;
  padding: 0.75rem 1.5rem;
  background: none;
  border: 2px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    background-color: rgba(var(--primary-color-rgb), 0.05);
  }

  &:active {
    transform: translateY(1px);
  }
}

// 반응형 디자인
@media (max-width: 480px) {
  .loading-modal {
    margin: 1rem;
    padding: 1.5rem;
    min-width: auto;

    &.modal-large {
      padding: 2rem;
    }
  }

  .loading-content {
    .loading-title {
      font-size: 1.125rem;
    }

    .loading-message {
      font-size: 0.875rem;
    }
  }
}
</style>