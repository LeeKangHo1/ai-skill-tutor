<!-- frontend/src/components/dashboard/ChapterList.vue -->
<template>
  <div class="chapter-list">
    <div class="list-header">
      <h3 class="list-title">학습 챕터</h3>
      <div class="list-controls">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="챕터 검색..."
            class="search-input"
          />
          <svg class="search-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
        </div>
        <select v-model="sortBy" @change="handleSort" class="sort-select">
          <option value="order">순서대로</option>
          <option value="progress">진행률순</option>
          <option value="difficulty">난이도순</option>
        </select>
      </div>
    </div>

    <!-- 챕터 목록 -->
    <div class="chapters-container">
      <div
        v-for="chapter in filteredChapters"
        :key="chapter.id"
        class="chapter-item"
        :class="{ 
          'locked': chapter.isLocked,
          'completed': chapter.progress >= 100,
          'in-progress': chapter.progress > 0 && chapter.progress < 100
        }"
        @click="handleChapterClick(chapter)"
      >
        <!-- 챕터 상태 아이콘 -->
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
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
          <div v-else class="status-icon available">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
        </div>

        <!-- 챕터 내용 -->
        <div class="chapter-content">
          <div class="chapter-header">
            <h4 class="chapter-title">{{ chapter.title }}</h4>
            <div class="chapter-meta">
              <span class="chapter-order">{{ chapter.order }}장</span>
              <span class="chapter-difficulty" :class="`difficulty-${chapter.difficulty}`">
                {{ getDifficultyText(chapter.difficulty) }}
              </span>
            </div>
          </div>

          <p class="chapter-description">{{ chapter.description }}</p>

          <!-- 진행률 바 -->
          <div class="progress-container">
            <div class="progress-info">
              <span class="progress-text">진행률</span>
              <span class="progress-percentage">{{ chapter.progress }}%</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: `${chapter.progress}%` }"
                :class="getProgressClass(chapter.progress)"
              ></div>
            </div>
          </div>

          <!-- 챕터 상세 정보 -->
          <div class="chapter-details">
            <div class="detail-item">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <span>{{ chapter.completedSessions }}/{{ chapter.totalSessions }} 세션</span>
            </div>
            <div class="detail-item">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
              </svg>
              <span>약 {{ chapter.estimatedTime }}분</span>
            </div>
            <div v-if="chapter.lastAccessed" class="detail-item">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 11H7v6h2v-6zm4 0h-2v6h2v-6zm4 0h-2v6h2v-6zm2-7h-1V2h-2v2H8V2H6v2H5c-1.1 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z"/>
              </svg>
              <span>{{ formatLastAccessed(chapter.lastAccessed) }}</span>
            </div>
          </div>
        </div>

        <!-- 액션 버튼 -->
        <div class="chapter-actions">
          <button
            v-if="!chapter.isLocked"
            @click.stop="handleStartChapter(chapter)"
            class="action-btn primary"
            :disabled="isLoading"
          >
            {{ getActionButtonText(chapter) }}
          </button>
          <button
            v-if="chapter.isLocked"
            class="action-btn locked"
            disabled
          >
            잠김
          </button>
        </div>
      </div>
    </div>

    <!-- 빈 상태 -->
    <div v-if="filteredChapters.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
        </svg>
      </div>
      <h4 class="empty-title">검색 결과가 없습니다</h4>
      <p class="empty-description">다른 검색어를 시도해보세요</p>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span class="loading-text">챕터를 불러오는 중...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 라우터 설정
const router = useRouter()

// Props 정의
const props = defineProps({
  // 사용자 ID
  userId: {
    type: [String, Number],
    required: true
  }
})

// 이벤트 정의
const emit = defineEmits(['chapter-select', 'chapter-start'])

// 반응형 데이터
const isLoading = ref(false)
const searchQuery = ref('')
const sortBy = ref('order')

