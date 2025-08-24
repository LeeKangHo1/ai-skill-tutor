// src/services/api.js

/**
 * HTTP 인터셉터가 포함된 API 클라이언트 (HttpOnly 쿠키 방식)
 * - 자동 토큰 첨부
 * - 쿠키 자동 전송 (refresh_token)
 * - 토큰 만료 시 자동 갱신
 * - 인증 실패 시 자동 처리
 */

import axios from 'axios'
import tokenManager from '../utils/tokenManager'

// Base URL 설정
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // 30초로 증가 (AI 응답 생성 시간 고려)
  withCredentials: true, // HttpOnly 쿠키 자동 전송 활성화
  headers: {
    'Content-Type': 'application/json'
  }
})

// 토큰 갱신 중복 호출 방지를 위한 플래그
let isRefreshing = false
let failedQueue = []

/**
 * 대기 중인 요청들을 처리하는 헬퍼 함수
 */
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  
  failedQueue = []
}

/**
 * 요청 인터셉터
 * - 모든 요청에 자동으로 Authorization 헤더 추가
 */
apiClient.interceptors.request.use(
  (config) => {
    const accessToken = tokenManager.getAccessToken()
    
    // 토큰이 있으면 헤더에 추가
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    
    console.log(`API 요청: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API 요청 에러:', error)
    return Promise.reject(error)
  }
)

/**
 * 응답 인터셉터
 * - 토큰 만료 시 자동 갱신 (HttpOnly 쿠키 사용)
 * - 인증 실패 시 자동 로그아웃
 */
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API 응답: ${response.status} ${response.config.url}`)
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // 401 에러 (인증 실패) 처리
    if (error.response?.status === 401 && !originalRequest._retry) {
      
      // 이미 토큰 갱신 중인 경우
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return apiClient(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // 토큰 갱신 시도 (refresh_token은 쿠키로 자동 전송됨)
        const response = await axios.post(`${BASE_URL}/auth/refresh`, {}, {
          withCredentials: true // 쿠키 전송 활성화
        })

        if (response.data.success && response.data.data) {
          const { access_token } = response.data.data
          
          // 새 Access Token 저장
          tokenManager.setAccessToken(access_token)

          // 대기 중인 요청들 처리
          processQueue(null, access_token)

          // 원래 요청 재시도
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } else {
          throw new Error('Token refresh failed')
        }
        
      } catch (refreshError) {
        // 토큰 갱신 실패 - 로그아웃 처리
        processQueue(refreshError, null)
        
        // 토큰 정리
        tokenManager.clearAll()
        
        // 로그인 페이지로 리다이렉트 (Vue Router를 통해)
        if (window.location.pathname !== '/login') {
          window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname)
        }
        
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // 403 에러 (권한 없음) 처리
    if (error.response?.status === 403) {
      const errorData = error.response.data
      
      // 진단 미완료 에러인 경우
      if (errorData?.error?.code === 'DIAGNOSIS_NOT_COMPLETED') {
        window.location.href = '/diagnosis'
        return Promise.reject(error)
      }
      
      // 기타 권한 오류
      console.error('권한이 없습니다:', errorData?.error?.message)
    }

    console.error('API 응답 에러:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API 서비스 함수들
export const apiService = {
  // 백엔드 연결 상태 확인 (기본 API 정보)
  async checkConnection() {
    try {
      const response = await apiClient.get('/system/version')
      return {
        success: true,
        data: response.data?.data || 'Connected successfully',
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

/**
 * API 연결 테스트
 */
export const testConnection = async () => {
  try {
    const response = await apiClient.get('/system/health')
    return {
      connected: true,
      data: response.data
    }
  } catch (error) {
    console.error('API 연결 실패:', error.message)
    return {
      connected: false,
      error: error.message
    }
  }
}

/**
 * 파일 업로드용 API 인스턴스
 */
export const createUploadAPI = () => {
  return axios.create({
    baseURL: BASE_URL,
    timeout: 30000, // 파일 업로드는 타임아웃을 길게
    withCredentials: true, // 쿠키 전송 활성화
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 디버그 모드에서 추가 로깅
 */
if (import.meta.env.MODE === 'development') {
  console.log('API 클라이언트 초기화 완료')
  console.log('Base URL:', BASE_URL)
  console.log('쿠키 전송 활성화: withCredentials = true')
}

// 기본 export
export default apiClient