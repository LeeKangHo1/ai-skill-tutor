<!-- frontend/src/components/diagnosis/ProgressBar.vue -->
<template>
  <div class="progress-bar-container">
    <!-- 진행률 헤더 -->
    <div class="progress-header">
      <div class="progress-info">
        <span class="progress-label">{{ label }}</span>
        <span class="progress-percentage">{{ Math.round(percentage) }}%</span>
      </div>
      <div v-if="showSteps" class="progress-steps">
        {{ currentStep }} / {{ totalSteps }}
      </div>
    </div>

    <!-- 진행률 바 -->
    <div class="progress-bar" :class="{ 'animated': animated }">
      <div 
        class="progress-fill" 
        :class="[
          `progress-${variant}`,
          { 'progress-striped': striped }
        ]"
        :style="{ width: `${percentage}%` }"
      >
        <!-- 스트라이프 애니메이션 -->
        <div v-if="striped" class="progress-stripes"></div>
      </div>
    </div>

    <!-- 단계별 마커 (선택적) -->
    <div v-if="showMarkers && markers.length > 0" class="progress-markers">
      <div
        v-for="(marker, index) in markers"
        :key="index"
        class="marker"
        :class="{ 
          'completed': marker.percentage <= percentage,
          'current': marker.percentage > percentage && index === currentMarkerIndex
        }"
        :style="{ left: `${marker.percentage}%` }"
        :title="marker.label"
      >
        <div class="marker-dot"></div>
        <div class="marker-label">{{ marker.label }}</div>
      </div>
    </div>

    <!-- 상세 정보 (선택적) -->
    <div v-if="showDetails" class="progress-details">
      <div class="detail-item">
        <span class="detail-label">완료:</span>
        <span class="detail-value">{{ completedItems }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">남은 시간:</span>
        <span class="detail-value">{{ estimatedTime }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

// Props 정의
const props = defineProps({
  // 진행률 (0-100)
  percentage: {
    type: Number,
    required: true,
    validator: (value) => value >= 0 && value <= 100
  },
  // 진행률 바 라벨
  label: {
    type: String,
    default: '진행률'
  },
  // 현재 단계
  currentStep: {
    type: Number,
    default: 0
  },
  // 전체 단계 수
  totalSteps: {
    type: Number,
    default: 0
  },
  // 단계 표시 여부
  showSteps: {
    type: Boolean,
    default: true
  },
  // 진행률 바 색상 변형
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  // 애니메이션 효과
  animated: {
    type: Boolean,
    default: true
  },
  // 스트라이프 패턴
  striped: {
    type: Boolean,
    default: false
  },
  // 마커 표시 여부
  showMarkers: {
    type: Boolean,
    default: false
  },
  // 마커 데이터
  markers: {
    type: Array,
    default: () => []
  },
  // 상세 정보 표시 여부
  showDetails: {
    type: Boolean,
    default: false
  },
  // 완료된 항목 수
  completedItems: {
    type: Number,
    default: 0
  },
  // 예상 소요 시간
  estimatedTime: {
    type: String,
    default: ''
  },
  // 크기
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
})

// 이벤트 정의
const emit = defineEmits(['progress-change', 'step-change', 'complete'])

// 반응형 데이터
const previousPercentage = ref(props.percentage)

// 계산된 속성
const currentMarkerIndex = computed(() => {
  return props.markers.findIndex(marker => marker.percentage > props.percentage)
})

const isComplete = computed(() => props.percentage >= 100)

// 진행률 변경 감지
watch(() => props.percentage, (newPercentage, oldPercentage) => {
  previousPercentage.value = oldPercentage
  
  emit('progress-change', {
    current: newPercentage,
    previous: oldPercentage,
    isComplete: newPercentage >= 100
  })

  // 완료 이벤트
  if (newPercentage >= 100 && oldPercentage < 100) {
    emit('complete')
  }
})

// 단계 변경 감지
watch(() => props.currentStep, (newStep, oldStep) => {
  emit('step-change', {
    current: newStep,
    previous: oldStep,
    total: props.totalSteps
  })
})
</script>

<style lang="scss" scoped>
.progress-bar-container {
  width: 100%;

  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;

    .progress-info {
      display: flex;
      align-items: center;
      gap: 0.5rem;

      .progress-label {
        font-weight: 500;
        color: var(--text-primary);
      }

      .progress-percentage {
        font-weight: 600;
        color: var(--primary-color);
        font-size: 0.875rem;
      }
    }

    .progress-steps {
      font-size: 0.875rem;
      color: var(--text-secondary);
      font-weight: 500;
    }
  }

  .progress-bar {
    width: 100%;
    background-color: #e9ecef;
    border-radius: 8px;
    overflow: hidden;
    position: relative;

    // 크기별 높이
    &.size-small { height: 6px; }
    &.size-medium { height: 10px; }
    &.size-large { height: 16px; }

    // 기본 크기
    height: 10px;

    .progress-fill {
      height: 100%;
      border-radius: 8px;
      position: relative;
      overflow: hidden;
      transition: width 0.6s ease;

      // 색상 변형
      &.progress-primary {
        background: linear-gradient(90deg, var(--primary-color), var(--primary-color-light));
      }

      &.progress-success {
        background: linear-gradient(90deg, #10b981, #34d399);
      }

      &.progress-warning {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
      }

      &.progress-danger {
        background: linear-gradient(90deg, #ef4444, #f87171);
      }

      &.progress-info {
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
      }

      // 스트라이프 패턴
      &.progress-striped {
        .progress-stripes {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-image: repeating-linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.1),
            rgba(255, 255, 255, 0.1) 10px,
            transparent 10px,
            transparent 20px
          );
          animation: progress-stripes 1s linear infinite;
        }
      }
    }

    &.animated .progress-fill {
      animation: progress-glow 2s ease-in-out infinite alternate;
    }
  }

  .progress-markers {
    position: relative;
    height: 20px;
    margin-top: 0.5rem;

    .marker {
      position: absolute;
      transform: translateX(-50%);
      display: flex;
      flex-direction: column;
      align-items: center;

      .marker-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: var(--border-color);
        border: 2px solid white;
        transition: all 0.3s ease;
      }

      .marker-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
        white-space: nowrap;
        font-weight: 500;
      }

      &.completed {
        .marker-dot {
          background-color: var(--primary-color);
        }

        .marker-label {
          color: var(--primary-color);
        }
      }

      &.current {
        .marker-dot {
          background-color: var(--warning-color);
          animation: pulse 2s infinite;
        }

        .marker-label {
          color: var(--warning-color);
          font-weight: 600;
        }
      }
    }
  }

  .progress-details {
    display: flex;
    justify-content: space-between;
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--border-light);

    .detail-item {
      display: flex;
      align-items: center;
      gap: 0.25rem;

      .detail-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
      }

      .detail-value {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-primary);
      }
    }
  }
}

// 애니메이션
@keyframes progress-stripes {
  0% { background-position: 0 0; }
  100% { background-position: 40px 0; }
}

@keyframes progress-glow {
  0% { box-shadow: 0 0 5px rgba(var(--primary-color-rgb), 0.5); }
  100% { box-shadow: 0 0 20px rgba(var(--primary-color-rgb), 0.8); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

// 반응형 디자인
@media (max-width: 480px) {
  .progress-bar-container {
    .progress-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.25rem;

      .progress-info {
        width: 100%;
        justify-content: space-between;
      }
    }

    .progress-details {
      flex-direction: column;
      gap: 0.5rem;

      .detail-item {
        justify-content: space-between;
      }
    }

    .progress-markers {
      .marker {
        .marker-label {
          font-size: 0.6875rem;
        }
      }
    }
  }
}
</style>