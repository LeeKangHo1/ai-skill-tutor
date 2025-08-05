// frontend/src/stores/authStore.js
// 인증 관련 상태 관리

import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    token: null
  }),

  getters: {
    // 사용자 정보 getter
    getUserInfo: (state) => state.user,
    // 인증 상태 확인
    isLoggedIn: (state) => state.isAuthenticated
  },

  actions: {
    // 로그인 액션
    login(userData) {
      this.user = userData
      this.isAuthenticated = true
      this.token = userData.token
    },

    // 로그아웃 액션
    logout() {
      this.user = null
      this.isAuthenticated = false
      this.token = null
    }
  }
})