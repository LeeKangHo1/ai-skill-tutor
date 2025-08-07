<!-- frontend/src/components/learning/SessionProgressIndicator.vue -->
<template>
  <div class="session-progress-indicator">
    <!-- 진행률 헤더 -->
    <div class="progress-header">
      <div class="session-info">
        <h3 class="chapter-title">{{ chapterTitle }}</h3>
        <div class="session-meta">
          <span class="session-number">세션 {{ currentSession }}/{{ totalSessions }}</span>
          <span class="session-type" :class="`type-${currentSessionType}`">
            {{ getSessionTypeText(currentSessionType) }}
          </span>
        </div>
      </div>
      <div class="progress-percentage">
        {{ Math.round(overallProgress) }}%
      </div>
    </div>

    <!-- 전체 진행률 바 -->
    <div class="overall-progress">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${overallProgress}%` }"
        ></div>
      </div>
    </div>

    <!-- 세션별 단계 표시 -->
    <div class="session-steps">
      <div
        v-for="(session, index) in sessions"
        :key="session.id"
        class="step-item"
        :class="{
          'completed': session.status === 'completed',
          'current': session.status === 'current',
          'upcoming': session.status === 'upcoming'
        }"
      >
        <!-- 단계 아이콘 -->
        <div class="step-icon">
          <div v-if="session.status === 'completed'" class="icon completed">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
          </div>
          <div v-else-if="session.status === 'current'" class="icon current">
            <div class="pulse-ring"></div>
            <span class="step-number">{{ index + 1 }}</span>
          </div>
          <div v-else class="icon upcoming">
            <span class="step-number">{{ index + 1 }}</span>
          </div>
        </div>

        <!-- 단계 내용 -->
        <div class="step-content">
          <div class="step-title">{{ session.title }}</div>
          <div class="step-description">{{ session.description }}</div>
          
          <!-- 현재 세션의 상세 진행률 -->
          <div v-if="session.status === 'current' && session.subSteps" class="sub-progress">
            <div class="sub-steps">
              <div
                v-for="(subStep, subIndex) in session.subSteps"
                :key="subIndex"
                class="sub-step"
                :class="{
                  'completed': subStep.completed,
                  'current': subStep.current
                }"
              >
                <div class="sub-step-icon">
                  <svg v-if="subStep.completed" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                  </svg>
                  <div v-else-if="subStep.current" class="current-dot"></div>
                  <div v-else class="pending-dot"></div>
                </div>
                <span class="sub-step-text">{{ subStep.title }}</span>
              </div>
            </div>
          </div>

          <!-- 완료 시간 표시 -->
          <div v-if="session.status === 'completed' && session.completedAt" class="completion-time">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
            </svg>
            <span>{{ formatCompletionTime(session.completedAt) }}</span>
          </div>

          <!-- 예상 소요 시간 -->
          <div v-if="session.status === 'upcoming'" class="estimated-time">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
            </svg>
            <span>약 {{ session.estimatedTime }}분</span>
          </div>
        </div>

        <!-- 연결선 -->
        <div v-if="index < sessions.length - 1" class="step-connector"></div>
      </div>
    </div>

    <!-- 학습 통계 -->
    <div class="learning-stats">
      <div class="stat-item">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatTime(totalTime) }}</div>
          <div class="stat-label">총 학습 시간</div>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ averageScore }}점</div>
          <div class="stat-label">평균 점수</div>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ completedSessions }}</div>
          <div class="stat-label">완료 세션</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Props 정의
const props = defineProps({
  // 챕터 제목
  chapterTitle: {
    type: String,
    required: true
  },
  // 현재 세션 번호
  currentSession: {
    type: Number,
    required: true
  },
  // 전체 세션 수
  totalSessions: {
    type: Number,
    required: true
  },
  // 현재 세션 타입
  currentSessionType: {
    type: String,
    default: 'theory',
    validator: (value) => ['theory', 'quiz', 'feedback', 'qna'].includes(value)
  },
  // 전체 진행률 (0-100)
  overallProgress: {
    type: Number,
    required: true,
    validator: (value) => value >= 0 && value <= 100
  },
  // 세션 데이터
  sessions: {
    type: Array,
    required: true
  },
  // 총 학습 시간 (분)
  totalTime: {
    type: Number,
    default: 0
  },
  // 평균 점수
  averageScore: {
    type: Number,
    default: 0
  }
})

// 이벤트 정의
const emit = defineEmits(['session-select'])

// 계산된 속성
const completedSessions = computed(() => {
  return props.sessions.filter(session => session.status === 'completed').length
})

// 세션 타입 텍스트 반환
const getSessionTypeText = (type) => {
  const typeMap = {
    'theory': '개념 학습',
    'quiz': '퀴즈',
    'feedback': '피드백',
    'qna': '질문 답변'
  }
  return typeMap[type] || '학습'
}

// 시간 포맷팅
const formatTime = (minutes) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (hours > 0) {
    return `${hours}시간 ${mins}분`
  }
  return `${mins}분`
}

// 완료 시간 포맷팅
const formatCompletionTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days > 0) {
    return `${days}일 전 완료`
  } else if (hours > 0) {
    return `${hours}시간 전 완료`
  } else if (minutes > 0) {
    return `${minutes}분 전 완료`
  } else {
    return '방금 완료'
  }
}
</script>

<style lang="scss" scoped>
.session-progress-indicator {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);

  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;

    .session-info {
      .chapter-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 0.5rem 0;
      }

      .session-meta {
        display: flex;
        gap: 1rem;
        align-items: center;

        .session-number {
          font-size: 0.875rem;
          color: var(--text-secondary);
          font-weight: 500;
        }

        .session-type {
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.75rem;
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
        }
      }
    }

    .progress-percentage {
      font-size: 2rem;
      font-weight: 700;
      color: var(--primary-color);
    }
  }

  .overall-progress {
    margin-bottom: 2rem;

    .progress-bar {
      width: 100%;
      height: 12px;
      background-color: #e9ecef;
      border-radius: 6px;
      overflow: hidden;

      .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--primary-color-light));
        border-radius: 6px;
        transition: width 0.6s ease;
        animation: progress-glow 2s ease-in-out infinite alternate;
      }
    }
  }

  .session-steps {
    margin-bottom: 2rem;

    .step-item {
      position: relative;
      display: flex;
      align-items: flex-start;
      gap: 1rem;
      margin-bottom: 2rem;

      &:last-child {
        margin-bottom: 0;

        .step-connector {
          display: none;
        }
      }

      .step-icon {
        position: relative;
        z-index: 2;

        .icon {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          transition: all 0.3s ease;

          &.completed {
            background-color: #10b981;
            color: white;

            svg {
              width: 24px;
              height: 24px;
            }
          }

          &.current {
            background-color: var(--primary-color);
            color: white;
            position: relative;

            .pulse-ring {
              position: absolute;
              width: 60px;
              height: 60px;
              border: 2px solid var(--primary-color);
              border-radius: 50%;
              animation: pulse 2s infinite;
              opacity: 0.6;
            }

            .step-number {
              position: relative;
              z-index: 1;
            }
          }

          &.upcoming {
            background-color: #e9ecef;
            color: var(--text-secondary);
          }
        }
      }

      .step-content {
        flex: 1;
        padding-top: 0.5rem;

        .step-title {
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 0.25rem;
        }

        .step-description {
          color: var(--text-secondary);
          margin-bottom: 1rem;
          line-height: 1.5;
        }

        .sub-progress {
          margin-bottom: 1rem;

          .sub-steps {
            .sub-step {
              display: flex;
              align-items: center;
              gap: 0.5rem;
              margin-bottom: 0.5rem;
              font-size: 0.875rem;

              &:last-child {
                margin-bottom: 0;
              }

              .sub-step-icon {
                width: 16px;
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: center;

                svg {
                  width: 12px;
                  height: 12px;
                  color: #10b981;
                }

                .current-dot {
                  width: 8px;
                  height: 8px;
                  background-color: var(--primary-color);
                  border-radius: 50%;
                  animation: pulse-dot 1.5s infinite;
                }

                .pending-dot {
                  width: 8px;
                  height: 8px;
                  background-color: #e9ecef;
                  border-radius: 50%;
                }
              }

              .sub-step-text {
                color: var(--text-secondary);

                &.completed {
                  color: #10b981;
                }

                &.current {
                  color: var(--primary-color);
                  font-weight: 500;
                }
              }
            }
          }
        }

        .completion-time,
        .estimated-time {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
          color: var(--text-secondary);

          svg {
            width: 14px;
            height: 14px;
          }
        }

        .completion-time {
          color: #10b981;
        }
      }

      .step-connector {
        position: absolute;
        left: 23px;
        top: 48px;
        width: 2px;
        height: calc(100% + 1rem);
        background-color: #e9ecef;
        z-index: 1;
      }

      &.completed .step-connector {
        background-color: #10b981;
      }

      &.current .step-connector {
        background: linear-gradient(to bottom, var(--primary-color) 0%, #e9ecef  50%);
      }
    }
  }

  .learning-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    padding-top: 1.5rem;
    border-top: 2px solid var(--border-light);

    .stat-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 1rem;
      background-color: var(--bg-light);
      border-radius: 8px;

      .stat-icon {
        width: 40px;
        height: 40px;
        background-color: rgba(var(--primary-color-rgb), 0.1);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary-color);

        svg {
          width: 20px;
          height: 20px;
        }
      }

      .stat-content {
        .stat-value {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 0.125rem;
        }

        .stat-label {
          font-size: 0.75rem;
          color: var(--text-secondary);
        }
      }
    }
  }
}

// 애니메이션
@keyframes progress-glow {
  0% { box-shadow: 0 0 5px rgba(var(--primary-color-rgb), 0.5); }
  100% { box-shadow: 0 0 20px rgba(var(--primary-color-rgb), 0.8); }
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.1); opacity: 0.3; }
  100% { transform: scale(1); opacity: 0.6; }
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

// 반응형 디자인
@media (max-width: 768px) {
  .session-progress-indicator {
    padding: 1.5rem;

    .progress-header {
      flex-direction: column;
      gap: 1rem;

      .progress-percentage {
        font-size: 1.5rem;
      }
    }

    .session-steps {
      .step-item {
        .step-content {
          .step-title {
            font-size: 1rem;
          }
        }
      }
    }

    .learning-stats {
      grid-template-columns: 1fr;

      .stat-item {
        .stat-icon {
          width: 32px;
          height: 32px;

          svg {
            width: 16px;
            height: 16px;
          }
        }

        .stat-content {
          .stat-value {
            font-size: 1.125rem;
          }
        }
      }
    }
  }
}
</style>