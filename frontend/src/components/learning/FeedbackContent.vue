<!-- frontend/src/components/learning/FeedbackContent.vue -->
<template>
  <div class="feedback-content" :class="{ 'content-active': isVisible, 'content-hidden': !isVisible }">
    <h3>✅ 평가 결과</h3>



    <!-- 답변 정보 섹션 -->
    <div v-if="parsedFeedback.answerInfo" class="answer-info-section">
      <div class="answer-details" v-html="parsedFeedback.answerInfo"></div>
    </div>

    <!-- 피드백 내용 섹션 -->
    <div v-if="parsedFeedback.feedbackContent" class="feedback-content-section">
      <h4>💬 피드백</h4>
      <div class="feedback-details" v-html="parsedFeedback.feedbackContent"></div>
    </div>


  </div>
</template>

<script setup>
import { defineProps, watch, computed } from 'vue'

// Props 정의
const props = defineProps({
  feedbackData: {
    type: Object,
    required: true,
    default: () => ({
      scoreText: '',
      explanation: '',
      nextStep: ''
    })
  },

  isVisible: {
    type: Boolean,
    default: true
  }
})

// 피드백 데이터 변화 감지 (디버깅용)
watch(() => props.feedbackData, (newData) => {
  console.log('🔍 FeedbackContent: 피드백 데이터 변화 감지:', newData)
}, { deep: true, immediate: true })

// 피드백 텍스트 파싱 함수 - 2개 섹션으로 단순화
const parsedFeedback = computed(() => {
  const scoreText = props.feedbackData.scoreText || ''

  if (!scoreText) {
    return {
      answerInfo: '',
      feedbackContent: ''
    }
  }

  // 📋 답변 정보 부분과 나머지 피드백 부분으로 분리
  const answerInfoPattern = /📋[^🎯]*?(?=💪|🎉|😊|$)/s
  const answerInfoMatch = scoreText.match(answerInfoPattern)
  
  let answerInfo = ''
  let feedbackContent = ''
  
  if (answerInfoMatch) {
    // 답변 정보 부분
    answerInfo = answerInfoMatch[0].trim()
    
    // 나머지 피드백 부분 (답변 정보 이후의 모든 내용)
    feedbackContent = scoreText.replace(answerInfoMatch[0], '').trim()
  } else {
    // 📋 패턴이 없으면 전체를 피드백으로 처리
    feedbackContent = scoreText
  }

  return {
    answerInfo: answerInfo ? formatText(answerInfo) : '',
    feedbackContent: feedbackContent ? formatText(feedbackContent) : ''
  }
})

// 텍스트 포맷팅 함수
const formatText = (text) => {
  if (!text) return ''

  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // **텍스트** -> <strong>텍스트</strong>
    .replace(/\n/g, '<br>') // 줄바꿈 -> <br>
    .replace(/•/g, '&bull;') // 불릿 포인트 정리
    .replace(/^\s*<br>\s*/, '') // 시작 부분의 불필요한 <br> 제거
    .replace(/\s*<br>\s*$/, '') // 끝 부분의 불필요한 <br> 제거
}
</script>

<style scoped>
.feedback-content {
  background: linear-gradient(135deg, #e8f5e8, #f1f8e9);
  border-left: 4px solid #4caf50;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

/* 답변 정보 섹션 */
.answer-info-section {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

/* 답변 정보 섹션은 제목 없이 내용만 표시 */

.answer-details {
  line-height: 1.6;
  color: #2e7d32;
}

/* 피드백 내용 섹션 */
.feedback-content-section {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.feedback-content-section h4 {
  margin: 0 0 0.75rem 0;
  color: #2e7d32;
  font-size: 1rem;
  font-weight: 600;
}

.feedback-details {
  line-height: 1.6;
  color: #2e7d32;
}

/* 다음 단계 안내 섹션은 제거됨 - 2개 섹션으로 단순화 */



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