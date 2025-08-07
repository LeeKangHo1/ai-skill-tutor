<!-- frontend/src/components/learning/MainContentArea.vue -->
<template>
  <div class="main-content-area">
    <!-- 콘텐츠 헤더 -->
    <div class="content-header">
      <div class="session-info">
        <h2 class="session-title">{{ sessionTitle }}</h2>
        <div class="session-meta">
          <span class="session-type" :class="`type-${sessionType}`">
            {{ getSessionTypeText(sessionType) }}
          </span>
          <span class="session-duration">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
            </svg>
            {{ formatDuration(elapsedTime) }}
          </span>
        </div>
      </div>
      
      <!-- 액션 버튼들 -->
      <div class="content-actions">
        <button
          v-if="showPauseButton"
          @click="handlePause"
          class="action-btn secondary"
          :disabled="isLoading"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
          </svg>
          일시정지
        </button>
        
        <button
          v-if="showHelpButton"
          @click="handleHelp"
          class="action-btn outline"
          :disabled="isLoading"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
          </svg>
          도움말
        </button>
      </div>
    </div>

    <!-- 메인 콘텐츠 영역 -->
    <div class="content-body" :class="`content-${sessionType}`">
      <!-- 이론 학습 콘텐츠 -->
      <div v-if="sessionType === 'theory'" class="theory-content">
        <slot name="theory-content">
          <div class="default-content">
            <div class="content-placeholder">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
              </svg>
              <p>이론 학습 콘텐츠가 로드됩니다...</p>
            </div>
          </div>
        </slot>
      </div>

      <!-- 퀴즈 콘텐츠 -->
      <div v-else-if="sessionType === 'quiz'" class="quiz-content">
        <slot name="quiz-content">
          <div class="default-content">
            <div class="content-placeholder">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
              </svg>
              <p>퀴즈 콘텐츠가 로드됩니다...</p>
            </div>
          </div>
        </slot>
      </div>

      <!-- 피드백 콘텐츠 -->
      <div v-else-if="sessionType === 'feedback'" class="feedback-content">
        <slot name="feedback-content">
          <div class="default-content">
            <div class="content-placeholder">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
              </svg>
              <p>피드백 콘텐츠가 로드됩니다...</p>
            </div>
          </div>
        </slot>
      </div>

      <!-- QnA 콘텐츠 -->
      <div v-else-if="sessionType === 'qna'" class="qna-content">
        <slot name="qna-content">
          <div class="default-content">
            <div class="content-placeholder">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V3c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h11c.55 0 1-.45 1-1z"/>
              </svg>
              <p>질문 답변 콘텐츠가 로드됩니다...</p>
            </div>
          </div>
        </slot>
      </div>

      <!-- 세션 완료 콘텐츠 -->
      <div v-else-if="sessionType === 'complete'" class="complete-content">
        <slot name="complete-content">
          <div class="completion-message">
            <div class="completion-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            </div>
            <h3 class="completion-title">세션 완료!</h3>
            <p class="completion-description">
              훌륭합니다! 이번 세션을 성공적으로 완료했습니다.
            </p>
          </div>
        </slot>
      </div>
    </div>

    <!-- 콘텐츠 푸터 -->
    <div class="content-footer">
      <!-- 진행률 표시 -->
      <div class="progress-indicator">
        <div class="progress-info">
          <span class="progress-text">진행률</span>
          <span class="progress-percentage">{{ Math.round(progress) }}%</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
      </div>

      <!-- 네비게이션 버튼들 -->
      <div class="navigation-buttons">
        <button
          v-if="showPreviousButton"
          @click="handlePrevious"
          class="nav-btn secondary"
          :disabled="isLoading"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
          </svg>
          이전
        </button>

        <button
          v-if="showNextButton"
          @click="handleNext"
          class="nav-btn primary"
          :disabled="isLoading || !canProceed"
        >
          {{ nextButtonText }}
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/>
          </svg>
        </button>

        <button
          v-if="showCompleteButton"
          @click="handleComplete"
          class="nav-btn success"
          :disabled="isLoading"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
          완료
        </button>
      </div>
    </div>

    <!-- 로딩 오버레이 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span class="loading-text">{{ loadingText }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'

// Props 정의
const props = defineProps({
  // 세션 제목
  sessionTitle: {
    type: String,
    required: true
  },
  // 세션 타입
  sessionType: {
    type: String,
    required: true,
    validator: (value) => ['theory', 'quiz', 'feedback', 'qna', 'complete'].includes(value)
  },
  // 진행률 (0-100)
  progress: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },
  // 다음 단계로 진행 가능 여부
  canProceed: {
    type: Boolean,
    default: true
  },
  // 로딩 상태
  isLoading: {
    type: Boolean,
    default: false
  },
  // 로딩 텍스트
  loadingText: {
    type: String,
    default: '처리 중...'
  },
  // 버튼 표시 옵션
  showPreviousButton: {
    type: Boolean,
    default: true
  },
  showNextButton: {
    type: Boolean,
    default: true
  },
  showCompleteButton: {
    type: Boolean,
    default: false
  },
  showPauseButton: {
    type: Boolean,
    default: true
  },
  showHelpButton: {
    type: Boolean,
    default: true
  },
  // 다음 버튼 텍스트
  nextButtonText: {
    type: String,
    default: '다음'
  }
})

