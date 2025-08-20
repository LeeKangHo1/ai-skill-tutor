// frontend/src/stores/dashboardStore.js

/**
 * 대시보드 상태 관리 스토어 (Pinia)
 * - 학습 현황 및 통계 데이터 관리
 * - 챕터별 진행 상태 관리
 * - 캐싱 및 자동 새로고침 처리
 */

import { defineStore } from 'pinia'
import dashboardService from '../services/dashboardService'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    // 사용자 진행 상태
    userProgress: {
      current_chapter: 1,
      current_section: 1,
      completion_percentage: 0,
      formatted_completion_percentage: '0%'
    },

    // 학습 통계
    learningStatistics: {
      total_study_time_minutes: 0,
      total_study_sessions: 0,
      multiple_choice_accuracy: 0,
      subjective_average_score: 0,
      total_multiple_choice_count: 0,
      total_subjective_count: 0,
      last_study_date: null,
      formatted_study_time: '0분',
      formatted_multiple_choice_accuracy: '0%',
      formatted_subjective_average_score: '0점',
      formatted_last_study_date: null
    },

    // 챕터별 상태
    chapterStatus: [],

    // 로딩 상태
    isLoading: false,
    isRefreshing: false,

    // 에러 상태
    error: null,

    // 마지막 업데이트 시간
    lastUpdated: null,

    // 초기화 완료 여부
    isInitialized: false
  }),

  getters: {
    /**
     * 현재 챕터 정보
     */
    currentChapterInfo: (state) => {
      return state.chapterStatus.find(chapter => 
        chapter.chapter_number === state.userProgress.current_chapter
      )
    },

    /**
     * 완료된 챕터 수
     */
    completedChaptersCount: (state) => {
      return state.chapterStatus.filter(chapter => 
        chapter.status === 'completed'
      ).length
    },

    /**
     * 진행 중인 챕터 수
     */
    inProgressChaptersCount: (state) => {
      return state.chapterStatus.filter(chapter => 
        chapter.status === 'in_progress'
      ).length
    },

    /**
     * 전체 챕터 수
     */
    totalChaptersCount: (state) => {
      return state.chapterStatus.length
    },

    /**
     * 학습 가능한 다음 챕터
     */
    nextAvailableChapter: (state) => {
      return state.chapterStatus.find(chapter => 
        chapter.status === 'available' || chapter.status === 'in_progress'
      )
    },

    /**
     * 학습 활동 여부 (최근 7일 기준)
     */
    isActivelearner: (state) => {
      if (!state.learningStatistics.last_study_date) return false
      
      const lastStudyDate = new Date(state.learningStatistics.last_study_date)
      const sevenDaysAgo = new Date()
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
      
      return lastStudyDate >= sevenDaysAgo
    },

    /**
     * 학습 성과 요약
     */
    learningPerformanceSummary: (state) => {
      const stats = state.learningStatistics
      
      return {
        totalQuestions: stats.total_multiple_choice_count + stats.total_subjective_count,
        averageAccuracy: stats.total_multiple_choice_count > 0 ? stats.multiple_choice_accuracy : 0,
        averageScore: stats.total_subjective_count > 0 ? stats.subjective_average_score : 0,
        studyFrequency: stats.total_study_sessions > 0 ? 
          Math.round(stats.total_study_time_minutes / stats.total_study_sessions) : 0
      }
    },

    /**
     * 데이터 신선도 확인 (5분 기준)
     */
    isDataFresh: (state) => {
      if (!state.lastUpdated) return false
      
      const fiveMinutesAgo = new Date()
      fiveMinutesAgo.setMinutes(fiveMinutesAgo.getMinutes() - 5)
      
      return new Date(state.lastUpdated) >= fiveMinutesAgo
    },

    /**
     * 진행률 단계별 분류
     */
    progressLevel: (state) => {
      const percentage = state.userProgress.completion_percentage
      
      if (percentage >= 80) return 'advanced'
      if (percentage >= 50) return 'intermediate' 
      if (percentage >= 20) return 'beginner'
      return 'starter'
    },

    /**
     * 챕터별 그룹화 (완료/진행중/잠금)
     */
    groupedChapters: (state) => {
      return {
        completed: state.chapterStatus.filter(ch => ch.status === 'completed'),
        inProgress: state.chapterStatus.filter(ch => ch.status === 'in_progress'),
        available: state.chapterStatus.filter(ch => ch.status === 'available'),
        locked: state.chapterStatus.filter(ch => ch.status === 'locked')
      }
    }
  },

  actions: {
    /**
     * 대시보드 데이터 초기화
     */
    async initialize() {
      if (this.isInitialized && this.isDataFresh) {
        return // 이미 초기화되고 데이터가 신선한 경우 스킵
      }

      this.isLoading = true
      this.error = null

      try {
        await this.fetchDashboardData()
        this.isInitialized = true
      } catch (error) {
        console.error('대시보드 초기화 실패:', error)
        this.handleError(error)
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 대시보드 데이터 조회
     */
    async fetchDashboardData(forceRefresh = false) {
      // 새로고침 중이면 중복 요청 방지
      if (this.isRefreshing && !forceRefresh) return

      this.isRefreshing = true
      this.error = null

      try {
        const response = await dashboardService.getFormattedDashboardData(forceRefresh)

        if (response.success) {
          this.updateDashboardData(response.data)
          this.lastUpdated = new Date().toISOString()
        } else {
          throw new Error('대시보드 데이터 조회 실패')
        }
      } catch (error) {
        console.error('대시보드 데이터 조회 실패:', error)
        this.handleError(error)
        throw error
      } finally {
        this.isRefreshing = false
      }
    },

    /**
     * 대시보드 데이터 업데이트
     */
    updateDashboardData(data) {
      const { userProgress, learningStatistics, chapterStatus } = data

      // 사용자 진행 상태 업데이트
      if (userProgress) {
        this.userProgress = { ...this.userProgress, ...userProgress }
      }

      // 학습 통계 업데이트
      if (learningStatistics) {
        this.learningStatistics = { ...this.learningStatistics, ...learningStatistics }
      }

      // 챕터 상태 업데이트
      if (chapterStatus) {
        this.chapterStatus = chapterStatus
      }
    },

    /**
     * 데이터 새로고침
     */
    async refreshData() {
      this.isLoading = true

      try {
        await this.fetchDashboardData(true) // 강제 새로고침
      } catch (error) {
        console.error('데이터 새로고침 실패:', error)
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 특정 챕터 정보 조회
     */
    getChapterInfo(chapterNumber) {
      return this.chapterStatus.find(chapter => 
        chapter.chapter_number === chapterNumber
      )
    },

    /**
     * 특정 챕터의 섹션 정보 조회
     */
    getChapterSections(chapterNumber) {
      const chapter = this.getChapterInfo(chapterNumber)
      return chapter?.sections || []
    },

    /**
     * 학습 진행 후 상태 업데이트
     */
    async updateAfterLearning(updatedProgress) {
      // 로컬 상태 즉시 업데이트
      if (updatedProgress.current_chapter) {
        this.userProgress.current_chapter = updatedProgress.current_chapter
      }
      if (updatedProgress.current_section) {
        this.userProgress.current_section = updatedProgress.current_section
      }

      // 서버에서 최신 데이터 조회
      try {
        await this.fetchDashboardData(true)
      } catch (error) {
        console.warn('학습 후 대시보드 업데이트 실패:', error)
      }
    },

    /**
     * 헬스 체크
     */
    async checkHealth() {
      try {
        const response = await dashboardService.checkDashboardHealth()
        return response
      } catch (error) {
        console.error('대시보드 헬스 체크 실패:', error)
        return { success: false, error: error.message }
      }
    },

    /**
     * 에러 처리
     */
    handleError(error) {
      this.error = {
        message: error.message || '알 수 없는 오류가 발생했습니다',
        code: error.code || 'UNKNOWN_ERROR',
        timestamp: new Date().toISOString()
      }
    },

    /**
     * 에러 초기화
     */
    clearError() {
      this.error = null
    },

    /**
     * 상태 초기화
     */
    resetState() {
      this.userProgress = {
        current_chapter: 1,
        current_section: 1,
        completion_percentage: 0,
        formatted_completion_percentage: '0%'
      }
      this.learningStatistics = {
        total_study_time_minutes: 0,
        total_study_sessions: 0,
        multiple_choice_accuracy: 0,
        subjective_average_score: 0,
        total_multiple_choice_count: 0,
        total_subjective_count: 0,
        last_study_date: null,
        formatted_study_time: '0분',
        formatted_multiple_choice_accuracy: '0%',
        formatted_subjective_average_score: '0점',
        formatted_last_study_date: null
      }
      this.chapterStatus = []
      this.error = null
      this.lastUpdated = null
      this.isInitialized = false
    },

    /**
     * 자동 새로고침 설정
     */
    startAutoRefresh(intervalMinutes = 10) {
      // 기존 인터벌 클리어
      if (this.autoRefreshInterval) {
        clearInterval(this.autoRefreshInterval)
      }

      // 새 인터벌 설정
      this.autoRefreshInterval = setInterval(async () => {
        if (!this.isLoading && !this.isRefreshing) {
          try {
            await this.fetchDashboardData()
          } catch (error) {
            console.warn('자동 새로고침 실패:', error)
          }
        }
      }, intervalMinutes * 60 * 1000)
    },

    /**
     * 자동 새로고침 중지
     */
    stopAutoRefresh() {
      if (this.autoRefreshInterval) {
        clearInterval(this.autoRefreshInterval)
        this.autoRefreshInterval = null
      }
    },

    /**
     * 데이터 유효성 확인
     */
    validateData() {
      const issues = []

      if (!this.userProgress.current_chapter || this.userProgress.current_chapter < 1) {
        issues.push('유효하지 않은 현재 챕터')
      }

      if (!this.userProgress.current_section || this.userProgress.current_section < 1) {
        issues.push('유효하지 않은 현재 섹션')
      }

      if (this.chapterStatus.length === 0) {
        issues.push('챕터 상태 데이터 없음')
      }

      return {
        isValid: issues.length === 0,
        issues
      }
    }
  }
})

export default useDashboardStore