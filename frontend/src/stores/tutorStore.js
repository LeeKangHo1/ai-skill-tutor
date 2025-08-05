// frontend/src/stores/tutorStore.js
// 학습 세션 상태 관리

import { defineStore } from 'pinia'

export const useTutorStore = defineStore('tutor', {
  state: () => ({
    currentSession: null,
    sessionHistory: [],
    currentChapter: null,
    learningProgress: 0
  }),

  getters: {
    // 현재 세션 정보
    getCurrentSession: (state) => state.currentSession,
    // 학습 진도율
    getProgress: (state) => state.learningProgress
  },

  actions: {
    // 새 세션 시작
    startSession(sessionData) {
      this.currentSession = sessionData
    },

    // 세션 종료
    endSession() {
      if (this.currentSession) {
        this.sessionHistory.push(this.currentSession)
        this.currentSession = null
      }
    },

    // 진도 업데이트
    updateProgress(progress) {
      this.learningProgress = progress
    }
  }
})