// 챕터 데이터 (실제로는 API에서 가져올 데이터)
const chapters = ref([
  {
    id: 1,
    order: 1,
    title: 'AI 기초 개념',
    description: 'AI의 기본 개념과 역사, 현재 활용 분야에 대해 학습합니다.',
    difficulty: 'beginner',
    progress: 100,
    completedSessions: 5,
    totalSessions: 5,
    estimatedTime: 45,
    isLocked: false,
    lastAccessed: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
  },
  {
    id: 2,
    order: 2,
    title: 'ChatGPT 활용법',
    description: 'ChatGPT의 기본 사용법부터 고급 활용 기법까지 배웁니다.',
    difficulty: 'beginner',
    progress: 80,
    completedSessions: 4,
    totalSessions: 5,
    estimatedTime: 60,
    isLocked: false,
    lastAccessed: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
  },
  {
    id: 3,
    order: 3,
    title: '프롬프트 엔지니어링',
    description: '효과적인 프롬프트 작성 기법과 최적화 방법을 학습합니다.',
    difficulty: 'intermediate',
    progress: 60,
    completedSessions: 3,
    totalSessions: 5,
    estimatedTime: 75,
    isLocked: false,
    lastAccessed: new Date(Date.now() - 3 * 60 * 60 * 1000)
  },
  {
    id: 4,
    order: 4,
    title: 'AI 도구 활용',
    description: '다양한 AI 도구들의 특징과 실무 활용 방법을 배웁니다.',
    difficulty: 'intermediate',
    progress: 20,
    completedSessions: 1,
    totalSessions: 5,
    estimatedTime: 90,
    isLocked: false,
    lastAccessed: null
  },
  {
    id: 5,
    order: 5,
    title: '고급 AI 활용',
    description: '전문가 수준의 AI 활용 기법과 실무 적용 사례를 학습합니다.',
    difficulty: 'advanced',
    progress: 0,
    completedSessions: 0,
    totalSessions: 6,
    estimatedTime: 120,
    isLocked: true,
    lastAccessed: null
  }
])

// 계산된 속성
const filteredChapters = computed(() => {
  let filtered = chapters.value

  // 검색 필터링
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(chapter =>
      chapter.title.toLowerCase().includes(query) ||
      chapter.description.toLowerCase().includes(query)
    )
  }

  // 정렬
  filtered = [...filtered].sort((a, b) => {
    switch (sortBy.value) {
      case 'progress':
        return b.progress - a.progress
      case 'difficulty':
        const difficultyOrder = { 'beginner': 1, 'intermediate': 2, 'advanced': 3 }
        return difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty]
      default:
        return a.order - b.order
    }
  })

  return filtered
})

// 난이도 텍스트 반환
const getDifficultyText = (difficulty) => {
  const difficultyMap = {
    'beginner': '초급',
    'intermediate': '중급',
    'advanced': '고급'
  }
  return difficultyMap[difficulty] || '초급'
}

// 진행률에 따른 클래스 반환
const getProgressClass = (progress) => {
  if (progress >= 100) return 'completed'
  if (progress >= 50) return 'medium'
  return 'low'
}

// 액션 버튼 텍스트 반환
const getActionButtonText = (chapter) => {
  if (chapter.progress >= 100) return '복습하기'
  if (chapter.progress > 0) return '계속하기'
  return '시작하기'
}

// 마지막 접근 시간 포맷팅
const formatLastAccessed = (timestamp) => {
  if (!timestamp) return ''
  
  const now = new Date()
  const diff = now - timestamp
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor(diff / (1000 * 60 * 60))

  if (days > 0) {
    return `${days}일 전`
  } else if (hours > 0) {
    return `${hours}시간 전`
  } else {
    return '방금 전'
  }
}

// 정렬 처리
const handleSort = () => {
  // 정렬은 computed에서 자동으로 처리됨
}

// 챕터 클릭 처리
const handleChapterClick = (chapter) => {
  if (chapter.isLocked) return
  
  emit('chapter-select', chapter)
}

// 챕터 시작 처리
const handleStartChapter = (chapter) => {
  if (chapter.isLocked) return

  emit('chapter-start', chapter)
  router.push(`/learning/${chapter.id}`)
}

