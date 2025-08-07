// frontend/src/router/index.js
// Vue Router 설정 - AI 활용법 학습 튜터 라우트 정의

import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'AI 활용법 학습 튜터 - 홈'
      }
    },
    {
      path: '/about',
      name: 'about',
      // 라우트 레벨 코드 분할
      // 해당 라우트 방문 시에만 로드되는 별도 청크 생성
      component: () => import('../views/AboutView.vue'),
      meta: {
        title: 'AI 활용법 학습 튜터 - 소개'
      }
    },
    {
      path: '/diagnosis',
      name: 'diagnosis',
      component: () => import('../views/DiagnosisPage.vue'),
      meta: {
        title: 'AI 활용법 학습 튜터 - 사용자 진단',
        requiresAuth: true // 로그인 필요한 페이지로 설정 (현재 비활성화)
      }
    },
    {
      path: '/diagnosis/result',
      name: 'diagnosis-result',
      component: () => import('../views/DiagnosisResultPage.vue'),
      meta: {
        title: 'AI 활용법 학습 튜터 - 진단 결과',
        requiresAuth: true // 로그인 필요한 페이지로 설정 (현재 비활성화)
      }
    },
  ],
})

// 라우트 변경 시 페이지 타이틀 업데이트
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'AI 활용법 학습 튜터'
  next()
})

export default router