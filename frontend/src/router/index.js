// src/router/index.js

/**
 * Vue Router 설정 (인증 가드 적용)
 * - 페이지별 접근 권한 설정
 * - 자동 리다이렉트 처리
 * - 메타 정보 기반 가드 적용
 */

import { createRouter, createWebHistory } from 'vue-router'
import {
  requireAuth,
  requireDiagnosis,
  requireUserType,
  requireGuest,
  requireLearningAccess,
  applyMetaGuards
} from './authGuard'

// 페이지 컴포넌트 import
import HomeView from '../views/common/HomeView.vue'
import AboutView from '../views/common/AboutView.vue'
import LoginPage from '../views/auth/LoginPage.vue'
import DiagnosisPage from '../views/diagnosis/DiagnosisPage.vue'
import DiagnosisResultPage from '../views/diagnosis/DiagnosisResultPage.vue'
import DashboardPage from '../views/dashboard/DashboardPage.vue'
// ✨ 수정: LearningPage 컴포넌트 import 활성화
import LearningPage from '../views/learning/LearningPage.vue'

const routes = [
  // 홈 페이지 (누구나 접근 가능)
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: 'AI 활용법 학습 튜터',
      description: '홈페이지'
    }
  },

  // 소개 페이지 (누구나 접근 가능)
  {
    path: '/about',
    name: 'about',
    component: AboutView,
    meta: {
      title: '소개',
      description: '서비스 소개'
    }
  },

  // 로그인/회원가입 페이지 (게스트 전용)
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    beforeEnter: requireGuest,
    meta: {
      title: '로그인',
      description: '로그인 및 회원가입',
      requireGuest: true
    }
  },

  // 사용자 진단 페이지 (인증 필요, 진단 미완료자만)
  {
    path: '/diagnosis',
    name: 'diagnosis',
    component: DiagnosisPage,
    beforeEnter: requireAuth,
    meta: {
      title: '사용자 진단',
      description: '학습자 유형 진단',
      requireAuth: true,
      requireDiagnosis: false // 진단 완료 전이므로 false
    }
  },

  // 진단 결과 페이지 (인증 필요, 진단 미완료자만)
  {
    path: '/diagnosis/result',
    name: 'diagnosis-result',
    component: DiagnosisResultPage,
    beforeEnter: requireAuth,
    meta: {
      title: '진단 결과',
      description: '진단 결과 및 유형 선택',
      requireAuth: true,
      requireDiagnosis: false
    }
  },

  // 대시보드 (인증 + 진단 완료 필요)
  {
    path: '/dashboard',
    name: 'dashboard', 
    component: DashboardPage,
    beforeEnter: requireDiagnosis,
    meta: {
      title: '대시보드',
      description: '학습 현황 대시보드',
      requireAuth: true,
      requireDiagnosis: true
    }
  },

  // ✨ 수정: 학습 진행 페이지 경로 활성화
  {
    path: '/learning',
    name: 'learning',
    component: LearningPage,
    beforeEnter: requireDiagnosis,
    meta: {
      title: '학습 진행',
      description: '학습 세션 진행',
      requireAuth: true,
      requireDiagnosis: true
    }
  },

  // frontend/src/router/index.js에 테스트 라우트 추가
  {
    path: '/test',
    name: 'ComponentTest',
    component: () => import('@/views/test/ComponentTest.vue')
  },
  
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // 스크롤 복원
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 전역 네비게이션 가드
router.beforeEach(async (to, from, next) => {
  try {
    // 로딩 표시 (필요시)
    // store.commit('setLoading', true)
    
    // 메타 정보 기반 자동 가드 적용
    await applyMetaGuards(to, from, next)
  } catch (error) {
    console.error('라우터 가드 오류:', error)
    next({ name: 'home' })
  }
})

// 네비게이션 완료 후 처리
router.afterEach((to, from) => {
  // 페이지 제목 설정
  if (to.meta.title) {
    document.title = `${to.meta.title} | AI 활용법 학습 튜터`
  }
  
  // 로딩 해제 (필요시)
  // store.commit('setLoading', false)
  
  // 페이지 조회 로그 (필요시)
  console.log(`페이지 이동: ${from.name || 'unknown'} → ${to.name}`)
})

// 네비게이션 에러 처리
router.onError((error) => {
  console.error('라우터 에러:', error)
  
  // 에러 페이지로 리다이렉트 또는 알림 표시
  if (error.message.includes('ChunkLoadError')) {
    // 청크 로딩 실패 시 새로고침 권장
    if (confirm('앱 업데이트가 있습니다. 페이지를 새로고침하시겠습니까?')) {
      window.location.reload()
    }
  }
})

export default router