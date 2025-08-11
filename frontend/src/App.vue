<!-- frontend/src/App.vue -->
<!-- AI 활용법 학습 튜터 루트 컴포넌트 -->

<script setup>
import { RouterView } from 'vue-router'
import { ref, onMounted } from 'vue'
import { apiService } from './services/api.js'
import { useAuthStore } from './stores/authStore.js'
import HeaderComponent from './components/common/HeaderComponent.vue'

// 백엔드 연결 상태 관리
const backendStatus = ref({
  isConnected: false,
  isLoading: true,
  message: '',
  lastChecked: null
})

// 백엔드 연결 상태 확인 함수
const checkBackendConnection = async () => {
  backendStatus.value.isLoading = true
  
  try {
    const result = await apiService.checkConnection()
    
    if (result.success) {
      backendStatus.value.isConnected = true
      backendStatus.value.message = result.data || 'Backend connected successfully'
    } else {
      backendStatus.value.isConnected = false
      backendStatus.value.message = `Connection failed: ${result.error}`
    }
  } catch (error) {
    backendStatus.value.isConnected = false
    backendStatus.value.message = `Unexpected error: ${error.message}`
  } finally {
    backendStatus.value.isLoading = false
    backendStatus.value.lastChecked = new Date().toLocaleTimeString('ko-KR')
  }
}

// 컴포넌트 마운트 시 초기화
onMounted(async () => {
  // 인증 스토어 초기화
  const authStore = useAuthStore()
  try {
    await authStore.initialize()
  } catch (error) {
    console.error('인증 초기화 실패:', error)
  }
  
  // 백엔드 연결 확인
  checkBackendConnection()
})
</script>

<template>
  <div id="app">
    <!-- 헤더 컴포넌트 사용 -->
    <HeaderComponent />

    <!-- 백엔드 연결 상태 표시 -->
    <div class="connection-status" :class="{ 
      'status-connected': backendStatus.isConnected && !backendStatus.isLoading,
      'status-disconnected': !backendStatus.isConnected && !backendStatus.isLoading,
      'status-loading': backendStatus.isLoading 
    }">
      <div class="container">
        <div class="status-content">
          <div class="status-indicator">
            <span v-if="backendStatus.isLoading" class="status-icon loading">⟳</span>
            <span v-else-if="backendStatus.isConnected" class="status-icon connected">●</span>
            <span v-else class="status-icon disconnected">●</span>
          </div>
          <div class="status-text">
            <span v-if="backendStatus.isLoading">백엔드 연결 확인 중...</span>
            <span v-else-if="backendStatus.isConnected">
              백엔드 연결됨: {{ backendStatus.message }}
            </span>
            <span v-else>
              백엔드 연결 실패: {{ backendStatus.message }}
            </span>
          </div>
          <div class="status-actions">
            <button 
              @click="checkBackendConnection" 
              :disabled="backendStatus.isLoading"
              class="refresh-btn"
            >
              {{ backendStatus.isLoading ? '확인 중...' : '다시 확인' }}
            </button>
            <span v-if="backendStatus.lastChecked" class="last-checked">
              마지막 확인: {{ backendStatus.lastChecked }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 메인 콘텐츠 영역 -->
    <main class="app-main">
      <div class="container">
        <RouterView />
      </div>
    </main>

    <!-- 푸터 영역 -->
    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2025 AI 활용법 학습 튜터 - 포트폴리오 프로젝트</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 전체 앱 레이아웃 */
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 헤더 스타일은 HeaderComponent에서 처리 */

/* 백엔드 연결 상태 스타일 */
.connection-status {
  padding: 0.75rem 0;
  border-bottom: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.status-connected {
  background-color: #d4edda;
  border-color: #c3e6cb;
}

.status-disconnected {
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

.status-loading {
  background-color: #fff3cd;
  border-color: #ffeaa7;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
}

.status-indicator {
  display: flex;
  align-items: center;
}

.status-icon {
  font-size: 1rem;
  font-weight: bold;
}

.status-icon.connected {
  color: #28a745;
}

.status-icon.disconnected {
  color: #dc3545;
}

.status-icon.loading {
  color: #ffc107;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-text {
  flex: 1;
  font-weight: 500;
}

.status-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.refresh-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #0056b3;
  transform: translateY(-1px);
}

.refresh-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  transform: none;
}

.last-checked {
  font-size: 0.8rem;
  color: #6c757d;
  font-style: italic;
}

/* 메인 콘텐츠 스타일 */
.app-main {
  flex: 1;
  padding: 2rem 0;
  background-color: #f8f9fa;
  min-height: calc(100vh - 180px);
}

/* 푸터 스타일 */
.app-footer {
  background-color: #34495e;
  color: white;
  text-align: center;
  padding: 1.5rem 0;
  margin-top: auto;
}

.app-footer p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .container {
    padding: 0 15px;
  }
  
  .app-main {
    padding: 1.5rem 0;
  }

  .status-content {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }

  .status-actions {
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .app-main {
    padding: 1rem 0;
  }

  .status-content {
    font-size: 0.8rem;
  }

  .refresh-btn {
    padding: 0.3rem 0.6rem;
    font-size: 0.7rem;
  }

  .last-checked {
    font-size: 0.7rem;
  }
}
</style>