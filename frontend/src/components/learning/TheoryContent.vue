<!-- frontend/src/components/learning/TheoryContent.vue -->
<template>
  <div v-if="theoryData" class="theory-content content-active">
    
    <h3 class="theory-title">{{ theoryData.title }}</h3>

    <div v-if="theoryData.sections" class="theory-sections">
      <div v-for="(section, index) in theoryData.sections" :key="index" class="theory-section" :class="`section-${section.type}`">

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

    <div v-else class="theory-body">
      <div class="theory-description">{{ theoryData.description || theoryData.content }}</div>
    </div>

  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import { storeToRefs } from 'pinia'

// --- Store 직접 연결 ---
const learningStore = useLearningStore()
const { mainContent } = storeToRefs(learningStore)

console.log('[TheoryContent] 🟢 컴포넌트 초기화. Store와 연결되었습니다.')

// --- Store 상태 기반 Computed 속성 ---
const theoryData = computed(() => {
  // store의 mainContent 상태가 'theory' 타입이고, 내부에 데이터가 있을 때만 값을 반환합니다.
  if (mainContent.value?.type === 'theory' && mainContent.value?.data) {
    // [수정] API 응답 형식에 맞춰 중첩된 content 객체를 바라보도록 수정
    const contentPayload = mainContent.value.data.content
    if (contentPayload && contentPayload.sections) {
      console.log('[TheoryContent] 🧠 이론 데이터를 Store에서 가져옵니다 (중첩 구조).', contentPayload)
      return contentPayload
    }
  }
  
  // 조건에 맞지 않으면 null을 반환하여 템플릿 렌더링을 막습니다.
  console.log('[TheoryContent] ⚠️ 현재 컨텐츠가 이론 타입이 아니거나 데이터가 없습니다.')
  return null
})

// 디버깅용 감시자
watch(theoryData, (newData) => {
  if (newData) {
    console.log('[TheoryContent] 🔄 이론 데이터가 변경되어 화면을 다시 그립니다.')
  }
})
</script>

<style lang="scss" scoped>
/* 스타일은 변경되지 않았으므로 그대로 유지합니다. */
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
.content-active {
  display: block;
  animation: fadeIn 0.3s ease-in;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>