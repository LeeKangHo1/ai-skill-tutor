<!-- frontend/src/components/learning/SessionCompletion.vue -->
<!-- 세션 완료 후 다음 단계 안내 및 옵션 제공 컴포넌트 -->
<template>
  <div class="session-completion">
    <div class="completion-header">
      <div class="completion-icon">
        <i class="fas fa-check-circle"></i>
      </div>
      <h2>🎉 학습 세션 완료!</h2>
      <p class="completion-subtitle">수고하셨습니다. 이번 세션을 성공적으로 완료했습니다.</p>
    </div>

    <!-- 세션 요약 정보 -->
    <div class="session-summary">
      <h3>📊 학습 요약</h3>
      <div class="summary-grid">
        <div class="summary-item">
          <div class="summary-label">학습 챕터</div>
          <div class="summary-value">{{ sessionInfo.chapter }}장 {{ sessionInfo.section }}절</div>
        </div>
        <div class="summary-item">
          <div class="summary-label">학습 시간</div>
          <div class="summary-value">{{ completionData.session_summary?.total_duration || '12분' }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-label">최종 점수</div>
          <div class="summary-value score">{{ completionData.final_score || 100 }}점</div>
        </div>
        <div class="summary-item">
          <div class="summary-label">완료 시간</div>
          <div class="summary-value">{{ formatCompletionTime(completionData.completed_at) }}</div>
        </div>
      </div>
      
      <!-- 학습한 개념들 -->
      <div v-if="completionData.session_summary?.concepts_learned" class="concepts-learned">
        <h4>💡 학습한 주요 개념</h4>
        <ul>
          <li v-for="concept in completionData.session_summary.concepts_learned" :key="concept">
            {{ concept }}
          </li>
        </ul>
      </div>
    </div>

    <!-- 다음 단계 안내 -->
    <div class="next-steps">
      <h3>🎯 다음 단계</h3>
      
      <!-- 다음 학습 단계가 있는 경우 -->
      <div v-if="hasNextStep" class="next-step-available">
        <div class="next-step-info">
          <div class="next-step-icon">
            <i class="fas fa-arrow-right"></i>
          </div>
          <div class="next-step-details">
            <h4>{{ nextStepTitle }}</h4>
            <p>{{ nextStepDescription }}</p>
          </div>
        </div>
        
        <div class="action-buttons">
          <button 
            class="btn btn-primary btn-large"
            @click="handleProceedToNext"
            :disabled="isLoading"
          >
            <i class="fas fa-play"></i>
            다음 단계로 계속하기
          </button>
          
          <button 
            class="btn btn-outline btn-large"
            @click="handleRetrySession"
            :disabled="isLoading"
          >
            <i class="fas fa-redo"></i>
            이번 섹션 다시 학습
          </button>
        </div>
      </div>
      
      <!-- 다음 학습 단계가 없는 경우 (코스 완료) -->
      <div v-else class="course-completed">
        <div class="completion-message">
          <i class="fas fa-trophy"></i>
          <h4>축하합니다! 전체 코스를 완료했습니다.</h4>
          <p>모든 학습 내용을 성공적으로 마스터했습니다.</p>
        </div>
        
        <div class="action-buttons">
          <button 
            class="btn btn-outline btn-large"
            @click="handleRetrySession"
            :disabled="isLoading"
          >
            <i class="fas fa-redo"></i>
            이번 섹션 다시 학습
          </button>
        </div>
      </div>
      
      <!-- 공통 액션 버튼 -->
      <div class="common-actions">
        <button 
          class="btn btn-secondary"
          @click="handleGoToDashboard"
          :disabled="isLoading"
        >
          <i class="fas fa-home"></i>
          대시보드로 돌아가기
        </button>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits, ref } from 'vue'
import { useLearningStore } from '../../stores/learningStore.js'
import { useRouter } from 'vue-router'

