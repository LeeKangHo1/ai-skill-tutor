<!-- frontend/src/views/AboutView.vue -->
<!-- AI 활용법 학습 튜터 소개 페이지 -->

<template>
  <div class="about-view">
    <!-- 프로젝트 소개 섹션 -->
    <section class="intro-section">
      <div class="intro-content">
        <h1 class="page-title">AI 활용법 학습 튜터 소개</h1>
        <p class="page-subtitle">
          개인화된 AI 학습 경험을 제공하는 혁신적인 교육 플랫폼
        </p>
      </div>
    </section>

    <!-- 프로젝트 정보 섹션 -->
    <section class="project-info">
      <div class="info-grid">
        <div class="info-card">
          <h3>프로젝트 목적</h3>
          <p>
            AI 입문자들이 체계적이고 효과적으로 AI 활용 능력을 학습할 수 있도록 
            개인화된 학습 경험을 제공하는 것이 목표입니다.
          </p>
        </div>

        <div class="info-card">
          <h3>기술 스택</h3>
          <ul>
            <li><strong>백엔드:</strong> Python Flask, MySQL, LangChain</li>
            <li><strong>프론트엔드:</strong> Vue 3, Pinia, Vite</li>
            <li><strong>AI:</strong> LangGraph, ChromaDB</li>
          </ul>
        </div>

        <div class="info-card">
          <h3>주요 특징</h3>
          <ul>
            <li>멀티에이전트 시스템 기반 개인화 학습</li>
            <li>실시간 피드백 및 평가</li>
            <li>사용자 수준별 맞춤 콘텐츠</li>
            <li>체계적인 진도 관리</li>
          </ul>
        </div>

        <div class="info-card">
          <h3>개발 정보</h3>
          <p>
            <strong>개발 목적:</strong> 입사 포트폴리오용 MVP 프로젝트<br>
            <strong>개발 기간:</strong> 2025년 1월 ~ 진행중<br>
            <strong>개발 환경:</strong> 로컬 개발 환경 기반
          </p>
        </div>
      </div>
    </section>

    <!-- 학습 플로우 섹션 -->
    <section class="learning-flow">
      <h2>학습 플로우</h2>
      <div class="flow-steps">
        <div class="step">
          <div class="step-number">1</div>
          <h4>사용자 진단</h4>
          <p>AI 활용 수준을 파악하여 개인화된 학습 경로를 설정합니다.</p>
        </div>
        
        <div class="step">
          <div class="step-number">2</div>
          <h4>챕터 학습</h4>
          <p>체계적으로 구성된 챕터별 학습을 통해 단계적으로 실력을 향상시킵니다.</p>
        </div>
        
        <div class="step">
          <div class="step-number">3</div>
          <h4>실시간 피드백</h4>
          <p>AI 튜터가 실시간으로 피드백을 제공하여 효과적인 학습을 지원합니다.</p>
        </div>
        
        <div class="step">
          <div class="step-number">4</div>
          <h4>진도 관리</h4>
          <p>학습 진도와 성취도를 체계적으로 관리하고 추적합니다.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.about-view {
  max-width: 100%;
}

/* 소개 섹션 */
.intro-section {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: white;
  padding: 4rem 2rem;
  text-align: center;
  margin: -2rem -20px 3rem -20px;
}

.intro-content {
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.page-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  line-height: 1.6;
}

/* 프로젝트 정보 섹션 */
.project-info {
  margin: 3rem 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.info-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.info-card:hover {
  transform: translateY(-5px);
}

.info-card h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.info-card p {
  color: #6c757d;
  line-height: 1.6;
  margin-bottom: 0;
}

.info-card ul {
  color: #6c757d;
  line-height: 1.8;
  padding-left: 1.2rem;
}

.info-card li {
  margin-bottom: 0.5rem;
}

/* 학습 플로우 섹션 */
.learning-flow {
  margin: 4rem 0;
}

.learning-flow h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 3rem;
  font-size: 2rem;
}

.flow-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.step {
  text-align: center;
  padding: 2rem 1rem;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 auto 1rem auto;
}

.step h4 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.step p {
  color: #6c757d;
  line-height: 1.6;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .flow-steps {
    grid-template-columns: 1fr;
  }
  
  .intro-section {
    padding: 2rem 1rem;
  }
}
</style>