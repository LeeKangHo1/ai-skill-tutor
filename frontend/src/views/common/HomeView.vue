<!-- frontend/src/views/HomeView.vue -->
<!-- AI 활용법 학습 튜터 홈 페이지 -->

<script setup>
import { ref, onMounted } from 'vue'

// 백엔드 연결 상태 확인용 반응형 데이터
const backendStatus = ref('연결 확인 중...')
const isConnected = ref(false)

// 컴포넌트 마운트 시 백엔드 연결 테스트
onMounted(async () => {
  try {
    // 추후 Axios를 사용하여 백엔드 API 호출 예정
    // const response = await axios.get('http://localhost:5000/')
    // 현재는 기본 메시지만 표시
    backendStatus.value = '백엔드 연결 준비 완료'
    isConnected.value = true
  } catch (error) {
    backendStatus.value = '백엔드 연결 실패'
    isConnected.value = false
  }
})
</script>

<template>
  <div class="home-view">
    <!-- 메인 헤더 섹션 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">AI 활용법 학습 튜터</h1>
        <p class="hero-subtitle">
          AI 입문자를 위한 맞춤형 학습 플랫폼
        </p>
        <p class="hero-description">
          개인화된 학습 경험을 통해 AI 활용 능력을 체계적으로 향상시켜보세요.
        </p>
        <div class="hero-actions">
          <button class="btn btn-primary">학습 시작하기</button>
          <button class="btn btn-secondary">더 알아보기</button>
        </div>
      </div>
    </section>

    <!-- 시스템 상태 섹션 -->
    <section class="status-section">
      <div class="status-card">
        <h3>시스템 상태</h3>
        <div class="status-item">
          <span class="status-label">백엔드 연결:</span>
          <span :class="['status-value', isConnected ? 'connected' : 'disconnected']">
            {{ backendStatus }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">프론트엔드:</span>
          <span class="status-value connected">정상 동작</span>
        </div>
      </div>
    </section>

    <!-- 기능 소개 섹션 -->
    <section class="features-section">
      <h2>주요 기능</h2>
      <div class="features-grid">
        <div class="feature-card">
          <h3>개인화된 학습</h3>
          <p>사용자의 수준에 맞는 맞춤형 학습 콘텐츠를 제공합니다.</p>
        </div>
        <div class="feature-card">
          <h3>실시간 피드백</h3>
          <p>학습 과정에서 즉시 피드백을 받아 효과적으로 학습할 수 있습니다.</p>
        </div>
        <div class="feature-card">
          <h3>진도 관리</h3>
          <p>학습 진도를 체계적으로 관리하고 성취도를 확인할 수 있습니다.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-view {
  max-width: 100%;
}

/* 히어로 섹션 */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4rem 2rem;
  text-align: center;
  margin: -2rem -20px 2rem -20px;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  opacity: 0.9;
}

.hero-description {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  opacity: 0.8;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #28a745;
  color: white;
}

.btn-primary:hover {
  background-color: #218838;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background-color: white;
  color: #667eea;
}

/* 상태 섹션 */
.status-section {
  margin: 2rem 0;
}

.status-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.status-card h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.status-label {
  font-weight: 500;
  color: #6c757d;
}

.status-value {
  font-weight: 600;
}

.status-value.connected {
  color: #28a745;
}

.status-value.disconnected {
  color: #dc3545;
}

/* 기능 섹션 */
.features-section {
  margin: 3rem 0;
}

.features-section h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #2c3e50;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #6c757d;
  line-height: 1.6;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1.2rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 200px;
  }
  
  .status-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>