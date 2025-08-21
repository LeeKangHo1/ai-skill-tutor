<!-- frontend/src/components/dashboard/ChapterSection.vue -->
<!-- 챕터 섹션 컴포넌트 - 챕터 목록 관리 및 표시 -->

<template>
  <div class="chapter-section">
    <div class="section-header">
      <h2 class="section-title">
        <i class="fas fa-list"></i>
        챕터별 학습 현황
      </h2>
      <div class="section-controls">
        <div class="chapter-summary">
          <span class="summary-item completed">
            <i class="fas fa-check-circle"></i>
            완료: {{ completedCount }}개
          </span>
          <span class="summary-item total">
            <i class="fas fa-book"></i>
            전체: {{ totalCount }}개
          </span>
        </div>
        <button
          @click="toggleChapterList"
          class="toggle-btn"
          :class="{ 'expanded': isExpanded }"
        >
          <i class="fas fa-chevron-down"></i>
          {{ isExpanded ? '접기' : '펼치기' }}
        </button>
      </div>
    </div>

    <div class="chapter-list">
      <ChapterCard
        v-for="chapter in currentChapterList"
        :key="chapter.chapter_number"
        :chapter="chapter"
        :is-current="chapter.chapter_number === currentChapter"
        :current-section="currentSection"
        :show-action-button="true"
        @start-learning="$emit('start-learning')"
      />

      <Transition name="chapter-expand">
        <div v-show="isExpanded" class="expanded-chapters">
          <ChapterCard
            v-for="chapter in otherChapterList"
            :key="chapter.chapter_number"
            :chapter="chapter"
            :is-current="chapter.chapter_number === currentChapter"
            :current-section="currentSection"
            :show-action-button="false"
            @start-learning="$emit('start-learning')"
          />
        </div>
      </Transition>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import ChapterCard from './ChapterCard.vue'

export default {
  name: 'ChapterSection',
  
  components: {
    ChapterCard
  },

  props: {
    chapterStatus: {
      type: Array,
      default: () => []
    },
    currentChapter: {
      type: Number,
      required: true
    },
    currentSection: {
      type: Number,
      required: true
    },
    completedCount: {
      type: Number,
      default: 0
    },
    totalCount: {
      type: Number,
      default: 0
    }
  },

  emits: ['start-learning'],

  setup(props) {
    const isExpanded = ref(false)

    // 현재 챕터만 필터링
    const currentChapterList = computed(() => {
      if (!props.chapterStatus || !Array.isArray(props.chapterStatus)) return []
      return props.chapterStatus.filter(chapter => 
        parseInt(chapter.chapter_number) === parseInt(props.currentChapter)
      )
    })

    // 다른 챕터들 필터링
    const otherChapterList = computed(() => {
      if (!props.chapterStatus || !Array.isArray(props.chapterStatus)) return []
      return props.chapterStatus.filter(chapter => 
        parseInt(chapter.chapter_number) !== parseInt(props.currentChapter)
      )
    })

    const toggleChapterList = () => {
      isExpanded.value = !isExpanded.value
    }

    return {
      isExpanded,
      currentChapterList,
      otherChapterList,
      toggleChapterList
    }
  }
}
</script>

<style lang="scss" scoped>
// 챕터 섹션
.chapter-section {
  margin-bottom: 3rem;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: $text-dark;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .section-controls {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .chapter-summary {
    display: flex;
    gap: 1rem;

    .summary-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.875rem;
      font-weight: 500;
      
      &.completed { 
        color: $success; 
      }
      
      &.total { 
        color: $secondary; 
      }
    }
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: $gray-100;
    border: 1px solid $gray-200;
    border-radius: $border-radius-lg;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: $gray-700;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: $gray-200;
      border-color: $gray-300;
    }

    i {
      transition: transform 0.3s ease;
    }

    &.expanded i {
      transform: rotate(180deg);
    }
  }
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  .expanded-chapters {
    margin-top: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.0rem;
  }
}

// 챕터 목록 펼치기/접기 애니메이션
.chapter-expand-enter-active,
.chapter-expand-leave-active {
  transition: all 0.4s ease;
  max-height: 2000px;
  overflow: hidden;
}

.chapter-expand-enter-from,
.chapter-expand-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}
</style>