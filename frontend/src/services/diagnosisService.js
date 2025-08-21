// frontend/src/services/diagnosisService.js
// 진단 관련 API 호출 서비스

import api from './api.js'

/**
 * 진단 문항 조회
 */
export const getDiagnosisQuestions = async () => {
  try {
    const response = await api.get('/diagnosis/questions')
    return response.data
  } catch (error) {
    console.error('진단 문항 조회 실패:', error)
    throw error
  }
}

/**
 * 진단 결과 제출
 * @param {Array} answers - 답변 배열 [{ question_id: 1, answer: "value" }]
 */
export const submitDiagnosisAnswers = async (answers) => {
  try {
    const response = await api.post('/diagnosis/submit', { answers })
    return response.data
  } catch (error) {
    console.error('진단 결과 제출 실패:', error)
    throw error
  }
}

/**
 * 사용자 유형 선택
 * @param {string} selectedType - 선택한 유형 ('beginner' | 'advanced')
 */
export const selectUserType = async (selectedType) => {
  try {
    const response = await api.post('/diagnosis/select-type', {
      selected_type: selectedType
    })

    // 유형 선택 후 새로운 토큰 처리 및 authStore 업데이트
    if (response.data.success) {
      // 새로운 access_token이 있으면 저장하고 사용자 정보 업데이트
      if (response.data.data.access_token) {
        const { default: tokenManager } = await import('../utils/tokenManager.js')
        tokenManager.setAccessToken(response.data.data.access_token)

        // 동적으로 authStore를 가져와서 사용자 상태 업데이트
        const { useAuthStore } = await import('../stores/authStore.js')
        const authStore = useAuthStore()
        authStore.updateUserFromToken(response.data.data.access_token)
      } else {
        // 토큰이 없는 경우 기존 방식으로 업데이트
        const { useAuthStore } = await import('../stores/authStore.js')
        const authStore = useAuthStore()
        authStore.updateDiagnosisStatus(selectedType)
      }
    }

    return response.data
  } catch (error) {
    console.error('사용자 유형 선택 실패:', error)
    throw error
  }
}

export default {
  getDiagnosisQuestions,
  submitDiagnosisAnswers,
  selectUserType
}