// 이벤트 정의
const emit = defineEmits([
  'previous', 
  'next', 
  'complete', 
  'pause', 
  'help',
  'time-update'
])

// 반응형 데이터
const elapsedTime = ref(0)
let timeInterval = null

// 계산된 속성
const sessionTypeText = computed(() => getSessionTypeText(props.sessionType))

// 세션 타입 텍스트 반환
const getSessionTypeText = (type) => {
  const typeMap = {
    'theory': '개념 학습',
    'quiz': '퀴즈',
    'feedback': '피드백',
    'qna': '질문 답변',
    'complete': '완료'
  }
  return typeMap[type] || '학습'
}

// 시간 포맷팅
const formatDuration = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes > 0) {
    return `${minutes}분 ${remainingSeconds}초`
  }
  return `${remainingSeconds}초`
}

// 이벤트 핸들러들
const handlePrevious = () => {
  emit('previous')
}

const handleNext = () => {
  emit('next')
}

const handleComplete = () => {
  emit('complete')
}

const handlePause = () => {
  emit('pause')
}

const handleHelp = () => {
  emit('help')
}

// 시간 추적 시작
const startTimeTracking = () => {
  timeInterval = setInterval(() => {
    elapsedTime.value += 1
    emit('time-update', elapsedTime.value)
  }, 1000)
}

// 시간 추적 중지
const stopTimeTracking = () => {
  if (timeInterval) {
    clearInterval(timeInterval)
    timeInterval = null
  }
}

// 라이프사이클 훅
onMounted(() => {
  startTimeTracking()
})

onUnmounted(() => {
  stopTimeTracking()
})
</script>

