<!-- frontend/src/components/dashboard/LearningStats.vue -->
<template>
  <div class="learning-stats">
    <div class="stats-header">
      <h3 class="stats-title">학습 통계</h3>
      <div class="stats-period">
        <select v-model="selectedPeriod" @change="handlePeriodChange" class="period-select">
          <option value="week">이번 주</option>
          <option value="month">이번 달</option>
          <option value="all">전체</option>
        </select>
      </div>
    </div>

    <!-- 주요 통계 카드들 -->
    <div class="stats-cards">
      <!-- 총 학습 시간 -->
      <div class="stat-card primary">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatTime(stats.totalLearningTime) }}</div>
          <div class="stat-label">총 학습 시간</div>
          <div class="stat-change" :class="{ 'positive': stats.timeChange > 0, 'negative': stats.timeChange < 0 }">
            <svg v-if="stats.timeChange > 0" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 14l5-5 5 5z"/>
            </svg>
            <svg v-else-if="stats.timeChange < 0" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 10l5 5 5-5z"/>
            </svg>
            {{ Math.abs(stats.timeChange) }}% {{ stats.timeChange > 0 ? '증가' : '감소' }}
          </div>
        </div>
      </div>

      <!-- 완료한 세션 수 -->
      <div class="stat-card success">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.completedSessions }}</div>
          <div class="stat-label">완료한 세션</div>
          <div class="stat-change positive">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 14l5-5 5 5z"/>
            </svg>
            {{ stats.sessionChange }}% 증가
          </div>
        </div>
      </div>

      <!-- 평균 점수 -->
      <div class="stat-card warning">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.averageScore }}점</div>
          <div class="stat-label">평균 점수</div>
          <div class="stat-change" :class="{ 'positive': stats.scoreChange > 0, 'negative': stats.scoreChange < 0 }">
            <svg v-if="stats.scoreChange > 0" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 14l5-5 5 5z"/>
            </svg>
            <svg v-else-if="stats.scoreChange < 0" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 10l5 5 5-5z"/>
            </svg>
            {{ Math.abs(stats.scoreChange) }}점 {{ stats.scoreChange > 0 ? '상승' : '하락' }}
          </div>
        </div>
      </div>

      <!-- 연속 학습 일수 -->
      <div class="stat-card info">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 11H7v6h2v-6zm4 0h-2v6h2v-6zm4 0h-2v6h2v-6zm2-7h-1V2h-2v2H8V2H6v2H5c-1.1 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.streakDays }}일</div>
          <div class="stat-label">연속 학습</div>
          <div class="stat-change positive">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67zM11.71 19c-1.78 0-3.22-1.4-3.22-3.14 0-1.62 1.05-2.76 2.81-3.12 1.77-.36 3.6-1.21 4.62-2.58.39 1.29.59 2.65.59 4.04 0 2.65-2.15 4.8-4.8 4.8z"/>
            </svg>
            최고 기록!
          </div>
        </div>
      </div>
    </div>

    <!-- 학습 진행률 차트 -->
    <div class="progress-section">
      <h4 class="section-title">챕터별 진행률</h4>
      <div class="progress-list">
        <div
          v-for="chapter in stats.chapterProgress"
          :key="chapter.id"
          class="progress-item"
        >
          <div class="progress-info">
            <span class="chapter-name">{{ chapter.name }}</span>
            <span class="progress-percentage">{{ chapter.progress }}%</span>
          </div>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: `${chapter.progress}%` }"
              :class="getProgressClass(chapter.progress)"
            ></div>
          </div>
          <div class="progress-details">
            <span class="sessions-completed">{{ chapter.completedSessions }}/{{ chapter.totalSessions }} 세션</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 최근 활동 -->
    <div class="recent-activity">
      <h4 class="section-title">최근 활동</h4>
      <div class="activity-list">
        <div
          v-for="activity in stats.recentActivities"
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-icon" :class="activity.type">
            <svg v-if="activity.type === 'completed'" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <svg v-else-if="activity.type === 'started'" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
            <svg v-else-if="activity.type === 'achievement'" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
            </svg>
          </div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-description">{{ activity.description }}</div>
            <div class="activity-time">{{ formatRelativeTime(activity.timestamp) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span class="loading-text">통계를 불러오는 중...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Props 정의
const props = defineProps({
  // 사용자 ID
  userId: {
    type: [String, Number],
    required: true
  },
  // 초기 기간
  initialPeriod: {
    type: String,
    default: 'week'
  }
})

// 이벤트 정의
const emit = defineEmits(['period-change', 'stats-loaded'])

// 반응형 데이터
const isLoading = ref(false)
const selectedPeriod = ref(props.initialPeriod)

// 통계 데이터 (실제로는 API에서 가져올 데이터)
const stats = ref({
  totalLearningTime: 1250, // 분 단위
  timeChange: 15.2,
  completedSessions: 24,
  sessionChange: 8.5,
  averageScore: 87,
  scoreChange: 3.2,
  streakDays: 7,
  chapterProgress: [
    {
      id: 1,
      name: 'AI 기초 개념',
      progress: 100,
      completedSessions: 5,
      totalSessions: 5
    },
    {
      id: 2,
      name: 'ChatGPT 활용법',
      progress: 80,
      completedSessions: 4,
      totalSessions: 5
    },
    {
      id: 3,
      name: '프롬프트 엔지니어링',
      progress: 60,
      completedSessions: 3,
      totalSessions: 5
    },
    {
      id: 4,
      name: 'AI 도구 활용',
      progress: 20,
      completedSessions: 1,
      totalSessions: 5
    }
  ],
  recentActivities: [
    {
      id: 1,
      type: 'completed',
      title: '프롬프트 엔지니어링 세션 완료',
      description: '효과적인 프롬프트 작성법을 학습했습니다',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2시간 전
    },
    {
      id: 2,
      type: 'achievement',
      title: '연속 학습 7일 달성!',
      description: '꾸준한 학습으로 새로운 기록을 세웠습니다',
      timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000) // 1일 전
    },
    {
      id: 3,
      type: 'started',
      title: 'AI 도구 활용 챕터 시작',
      description: '새로운 챕터 학습을 시작했습니다',
      timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) // 3일 전
    }
  ]
})