// 챕터 데이터 로드
const loadChapters = async () => {
  isLoading.value = true
  
  try {
    // 실제로는 API 호출
    await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (error) {
    console.error('챕터 로딩 실패:', error)
  } finally {
    isLoading.value = false
  }
}

// 라이프사이클 훅
onMounted(() => {
  loadChapters()
})
</script>

<style lang="scss" scoped>
.chapter-list {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: relative;

  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    gap: 1rem;

    .list-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0;
    }

    .list-controls {
      display: flex;
      gap: 1rem;
      align-items: center;

      .search-box {
        position: relative;

        .search-input {
          padding: 0.5rem 2.5rem 0.5rem 1rem;
          border: 2px solid var(--border-color);
          border-radius: 8px;
          font-size: 0.875rem;
          width: 200px;

          &:focus {
            outline: none;
            border-color: var(--primary-color);
          }
        }

        .search-icon {
          position: absolute;
          right: 0.75rem;
          top: 50%;
          transform: translateY(-50%);
          width: 16px;
          height: 16px;
          color: var(--text-secondary);
        }
      }

      .sort-select {
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
  }

  .chapters-container {
    .chapter-item {
      display: flex;
      align-items: center;
      gap: 1.5rem;
      padding: 1.5rem;
      border: 2px solid var(--border-light);
      border-radius: 12px;
      margin-bottom: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover:not(.locked) {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
      }

      &.locked {
        opacity: 0.6;
        cursor: not-allowed;
        background-color: var(--bg-disabled);
      }

      &.completed {
        border-color: #10b981;
        background-color: rgba(16, 185, 129, 0.02);
      }

      &.in-progress {
        border-color: var(--primary-color);
        background-color: rgba(var(--primary-color-rgb), 0.02);
      }

      .chapter-status {
        .status-icon {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;

          svg {
            width: 24px;
            height: 24px;
          }

          &.locked {
            background-color: rgba(107, 114, 128, 0.1);
            color: #6b7280;
          }

          &.completed {
            background-color: rgba(16, 185, 129, 0.1);
            color: #10b981;
          }

          &.in-progress {
            background-color: rgba(var(--primary-color-rgb), 0.1);
            color: var(--primary-color);
          }

          &.available {
            background-color: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
          }
        }
      }

      .chapter-content {
        flex: 1;

        .chapter-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 0.5rem;

          .chapter-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
          }

          .chapter-meta {
            display: flex;
            gap: 0.5rem;
            align-items: center;

            .chapter-order {
              background-color: var(--bg-light);
              color: var(--text-secondary);
              padding: 0.25rem 0.5rem;
              border-radius: 4px;
              font-size: 0.75rem;
              font-weight: 500;
            }

            .chapter-difficulty {
              padding: 0.25rem 0.5rem;
              border-radius: 4px;
              font-size: 0.75rem;
              font-weight: 500;

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
          }
        }

        .chapter-description {
          color: var(--text-secondary);
          margin: 0 0 1rem 0;
          line-height: 1.5;
        }

        .progress-container {
          margin-bottom: 1rem;

          .progress-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;

            .progress-text {
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

            .progress-fill {
              height: 100%;
              border-radius: 3px;
              transition: width 0.6s ease;

              &.completed {
                background: linear-gradient(90deg, #10b981, #34d399);
              }

              &.medium {
                background: linear-gradient(90deg, var(--primary-color), var(--primary-color-light));
              }

              &.low {
                background: linear-gradient(90deg, #f59e0b, #fbbf24);
              }
            }
          }
        }

        .chapter-details {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;

          .detail-item {
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

      .chapter-actions {
        .action-btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;

          &.primary {
            background-color: var(--primary-color);
            color: white;

            &:hover:not(:disabled) {
              background-color: var(--primary-color-dark);
              transform: translateY(-1px);
            }
          }

          &.locked {
            background-color: var(--bg-disabled);
            color: var(--text-secondary);
            cursor: not-allowed;
          }

          &:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
          }
        }
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 3rem 1rem;

    .empty-icon {
      width: 64px;
      height: 64px;
      margin: 0 auto 1rem;
      color: var(--text-tertiary);

      svg {
        width: 100%;
        height: 100%;
      }
    }

    .empty-title {
      font-size: 1.25rem;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 0.5rem 0;
    }

    .empty-description {
      color: var(--text-secondary);
      margin: 0;
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
  .chapter-list {
    padding: 1.5rem;

    .list-header {
      flex-direction: column;
      align-items: flex-start;

      .list-controls {
        width: 100%;
        justify-content: space-between;

        .search-box {
          .search-input {
            width: 150px;
          }
        }
      }
    }

    .chapters-container {
      .chapter-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;

        .chapter-content {
          width: 100%;

          .chapter-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
          }

          .chapter-details {
            justify-content: space-between;
          }
        }

        .chapter-actions {
          width: 100%;

          .action-btn {
            width: 100%;
          }
        }
      }
    }
  }
}
</style>