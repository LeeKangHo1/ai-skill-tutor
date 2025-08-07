<!-- frontend/src/components/dashboard/ChapterCard.vue -->
<template>
  <div 
    class="chapter-card" 
    :class="{ 
      'locked': chapter.isLocked,
      'completed': chapter.progress >= 100,
      'in-progress': chapter.progress > 0 && chapter.progress < 100
    }"
    @click="handleCardClick"
  >
    <!-- 카드 헤더 -->
    <div class="card-header">
      <div class="chapter-badge">{{ chapter.order }}장</div>
      <div class="chapter-status">
        <div v-if="chapter.isLocked" class="status-icon locked">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
          </svg>
        </div>
        <div v-else-if="chapter.progress >= 100" class="status-icon completed">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
        </div>
        <div v-else-if="chapter.progress > 0" class="status-icon in-progress">
          <div class="progress-ring">
            <svg viewBox="0 0 36 36">
              <path
                class="progress-ring-bg"
                d="M18 2.0845
                  a 15.9155 15.9155 0 0 1 0 31.831
                  a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-opacity="0.2"
              />
              <path
                class="progress-ring-fill"
                :stroke-dasharray="`${chapter.progress}, 100`"
                d="M18 2.0845
                  a 15.9155 15.9155 0 0 1 0 31.831
                  a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
            <span class="progress-text">{{ chapter.progress }}%</span>
          </div>
        </div>
        <div v-else class="status-icon available">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 카드 내용 -->
    <div class="card-content">
      <h3 class="chapter-title">{{ chapter.title }}</h3>
      <p class="chapter-description">{{ chapter.description }}</p>

      <!-- 난이도 및 메타 정보 -->
      <div class="chapter-meta">
        <div class="difficulty-badge" :class="`difficulty-${chapter.difficulty}`">
          {{ getDifficultyText(chapter.difficulty) }}
        </div>
        <div class="meta-info">
          <div class="meta-item">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
            </svg>
            <span>{{ chapter.estimatedTime }}분</span>
          </div>
          <div class="meta-item">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <span>{{ chapter.totalSessions }}세션</span>
          </div>
        </div>
      </div>

      <!-- 진행률 바 (진행 중인 경우만) -->
      <div v-if="chapter.progress > 0 && chapter.progress < 100" class="progress-section">
        <div class="progress-info">
          <span class="progress-label">진행률</span>
          <span class="progress-percentage">{{ chapter.progress }}%</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${chapter.progress}%` }"
          ></div>
        </div>
        <div class="session-info">
          {{ chapter.completedSessions }}/{{ chapter.totalSessions }} 세션 완료
        </div>
      </div>

      <!-- 완료 정보 (완료된 경우만) -->
      <div v-if="chapter.progress >= 100" class="completion-info">
        <div class="completion-badge">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
          <span>완료</span>
        </div>
        <div class="completion-details">
          <div class="detail-item">
            <span>완료일:</span>
            <span>{{ formatCompletionDate(chapter.completedAt) }}</span>
          </div>
          <div v-if="chapter.averageScore" class="detail-item">
            <span>평균 점수:</span>
            <span>{{ chapter.averageScore }}점</span>
          </div>
        </div>
      </div>

      <!-- 잠금 정보 (잠긴 경우만) -->
      <div v-if="chapter.isLocked" class="lock-info">
        <div class="lock-message">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
          </svg>
          <span>{{ chapter.unlockCondition || '이전 챕터를 완료하세요' }}</span>
        </div>
      </div>
    </div>

    <!-- 카드 푸터 -->
    <div class="card-footer">
      <button
        v-if="!chapter.isLocked"
        @click.stop="handleStartChapter"
        class="action-btn"
        :class="getActionButtonClass(chapter)"
        :disabled="isLoading"
      >
        <svg v-if="chapter.progress >= 100" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
        </svg>
        <svg v-else-if="chapter.progress > 0" viewBox="0 0 24 24" fill="currentColor">
          <path d="M8 5v14l11-7z"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="currentColor">
          <path d="M8 5v14l11-7z"/>
        </svg>
        {{ getActionButtonText(chapter) }}
      </button>

      <!-- 추가 액션 버튼들 -->
      <div v-if="!chapter.isLocked" class="additional-actions">
        <button
          @click.stop="handleViewDetails"
          class="icon-btn"
          title="상세 정보"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
        </button>
        <button
          v-if="chapter.progress > 0"
          @click.stop="handleViewProgress"
          class="icon-btn"
          title="진행 상황"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 로딩 오버레이 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// 라우터 설정
const router = useRouter()

// Props 정의
const props = defineProps({
  // 챕터 데이터
  chapter: {
    type: Object,
    required: true,
    validator: (chapter) => {
      return chapter.id && chapter.title && chapter.description
    }
  },
  // 카드 크기
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 클릭 가능 여부
  clickable: {
    type: Boolean,
    default: true
  }
})

// 이벤트 정의
const emit = defineEmits(['click', 'start', 'view-details', 'view-progress'])

// 반응형 데이터
const isLoading = ref(false)

// 난이도 텍스트 반환
const getDifficultyText = (difficulty) => {
  const difficultyMap = {
    'beginner': '초급',
    'intermediate': '중급',
    'advanced': '고급'
  }
  return difficultyMap[difficulty] || '초급'
}

// 액션 버튼 텍스트 반환
const getActionButtonText = (chapter) => {
  if (chapter.progress >= 100) return '복습하기'
  if (chapter.progress > 0) return '계속하기'
  return '시작하기'
}

// 액션 버튼 클래스 반환
const getActionButtonClass = (chapter) => {
  if (chapter.progress >= 100) return 'completed'
  if (chapter.progress > 0) return 'in-progress'
  return 'start'
}

// 완료일 포맷팅
const formatCompletionDate = (date) => {
  if (!date) return ''
  
  const options = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  }
  return new Date(date).toLocaleDateString('ko-KR', options)
}

// 카드 클릭 처리
const handleCardClick = () => {
  if (!props.clickable || props.chapter.isLocked) return
  
  emit('click', props.chapter)
}

// 챕터 시작 처리
const handleStartChapter = async () => {
  if (props.chapter.isLocked) return

  isLoading.value = true
  
  try {
    emit('start', props.chapter)
    router.push(`/learning/${props.chapter.id}`)
  } catch (error) {
    console.error('챕터 시작 실패:', error)
  } finally {
    isLoading.value = false
  }
}

// 상세 정보 보기
const handleViewDetails = () => {
  emit('view-details', props.chapter)
}

// 진행 상황 보기
const handleViewProgress = () => {
  emit('view-progress', props.chapter)
}
</script>

<style lang="scss" scoped>
.chapter-card {
  background: white;
  border: 2px solid var(--border-light);
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &:hover:not(.locked) {
    border-color: var(--primary-color);
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
  }

  &.locked {
    opacity: 0.6;
    cursor: not-allowed;
    background-color: var(--bg-disabled);

    &:hover {
      transform: none;
      box-shadow: none;
    }
  }

  &.completed {
    border-color: #10b981;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.02), rgba(16, 185, 129, 0.05));

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #10b981, #34d399);
    }
  }

  &.in-progress {
    border-color: var(--primary-color);
    background: linear-gradient(135deg, rgba(var(--primary-color-rgb), 0.02), rgba(var(--primary-color-rgb), 0.05));

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, var(--primary-color), var(--primary-color-light));
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;

    .chapter-badge {
      background-color: var(--primary-color);
      color: white;
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.875rem;
      font-weight: 600;
    }

    .chapter-status {
      .status-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        svg {
          width: 20px;
          height: 20px;
        }

        &.locked {
          background-color: rgba(107, 114, 128, 0.1);
          color: #6b7280;
        }

        &.completed {
          background-color: rgba(16, 185, 129, 0.1);
          color: #10b981;
        }

        &.available {
          background-color: rgba(59, 130, 246, 0.1);
          color: #3b82f6;
        }

        &.in-progress {
          .progress-ring {
            position: relative;
            width: 40px;
            height: 40px;

            svg {
              width: 100%;
              height: 100%;
              transform: rotate(-90deg);
            }

            .progress-ring-bg {
              color: var(--border-light);
            }

            .progress-ring-fill {
              color: var(--primary-color);
              transition: stroke-dasharray 0.6s ease;
            }

            .progress-text {
              position: absolute;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%);
              font-size: 0.625rem;
              font-weight: 600;
              color: var(--primary-color);
            }
          }
        }
      }
    }
  }

  .card-content {
    .chapter-title {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0 0 0.5rem 0;
      line-height: 1.3;
    }

    .chapter-description {
      color: var(--text-secondary);
      line-height: 1.5;
      margin: 0 0 1rem 0;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .chapter-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;

      .difficulty-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;

        &.difficulty-beginner {
          background-color: rgba(16, 185, 129, 0.1);
          color: #10b981;
        }

        &.difficulty-intermediate {
          background-color: rgba(245, 158, 11, 0.1);
          color: #f59e0b;
        }

        &.difficulty-advanced {
          background-color: rgba(239, 68, 68, 0.1);
          color: #ef4444;
        }
      }

      .meta-info {
        display: flex;
        gap: 1rem;

        .meta-item {
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

    .progress-section {
      margin-bottom: 1rem;
      padding: 1rem;
      background-color: var(--bg-light);
      border-radius: 8px;

      .progress-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;

        .progress-label {
          font-size: 0.875rem;
          color: var(--text-secondary);
        }

        .progress-percentage {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--primary-color);
        }
      }

      .progress-bar {
        width: 100%;
        height: 6px;
        background-color: #e9ecef;
        border-radius: 3px;
        overflow: hidden;
        margin-bottom: 0.5rem;

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--primary-color), var(--primary-color-light));
          border-radius: 3px;
          transition: width 0.6s ease;
        }
      }

      .session-info {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-align: center;
      }
    }

    .completion-info {
      margin-bottom: 1rem;
      padding: 1rem;
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.1));
      border-radius: 8px;

      .completion-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #10b981;
        font-weight: 600;
        margin-bottom: 0.5rem;

        svg {
          width: 16px;
          height: 16px;
        }
      }

      .completion-details {
        .detail-item {
          display: flex;
          justify-content: space-between;
          font-size: 0.875rem;
          color: var(--text-secondary);
          margin-bottom: 0.25rem;

          &:last-child {
            margin-bottom: 0;
          }
        }
      }
    }

    .lock-info {
      margin-bottom: 1rem;
      padding: 1rem;
      background-color: rgba(107, 114, 128, 0.05);
      border-radius: 8px;

      .lock-message {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #6b7280;
        font-size: 0.875rem;

        svg {
          width: 16px;
          height: 16px;
        }
      }
    }
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;

    .action-btn {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.75rem 1rem;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;

      svg {
        width: 16px;
        height: 16px;
      }

      &.start {
        background-color: var(--primary-color);
        color: white;

        &:hover:not(:disabled) {
          background-color: var(--primary-color-dark);
          transform: translateY(-1px);
        }
      }

      &.in-progress {
        background-color: var(--primary-color);
        color: white;

        &:hover:not(:disabled) {
          background-color: var(--primary-color-dark);
          transform: translateY(-1px);
        }
      }

      &.completed {
        background-color: #10b981;
        color: white;

        &:hover:not(:disabled) {
          background-color: #059669;
          transform: translateY(-1px);
        }
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
      }
    }

    .additional-actions {
      display: flex;
      gap: 0.5rem;

      .icon-btn {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: none;
        border: 2px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s ease;

        svg {
          width: 16px;
          height: 16px;
        }

        &:hover {
          border-color: var(--primary-color);
          color: var(--primary-color);
          background-color: rgba(var(--primary-color-rgb), 0.05);
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
    background-color: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    z-index: 10;

    .loading-spinner {
      width: 24px;
      height: 24px;
      border: 2px solid #f3f3f3;
      border-top: 2px solid var(--primary-color);
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 크기별 스타일
.chapter-card {
  &.size-small {
    padding: 1rem;

    .card-content {
      .chapter-title {
        font-size: 1.125rem;
      }

      .chapter-description {
        -webkit-line-clamp: 1;
      }
    }
  }

  &.size-large {
    padding: 2rem;

    .card-content {
      .chapter-title {
        font-size: 1.5rem;
      }

      .chapter-description {
        -webkit-line-clamp: 3;
      }
    }
  }
}

// 반응형 디자인
@media (max-width: 480px) {
  .chapter-card {
    padding: 1rem;

    .card-header {
      .chapter-status {
        .status-icon {
          width: 32px;
          height: 32px;

          svg {
            width: 16px;
            height: 16px;
          }

          &.in-progress {
            .progress-ring {
              width: 32px;
              height: 32px;

              .progress-text {
                font-size: 0.5rem;
              }
            }
          }
        }
      }
    }

    .card-content {
      .chapter-title {
        font-size: 1.125rem;
      }

      .chapter-meta {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
      }
    }

    .card-footer {
      flex-direction: column;

      .action-btn {
        width: 100%;
      }

      .additional-actions {
        width: 100%;
        justify-content: center;
      }
    }
  }
}
</style>