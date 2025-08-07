// frontend/src/composables/useNotification.js
// 알림 관련 컴포저블 - 성공, 에러, 정보 메시지 등의 사용자 알림을 담당

import { ref, computed } from 'vue'

// 알림 타입 상수
const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
}

// 전역 알림 상태
const notifications = ref([])
let notificationId = 0

export function useNotification() {
  
  // 새 알림 추가
  const addNotification = (message, type = NOTIFICATION_TYPES.INFO, options = {}) => {
    const {
      duration = 5000, // 기본 5초 후 자동 제거
      persistent = false, // 수동으로만 제거 가능
      action = null // 액션 버튼 (예: 재시도)
    } = options

    const notification = {
      id: ++notificationId,
      message,
      type,
      timestamp: new Date(),
      persistent,
      action
    }

    notifications.value.push(notification)

    // 자동 제거 설정 (persistent가 아닌 경우)
    if (!persistent && duration > 0) {
      setTimeout(() => {
        removeNotification(notification.id)
      }, duration)
    }

    return notification.id
  }

  // 알림 제거
  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  // 모든 알림 제거
  const clearAllNotifications = () => {
    notifications.value = []
  }

  // 특정 타입의 알림만 제거
  const clearNotificationsByType = (type) => {
    notifications.value = notifications.value.filter(n => n.type !== type)
  }

  // 성공 메시지 표시
  const showSuccess = (message, options = {}) => {
    return addNotification(message, NOTIFICATION_TYPES.SUCCESS, {
      duration: 3000,
      ...options
    })
  }

  // 에러 메시지 표시
  const showError = (message, options = {}) => {
    return addNotification(message, NOTIFICATION_TYPES.ERROR, {
      duration: 7000, // 에러는 조금 더 오래 표시
      ...options
    })
  }

  // 경고 메시지 표시
  const showWarning = (message, options = {}) => {
    return addNotification(message, NOTIFICATION_TYPES.WARNING, {
      duration: 5000,
      ...options
    })
  }

  // 정보 메시지 표시
  const showInfo = (message, options = {}) => {
    return addNotification(message, NOTIFICATION_TYPES.INFO, {
      duration: 4000,
      ...options
    })
  }

  // 확인 대화상자 (간단한 구현)
  const showConfirm = (message, onConfirm, onCancel = null) => {
    return addNotification(message, NOTIFICATION_TYPES.WARNING, {
      persistent: true,
      action: {
        confirm: {
          text: '확인',
          handler: () => {
            if (onConfirm) onConfirm()
          }
        },
        cancel: {
          text: '취소',
          handler: () => {
            if (onCancel) onCancel()
          }
        }
      }
    })
  }

  // 로딩 메시지 표시 (수동 제거 필요)
  const showLoading = (message = '처리 중...') => {
    return addNotification(message, NOTIFICATION_TYPES.INFO, {
      persistent: true
    })
  }

  // API 에러 처리 헬퍼
  const handleApiError = (error, customMessage = null) => {
    let message = customMessage

    if (!message) {
      if (error.response) {
        // 서버 응답이 있는 경우
        const status = error.response.status
        const data = error.response.data

        switch (status) {
          case 400:
            message = data.message || '잘못된 요청입니다.'
            break
          case 401:
            message = '인증이 필요합니다. 다시 로그인해주세요.'
            break
          case 403:
            message = '접근 권한이 없습니다.'
            break
          case 404:
            message = '요청한 리소스를 찾을 수 없습니다.'
            break
          case 500:
            message = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
            break
          default:
            message = data.message || `오류가 발생했습니다. (${status})`
        }
      } else if (error.request) {
        // 네트워크 오류
        message = '네트워크 연결을 확인해주세요.'
      } else {
        // 기타 오류
        message = error.message || '알 수 없는 오류가 발생했습니다.'
      }
    }

    return showError(message)
  }

  // 계산된 속성
  const hasNotifications = computed(() => notifications.value.length > 0)
  const notificationCount = computed(() => notifications.value.length)
  const latestNotification = computed(() => 
    notifications.value.length > 0 ? notifications.value[notifications.value.length - 1] : null
  )

  return {
    // 상태
    notifications: computed(() => notifications.value),
    hasNotifications,
    notificationCount,
    latestNotification,

    // 기본 메서드
    addNotification,
    removeNotification,
    clearAllNotifications,
    clearNotificationsByType,

    // 편의 메서드
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showConfirm,
    showLoading,
    handleApiError,

    // 상수
    NOTIFICATION_TYPES
  }
}