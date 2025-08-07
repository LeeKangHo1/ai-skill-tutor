// frontend/src/services/api.js
// 백엔드 API 호출을 위한 Axios 설정 및 서비스 함수

import axios from 'axios'

// API 베이스 URL 설정 (환경변수에서 가져옴)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10초 타임아웃
  headers: {
    'Content-Type': 'application/json',
  }
})

// 요청 인터셉터 (필요시 인증 토큰 추가 등)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API 요청: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API 요청 에러:', error)
    return Promise.reject(error)
  }
)

// 응답 인터셉터 (에러 처리 등)
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API 응답: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API 응답 에러:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API 서비스 함수들
export const apiService = {
  // 백엔드 연결 상태 확인 (기본 API 정보)
  async checkConnection() {
    try {
      const response = await apiClient.get('/system/')
      return {
        success: true,
        data: response.data?.message || 'Connected successfully',
        status: response.status
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
        status: error.response?.status || 0
      }
    }
  },

  // 헬스 체크 (서버 상태 확인)
  async healthCheck() {
    try {
      const response = await apiClient.get('/system/health')
      return {
        success: true,
        data: response.data,
        status: response.status
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
        status: error.response?.status || 0
      }
    }
  }
}

// 기본 export
export default apiClient