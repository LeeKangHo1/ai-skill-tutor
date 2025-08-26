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

<style lang="scss" scoped>
/* 이론 컨텐츠 스타일 */
.theory-content {
  background: linear-gradient(135deg, lighten($primary, 40%), lighten($brand-purple, 40%));
  border-left: 4px solid $primary;
  padding: $spacing-lg;
  border-radius: $border-radius-lg;
  margin-bottom: $spacing-md;
}

/* 새로운 JSON 구조 스타일 */

.theory-title {
  font-size: $font-size-lg * 1.1; // 1.4rem
  color: $text-dark;
  margin-bottom: $spacing-lg;
  font-weight: 600;
}

.theory-sections {
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

.theory-section {
  border-radius: $border-radius;
  padding: $spacing-md;
}

/* 소개 섹션 */
.section-introduction {
  background: rgba($white, 0.8);
  border: 1px solid rgba($primary, 0.2);
}

.introduction-text {
  font-size: $font-size-base * 1.1;
  line-height: 1.6;
  color: $gray-700;
  margin: 0;
}

/* 정의 섹션 */
.section-definition {
  background: rgba($white, 0.9);
  border: 1px solid rgba($primary, 0.3);
}

.section-title {
  font-size: $font-size-lg;
  color: $text-dark;
  margin-bottom: $spacing-md * 0.75;
  font-weight: 600;
}

.definition-content {
  font-size: $font-size-base;
  line-height: 1.6;
  color: $gray-700;
  margin-bottom: $spacing-md;
}

.analogy-box {
  background: linear-gradient(135deg, lighten($warning, 45%), lighten($success, 50%));
  border: 1px solid lighten($success, 30%);
  border-radius: $border-radius;
  padding: $spacing-md;
  margin-top: $spacing-md;
}

.analogy-title {
  font-size: $font-size-base;
  color: darken($success, 5%);
  margin-bottom: $spacing-sm;
  font-weight: 600;
}

.analogy-content p {
  margin-bottom: $spacing-sm;
  color: darken($success, 20%);
}

.analogy-details {
  list-style: none;
  padding-left: 0;
  margin: $spacing-sm 0 0 0;
}

.analogy-details li {
  background: rgba($white, 0.7);
  padding: $spacing-xs $spacing-sm;
  margin-bottom: $spacing-xs;
  border-radius: $border-radius-sm;
  font-size: $font-size-sm;
  color: darken($success, 20%);
}

/* 예시 섹션 */
.section-examples {
  background: rgba($white, 0.9);
  border: 1px solid rgba($primary, 0.3);
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: $spacing-md;
  margin-top: $spacing-md;
}

.example-item {
  background: linear-gradient(135deg, lighten($success, 55%), lighten($success, 50%));
  border: 1px solid lighten($success, 40%);
  border-radius: $border-radius;
  padding: $spacing-md;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.example-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba($black, 0.1);
}

.example-category {
  font-size: $font-size-base * 1.1;
  color: darken($success, 15%);
  margin-bottom: $spacing-sm;
  font-weight: 600;
}

.example-description {
  color: $gray-800;
  line-height: 1.5;
  margin-bottom: $spacing-md * 0.75;
}

.example-benefit {
  display: flex;
  align-items: flex-start;
  gap: $spacing-sm;
}

.benefit-label {
  color: darken($success, 5%);
  font-weight: 500;
  font-size: $font-size-sm;
  flex-shrink: 0;
}

.benefit-text {
  color: darken($success, 20%);
  font-size: $font-size-sm;
  line-height: 1.4;
}

.theory-body {
  line-height: 1.6;
}

.theory-description {
  font-size: $font-size-base;
  line-height: 1.6;
  color: $gray-700;
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
</style>