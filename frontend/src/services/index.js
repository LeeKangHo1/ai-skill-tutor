// frontend/src/services/index.js
// 모든 서비스를 통합하여 export하는 인덱스 파일

// 기본 API 클라이언트
export { default as apiClient } from './api.js'
export { apiService } from './api.js'

// 도메인별 서비스들
export { authService } from './authService.js'
export { learningService } from './learningService.js'
export { dashboardService } from './dashboardService.js'
export { diagnosisService } from './diagnosisService.js'

// 기본 export (가장 많이 사용될 것으로 예상되는 서비스들)
export default {
  api: apiClient,
  auth: authService,
  learning: learningService,
  dashboard: dashboardService,
  diagnosis: diagnosisService
}