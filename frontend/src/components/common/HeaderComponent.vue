<!-- frontend/src/components/common/HeaderComponent.vue -->
<template>
  <header class="header-component">
    <div class="container">
      <div class="header-content">
        <!-- 로고 영역 -->
        <div class="logo-section">
          <router-link to="/" class="logo-link">
            <i class="fas fa-robot logo-icon"></i>
            <span class="logo-text">AI 활용법 학습 튜터</span>
          </router-link>
        </div>

        <!-- 네비게이션 영역 -->
        <nav class="navigation">
          <router-link to="/" class="nav-link">홈</router-link>
          <router-link to="/about" class="nav-link">소개</router-link>
          <template v-if="isAuthenticated">
            <router-link to="/diagnosis" class="nav-link">진단하기</router-link>
            <router-link to="/dashboard" class="nav-link">대시보드</router-link>
            <router-link to="/learning" class="nav-link">학습하기</router-link>
          </template>
          <template v-else>
            <router-link to="/diagnosis" class="nav-link">진단하기</router-link>
          </template>
        </nav>

        <!-- 사용자 메뉴 영역 -->
        <div class="user-menu">
          <div v-if="isAuthenticated" class="user-info">
            <span class="user-name">{{ userName }}</span>
            <button @click="handleLogout" class="logout-btn">로그아웃</button>
          </div>
          <div v-else class="auth-buttons">
            <router-link to="/login" class="btn btn-primary">로그인</router-link>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

// 라우터 및 스토어 설정
const router = useRouter()
const authStore = useAuthStore()

// 계산된 속성
const isAuthenticated = computed(() => authStore.isAuthenticated)
const userName = computed(() => {
  // 초기화가 완료되지 않았거나 로딩 중이면 기본값 표시
  if (!authStore.isInitialized || authStore.isLoading) {
    return '로딩 중...'
  }
  // 인증되었지만 사용자 정보가 없으면 기본값
  return authStore.user?.username || authStore.user?.login_id || '사용자'
})

// 로그아웃 처리
const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/')
  } catch (error) {
    console.error('로그아웃 실패:', error)
    // 에러가 발생해도 홈으로 이동
    router.push('/')
  }
}
</script>

<style lang="scss" scoped>
.header-component {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0;
  }

  .logo-section {
    .logo-link {
      display: flex;
      align-items: center;
      text-decoration: none;
      color: white;

      .logo-icon {
        font-size: 1.8rem;
        margin-right: 0.5rem;
        color: #3498db;
      }

      .logo-text {
        font-size: 1.5rem;
        font-weight: bold;
      }
    }
  }

  .navigation {
    display: flex;
    gap: 1.5rem;

    .nav-link {
      color: white;
      text-decoration: none;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      transition: all 0.3s;
      font-weight: 500;

      &:hover {
        background-color: rgba(255, 255, 255, 0.1);
        transform: translateY(-1px);
      }

      &.router-link-active {
        background-color: rgba(255, 255, 255, 0.2);
        font-weight: 600;
      }
    }
  }

  .user-menu {
    .user-info {
      display: flex;
      align-items: center;
      gap: 1rem;
      color: white;

      .user-name {
        font-weight: 500;
      }

      .logout-btn {
        background: none;
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background-color: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.5);
        }
      }
    }

    .auth-buttons {
      display: flex;
      gap: 0.5rem;

      .btn {
        padding: 0.5rem 1rem;
        border-radius: 4px;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.2s;

        &.btn-outline {
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.3);

          &:hover {
            background-color: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.5);
          }
        }

        &.btn-primary {
          background-color: #3498db;
          color: white;
          border: 1px solid #3498db;

          &:hover {
            background-color: #2980b9;
            border-color: #2980b9;
          }
        }
      }
    }
  }
}

// 반응형 디자인
@media (max-width: 768px) {
  .header-component {
    .navigation {
      display: none;
    }

    .user-menu {
      .auth-buttons {
        flex-direction: column;
        gap: 0.25rem;

        .btn {
          padding: 0.25rem 0.75rem;
          font-size: 0.875rem;
        }
      }
    }
  }
}
</style>