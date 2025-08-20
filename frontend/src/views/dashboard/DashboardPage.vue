<!-- frontend/src/views/dashboard/DashboardPage.vue -->
<!-- 대시보드 메인 페이지 -->

<template>
  <div class="dashboard-page">
    <!-- 로딩 오버레이 -->
    <div v-if="isLoading && !isInitialized" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">대시보드 로딩 중...</span>
        </div>
        <p class="loading-text">학습 현황을 불러오는 중입니다...</p>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
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
              :disabled="isRefreshing"
              class="refresh-btn"
            >
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isRefreshing }"></i>
              {{ isRefreshing ? '새로고침 중...' : '새로고침' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 에러 메시지 -->
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

      <!-- 학습 현황 요약 -->
      <div class="learning-overview">
        <div class="overview-grid">
          <!-- 현재 진행 상황 -->
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
                  <div class="percentage-circle">
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

          <!-- 학습 통계 -->
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

      <!-- 챕터 목록 -->
      <div class="chapter-section">
        <div class="section-header">
          <h2 class="section-title">
            <i class="fas fa-list"></i>
            챕터별 학습 현황
          </h2>
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
        </div>

        <!-- 챕터 카드 리스트 -->
        <div class="chapter-list">
          <div 
            v-for="chapter in chapterStatus" 
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

            <!-- 섹션 목록 -->
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

            <!-- 학습 시작 버튼 -->
            <div class="chapter-actions">
              <button 
                v-if="chapter.status === 'in_progress' || chapter.status === 'available'"
                @click="startLearning(chapter.chapter_number)"
                class="btn btn-primary start-learning-btn"
                :disabled="isStartingLearning"
              >
                <i class="fas fa-play"></i>
                {{ chapter.status === 'in_progress' ? '학습 계속하기' : '학습 시작하기' }}
              </button>
              <button 
                v-else-if="chapter.status === 'completed'"
                @click="reviewChapter(chapter.chapter_number)"
                class="btn btn-outline-secondary review-btn"
              >
                <i class="fas fa-eye"></i>
                복습하기
              </button>
              <div v-else class="locked-message">
                <i class="fas fa-lock"></i>
                이전 챕터를 완료해주세요
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 빠른 액션 -->
      <div class="quick-actions">
        <div class="actions-header">
          <h3 class="actions-title">
            <i class="fas fa-rocket"></i>
            빠른 학습
          </h3>
        </div>
        <div class="actions-grid">
          <button 
            @click="continueCurrentLearning"
            class="action-btn primary-action"
            :disabled="!canContinueLearning"
          >
            <i class="fas fa-play-circle"></i>
            <div class="action-content">
              <div class="action-title">현재 학습 계속하기</div>
              <div class="action-subtitle">
                {{ userProgress.current_chapter }}챕터 {{ userProgress.current_section }}섹션
              </div>
            </div>
          </button>
          <button 
            @click="goToLearningPage"
            class="action-btn secondary-action"
          >
            <i class="fas fa-book"></i>
            <div class="action-content">
              <div class="action-title">학습 페이지로</div>
              <div class="action-subtitle">전체 학습 진행</div>
            </div>
          </button>
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

export default {
  name: 'DashboardPage',
  
  setup() {
    const router = useRouter()
    const dashboardStore = useDashboardStore()
    const authStore = useAuthStore()

    // 반응형 데이터
    const isStartingLearning = ref(false)

    // 스토어에서 데이터 가져오기
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
    } = dashboardStore

    // 계산된 속성
    const canContinueLearning = computed(() => {
      return userProgress.current_chapter && userProgress.current_section
    })

    // 메서드들
    const getStatusText = (status) => {
      const statusMap = {
        'completed': '완료',
        'in_progress': '진행중',
        'available': '시작 가능',
        'locked': '잠금'
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

    const startLearning = async (chapterNumber) => {
      isStartingLearning.value = true
      
      try {
        // 학습 페이지로 이동 (챕터 지정)
        await router.push(`/learning/chapter/${chapterNumber}`)
      } catch (error) {
        console.error('학습 시작 실패:', error)
        alert('학습을 시작할 수 없습니다. 잠시 후 다시 시도해주세요.')
      } finally {
        isStartingLearning.value = false
      }
    }

    const reviewChapter = (chapterNumber) => {
      // 복습 모드로 학습 페이지 이동
      router.push(`/learning/chapter/${chapterNumber}?mode=review`)
    }

    const continueCurrentLearning = () => {
      if (!canContinueLearning.value) return
      
      // 현재 진행 중인 챕터로 이동
      router.push(`/learning/chapter/${userProgress.current_chapter}`)
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
      
      // 메서드
      getStatusText,
      refreshDashboard,
      clearError,
      startLearning,
      reviewChapter,
      continueCurrentLearning,
      goToLearningPage
    }
  }
}
</script>

/* frontend/src/views/dashboard/DashboardPage.vue - CSS 스타일 */

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  position: relative;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
}

.loading-text {
  margin-top: 1rem;
  color: #6c757d;
  font-weight: 500;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* 페이지 헤더 */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 1.5rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.header-info {
  flex: 1;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-icon {
  color: #4f46e5;
}

.page-description {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0;
}

.refresh-btn {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.refresh-btn:hover:not(:disabled) {
  background: #3730a3;
  transform: translateY(-2px);
}

.refresh-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
}

/* 에러 알림 */
.error-alert {
  margin-bottom: 2rem;
}

.alert {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  border-radius: 0.75rem;
  border: none;
}

.alert-danger {
  background: #fee2e2;
  color: #dc2626;
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
  color: #dc2626;
  cursor: pointer;
  padding: 0.25rem;
  margin-left: 1rem;
}

/* 학습 현황 요약 */
.learning-overview {
  margin-bottom: 3rem;
}

.overview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.overview-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: transform 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
}

.card-header {
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #e9ecef;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-body {
  padding: 1.5rem;
}

/* 진행 상황 카드 */
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
  color: #4f46e5;
}

.section-label {
  font-size: 1rem;
  color: #6c757d;
}

.percentage-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: conic-gradient(#4f46e5 var(--percentage, 0%), #e9ecef 0%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.percentage-circle::before {
  content: '';
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: white;
  position: absolute;
}

.percentage-text {
  font-size: 1rem;
  font-weight: 700;
  color: #4f46e5;
  z-index: 1;
}

.progress-bar-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-bar {
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
  transition: width 0.3s ease;
}

.progress-label {
  font-size: 0.875rem;
  color: #6c757d;
  text-align: center;
}

/* 통계 카드 */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  text-align: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
}

.last-study {
  text-align: center;
  padding: 0.75rem;
  background: #e7f3ff;
  border-radius: 0.5rem;
  color: #0066cc;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* 챕터 섹션 */
.chapter-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chapter-summary {
  display: flex;
  gap: 1rem;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.summary-item.completed {
  color: #10b981;
}

.summary-item.total {
  color: #6c757d;
}

/* 챕터 카드 */
.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chapter-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.chapter-card.current {
  border-left-color: #4f46e5;
  box-shadow: 0 8px 30px rgba(79, 70, 229, 0.15);
}

.chapter-card.status-completed {
  border-left-color: #10b981;
}

.chapter-card.status-in_progress {
  border-left-color: #f59e0b;
}

.chapter-card.status-locked {
  opacity: 0.6;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
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
  color: #6c757d;
  text-transform: uppercase;
}

.chapter-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.chapter-status {
  text-align: right;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.badge-completed {
  background: #d1fae5;
  color: #065f46;
}

.badge-in_progress {
  background: #fef3c7;
  color: #92400e;
}

.badge-available {
  background: #dbeafe;
  color: #1e40af;
}

.badge-locked {
  background: #f3f4f6;
  color: #6b7280;
}

.completion-date {
  font-size: 0.75rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* 섹션 리스트 */
.section-list {
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.section-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e9ecef;
}

.section-item:last-child {
  border-bottom: none;
}

.section-item.current {
  background: rgba(79, 70, 229, 0.1);
  margin: 0 -0.5rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
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
  color: #495057;
}

.section-date {
  font-size: 0.75rem;
  color: #6c757d;
}

/* 챕터 액션 */
.chapter-actions {
  padding: 1.5rem;
}

.start-learning-btn,
.review-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #4f46e5;
  border: 1px solid #4f46e5;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #3730a3;
  border-color: #3730a3;
}

.btn-outline-secondary {
  background: transparent;
  border: 1px solid #6c757d;
  color: #6c757d;
}

.btn-outline-secondary:hover {
  background: #6c757d;
  color: white;
}

.locked-message {
  text-align: center;
  color: #6c757d;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* 빠른 액션 */
.quick-actions {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 2rem;
}

.actions-header {
  margin-bottom: 1.5rem;
}

.actions-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.primary-action {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
}

.primary-action:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
}

.secondary-action {
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #e9ecef;
}

.secondary-action:hover {
  background: #e9ecef;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.action-btn i {
  font-size: 1.5rem;
}

.action-content {
  flex: 1;
}

.action-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.action-subtitle {
  font-size: 0.875rem;
  opacity: 0.8;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }

  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .overview-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .section-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .chapter-summary {
    justify-content: center;
  }

  .chapter-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .section-title {
    font-size: 1.25rem;
  }
}

@media (max-width: 576px) {
  .dashboard-container {
    padding: 0.5rem;
  }

  .page-header,
  .learning-overview,
  .chapter-section,
  .quick-actions {
    margin-bottom: 1.5rem;
  }

  .header-content,
  .overview-card,
  .chapter-card,
  .quick-actions {
    padding: 1rem;
  }

  .card-header,
  .card-body,
  .chapter-header,
  .chapter-actions {
    padding: 1rem;
  }

  .section-list {
    padding: 0.75rem 1rem;
  }

  .action-btn {
    padding: 1rem;
    gap: 0.75rem;
  }

  .action-btn i {
    font-size: 1.25rem;
  }
}

/* 애니메이션 */
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

.overview-card,
.chapter-card {
  animation: fadeInUp 0.5s ease-out;
}

.chapter-card:nth-child(2) {
  animation-delay: 0.1s;
}

.chapter-card:nth-child(3) {
  animation-delay: 0.2s;
}

.chapter-card:nth-child(4) {
  animation-delay: 0.3s;
}

/* 기타 유틸리티 */
.percentage-circle {
  --percentage: 0%;
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

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