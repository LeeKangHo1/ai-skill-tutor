<!-- frontend/src/components/learning/TheoryContent.vue -->
<template>
  <div class="theory-content content-active"
    :class="{ 'content-hidden': !isVisible }">





    <!-- 제목 -->
    <h3 class="theory-title">{{ theoryData.title || '🧠 LLM(Large Language Model)이란?' }}</h3>

    <!-- 섹션들 -->
    <div v-if="theoryData.sections" class="theory-sections">
      <div v-for="(section, index) in theoryData.sections" :key="index" class="theory-section"
        :class="`section-${section.type}`">

        <!-- 소개 섹션 -->
        <div v-if="section.type === 'introduction'" class="introduction-section">
          <p class="introduction-text">{{ section.content }}</p>
        </div>

        <!-- 정의 섹션 -->
        <div v-else-if="section.type === 'definition'" class="definition-section">
          <h4 v-if="section.title" class="section-title">{{ section.title }}</h4>
          <p class="definition-content">{{ section.content }}</p>

          <!-- 비유 설명 -->
          <div v-if="section.analogy" class="analogy-box">
            <h5 class="analogy-title">💡 쉬운 비유</h5>
            <div class="analogy-content">
              <p><strong>{{ section.analogy.concept }}</strong>는 <strong>{{ section.analogy.comparison }}</strong>와
                같아요!</p>
              <ul v-if="section.analogy.details" class="analogy-details">
                <li v-for="(detail, idx) in section.analogy.details" :key="idx">{{ detail }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 예시 섹션 -->
        <div v-else-if="section.type === 'examples'" class="examples-section">
          <h4 v-if="section.title" class="section-title">{{ section.title }}</h4>
          <div v-if="section.items" class="examples-grid">
            <div v-for="(item, idx) in section.items" :key="idx" class="example-item">
              <h5 class="example-category">{{ item.category }}</h5>
              <p class="example-description">{{ item.description }}</p>
              <div class="example-benefit">
                <span class="benefit-label">💡 효과:</span>
                <span class="benefit-text">{{ item.benefit }}</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 폴백: 기존 형태의 데이터인 경우 -->
    <div v-else class="theory-body">
      <div class="theory-description">{{ theoryData.description || theoryData.content }}</div>
    </div>

  </div>
</template>

<script setup>
import { defineProps } from 'vue'

// Props 정의
const props = defineProps({
  theoryData: {
    type: Object,
    required: true,
    default: () => ({
      title: '',
      content: '',
      sections: []
    })
  },
  isVisible: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
/* 이론 컨텐츠 스타일 */
.theory-content {
  background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
  border-left: 4px solid #2196f3;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

/* 새로운 JSON 구조 스타일 */

.theory-title {
  font-size: 1.4rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.theory-sections {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.theory-section {
  border-radius: 0.375rem;
  padding: 1rem;
}

/* 소개 섹션 */
.section-introduction {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(33, 150, 243, 0.2);
}

.introduction-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #495057;
  margin: 0;
}

/* 정의 섹션 */
.section-definition {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(33, 150, 243, 0.3);
}

.section-title {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.definition-content {
  font-size: 1rem;
  line-height: 1.6;
  color: #495057;
  margin-bottom: 1rem;
}

.analogy-box {
  background: linear-gradient(135deg, #fff9c4, #f0f4c3);
  border: 1px solid #dce775;
  border-radius: 0.375rem;
  padding: 1rem;
  margin-top: 1rem;
}

.analogy-title {
  font-size: 1rem;
  color: #558b2f;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.analogy-content p {
  margin-bottom: 0.5rem;
  color: #33691e;
}

.analogy-details {
  list-style: none;
  padding-left: 0;
  margin: 0.5rem 0 0 0;
}

.analogy-details li {
  background: rgba(255, 255, 255, 0.7);
  padding: 0.25rem 0.5rem;
  margin-bottom: 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.9rem;
  color: #33691e;
}

/* 예시 섹션 */
.section-examples {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(33, 150, 243, 0.3);
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.example-item {
  background: linear-gradient(135deg, #e8f5e8, #f1f8e9);
  border: 1px solid #c8e6c9;
  border-radius: 0.375rem;
  padding: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.example-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.example-category {
  font-size: 1.1rem;
  color: #2e7d32;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.example-description {
  color: #424242;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.example-benefit {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.benefit-label {
  color: #558b2f;
  font-weight: 500;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.benefit-text {
  color: #33691e;
  font-size: 0.9rem;
  line-height: 1.4;
}

.theory-body {
  line-height: 1.6;
}

.theory-description {
  font-size: 1rem;
  line-height: 1.6;
  color: #495057;
}

/* 컨텐츠 표시/숨김 */
.content-active {
  display: block;
  animation: fadeIn 0.3s ease-in;
}

.content-hidden {
  display: none;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 데스크톱 전용 - 모바일/태블릿 대응 제거 */
</style>