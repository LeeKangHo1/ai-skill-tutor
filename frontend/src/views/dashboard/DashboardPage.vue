<!-- frontend/src/views/dashboard/DashboardPage.vue -->
<!-- 대시보드 페이지 -->

<template>
  <div class="dashboard-page">
    <div v-if="isLoading && !isInitialized" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">대시보드 로딩 중...</span>
        </div>
        <p class="loading-text">학습 현황을 불러오는 중입니다...</p>
      </div>
    </div>

    <div v-else class="dashboard-container">
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
              :disabled="isRefreshing"
              class="refresh-btn"
            >
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isRefreshing }"></i>
              {{ isRefreshing ? '새로고침 중...' : '새로고침' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="error" class="error-alert">
        <div class="alert alert-danger">
          <i class="fas fa-exclamation-triangle"></i>
          <div class="error-content">
            <strong>오류 발생:</strong> {{ error.message }}
            <button @click="clearError" class="error-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>

      <div class="learning-overview">
        <div class="overview-grid">
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
                  <span class="chapter-label">{{ userProgress.current_chapter }}챕터</span>
                  <span class="section-label">{{ userProgress.current_section }}섹션</span>
                </div>
                <div class="progress-percentage">
                  <div class="percentage-circle" :style="{'--percentage': userProgress.completion_percentage + '%'}">
                    <div class="percentage-text">
                      {{ userProgress.formatted_completion_percentage }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="progress-bar-wrapper">
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: userProgress.formatted_completion_percentage }"
                  ></div>
                </div>
                <span class="progress-label">전체 진행률</span>
              </div>
            </div>
          </div>

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
                  <div class="stat-value">{{ learningStatistics.formatted_study_time }}</div>
                  <div class="stat-label">총 학습시간</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ learningStatistics.total_study_sessions }}회</div>
                  <div class="stat-label">학습 세션</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ learningStatistics.formatted_multiple_choice_accuracy }}</div>
                  <div class="stat-label">객관식 정답률</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ learningStatistics.formatted_subjective_average_score }}</div>
                  <div class="stat-label">주관식 평균</div>
                </div>
              </div>
              <div v-if="learningStatistics.formatted_last_study_date" class="last-study">
                <i class="fas fa-calendar-alt"></i>
                마지막 학습: {{ learningStatistics.formatted_last_study_date }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="chapter-section">
        <div class="section-header">
          <h2 class="section-title">
            <i class="fas fa-list"></i>
            챕터별 학습 현황
          </h2>
          <div class="section-controls">
            <div class="chapter-summary">
              <span class="summary-item completed">
                <i class="fas fa-check-circle"></i>
                완료: {{ completedChaptersCount }}개
              </span>
              <span class="summary-item total">
                <i class="fas fa-book"></i>
                전체: {{ totalChaptersCount }}개
              </span>
            </div>
            <button
              @click="toggleChapterList"
              class="toggle-btn"
              :class="{ 'expanded': isChapterListExpanded }"
            >
              <i class="fas fa-chevron-down"></i>
              {{ isChapterListExpanded ? '접기' : '펼치기' }}
            </button>
          </div>
        </div>

        <div class="chapter-list">
          <div
            v-for="chapter in currentChapterList"
            :key="chapter.chapter_number"
            class="chapter-card"
            :class="[
              `status-${chapter.status}`,
              { 'current': chapter.chapter_number === userProgress.current_chapter }
            ]"
          >
            <div class="chapter-header">
              <div class="chapter-info">
                <div class="chapter-number">
                  <span class="chapter-icon">{{ chapter.status_icon }}</span>
                  <span class="chapter-text">{{ chapter.chapter_number }}챕터</span>
                </div>
                <h3 class="chapter-title">{{ chapter.chapter_title }}</h3>
              </div>
              <div class="chapter-status">
                <span class="status-badge" :class="`badge-${chapter.status}`">
                  {{ getStatusText(chapter.status) }}
                </span>
                <div v-if="chapter.formatted_completion_date" class="completion-date">
                  <i class="fas fa-calendar-check"></i>
                  {{ chapter.formatted_completion_date }}
                </div>
              </div>
            </div>

            <div v-if="chapter.sections && chapter.sections.length > 0" class="section-list">
              <div
                v-for="section in chapter.sections"
                :key="`${chapter.chapter_number}-${section.section_number}`"
                class="section-item"
                :class="[
                  `status-${section.status}`,
                  {
                    'current': chapter.chapter_number === userProgress.current_chapter &&
                               section.section_number === userProgress.current_section
                  }
                ]"
              >
                <div class="section-info">
                  <span class="section-icon">{{ section.status_icon }}</span>
                  <span class="section-title">{{ section.section_title }}</span>
                </div>
                <div v-if="section.formatted_completion_date" class="section-date">
                  {{ section.formatted_completion_date }}
                </div>
              </div>
            </div>

            <div class="chapter-actions">
              <button
                @click="goToLearningPage"
                class="btn btn-primary start-learning-btn"
              >
                <i class="fas fa-play"></i>
                학습 계속하기
              </button>
            </div>
          </div>

          <Transition name="chapter-expand">
            <div v-show="isChapterListExpanded" class="expanded-chapters">
              <div
                v-for="chapter in otherChapterList"
                :key="chapter.chapter_number"
                class="chapter-card"
                :class="[
                  `status-${chapter.status}`,
                  { 'current': chapter.chapter_number === userProgress.current_chapter }
                ]"
              >
                <div class="chapter-header">
                  <div class="chapter-info">
                    <div class="chapter-number">
                      <span class="chapter-icon">{{ chapter.status_icon }}</span>
                      <span class="chapter-text">{{ chapter.chapter_number }}챕터</span>
                    </div>
                    <h3 class="chapter-title">{{ chapter.chapter_title }}</h3>
                  </div>
                  <div class="chapter-status">
                    <span class="status-badge" :class="`badge-${chapter.status}`">
                      {{ getStatusText(chapter.status) }}
                    </span>
                    <div v-if="chapter.formatted_completion_date" class="completion-date">
                      <i class="fas fa-calendar-check"></i>
                      {{ chapter.formatted_completion_date }}
                    </div>
                  </div>
                </div>

                <div v-if="chapter.sections && chapter.sections.length > 0" class="section-list">
                  <div
                    v-for="section in chapter.sections"
                    :key="`${chapter.chapter_number}-${section.section_number}`"
                    class="section-item"
                    :class="[
                      `status-${section.status}`,
                      {
                        'current': chapter.chapter_number === userProgress.current_chapter &&
                                   section.section_number === userProgress.current_section
                      }
                    ]"
                  >
                    <div class="section-info">
                      <span class="section-icon">{{ section.status_icon }}</span>
                      <span class="section-title">{{ section.section_title }}</span>
                    </div>
                    <div v-if="section.formatted_completion_date" class="section-date">
                      {{ section.formatted_completion_date }}
                    </div>
                  </div>
                </div>

                </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '../../stores/dashboardStore'
