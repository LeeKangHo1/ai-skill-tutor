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
// import DashboardPage from '../views/dashboard/DashboardPage.vue'
// import LearningPage from '../views/learning/LearningPage.vue'

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

  
  // ================== 향후 구현 예정 (주석 처리) ==================
  
  // 대시보드 (인증 + 진단 완료 필요)
  // {
  //   path: '/dashboard',
  //   name: 'dashboard',
  //   component: DashboardPage,
  //   beforeEnter: requireDiagnosis,
  //   meta: {
  //     title: '대시보드',
  //     description: '학습 현황 대시보드',
  //     requireAuth: true,
  //     requireDiagnosis: true
  //   }
  // },

  // 학습 진행 페이지 (인증 + 진단 완료 필요)
  // {
  //   path: '/learning',
  //   name: 'learning',
  //   component: LearningPage,
  //   beforeEnter: requireDiagnosis,
  //   meta: {
  //     title: '학습 진행',
  //     description: '학습 세션 진행',
  //     requireAuth: true,
  //     requireDiagnosis: true
  //   }
  // },

  // 특정 챕터 학습 (챕터별 접근 권한)
  // {
  //   path: '/learning/chapter/:chapterNumber',
  //   name: 'learning-chapter',
  //   component: LearningPage,
  //   beforeEnter: (to, from, next) => {
  //     const chapterNumber = parseInt(to.params.chapterNumber)
  //     return requireLearningAccess(chapterNumber)(to, from, next)
  //   },
  //   meta: {
  //     title: '챕터 학습',
  //     description: '특정 챕터 학습',
  //     requireAuth: true,
  //     requireDiagnosis: true
  //   }
  // },

  // AI 입문자 전용 페이지 (향후 구현)
  /*
  {
    path: '/beginner',
    name: 'beginner-content',
    component: () => import('../views/BeginnerContentPage.vue'),
    beforeEnter: requireUserType('beginner'),
    meta: {
      title: 'AI 입문자 콘텐츠',
      description: 'AI 입문자 전용 콘텐츠',
      requireAuth: true,
      requireDiagnosis: true,
      requiredUserType: 'beginner'
    }
  },
  */

  // 실무 응용형 전용 페이지 (향후 구현)
  /*
  {
    path: '/advanced',
    name: 'advanced-content',
    component: () => import('../views/AdvancedContentPage.vue'),
    beforeEnter: requireUserType('advanced'),
    meta: {
      title: '실무 응용형 콘텐츠',
      description: '실무 응용형 전용 콘텐츠',
      requireAuth: true,
      requireDiagnosis: true,
      requiredUserType: 'advanced'
    }
  },
  */

  // 프로필 페이지 (향후 구현)
  /*
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfilePage.vue'),
    beforeEnter: requireAuth,
    meta: {
      title: '프로필',
      description: '사용자 프로필 관리',
      requireAuth: true,
      requireDiagnosis: false
    }
  },
  */

  // 설정 페이지 (향후 구현)
  /*
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/SettingsPage.vue'),
    beforeEnter: requireAuth,
    meta: {
      title: '설정',
      description: '계정 설정',
      requireAuth: true,
      requireDiagnosis: false
    }
  },
  */

  // 404 에러 페이지 (향후 구현)
  /*
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundPage.vue'),
    meta: {
      title: '페이지를 찾을 수 없음',
      description: '404 에러'
    }
  }
  */
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