<style lang="scss" scoped>
.main-content-area {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  min-height: 600px;
  position: relative;
  overflow: hidden;

  .content-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 2rem 2rem 1rem 2rem;
    border-bottom: 2px solid var(--border-light);

    .session-info {
      .session-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 0.5rem 0;
        line-height: 1.3;
      }

      .session-meta {
        display: flex;
        gap: 1rem;
        align-items: center;

        .session-type {
          padding: 0.375rem 0.75rem;
          border-radius: 16px;
          font-size: 0.875rem;
          font-weight: 600;

          &.type-theory {
            background-color: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
          }

          &.type-quiz {
            background-color: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
          }

          &.type-feedback {
            background-color: rgba(16, 185, 129, 0.1);
            color: #10b981;
          }

          &.type-qna {
            background-color: rgba(139, 92, 246, 0.1);
            color: #8b5cf6;
          }

          &.type-complete {
            background-color: rgba(16, 185, 129, 0.1);
            color: #10b981;
          }
        }

        .session-duration {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.875rem;
          color: var(--text-secondary);

          svg {
            width: 14px;
            height: 14px;
          }
        }
      }
    }

    .content-actions {
      display: flex;
      gap: 0.75rem;

      .action-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;

        svg {
          width: 16px;
          height: 16px;
        }

        &.secondary {
          background-color: var(--bg-light);
          color: var(--text-secondary);
          border: 2px solid var(--border-color);

          &:hover:not(:disabled) {
            background-color: var(--border-color);
            color: var(--text-primary);
          }
        }

        &.outline {
          background: none;
          color: var(--text-secondary);
          border: 2px solid var(--border-color);

          &:hover:not(:disabled) {
            border-color: var(--primary-color);
            color: var(--primary-color);
          }
        }

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
    }
  }

  .content-body {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;

    .default-content {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      min-height: 300px;

      .content-placeholder {
        text-align: center;
        color: var(--text-secondary);

        svg {
          width: 64px;
          height: 64px;
          margin-bottom: 1rem;
          opacity: 0.5;
        }

        p {
          font-size: 1.125rem;
          margin: 0;
        }
      }
    }

    .completion-message {
      text-align: center;
      padding: 3rem 1rem;

      .completion-icon {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #10b981, #34d399);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        animation: success-bounce 0.6s ease-out;

        svg {
          width: 40px;
          height: 40px;
          color: white;
        }
      }

      .completion-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 1rem 0;
      }

      .completion-description {
        font-size: 1.125rem;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.5;
      }
    }

    // 세션 타입별 스타일
    &.content-theory {
      background: linear-gradient(135deg, rgba(59, 130, 246, 0.02), rgba(59, 130, 246, 0.05));
    }

    &.content-quiz {
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.02), rgba(245, 158, 11, 0.05));
    }

    &.content-feedback {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.02), rgba(16, 185, 129, 0.05));
    }

    &.content-qna {
      background: linear-gradient(135deg, rgba(139, 92, 246, 0.02), rgba(139, 92, 246, 0.05));
    }

    &.content-complete {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.02), rgba(16, 185, 129, 0.05));
    }
  }

  .content-footer {
    padding: 1.5rem 2rem 2rem 2rem;
    border-top: 2px solid var(--border-light);
    background-color: var(--bg-light);

    .progress-indicator {
      margin-bottom: 1.5rem;

      .progress-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;

        .progress-text {
          font-size: 0.875rem;
          color: var(--text-secondary);
          font-weight: 500;
        }

        .progress-percentage {
          font-size: 0.875rem;
          font-weight: 700;
          color: var(--primary-color);
        }
      }

      .progress-bar {
        width: 100%;
        height: 8px;
        background-color: #e9ecef;
        border-radius: 4px;
        overflow: hidden;

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--primary-color), var(--primary-color-light));
          border-radius: 4px;
          transition: width 0.6s ease;
        }
      }
    }

    .navigation-buttons {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;

      .nav-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.875rem 1.5rem;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;

        svg {
          width: 18px;
          height: 18px;
        }

        &.secondary {
          background-color: var(--bg-light);
          color: var(--text-secondary);
          border: 2px solid var(--border-color);

          &:hover:not(:disabled) {
            background-color: var(--border-color);
            color: var(--text-primary);
            transform: translateY(-1px);
          }
        }

        &.primary {
          background-color: var(--primary-color);
          color: white;

          &:hover:not(:disabled) {
            background-color: var(--primary-color-dark);
            transform: translateY(-1px);
          }
        }

        &.success {
          background-color: #10b981;
          color: white;

          &:hover:not(:disabled) {
            background-color: #059669;
            transform: translateY(-1px);
          }
        }

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
        }
      }
    }
  }

  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.95);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 100;

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 4px solid #f3f3f3;
      border-top: 4px solid var(--primary-color);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }

    .loading-text {
      font-size: 1rem;
      color: var(--text-secondary);
      font-weight: 500;
    }
  }
}

// 애니메이션
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes success-bounce {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { transform: scale(1); opacity: 1; }
}

// 반응형 디자인
@media (max-width: 768px) {
  .main-content-area {
    .content-header {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
      padding: 1.5rem;

      .session-info {
        .session-title {
          font-size: 1.5rem;
        }

        .session-meta {
          flex-wrap: wrap;
        }
      }

      .content-actions {
        width: 100%;
        justify-content: flex-end;
      }
    }

    .content-body {
      padding: 1.5rem;

      .completion-message {
        padding: 2rem 1rem;

        .completion-icon {
          width: 64px;
          height: 64px;

          svg {
            width: 32px;
            height: 32px;
          }
        }

        .completion-title {
          font-size: 1.5rem;
        }

        .completion-description {
          font-size: 1rem;
        }
      }
    }

    .content-footer {
      padding: 1.5rem;

      .navigation-buttons {
        flex-direction: column;

        .nav-btn {
          width: 100%;
          justify-content: center;
        }
      }
    }
  }
}
</style>