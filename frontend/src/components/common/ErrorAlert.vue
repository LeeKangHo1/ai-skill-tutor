<!-- frontend/src/components/common/ErrorAlert.vue -->
<!-- 사용자 친화적 에러 표시 컴포넌트 -->

<template>
  <div v-if="show" class="error-alert" :class="alertClass">
    <div class="error-content">
      <!-- 에러 아이콘 -->
      <div class="error-icon">
        <i :class="iconClass"></i>
      </div>
      
      <!-- 에러 메시지 -->
      <div class="error-message">
        <h5 class="error-title">{{ errorTitle }}</h5>
        <p class="error-description">{{ errorMessage }}</p>
        
        <!-- 기본값 모드 알림 -->
        <div v-if="showFallbackNotice" class="fallback-notice">
          <i class="fas fa-info-circle"></i>
          현재 오프라인 모드로 제한적인 기능만 사용 가능합니다.
        </div>
        
        <!-- 에러 코드 표시 (개발 모드에서만) -->
        <small v-if="showErrorCode && errorCode" class="error-code">
          오류 코드: {{ errorCode }}
        </small>
      </div>
      
      <!-- 액션 버튼들 -->
      <div class="error-actions">
        <!-- 재시도 버튼 -->
        <button 
          v-if="canRetry" 
          @click="handleRetry"
          class="btn btn-outline-primary btn-sm"
          :disabled="retrying"
        >
          <i class="fas fa-redo-alt" :class="{ 'fa-spin': retrying }"></i>
          {{ retrying ? '재시도 중...' : '다시 시도' }}
        </button>
        
        <!-- 닫기 버튼 -->
        <button 
          @click="handleClose"
          class="btn btn-outline-secondary btn-sm ms-2"
        >
          <i class="fas fa-times"></i>
          닫기
        </button>
        
        <!-- 추가 도움말 버튼 -->
        <button 
          v-if="showHelpButton"
          @click="handleHelp"
          class="btn btn-outline-info btn-sm ms-2"
        >
          <i class="fas fa-question-circle"></i>
          도움말
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref } from 'vue'

export default {
  name: 'ErrorAlert',
  props: {
    // 에러 표시 여부
    show: {
      type: Boolean,
      default: false
    },
    
    // 에러 타입 ('network', 'auth', 'server', 'validation', 'unknown')
    errorType: {
      type: String,
      default: 'unknown'
    },
    
    // 에러 메시지
    errorMessage: {
      type: String,
      default: '알 수 없는 오류가 발생했습니다.'
    },
    
    // 에러 코드
    errorCode: {
      type: [String, Number],
      default: null
    },
    
    // 재시도 가능 여부
    canRetry: {
      type: Boolean,
      default: false
    },
    
    // 도움말 버튼 표시 여부
    showHelpButton: {
      type: Boolean,
      default: false
    },
    
    // 자동 닫기 시간 (밀리초, 0이면 자동 닫기 안함)
    autoCloseDelay: {
      type: Number,
      default: 0
    },
    
    // 기본값 모드 여부
    isFallbackMode: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['close', 'retry', 'help'],
  
  setup(props, { emit }) {
    const retrying = ref(false)
    
    // 에러 타입별 제목 설정
    const errorTitle = computed(() => {
      switch (props.errorType) {
        case 'network':
          return '네트워크 연결 오류'
        case 'auth':
          return '인증 오류'
        case 'server':
          return '서버 오류'
        case 'validation':
          return '입력 데이터 오류'
        case 'permission':
          return '권한 오류'
        default:
          return '오류 발생'
      }
    })
    
    // 에러 타입별 아이콘 클래스
    const iconClass = computed(() => {
      switch (props.errorType) {
        case 'network':
          return 'fas fa-wifi text-warning'
        case 'auth':
          return 'fas fa-lock text-danger'
        case 'server':
          return 'fas fa-server text-danger'
        case 'validation':
          return 'fas fa-exclamation-triangle text-warning'
        case 'permission':
          return 'fas fa-ban text-danger'
        default:
          return 'fas fa-exclamation-circle text-danger'
      }
    })
    
    // 알림 박스 스타일 클래스
    const alertClass = computed(() => {
      switch (props.errorType) {
        case 'network':
          return 'alert-warning'
        case 'auth':
          return 'alert-danger'
        case 'server':
          return 'alert-danger'
        case 'validation':
          return 'alert-warning'
        case 'permission':
          return 'alert-danger'
        default:
          return 'alert-danger'
      }
    })
    
    // 에러 코드 표시 여부 (개발 모드에서만)
    const showErrorCode = computed(() => {
      return import.meta.env.MODE === 'development' && props.errorCode
    })
    
    // 기본값 모드 알림 표시 여부
    const showFallbackNotice = computed(() => {
      return props.isFallbackMode && (props.errorType === 'network' || props.errorType === 'server')
    })
    
    // 재시도 처리
    const handleRetry = async () => {
      if (retrying.value) return
      
      retrying.value = true
      
      try {
        await new Promise(resolve => setTimeout(resolve, 500)) // 최소 대기 시간
        emit('retry')
      } finally {
        retrying.value = false
      }
    }
    
    // 닫기 처리
    const handleClose = () => {
      emit('close')
    }
    
    // 도움말 처리
    const handleHelp = () => {
      emit('help')
    }
    
    // 자동 닫기 처리
    if (props.autoCloseDelay > 0) {
      setTimeout(() => {
        if (props.show) {
          handleClose()
        }
      }, props.autoCloseDelay)
    }
    
    return {
      retrying,
      errorTitle,
      iconClass,
      alertClass,
      showErrorCode,
      showFallbackNotice,
      handleRetry,
      handleClose,
      handleHelp
    }
  }
}
</script>

<style scoped>
.error-alert {
  @apply alert mb-3 border-l-4;
  animation: slideDown 0.3s ease-out;
}

.error-content {
  @apply flex items-start gap-3;
}

.error-icon {
  @apply flex-shrink-0 mt-1;
}

.error-icon i {
  @apply text-xl;
}

.error-message {
  @apply flex-grow;
}

.error-title {
  @apply text-sm font-semibold mb-1 text-gray-800;
}

.error-description {
  @apply text-sm text-gray-700 mb-2;
}

.error-code {
  @apply text-xs text-gray-500 font-mono;
}

.fallback-notice {
  @apply flex items-center gap-2 text-sm text-blue-700 bg-blue-50 border border-blue-200 rounded px-3 py-2 mt-2;
}

.fallback-notice i {
  @apply text-blue-500;
}

.error-actions {
  @apply flex-shrink-0 flex flex-col gap-2;
}

.alert-warning {
  @apply bg-yellow-50 border-yellow-400 text-yellow-800;
}

.alert-danger {
  @apply bg-red-50 border-red-400 text-red-800;
}

.alert-info {
  @apply bg-blue-50 border-blue-400 text-blue-800;
}

/* 애니메이션 */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .error-content {
    @apply flex-col gap-2;
  }
  
  .error-actions {
    @apply flex-row justify-end;
  }
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark) {
  .error-title {
    @apply text-gray-200;
  }
  
  .error-description {
    @apply text-gray-300;
  }
  
  .error-code {
    @apply text-gray-400;
  }
  
  .alert-warning {
    @apply bg-yellow-900 border-yellow-600 text-yellow-200;
  }
  
  .alert-danger {
    @apply bg-red-900 border-red-600 text-red-200;
  }
  
  .alert-info {
    @apply bg-blue-900 border-blue-600 text-blue-200;
  }
}
</style>