// frontend/src/services/diagnosisService.js
// 진단 관련 API 호출 서비스

import api from './api.js'
import { useAuthStore } from '../stores/authStore.js' // 추가

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
    
    // 유형 선택 후 authStore 업데이트 - 추가된 부분
    if (response.data.success) {
      const authStore = useAuthStore()
      authStore.updateDiagnosisStatus(selectedType)
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