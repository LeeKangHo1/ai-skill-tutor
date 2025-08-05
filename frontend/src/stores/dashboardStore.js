// frontend/src/stores/dashboardStore.js
// 대시보드 상태 관리

import { defineStore } from 'pinia'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    chapters: [],
    userStats: null,
    recentActivity: []
  }),

  getters: {
    // 사용 가능한 챕터 목록
    getAvailableChapters: (state) => state.chapters,
    // 사용자 통계
    getUserStats: (state) => state.userStats
  },

  actions: {
    // 챕터 목록 설정
    setChapters(chapters) {
      this.chapters = chapters
    },

    // 사용자 통계 업데이트
    updateUserStats(stats) {
      this.userStats = stats
    },

    // 최근 활동 추가
    addRecentActivity(activity) {
      this.recentActivity.unshift(activity)
      // 최대 10개까지만 유지
      if (this.recentActivity.length > 10) {
        this.recentActivity = this.recentActivity.slice(0, 10)
      }
    }
  }
})