<!-- frontend/src/components/learning/MainContentArea.vue -->
<template>
  <div class="main-content-area">
    <div class="content-header">
      <h2 class="content-title">{{ chapterTitle }}</h2>
      <p class="content-subtitle">{{ sectionTitle }}</p>
    </div>

    <div class="content-body">
      <!-- 이론 설명 컨텐츠 -->
      <div 
        v-if="shouldShowContent('theory')"
        class="theory-content content-active"
        :class="{ 'content-hidden': !isContentVisible('theory') }"
      >
        <h3>🧠 {{ contentData.title || 'LLM(Large Language Model)이란?' }}</h3>
        <div class="theory-body">
          <p>{{ theoryContent.description }}</p>
          <br>
          <div class="key-points">
            <p><strong>💡 핵심 포인트:</strong></p>
            <ul>
              <li v-for="point in theoryContent.keyPoints" :key="point">{{ point }}</li>
            </ul>
          </div>
          <br>
          <div class="examples">
            <p><strong>📋 대표 예시:</strong></p>
            <ul>
              <li v-for="example in theoryContent.examples" :key="example">{{ example }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 퀴즈 컨텐츠 -->
      <div 
        v-if="shouldShowContent('quiz')"
        class="quiz-content"
        :class="{ 'content-active': isContentVisible('quiz'), 'content-hidden': !isContentVisible('quiz') }"
      >
        <h3>📝 퀴즈 문제</h3>
        <div class="quiz-question-display">
          <p><strong>{{ quizContent.question }}</strong></p>
          <div class="quiz-description">
            <p>💡 오른쪽 상호작용 영역에서 답변을 선택해주세요.</p>
            <p>⚠️ 답변을 제출하기 전까지는 다른 내용을 볼 수 없습니다.</p>
          </div>
        </div>
      </div>

      <!-- 피드백 컨텐츠 -->
      <div 
        v-if="shouldShowContent('feedback')"
        class="feedback-content"
        :class="{ 'content-active': isContentVisible('feedback'), 'content-hidden': !isContentVisible('feedback') }"
      >
        <h3>✅ 평가 결과</h3>
        <div class="feedback-score">
          <p><strong>{{ feedbackContent.scoreText }}</strong></p>
        </div>
        <div class="feedback-explanation">
          <p><strong>📝 상세 피드백:</strong></p>
          <p>{{ feedbackContent.explanation }}</p>
        </div>
        <div class="feedback-next-steps">
          <p><strong>🎯 다음 단계 결정:</strong></p>
          <p>{{ feedbackContent.nextStep }}</p>
        </div>
      </div>

      <!-- QnA 컨텐츠 (이론 유지하면서 질답 추가) -->
      <div 
        v-if="shouldShowContent('qna')"
        class="qna-content"
        :class="{ 'content-active': isContentVisible('qna'), 'content-hidden': !isContentVisible('qna') }"
      >
        <h4>❓ 질문 답변</h4>
        <div class="qna-item">
          <p><strong>질문:</strong> {{ qnaContent.question }}</p>
          <p><strong>답변:</strong> {{ qnaContent.answer }}</p>
        </div>
        <div v-if="qnaContent.relatedInfo" class="qna-related">
          <p><strong>🔗 관련 학습:</strong></p>
          <p>{{ qnaContent.relatedInfo }}</p>
        </div>
      </div>
    </div>

    <!-- 이전 컨텐츠 접근 버튼 -->
    <div class="content-navigation">
      <button 
        v-if="canShowNavigationButton('theory')"
        class="btn btn-outline"
        @click="handleNavigationClick('theory')"
      >
        📖 이론 다시 보기
      </button>
      <button 
        v-if="canShowNavigationButton('quiz')"
        class="btn btn-outline"
        @click="handleNavigationClick('quiz')"
      >
        📝 퀴즈 다시 보기
      </button>
      <button 
        v-if="canShowNavigationButton('current')"
        class="btn btn-outline"
        @click="handleNavigationClick('current')"
      >
        ← 현재 단계로
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits } from 'vue'

// Props 정의
const props = defineProps({
  currentAgent: {
    type: String,
    required: true,
    default: 'theory_educator'
  },
  contentData: {
    type: Object,
    required: true,
    default: () => ({
      title: '',
      subtitle: '',
      content: '',
      type: 'theory'
    })
  },
  currentContentMode: {
    type: String,
    default: 'current' // 'current', 'review_theory', 'review_quiz'
  },
  completedSteps: {
    type: Object,
    default: () => ({ theory: true, quiz: false, feedback: false })
  }
})

// Emits 정의
const emit = defineEmits(['navigation-click'])

// 에이전트별 컨텐츠 매핑
const agentContentMap = {
  theory_educator: 'theory',
  quiz_generator: 'quiz',
  evaluation_feedback: 'feedback',
  qna_resolver: 'qna'
}

// 컴퓨티드 속성들
const chapterTitle = computed(() => '2챕터 1섹션')
const sectionTitle = computed(() => 'LLM이란 무엇인가')

// 이론 컨텐츠 데이터
const theoryContent = computed(() => ({
  description: 'LLM은 대규모 언어 모델로, 방대한 텍스트 데이터를 학습하여 인간과 유사한 언어 이해와 생성 능력을 가진 AI 모델입니다.',
  keyPoints: [
    '대규모 데이터 학습',
    '언어 이해 및 생성',
    '문맥 파악 능력'
  ],
  examples: [
    'ChatGPT (OpenAI)',
    'Claude (Anthropic)',
    'Bard (Google)'
  ]
}))