// 계산된 속성
const totalProgress = computed(() => {
  const total = stats.value.chapterProgress.reduce((sum, chapter) => sum + chapter.progress, 0)
  return Math.round(total / stats.value.chapterProgress.length)
})

// 시간 포맷팅 함수
const formatTime = (minutes) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (hours > 0) {
    return `${hours}시간 ${mins}분`
  }
  return `${mins}분`
}

// 상대 시간 포맷팅 함수
const formatRelativeTime = (timestamp) => {
  const now = new Date()
  const diff = now - timestamp
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days > 0) {
    return `${days}일 전`
  } else if (hours > 0) {
    return `${hours}시간 전`
  } else if (minutes > 0) {
    return `${minutes}분 전`
  } else {
    return '방금 전'
  }
}

// 진행률에 따른 클래스 반환
const getProgressClass = (progress) => {
  if (progress >= 80) return 'high'
  if (progress >= 50) return 'medium'
  return 'low'
}

// 기간 변경 처리
const handlePeriodChange = async () => {
  isLoading.value = true
  
  try {
    // 실제로는 API 호출
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    emit('period-change', selectedPeriod.value)
    emit('stats-loaded', stats.value)
  } catch (error) {
    console.error('통계 로딩 실패:', error)
  } finally {
    isLoading.value = false
  }
}

// 통계 데이터 로드
const loadStats = async () => {
  isLoading.value = true
  
  try {
    // 실제로는 API 호출
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    emit('stats-loaded', stats.value)
  } catch (error) {
    console.error('통계 로딩 실패:', error)
  } finally {
    isLoading.value = false
  }
}