import { useAuthStore } from '../../stores/authStore'
import { storeToRefs } from 'pinia'

export default {
  name: 'DashboardPage',
  
  setup() {
    const router = useRouter()
    const dashboardStore = useDashboardStore()
    const authStore = useAuthStore()

    // 반응성을 유지하며 스토어에서 데이터 가져오기
    const {
      userProgress,
      learningStatistics,
      chapterStatus,
      isLoading,
      isRefreshing,
      error,
      isInitialized,
      completedChaptersCount,
      totalChaptersCount
    } = storeToRefs(dashboardStore)

    // 반응형 데이터
    const isStartingLearning = ref(false)
    const isChapterListExpanded = ref(false)

    // 계산된 속성
    const canContinueLearning = computed(() => {
      return userProgress.value.current_chapter && userProgress.value.current_section
    })

    // 현재 진행 중인 챕터만 필터링 (항상 표시)
    const currentChapterList = computed(() => {
      if (!chapterStatus.value || !Array.isArray(chapterStatus.value)) return []
      return chapterStatus.value.filter(chapter => 
        // 데이터 타입을 숫자로 변환하여 비교
        parseInt(chapter.chapter_number) === parseInt(userProgress.value.current_chapter)
      )
    })

    // 현재 진행 중인 챕터를 제외한 나머지 챕터들 (펼치기 시 표시)
    const otherChapterList = computed(() => {
      if (!chapterStatus.value || !Array.isArray(chapterStatus.value)) return []
      return chapterStatus.value.filter(chapter => 
        // 데이터 타입을 숫자로 변환하여 비교
        parseInt(chapter.chapter_number) !== parseInt(userProgress.value.current_chapter)
      )
    })

    // 메서드들
    const getStatusText = (status) => {
      const statusMap = {
        'completed': '완료',
        'in_progress': '진행중',
        'available': '시작 가능',
        'locked': '잠김'
      }
      return statusMap[status] || '알 수 없음'
    }

    const refreshDashboard = async () => {
      try {
        await dashboardStore.refreshData()
      } catch (error) {
        console.error('대시보드 새로고침 실패:', error)
      }
    }

    const clearError = () => {
      dashboardStore.clearError()
    }

    // 챕터 목록 펼치기/접기 토글
    const toggleChapterList = () => {
      isChapterListExpanded.value = !isChapterListExpanded.value
    }

    const goToLearningPage = () => {
      // 일반 학습 페이지로 이동
      router.push('/learning')
    }

    // 컴포넌트 라이프사이클
    onMounted(async () => {
      try {
        // 대시보드 데이터 초기화
        await dashboardStore.initialize()
        
        // 자동 새로고침 시작 (10분마다)
        dashboardStore.startAutoRefresh(10)
      } catch (error) {
        console.error('대시보드 초기화 실패:', error)
      }
    })

    onUnmounted(() => {
      // 자동 새로고침 중지
      dashboardStore.stopAutoRefresh()
    })

    return {
      // 상태
      userProgress,
      learningStatistics,
      chapterStatus,
      isLoading,
      isRefreshing,
      error,
      isInitialized,
      completedChaptersCount,
      totalChaptersCount,
      isStartingLearning,
      canContinueLearning,
      isChapterListExpanded,
      currentChapterList,
      otherChapterList,
      
      // 메서드
      getStatusText,
      refreshDashboard,
      clearError,
      toggleChapterList,
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

// 챕터 섹션
.chapter-section {
  margin-bottom: 3rem;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: $text-dark;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .section-controls {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .chapter-summary {
    display: flex;
    gap: 1rem;

    .summary-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.875rem;
      font-weight: 500;
      
      &.completed { color: $success; }
      &.total { color: $secondary; }
    }
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: $gray-100;
    border: 1px solid $gray-200;
    border-radius: $border-radius-lg;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: $gray-700;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: $gray-200;
      border-color: $gray-300;
    }

    i {
      transition: transform 0.3s ease;
    }

    &.expanded i {
      transform: rotate(180deg);
    }
  }
}

// 챕터 카드
.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  .expanded-chapters {
    margin-top: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.0rem;
  }

  .chapter-card {
    background: $white;
    border-radius: 1rem;
    box-shadow: 0 4px 20px rgba($black, 0.08);
    overflow: hidden;
    transition: all 0.3s ease;
    border-left: 4px solid transparent;
    animation: fadeInUp 0.5s ease-out;

    &:nth-child(2) { animation-delay: 0.1s; }
    &:nth-child(3) { animation-delay: 0.2s; }
    &:nth-child(4) { animation-delay: 0.3s; }
    
    &.current {
      border-left-color: $brand-purple;
      box-shadow: 0 8px 30px rgba($brand-purple, 0.15);
    }
    &.status-completed { border-left-color: $success; }
    &.status-in_progress { border-left-color: $warning; }
    &.status-locked { opacity: 0.6; }

    .chapter-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem;
      border-bottom: 1px solid $gray-200;
    }

    .chapter-info {
      flex: 1;
    }

    .chapter-number {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
    }

    .chapter-icon {
      font-size: 1.25rem;
    }

    .chapter-text {
      font-size: 0.875rem;
      font-weight: 600;
      color: $secondary;
      text-transform: uppercase;
    }

    .chapter-title {
      font-size: 1.25rem;
      font-weight: 600;
      color: $text-dark;
      margin: 0;
    }

    .chapter-status {
      text-align: right;
    }

    .status-badge {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: $border-radius-pill;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      margin-bottom: 0.5rem;
      
      &.badge-completed { background: lighten($success, 35%); color: darken($success, 20%); }
      &.badge-in_progress { background: lighten($warning, 25%); color: darken($warning, 30%); }
      &.badge-available { background: lighten($primary, 40%); color: darken($primary, 15%); }
      &.badge-locked { background: $gray-100; color: $secondary; }
    }

    .completion-date {
      font-size: 0.75rem;
      color: $secondary;
      display: flex;
      align-items: center;
      gap: 0.25rem;
    }
  }
}

