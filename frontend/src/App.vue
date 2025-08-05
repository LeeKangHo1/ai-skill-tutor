<!-- frontend/src/App.vue -->
<!-- AI 활용법 학습 튜터 루트 컴포넌트 -->

<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <!-- 헤더 영역 -->
    <header class="app-header">
      <div class="container">
        <div class="header-content">
          <h1 class="app-title">
            <router-link to="/" class="title-link">
              AI 활용법 학습 튜터
            </router-link>
          </h1>
          <nav class="app-nav">
            <router-link to="/" class="nav-link">홈</router-link>
            <router-link to="/about" class="nav-link">소개</router-link>
          </nav>
        </div>
      </div>
    </header>

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

/* 헤더 스타일 */
.app-header {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
}

.title-link {
  color: white;
  text-decoration: none;
  transition: opacity 0.3s;
}

.title-link:hover {
  opacity: 0.8;
}

.app-nav {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s;
  font-weight: 500;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

/* 메인 콘텐츠 스타일 */
.app-main {
  flex: 1;
  padding: 2rem 0;
  background-color: #f8f9fa;
  min-height: calc(100vh - 140px);
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
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .app-title {
    font-size: 1.3rem;
  }
  
  .app-nav {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .container {
    padding: 0 15px;
  }
  
  .app-main {
    padding: 1.5rem 0;
  }
}

@media (max-width: 480px) {
  .app-title {
    font-size: 1.1rem;
  }
  
  .nav-link {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .app-main {
    padding: 1rem 0;
  }
}
</style>