<!-- frontend/src/components/dashboard/ChapterCard.vue -->
<!-- 챕터 카드 컴포넌트 - 개별 챕터 정보 및 섹션 목록 표시 -->

<template>
  <div
    class="chapter-card"
    :class="[
      `status-${chapter.status}`,
      { 'current': isCurrent }
    ]"
  >
    <div class="chapter-header">
      <div class="chapter-info">
        <div class="chapter-number">
          <span class="chapter-icon">{{ chapter.status_icon }}</span>
          <span class="chapter-text">{{ chapter.chapter_number }}챕터</span>
        </div>
        <h3 class="chapter-title">{{ chapter.chapter_title }}</h3>
      </div>
      <div class="chapter-status">
        <span class="status-badge" :class="`badge-${chapter.status}`">
          {{ getStatusText(chapter.status) }}
        </span>
        <div v-if="chapter.formatted_completion_date" class="completion-date">
          <i class="fas fa-calendar-check"></i>
          {{ chapter.formatted_completion_date }}
        </div>
      </div>
    </div>

    <div v-if="chapter.sections && chapter.sections.length > 0" class="section-list">
      <div
        v-for="section in chapter.sections"
        :key="`${chapter.chapter_number}-${section.section_number}`"
        class="section-item"
        :class="[
          `status-${section.status}`,
          {
            'current': isCurrent && section.section_number === currentSection
          }
        ]"
      >
        <div class="section-info">
          <span class="section-icon">{{ section.status_icon }}</span>
          <span class="section-title">{{ section.section_title }}</span>
        </div>
        <div v-if="section.formatted_completion_date" class="section-date">
          {{ section.formatted_completion_date }}
        </div>
      </div>
    </div>

    <div v-if="showActionButton" class="chapter-actions">
      <button
        @click="handleStartLearning"
        class="btn btn-primary start-learning-btn"
      >
        <i class="fas fa-play"></i>
        학습 계속하기
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChapterCard',
  
  props: {
    chapter: {
      type: Object,
      required: true
    },
    isCurrent: {
      type: Boolean,
      default: false
    },
    currentSection: {
      type: Number,
      default: 1
    },
    showActionButton: {
      type: Boolean,
      default: true
    }
  },

  emits: ['start-learning'],

  setup(props, { emit }) {
    const getStatusText = (status) => {
      const statusMap = {
        'completed': '완료',
        'in_progress': '진행중',
        'available': '시작 가능',
        'locked': '잠김'
      }
      return statusMap[status] || '알 수 없음'
    }

    const handleStartLearning = () => {
      emit('start-learning')
    }

    return {
      getStatusText,
      handleStartLearning
    }
  }
}
</script>

<style lang="scss" scoped>
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chapter-card {
  background: $white;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba($black, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  animation: fadeInUp 0.5s ease-out;

  &:nth-child(2) { 
    animation-delay: 0.1s; 
  }
  
  &:nth-child(3) { 
    animation-delay: 0.2s; 
  }
  
  &:nth-child(4) { 
    animation-delay: 0.3s; 
  }
  
  &.current {
    border-left-color: $brand-purple;
    box-shadow: 0 8px 30px rgba($brand-purple, 0.15);
  }
  
  &.status-completed { 
    border-left-color: $success; 
  }
  
  &.status-in_progress { 
    border-left-color: $warning; 
  }
  
  &.status-locked { 
    opacity: 0.6; 
  }

  .chapter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid $gray-200;
  }

  .chapter-info {
    flex: 1;
  }

  .chapter-number {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .chapter-icon {
    font-size: 1.25rem;
  }

  .chapter-text {
    font-size: 0.875rem;
    font-weight: 600;
    color: $secondary;
    text-transform: uppercase;
  }

  .chapter-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: $text-dark;
    margin: 0;
  }

  .chapter-status {
    text-align: right;
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: $border-radius-pill;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    
    &.badge-completed { 
      background: lighten($success, 35%); 
      color: darken($success, 20%); 
    }
    
    &.badge-in_progress { 
      background: lighten($warning, 25%); 
      color: darken($warning, 30%); 
    }
    
    &.badge-available { 
      background: lighten($primary, 40%); 
      color: darken($primary, 15%); 
    }
    
    &.badge-locked { 
      background: $gray-100; 
      color: $secondary; 
    }
  }

  .completion-date {
    font-size: 0.75rem;
    color: $secondary;
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }
}

// 섹션 리스트
.section-list {
  padding: 1rem 1.5rem;
  background: $gray-100;
  border-bottom: 1px solid $gray-200;

  .section-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid $gray-200;

    &:last-child {
      border-bottom: none;
    }

    &.current {
      background: rgba($brand-purple, 0.1);
      margin: 0 -0.5rem;
      padding: 0.5rem;
      border-radius: $border-radius-lg;
    }
  }

  .section-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
  }

  .section-icon {
    font-size: 0.875rem;
  }

  .section-title {
    font-size: 0.875rem;
    color: $gray-700;
  }

  .section-date {
    font-size: 0.75rem;
    color: $secondary;
  }
}

// 챕터 액션
.chapter-actions {
  padding: 1.5rem;

  .start-learning-btn {
    width: 100%;
    padding: 0.75rem 1rem;
    border-radius: $border-radius-lg;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    background: $brand-purple;
    border: 1px solid $brand-purple;
    color: $white;

    &:hover:not(:disabled) {
      background: darken($brand-purple, 10%);
      border-color: darken($brand-purple, 10%);
    }
  }
}
</style>