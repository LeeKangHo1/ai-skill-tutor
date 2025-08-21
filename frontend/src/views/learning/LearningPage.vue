<!-- frontend/src/views/learning/LearningPage.vue -->
<!-- 학습 진행 페이지 (임시) -->

<template>
  <div class="learning-page">
    <div class="container">
      <h1>학습 진행 페이지</h1>
      <p>이 페이지는 현재 개발 중입니다.</p>
      <router-link to="/dashboard">대시보드로 돌아가기</router-link>
    </div>
  </div>
</template>

<script setup>
// 이 페이지의 로직은 향후 구현될 예정입니다.
import { RouterLink } from 'vue-router';
</script>

<style lang="scss" scoped>
.learning-page {
  padding: 4rem 0;
  text-align: center;

  .container {
    max-width: 800px;
    margin: 0 auto;
  }

  h1 {
    font-size: 2.5rem;
    color: $text-dark;
    margin-bottom: 1rem;
  }

  p {
    font-size: 1.2rem;
    color: $secondary;
    margin-bottom: 2rem;
  }

  a {
    color: $primary;
    text-decoration: none;
    font-weight: 500;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