// 라이프사이클 훅
onMounted(() => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.learning-stats {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: relative;

  .stats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;

    .stats-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0;
    }

    .period-select {
      padding: 0.5rem 1rem;
      border: 2px solid var(--border-color);
      border-radius: 8px;
      background: white;
      font-size: 0.875rem;
      cursor: pointer;

      &:focus {
        outline: none;
        border-color: var(--primary-color);
      }
    }
  }

  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;

    .stat-card {
      padding: 1.5rem;
      border-radius: 12px;
      display: flex;
      align-items: center;
      gap: 1rem;
      transition: transform 0.2s ease;

      &:hover {
        transform: translateY(-2px);
      }

      &.primary {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-color-light));
        color: white;
      }

      &.success {
        background: linear-gradient(135deg, #10b981, #34d399);
        color: white;
      }

      &.warning {
        background: linear-gradient(135deg, #f59e0b, #fbbf24);
        color: white;
      }

      &.info {
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
        color: white;
      }

      .stat-icon {
        width: 48px;
        height: 48px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;

        svg {
          width: 24px;
          height: 24px;
        }
      }

      .stat-content {
        flex: 1;

        .stat-value {
          font-size: 2rem;
          font-weight: 700;
          margin-bottom: 0.25rem;
        }

        .stat-label {
          font-size: 0.875rem;
          opacity: 0.9;
          margin-bottom: 0.5rem;
        }

        .stat-change {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.75rem;
          opacity: 0.8;

          svg {
            width: 12px;
            height: 12px;
          }

          &.positive {
            color: rgba(255, 255, 255, 0.9);
          }

          &.negative {
            color: rgba(255, 255, 255, 0.7);
          }
        }
      }
    }
  }

  .progress-section,
  .recent-activity {
    margin-bottom: 2rem;

    .section-title {
      font-size: 1.25rem;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 1rem 0;
    }
  }

  .progress-list {
    .progress-item {
      margin-bottom: 1.5rem;
      padding: 1rem;
      background: var(--bg-light);
      border-radius: 8px;

      .progress-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;

        .chapter-name {
          font-weight: 500;
          color: var(--text-primary);
        }

        .progress-percentage {
          font-weight: 600;
          color: var(--primary-color);
        }
      }

      .progress-bar {
        width: 100%;
        height: 8px;
        background-color: #e9ecef;
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 0.5rem;

        .progress-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 0.6s ease;

          &.high {
            background: linear-gradient(90deg, #10b981, #34d399);
          }

          &.medium {
            background: linear-gradient(90deg, #f59e0b, #fbbf24);
          }

          &.low {
            background: linear-gradient(90deg, #ef4444, #f87171);
          }
        }
      }

      .progress-details {
        .sessions-completed {
          font-size: 0.875rem;
          color: var(--text-secondary);
        }
      }
    }
  }

  .activity-list {
    .activity-item {
      display: flex;
      align-items: flex-start;
      gap: 1rem;
      padding: 1rem;
      border-radius: 8px;
      margin-bottom: 1rem;
      transition: background-color 0.2s ease;

      &:hover {
        background-color: var(--bg-light);
      }

      .activity-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;

        svg {
          width: 20px;
          height: 20px;
        }

        &.completed {
          background-color: rgba(16, 185, 129, 0.1);
          color: #10b981;
        }

        &.started {
          background-color: rgba(59, 130, 246, 0.1);
          color: #3b82f6;
        }

        &.achievement {
          background-color: rgba(245, 158, 11, 0.1);
          color: #f59e0b;
        }
      }

      .activity-content {
        flex: 1;

        .activity-title {
          font-weight: 500;
          color: var(--text-primary);
          margin-bottom: 0.25rem;
        }

        .activity-description {
          font-size: 0.875rem;
          color: var(--text-secondary);
          margin-bottom: 0.25rem;
        }

        .activity-time {
          font-size: 0.75rem;
          color: var(--text-tertiary);
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
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    z-index: 10;

    .loading-spinner {
      width: 32px;
      height: 32px;
      border: 3px solid #f3f3f3;
      border-top: 3px solid var(--primary-color);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }

    .loading-text {
      color: var(--text-secondary);
      font-weight: 500;
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 반응형 디자인
@media (max-width: 768px) {
  .learning-stats {
    padding: 1.5rem;

    .stats-header {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }

    .stats-cards {
      grid-template-columns: 1fr;
      gap: 1rem;

      .stat-card {
        padding: 1rem;

        .stat-content {
          .stat-value {
            font-size: 1.5rem;
          }
        }
      }
    }
  }
}
</style>