// Props 정의
const props = defineProps({
  completionData: {
    type: Object,
    required: true,
    default: () => ({})
  },
  sessionInfo: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

// Emits 정의
const emit = defineEmits([
  'proceed-to-next',
  'retry-session', 
  'go-to-dashboard'
])

// Store 및 라우터
const learningStore = useLearningStore()
const router = useRouter()

// 반응형 상태
const isLoading = ref(false)
const loadingMessage = ref('')

// ===== 컴퓨티드 속성 =====

// 다음 단계 존재 여부
const hasNextStep = computed(() => {
  return props.completionData.next_chapter !== null && 
         props.completionData.next_section !== null
})

// 다음 단계 제목
const nextStepTitle = computed(() => {
  if (!hasNextStep.value) return ''
  
  return props.completionData.next_chapter_title || 
         `${props.completionData.next_chapter}장 - 다음 학습 단계`
})

// 다음 단계 설명
const nextStepDescription = computed(() => {
  if (!hasNextStep.value) return ''
  
  return props.completionData.next_section_title || 
         `${props.completionData.next_section}절을 학습하게 됩니다.`
})

// ===== 유틸리티 함수 =====

// 완료 시간 포맷팅
const formatCompletionTime = (completedAt) => {
  if (!completedAt) return '방금 전'
  
  try {
    const date = new Date(completedAt)
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('시간 포맷팅 오류:', error)
    return '방금 전'
  }
}

// ===== 이벤트 핸들러 =====

// 다음 단계로 진행
const handleProceedToNext = async () => {
  if (!hasNextStep.value) return
  
  try {
    isLoading.value = true
    loadingMessage.value = '다음 학습 단계를 준비하고 있습니다...'
    
    console.log('다음 단계로 진행:', {
      next_chapter: props.completionData.next_chapter,
      next_section: props.completionData.next_section
    })
    
    // learningStore를 통해 세션 완료 처리 (proceed 결정)
    const result = await learningStore.completeSession('proceed')
    
    if (result.success) {
      // 다음 챕터/섹션으로 라우팅
      const nextChapter = props.completionData.next_chapter
      const nextSection = props.completionData.next_section
      
      // 상위 컴포넌트에 이벤트 전달
      emit('proceed-to-next', {
        chapter: nextChapter,
        section: nextSection
      })
      
      // 라우터를 통해 다음 학습 페이지로 이동
      await router.push(`/learning/${nextChapter}/${nextSection}`)
    } else {
      console.error('다음 단계 진행 실패:', result.error)
    }
  } catch (error) {
    console.error('다음 단계 진행 중 오류:', error)
  } finally {
    isLoading.value = false
  }
}

// 세션 재시도
const handleRetrySession = async () => {
  try {
    isLoading.value = true
    loadingMessage.value = '세션을 다시 시작하고 있습니다...'
    
    console.log('세션 재시도:', {
      chapter: props.sessionInfo.chapter,
      section: props.sessionInfo.section
    })
    
    // learningStore를 통해 세션 완료 처리 (retry 결정)
    const result = await learningStore.completeSession('retry')
    
    if (result.success) {
      // 상위 컴포넌트에 이벤트 전달
      emit('retry-session', {
        chapter: props.sessionInfo.chapter,
        section: props.sessionInfo.section
      })
      
      // 현재 챕터/섹션을 다시 시작
      const currentChapter = props.sessionInfo.chapter
      const currentSection = props.sessionInfo.section
      
      // 라우터를 통해 현재 학습 페이지 새로고침
      await router.push(`/learning/${currentChapter}/${currentSection}`)
      
      // 페이지 새로고침으로 세션 재시작
      window.location.reload()
    } else {
      console.error('세션 재시도 실패:', result.error)
    }
  } catch (error) {
    console.error('세션 재시도 중 오류:', error)
  } finally {
    isLoading.value = false
  }
}

// 대시보드로 이동
const handleGoToDashboard = async () => {
  try {
    isLoading.value = true
    loadingMessage.value = '대시보드로 이동하고 있습니다...'
    
    console.log('대시보드로 이동')
    
    // learningStore를 통해 세션 완료 처리 (dashboard 결정)
    const result = await learningStore.completeSession('dashboard')
    
    if (result.success) {
      // 상위 컴포넌트에 이벤트 전달
      emit('go-to-dashboard')
      
      // 라우터를 통해 대시보드로 이동
      await router.push('/dashboard')
    } else {
      console.error('대시보드 이동 실패:', result.error)
    }
  } catch (error) {
    console.error('대시보드 이동 중 오류:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.session-completion {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  max-width: 600px;
  margin: 0 auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  position: relative;
}

/* ===== 완료 헤더 ===== */
.completion-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #f8f9fa;
}

.completion-icon {
  font-size: 4rem;
  color: #28a745;
  margin-bottom: 1rem;
  animation: bounceIn 0.6s ease-out;
}

.completion-header h2 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.8rem;
  font-weight: 700;
}

.completion-subtitle {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0;
}

/* ===== 세션 요약 ===== */
.session-summary {
  margin-bottom: 2rem;
  background: #f8f9fa;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.session-summary h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
  font-weight: 600;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.summary-item {
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  text-align: center;
  border: 1px solid #e9ecef;
  transition: all 0.2s ease;
}

.summary-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.summary-label {
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.summary-value {
  font-size: 1.1rem;
  color: #2c3e50;
  font-weight: 600;
}

.summary-value.score {
  color: #28a745;
  font-size: 1.3rem;
}

/* 학습한 개념들 */
.concepts-learned {
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #e9ecef;
}

.concepts-learned h4 {
  color: #2c3e50;
  margin-bottom: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
}

.concepts-learned ul {
  margin: 0;
  padding-left: 1.5rem;
}

.concepts-learned li {
  color: #495057;
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

/* ===== 다음 단계 안내 ===== */
.next-steps {
  margin-bottom: 1rem;
}

.next-steps h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
  font-weight: 600;
}

/* 다음 단계 정보 */
.next-step-available {
  margin-bottom: 1.5rem;
}

.next-step-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(33, 150, 243, 0.2);
}

.next-step-icon {
  font-size: 2rem;
  color: #2196f3;
  flex-shrink: 0;
}

.next-step-details h4 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.next-step-details p {
  color: #6c757d;
  margin: 0;
  line-height: 1.5;
}

/* 코스 완료 */
.course-completed {
  margin-bottom: 1.5rem;
}

.completion-message {
  text-align: center;
  background: linear-gradient(135deg, #fff3cd, #d1ecf1);
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.completion-message i {
  font-size: 3rem;
  color: #ffc107;
  margin-bottom: 1rem;
}

.completion-message h4 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.3rem;
  font-weight: 600;
}

.completion-message p {
  color: #6c757d;
  margin: 0;
  font-size: 1.1rem;
}

/* ===== 액션 버튼들 ===== */
.action-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.common-actions {
  display: flex;
  justify-content: center;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1rem;
  flex: 1;
  min-width: 200px;
}

.btn-primary {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 123, 255, 0.4);
}

.btn-outline {
  background: white;
  color: #6c757d;
  border: 2px solid #6c757d;
}

.btn-outline:hover:not(:disabled) {
  background: #6c757d;
  color: white;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
  transform: translateY(-2px);
}

/* ===== 로딩 오버레이 ===== */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 1rem;
  z-index: 10;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.loading-spinner p {
  color: #6c757d;
  font-weight: 500;
}

/* ===== 애니메이션 ===== */
@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ===== 반응형 디자인 ===== */
@media (max-width: 768px) {
  .session-completion {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .completion-header h2 {
    font-size: 1.5rem;
  }
  
  .completion-subtitle {
    font-size: 1rem;
  }
  
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
  
  .next-step-info {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn-large {
    min-width: auto;
    width: 100%;
  }
  
  .completion-icon {
    font-size: 3rem;
  }
  
  .completion-message i {
    font-size: 2.5rem;
  }
}

@media (max-width: 480px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-item {
    padding: 0.75rem;
  }
  
  .session-summary,
  .next-step-info,
  .completion-message {
    padding: 1rem;
  }
}
</style>