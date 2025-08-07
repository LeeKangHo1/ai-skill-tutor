<!-- frontend/src/components/diagnosis/ProgressBar.vue -->
<!-- 진단 진행률 표시 컴포넌트 -->

<template>
  <div class="progress-container">
    <!-- 진행률 텍스트 -->
    <div class="progress-text">
      <span class="current">{{ currentStep }}</span>
      <span class="separator">/</span>
      <span class="total">{{ totalSteps }}</span>
      <span class="percentage">({{ percentage }}%)</span>
    </div>
    
    <!-- 진행률 바 -->
    <div class="progress-bar">
      <div 
        class="progress-fill" 
        :style="{ width: percentage + '%' }"
      ></div>
    </div>
    
    <!-- 단계별 점 표시 -->
    <div class="progress-dots" v-if="showDots">
      <div 
        v-for="(step, index) in totalSteps" 
        :key="index"
        class="dot"
        :class="{
          'completed': index < currentStep,
          'current': index === currentStep - 1,
          'pending': index >= currentStep
        }"
        @click="$emit('goToStep', index)"
      >
        {{ index + 1 }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  
  props: {
    // 현재 단계 (1부터 시작)
    currentStep: {
      type: Number,
      required: true,
      default: 1
    },
    
    // 전체 단계 수
    totalSteps: {
      type: Number,
      required: true,
      default: 1
    },
    
    // 단계별 점 표시 여부
    showDots: {
      type: Boolean,
      default: true
    }
  },
  
  emits: ['goToStep'],
  
  computed: {
    // 진행률 계산
    percentage() {
      if (this.totalSteps === 0) return 0
      return Math.round((this.currentStep / this.totalSteps) * 100)
    }
  }
}
</script>

<style scoped lang="scss">
.progress-container {
  margin: 1rem 0;
  
  .progress-text {
    text-align: center;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: #666;
    
    .current {
      font-weight: bold;
      color: #007bff;
    }
    
    .separator {
      margin: 0 0.25rem;
    }
    
    .percentage {
      margin-left: 0.5rem;
      font-size: 0.85rem;
    }
  }
  
  .progress-bar {
    width: 100%;
    height: 8px;
    background-color: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 1rem;
    
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
      border-radius: 4px;
      transition: width 0.3s ease;
    }
  }
  
  .progress-dots {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    
    .dot {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.8rem;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &.completed {
        background-color: #28a745;
        color: white;
        
        &:hover {
          background-color: #218838;
        }
      }
      
      &.current {
        background-color: #007bff;
        color: white;
        box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.3);
      }
      
      &.pending {
        background-color: #e9ecef;
        color: #6c757d;
        
        &:hover {
          background-color: #dee2e6;
        }
      }
    }
  }
}

// 반응형 디자인
@media (max-width: 768px) {
  .progress-container {
    .progress-dots {
      gap: 0.3rem;
      
      .dot {
        width: 28px;
        height: 28px;
        font-size: 0.75rem;
      }
    }
  }
}
</style>