// 섹션 리스트
.section-list {
  padding: 1rem 1.5rem;
  background: $gray-100;
  border-bottom: 1px solid $gray-200;

  .section-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid $gray-200;

    &:last-child {
      border-bottom: none;
    }

    &.current {
      background: rgba($brand-purple, 0.1);
      margin: 0 -0.5rem;
      padding: 0.5rem;
      border-radius: $border-radius-lg;
    }
  }

  .section-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
  }

  .section-icon {
    font-size: 0.875rem;
  }

  .section-title {
    font-size: 0.875rem;
    color: $gray-700;
  }

  .section-date {
    font-size: 0.75rem;
    color: $secondary;
  }
}

// 챕터 액션
.chapter-actions {
  padding: 1.5rem;

  .start-learning-btn {
    width: 100%;
    padding: 0.75rem 1rem;
    border-radius: $border-radius-lg;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    background: $brand-purple;
    border: 1px solid $brand-purple;
    color: $white;

    &:hover:not(:disabled) {
      background: darken($brand-purple, 10%);
      border-color: darken($brand-purple, 10%);
    }
  }
}

// 챕터 목록 펼치기/접기 애니메이션
.chapter-expand-enter-active,
.chapter-expand-leave-active {
  transition: all 0.4s ease;
  max-height: 2000px;
  overflow: hidden;
}

.chapter-expand-enter-from,
.chapter-expand-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
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