// 퀴즈 컨텐츠 데이터
const quizContent = computed(() => ({
  question: '다음 중 LLM의 특징이 아닌 것은?'
}))

// 피드백 컨텐츠 데이터
const feedbackContent = computed(() => ({
  scoreText: '정답입니다! (100점)',
  explanation: '훌륭합니다! LLM의 핵심 특징을 정확히 이해하고 계시네요. 실시간 인터넷 검색은 LLM의 기본 기능이 아닙니다. LLM은 학습된 데이터를 바탕으로 응답을 생성합니다.',
  nextStep: '점수가 우수하므로 다음 섹션으로 진행하는 것을 권장합니다.'
}))

// QnA 컨텐츠 데이터
const qnaContent = computed(() => ({
  question: 'AI와 머신러닝의 차이가 뭐예요?',
  answer: 'AI는 더 넓은 개념으로, 인간의 지능을 모방하는 모든 기술을 포함합니다. 머신러닝은 AI의 한 분야로, 데이터를 통해 학습하는 방법론입니다. LLM은 머신러닝의 딥러닝 분야에 속하는 특화된 모델입니다.',
  relatedInfo: '3챕터에서 AI의 역사와 발전 과정을 더 자세히 다룹니다.'
}))

// 컨텐츠 표시/숨김 로직
const shouldShowContent = (contentType) => {
  // 현재 에이전트의 컨텐츠이거나, 리뷰 모드인 경우
  const currentContentType = agentContentMap[props.currentAgent]
  
  if (props.currentContentMode === 'current') {
    return contentType === currentContentType
  } else if (props.currentContentMode === 'review_theory') {
    return contentType === 'theory'
  } else if (props.currentContentMode === 'review_quiz') {
    return contentType === 'quiz'
  }
  
  // QnA의 경우 이론도 함께 표시
  if (currentContentType === 'qna') {
    return contentType === 'qna' || contentType === 'theory'
  }
  
  return contentType === currentContentType
}

const isContentVisible = (contentType) => {
  return shouldShowContent(contentType)
}

// 네비게이션 버튼 표시 로직
const canShowNavigationButton = (buttonType) => {
  if (buttonType === 'theory') {
    // 피드백 단계에서 이론이 완료된 경우만
    return props.currentAgent === 'evaluation_feedback' && 
           props.currentContentMode === 'current' && 
           props.completedSteps.theory
  }
  
  if (buttonType === 'quiz') {
    // 피드백 단계에서 퀴즈가 완료된 경우만
    return props.currentAgent === 'evaluation_feedback' && 
           props.currentContentMode === 'current' && 
           props.completedSteps.quiz
  }
  
  if (buttonType === 'current') {
    // 리뷰 모드일 때만
    return props.currentContentMode !== 'current'
  }
  
  return false
}

// 이벤트 핸들러
const handleNavigationClick = (navigationType) => {
  emit('navigation-click', navigationType)
}
</script>

<style scoped>
.main-content-area {
  background: white;
  padding: 2rem;
  overflow-y: auto;
  border-right: 1px solid #dee2e6;
  height: 100%;
}

.content-header {
  margin-bottom: 1.5rem;
}

.content-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.content-subtitle {
  color: #6c757d;
  font-size: 1rem;
}

.content-body {
  min-height: 400px;
}

/* 에이전트별 컨텐츠 스타일 */
.theory-content {
  background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
  border-left: 4px solid #2196f3;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.theory-body {
  line-height: 1.6;
}

.key-points ul,
.examples ul {
  padding-left: 1.5rem;
  margin-top: 0.5rem;
}

.key-points li,
.examples li {
  margin-bottom: 0.25rem;
}

.quiz-content {
  background: linear-gradient(135deg, #fff3e0, #fce4ec);
  border-left: 4px solid #ff9800;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.quiz-question-display p {
  margin-bottom: 1rem;
}

.quiz-description {
  background: rgba(255, 255, 255, 0.7);
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.quiz-description p {
  margin-bottom: 0.5rem;
}

.quiz-description p:last-child {
  margin-bottom: 0;
}

.feedback-content {
  background: linear-gradient(135deg, #e8f5e8, #f1f8e9);
  border-left: 4px solid #4caf50;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.feedback-score {
  margin-bottom: 1.5rem;
}

.feedback-score p {
  font-size: 1.2rem;
  color: #2e7d32;
}

.feedback-explanation,
.feedback-next-steps {
  margin-bottom: 1rem;
}

.feedback-explanation p:last-child,
.feedback-next-steps p:last-child {
  margin-top: 0.5rem;
  line-height: 1.6;
}

.qna-content {
  background: linear-gradient(135deg, #f3e5f5, #fce4ec);
  border-left: 4px solid #9c27b0;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.qna-item {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.qna-item p {
  margin-bottom: 0.75rem;
}

.qna-related {
  background: rgba(255, 255, 255, 0.7);
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(156, 39, 176, 0.3);
}

.qna-related p {
  margin-bottom: 0.5rem;
}

.qna-related p:last-child {
  margin-bottom: 0;
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
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 이전 컨텐츠 접근 버튼 */
.content-navigation {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-outline {
  background: white;
  color: #6c757d;
  border: 1px solid #6c757d;
}

.btn-outline:hover {
  background: #f8f9fa;
  border-color: #495057;
  color: #495057;
  transform: translateY(-1px);
}

/* 반응형 */
@media (max-width: 768px) {
  .main-content-area {
    padding: 1rem;
  }
  
  .content-title {
    font-size: 1.25rem;
  }
  
  .theory-content,
  .quiz-content,
  .feedback-content,
  .qna-content {
    padding: 1rem;
  }
  
  .content-navigation {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>