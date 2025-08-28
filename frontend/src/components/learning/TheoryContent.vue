<!-- frontend/src/components/learning/TheoryContent.vue -->
<template>
  <div v-if="theoryData" class="theory-content content-active">
    
    <h3 class="theory-title">{{ theoryData.title || theoryData.content?.title }}</h3>

    <!-- API 응답 구조: theoryData.content.sections 경로로 sections 접근 -->
    <div v-if="theoryData.content?.sections" class="theory-sections">
      <div v-for="(section, index) in theoryData.content.sections" :key="index" class="theory-section" :class="`section-${section.type}`">

        <div v-if="section.type === 'introduction'" class="introduction-section">
          <p class="introduction-text">{{ section.content }}</p>
        </div>

        <div v-else-if="section.type === 'definition'" class="definition-section">
          <h4 v-if="section.title" class="section-title">{{ section.title }}</h4>
          <p class="definition-content">{{ section.content }}</p>

          <div v-if="section.analogy" class="analogy-box">
            <h5 class="analogy-title">💡 쉬운 비유</h5>
            <div class="analogy-content">
              <p><strong>{{ section.analogy.concept }}</strong>는 <strong>{{ section.analogy.comparison }}</strong>와 같아요!</p>
              <ul v-if="section.analogy.details" class="analogy-details">
                <li v-for="(detail, idx) in section.analogy.details" :key="idx">{{ detail }}</li>
              </ul>
            </div>
          </div>
        </div>

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

    <!-- sections가 없을 때 fallback - 단순 텍스트 표시 -->
    <div v-else class="theory-body">
      <div class="theory-description">{{ theoryData.description || theoryData.content || '이론 내용을 불러오는 중입니다.' }}</div>
    </div>

  </div>

  <!-- 이론 데이터가 없을 때 로딩 메시지 표시 -->
  <div v-else class="loading-state">
    <div class="loading-content">
      <div class="loading-icon">📚</div>
      <h3>이론 내용을 준비하고 있습니다...</h3>
      <p>잠시만 기다려주세요.</p>
    </div>
  </div>
</template>

<script setup>
import { watch } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

// --- Store 직접 연결 ---
const learningStore = useLearningStore()
// 분리된 theoryData를 직접 구독
const { theoryData } = storeToRefs(learningStore)

console.log('[TheoryContent] 🟢 컴포넌트 초기화. Store의 theoryData와 연결되었습니다.')

// 디버깅용 감시자
watch(theoryData, (newData) => {
  if (newData) {
    console.log('[TheoryContent] 📄 이론 데이터가 변경되어 화면을 다시 그립니다.', newData)
  } else {
    console.log('[TheoryContent] ⏳ 이론 데이터가 없어 로딩 상태를 표시합니다.')
  }
}, { immediate: true })
</script>

<style lang="scss" scoped>
.theory-content {
  background: linear-gradient(135deg, lighten($primary, 40%), lighten($brand-purple, 40%));
  border-left: 4px solid $primary;
  padding: $spacing-lg;
  border-radius: $border-radius-lg;
  margin-bottom: $spacing-md;
}
.theory-title {
  font-size: $font-size-lg * 1.1; /* 1.4rem */
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

/* 로딩 상태 스타일 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  background: linear-gradient(135deg, lighten($primary, 50%), lighten($brand-purple, 50%));
  border: 1px solid rgba($primary, 0.2);
  border-radius: $border-radius-lg;
  padding: $spacing-lg * 2;
}

.loading-content {
  text-align: center;
  color: darken($primary, 10%);
}

.loading-icon {
  font-size: 3rem;
  margin-bottom: $spacing-md;
  animation: pulse 2s infinite;
}

.loading-state h3 {
  margin: 0 0 $spacing-sm 0;
  font-size: $font-size-lg;
  color: darken($primary, 15%);
}

.loading-state p {
  margin: 0;
  font-size: $font-size-base;
  color: darken($primary, 10%);
  opacity: 0.8;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.7; }
}

.content-active {
  display: block;
  animation: fadeIn 0.3s ease-in;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>