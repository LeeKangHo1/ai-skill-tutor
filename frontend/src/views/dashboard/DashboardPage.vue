<!-- frontend/src/views/dashboard/DashboardPage.vue -->
<!-- 대시보드 페이지 - 로딩 조건 개선 -->
 
<template>
  <div class="dashboard-page">
    <div v-if="dashboardStore.isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">대시보드 로딩 중...</span>
        </div>
        <p class="loading-text">학습 현황을 불러오는 중입니다...</p>
      </div>
    </div>

    <div v-else class="dashboard-container">
      <!-- 페이지 헤더 -->
      <div class="page-header">
        <div class="header-content">
          <div class="header-info">
            <h1 class="page-title">
              <i class="fas fa-chart-line title-icon"></i>
              학습 대시보드
            </h1>
            <p class="page-description">
              당신의 AI 학습 여정을 한눈에 확인하세요
            </p>
          </div>
          <div class="header-actions">
            <button
              @click="refreshDashboard"
              :disabled="dashboardStore.isRefreshing"
              class="refresh-btn"
            >
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': dashboardStore.isRefreshing }"></i>
              {{ dashboardStore.isRefreshing ? '새로고침 중...' : '새로고침' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 에러 알림 -->
      <div v-if="dashboardStore.error" class="error-alert">
        <div class="alert alert-danger">
          <i class="fas fa-exclamation-triangle"></i>
          <div class="error-content">
            <strong>오류 발생:</strong> {{ dashboardStore.error.message }}
            <button @click="clearError" class="error-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 학습 현황 요약 -->
      <div v-if="!dashboardStore.isLoading" class="learning-overview">
        <div class="overview-grid">
          <!-- 진행률 카드 -->
          <div class="overview-card progress-card">
            <div class="card-header">
              <h3 class="card-title">
                <i class="fas fa-book-open"></i>
                현재 진행
              </h3>
            </div>
            <div class="card-body">
              <div class="progress-info">
                <div class="current-chapter">
                  <span class="chapter-label">{{ dashboardStore.userProgress.current_chapter }}챕터</span>
                  <span class="section-label">{{ dashboardStore.userProgress.current_section }}섹션</span>
                </div>
                <div class="progress-percentage">
                  <div class="percentage-circle" :style="{'--percentage': dashboardStore.userProgress.completion_percentage + '%'}">
                    <div class="percentage-text">
                      {{ dashboardStore.userProgress.formatted_completion_percentage }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="progress-bar-wrapper">
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: dashboardStore.userProgress.formatted_completion_percentage }"
                  ></div>
                </div>
                <span class="progress-label">전체 진행률</span>
              </div>
            </div>
          </div>

          <!-- 통계 카드 -->
          <div class="overview-card stats-card">
            <div class="card-header">
              <h3 class="card-title">
                <i class="fas fa-chart-bar"></i>
                학습 통계
              </h3>
            </div>
            <div class="card-body">
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">{{ dashboardStore.learningStatistics.formatted_study_time }}</div>
                  <div class="stat-label">총 학습시간</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ dashboardStore.learningStatistics.total_study_sessions }}회</div>
                  <div class="stat-label">학습 세션</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ dashboardStore.learningStatistics.formatted_multiple_choice_accuracy }}</div>
                  <div class="stat-label">객관식 정답률</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ dashboardStore.learningStatistics.formatted_subjective_average_score }}</div>
                  <div class="stat-label">주관식 평균</div>
                </div>
              </div>
              <div v-if="dashboardStore.learningStatistics.formatted_last_study_date" class="last-study">
                <i class="fas fa-calendar-alt"></i>
                마지막 학습: {{ dashboardStore.learningStatistics.formatted_last_study_date }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 챕터 섹션 -->
      <ChapterSection
        v-if="!dashboardStore.isLoading"
        :chapter-status="dashboardStore.chapterStatus"
        :current-chapter="dashboardStore.userProgress.current_chapter"
        :current-section="dashboardStore.userProgress.current_section"
        :completed-count="dashboardStore.completedChaptersCount"
        :total-count="dashboardStore.totalChaptersCount"
        @start-learning="goToLearningPage"
      />
    </div>
  </div>
</template>

<script>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '../../stores/dashboardStore'
import ChapterSection from '../../components/dashboard/ChapterSection.vue'

export default {
  name: 'DashboardPage',
  
  components: {
    ChapterSection
  },
  
  setup() {
    const router = useRouter()
    const dashboardStore = useDashboardStore()

    // storeToRefs를 사용하지 않고, 스토어 인스턴스 자체를 템플릿에서 사용합니다.

    // 메서드들
    const refreshDashboard = async () => {
      await dashboardStore.refreshData()
    }

    const clearError = () => {
      dashboardStore.clearError()
    }

    const goToLearningPage = () => {
      router.push('/learning')
    }

    // 컴포넌트 라이프사이클
    onMounted(async () => {
      await nextTick()
      await dashboardStore.initialize()
      dashboardStore.startAutoRefresh(10)
    })

    onUnmounted(() => {
      dashboardStore.stopAutoRefresh()
    })

    return {
      // 템플릿에서 스토어의 상태와 getter에 접근할 수 있도록 인스턴스를 반환합니다.
      dashboardStore,

      // 템플릿에서 사용할 수 있도록 메서드를 반환합니다.
      refreshDashboard,
      clearError,
      goToLearningPage
    }
  }
}
</script>

<style lang="scss" scoped>
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dashboard-page {
  min-height: 100vh;
  background: $body-bg-gradient;
  position: relative;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba($white, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;

  .loading-spinner {
    text-align: center;
  }

  .loading-text {
    margin-top: 1rem;
    color: $secondary;
    font-weight: 500;
  }

  .spinner-border {
    width: 3rem;
    height: 3rem;
  }
}

.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

// 페이지 헤더
.page-header {
  margin-bottom: 2rem;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding: 1.5rem;
    background: $white;
    border-radius: 1rem;
    box-shadow: 0 4px 20px rgba($black, 0.08);
  }

  .header-info {
    flex: 1;
  }

  .page-title {
    font-size: 2rem;
    font-weight: 700;
    color: $text-dark;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;

    .title-icon {
      color: $brand-purple;
    }
  }

  .page-description {
    color: $secondary;
    font-size: 1.1rem;
    margin: 0;
  }

  .refresh-btn {
    background: $brand-purple;
    color: $white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: $border-radius-lg;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;

    &:hover:not(:disabled) {
      background: darken($brand-purple, 10%);
      transform: translateY(-2px);
    }

    &:disabled {
      background: $secondary;
      cursor: not-allowed;
      transform: none;
    }
  }
}

// 에러 알림
.error-alert {
  margin-bottom: 2rem;

  .alert {
    display: flex;
    align-items: center;
    padding: 1rem 1.5rem;
    border-radius: $border-radius-lg;
    border: none;

    &.alert-danger {
      background: lighten($danger, 35%);
      color: $danger;
    }
  }

  .error-content {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .error-close {
    background: none;
    border: none;
    color: $danger;
    cursor: pointer;
    padding: 0.25rem;
    margin-left: 1rem;
  }
}

// 학습 현황 요약
.learning-overview {
  margin-bottom: 3rem;

  .overview-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }

  .overview-card {
    background: $white;
    border-radius: 1rem;
    box-shadow: 0 4px 20px rgba($black, 0.08);
    overflow: hidden;
    transition: transform 0.3s ease;
    animation: fadeInUp 0.5s ease-out;

    &:hover {
      transform: translateY(-4px);
    }
    
    .card-header {
      padding: 1.5rem 1.5rem 1rem;
      border-bottom: 1px solid $gray-200;
    }

    .card-title {
      font-size: 1.25rem;
      font-weight: 600;
      color: $text-dark;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .card-body {
      padding: 1.5rem;
    }
  }

  .progress-card {
    .progress-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .current-chapter {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .chapter-label {
      font-size: 1.5rem;
      font-weight: 700;
      color: $brand-purple;
    }

    .section-label {
      font-size: 1rem;
      color: $secondary;
    }

    .percentage-circle {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: conic-gradient($brand-purple var(--percentage, 0%), $gray-200 0%);
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;

      &::before {
        content: '';
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: $white;
        position: absolute;
      }
    }

    .percentage-text {
      font-size: 1rem;
      font-weight: 700;
      color: $brand-purple;
      z-index: 1;
    }

    .progress-bar-wrapper {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .progress-bar {
      height: 8px;
      background: $gray-200;
      border-radius: 4px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, $brand-purple, #7c3aed);
      transition: width 0.3s ease;
    }

    .progress-label {
      font-size: 0.875rem;
      color: $secondary;
      text-align: center;
    }
  }

  .stats-card {
    .stats-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .stat-item {
      text-align: center;
      padding: 0.75rem;
      background: $gray-100;
      border-radius: $border-radius-lg;
    }

    .stat-value {
      font-size: 1.25rem;
      font-weight: 700;
      color: $text-dark;
      margin-bottom: 0.25rem;
    }

    .stat-label {
      font-size: 0.875rem;
      color: $secondary;
    }

    .last-study {
      text-align: center;
      padding: 0.75rem;
      background: lighten($primary, 40%);
      border-radius: $border-radius-lg;
      color: darken($primary, 10%);
      font-size: 0.875rem;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
    }
  }
}

// 기타 유틸리티
.visually-hidden {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}
</style>