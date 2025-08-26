<!-- frontend/src/App.vue -->
<!-- AI 활용법 학습 튜터 루트 컴포넌트 -->

<template>
  <div id="app">
    <HeaderComponent />

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

    <main class="app-main">
      <div class="container">
        <RouterView />
      </div>
    </main>

    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2025 AI 활용법 학습 튜터</p>
      </div>
    </footer>
  </div>
</template>

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

<style lang="scss" scoped>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

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

// 백엔드 연결 상태
.connection-status {
  padding: 0.75rem 0;
  border-bottom: 1px solid $gray-200;
  transition: all 0.3s ease;

  &.status-connected {
    background-color: lighten($success, 40%);
    border-color: lighten($success, 30%);
  }
  &.status-disconnected {
    background-color: lighten($danger, 35%);
    border-color: lighten($danger, 30%);
  }
  &.status-loading {
    background-color: lighten($warning, 30%);
    border-color: lighten($warning, 20%);
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

    &.connected { color: $success; }
    &.disconnected { color: $danger; }
    &.loading {
      color: $warning;
      animation: spin 1s linear infinite;
    }
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
    background-color: $primary;
    color: $white;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.3s;

    &:hover:not(:disabled) {
      background-color: darken($primary, 10%);
      transform: translateY(-1px);
    }

    &:disabled {
      background-color: $secondary;
      cursor: not-allowed;
      transform: none;
    }
  }

  .last-checked {
    font-size: 0.8rem;
    color: $secondary;
    font-style: italic;
  }
}

// 메인 콘텐츠
.app-main {
  flex: 1;
  padding: 2rem 0;
  background-color: $gray-100;
  min-height: calc(100vh - 180px);
}

// 푸터
.app-footer {
  background-color: $header-gradient-end;
  color: $white;
  text-align: center;
  padding: 1.5rem 0;
  margin-top: auto;

  p {
    margin: 0;
    font-size: 0.9rem;
    opacity: 0.8;
  }
}
</style>