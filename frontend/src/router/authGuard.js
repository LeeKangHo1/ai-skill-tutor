// src/router/authGuard.js

/**
 * Vue Router 인증 가드
 * - 인증 필수 페이지 보호
 * - 진단 완료 여부 확인
 * - 사용자 유형별 접근 제어
 * - 자동 리다이렉트 처리
 */

import { useAuthStore } from '../stores/authStore'

/**
 * 인증이 필요한 라우트 보호
 */
export const requireAuth = async (to, from, next) => {
  const authStore = useAuthStore()
  
  try {
    // 인증 상태 초기화 (앱 시작 시 토큰 확인)
    if (!authStore.isInitialized) {
      await authStore.initialize()
    }
    
    if (authStore.isAuthenticated) {
      next()
    } else {
      // 인증되지 않은 경우 로그인 페이지로 리다이렉트
      next({
        name: 'login',
        query: { redirect: to.fullPath }
      })
    }
  } catch (error) {
    console.error('인증 가드 오류:', error)
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
  }
}

/**
 * 진단 완료가 필요한 라우트 보호
 */
export const requireDiagnosis = async (to, from, next) => {
  const authStore = useAuthStore()
  
  try {
    // 먼저 인증 확인
    if (!authStore.isInitialized) {
      await authStore.initialize()
    }
    
    if (!authStore.isAuthenticated) {
      next({
        name: 'login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    if (authStore.isDiagnosisCompleted) {
      next()
    } else {
      // 진단이 완료되지 않은 경우 진단 페이지로 리다이렉트
      next({ name: 'diagnosis' })
    }
  } catch (error) {
    console.error('진단 가드 오류:', error)
    next({ name: 'diagnosis' })
  }
}

/**
 * 특정 사용자 유형만 접근 가능한 라우트 보호
 */
export const requireUserType = (requiredType) => {
  return async (to, from, next) => {
    const authStore = useAuthStore()
    
    try {
      // 먼저 인증 및 진단 확인
      if (!authStore.isInitialized) {
        await authStore.initialize()
      }
      
      const permission = authStore.checkPermission(requiredType, true)
      
      if (permission.allowed) {
        next()
      } else {
        switch (permission.reason) {
          case 'NOT_AUTHENTICATED':
            next({
              name: 'login',
              query: { redirect: to.fullPath }
            })
            break
          case 'DIAGNOSIS_NOT_COMPLETED':
            next({ name: 'diagnosis' })
            break
          case 'INSUFFICIENT_USER_TYPE':
            next({
              name: 'dashboard',
              query: { error: 'access_denied' }
            })
            break
          default:
            next({ name: 'dashboard' })
        }
      }
    } catch (error) {
      console.error('사용자 유형 가드 오류:', error)
      next({ name: 'dashboard' })
    }
  }
}

/**
 * 게스트 전용 라우트 보호 (로그인된 사용자는 접근 불가)
 */
export const requireGuest = async (to, from, next) => {
  const authStore = useAuthStore()
  
  try {
    if (!authStore.isInitialized) {
      await authStore.initialize()
    }
    
    if (!authStore.isAuthenticated) {
      next()
    } else {
      // 이미 로그인된 경우 대시보드로 리다이렉트
      if (authStore.isDiagnosisCompleted) {
        next({ name: 'dashboard' })
      } else {
        next({ name: 'diagnosis' })
      }
    }
  } catch (error) {
    console.error('게스트 가드 오류:', error)
    next()
  }
}

/**
 * 선택적 인증 (로그인하지 않아도 접근 가능하지만 인증 상태는 확인)
 */
export const optionalAuth = async (to, from, next) => {
  const authStore = useAuthStore()
  
  try {
    if (!authStore.isInitialized) {
      await authStore.initialize()
    }
    next()
  } catch (error) {
    console.error('선택적 인증 가드 오류:', error)
    next()
  }
}

/**
 * 학습 접근 가드 (인증 + 진단 완료 + 챕터 접근 권한)
 */
export const requireLearningAccess = (requiredChapter = null) => {
  return async (to, from, next) => {
    const authStore = useAuthStore()
    
    try {
      if (!authStore.isInitialized) {
        await authStore.initialize()
      }
      
      // 기본 권한 확인
      const permission = authStore.checkPermission(null, true)
      
      if (!permission.allowed) {
        switch (permission.reason) {
          case 'NOT_AUTHENTICATED':
            next({
              name: 'login',
              query: { redirect: to.fullPath }
            })
            break
          case 'DIAGNOSIS_NOT_COMPLETED':
            next({ name: 'diagnosis' })
            break
          default:
            next({ name: 'dashboard' })
        }
        return
      }
      
      // 특정 챕터 접근 권한 확인
      if (requiredChapter) {
        const currentChapter = authStore.currentChapter
        
        if (requiredChapter > currentChapter) {
          next({
            name: 'dashboard',
            query: { 
              error: 'chapter_locked',
              required: requiredChapter,
              current: currentChapter
            }
          })
          return
        }
      }
      
      next()
    } catch (error) {
      console.error('학습 접근 가드 오류:', error)
      next({ name: 'dashboard' })
    }
  }
}

/**
 * 관리자 전용 가드 (향후 확장용)
 */
export const requireAdmin = async (to, from, next) => {
  const authStore = useAuthStore()
  
  try {
    if (!authStore.isInitialized) {
      await authStore.initialize()
    }
    
    // 현재는 user_type으로 관리자 구분이 없으므로 기본 구현
    const permission = authStore.checkPermission('advanced', true)
    
    if (permission.allowed) {
      next()
    } else {
      next({
        name: 'dashboard',
        query: { error: 'admin_required' }
      })
    }
  } catch (error) {
    console.error('관리자 가드 오류:', error)
    next({ name: 'dashboard' })
  }
}

/**
 * 복합 가드 생성 함수 (여러 가드를 조합)
 */
export const createGuard = (...guards) => {
  return async (to, from, next) => {
    let currentIndex = 0
    
    const runNextGuard = async () => {
      if (currentIndex >= guards.length) {
        next()
        return
      }
      
      const guard = guards[currentIndex++]
      
      await guard(to, from, (result) => {
        if (result === undefined || result === true) {
          // 가드 통과, 다음 가드 실행
          runNextGuard()
        } else {
          // 가드 실패, 리다이렉트
          next(result)
        }
      })
    }
    
    await runNextGuard()
  }
}

/**
 * 라우트 메타 정보 기반 자동 가드 적용
 */
export const applyMetaGuards = async (to, from, next) => {
  const authStore = useAuthStore()
  const meta = to.meta || {}
  
  try {
    // 초기화
    if (!authStore.isInitialized) {
      await authStore.initialize()
    }
    
    // 게스트 전용
    if (meta.requireGuest) {
      return requireGuest(to, from, next)
    }
    
    // 인증 필요
    if (meta.requireAuth) {
      const permission = authStore.checkPermission(
        meta.requiredUserType, 
        meta.requireDiagnosis !== false
      )
      
      if (!permission.allowed) {
        switch (permission.reason) {
          case 'NOT_AUTHENTICATED':
            return next({
              name: 'login',
              query: { redirect: to.fullPath }
            })
          case 'DIAGNOSIS_NOT_COMPLETED':
            return next({ name: 'diagnosis' })
          case 'INSUFFICIENT_USER_TYPE':
            return next({
              name: 'dashboard',
              query: { error: 'access_denied' }
            })
        }
      }
    }
    
    // 챕터 접근 권한
    if (meta.requiredChapter) {
      const currentChapter = authStore.currentChapter
      if (meta.requiredChapter > currentChapter) {
        return next({
          name: 'dashboard',
          query: { 
            error: 'chapter_locked',
            required: meta.requiredChapter,
            current: currentChapter
          }
        })
      }
    }
    
    next()
  } catch (error) {
    console.error('메타 가드 오류:', error)
    next({ name: 'dashboard' })
  }
}