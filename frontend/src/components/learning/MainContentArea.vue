<!-- frontend/src/components/learning/MainContentArea.vue -->
<template>
  <div class="main-content-area" :class="agentThemeClass">
    <!-- 에러 알림 -->
    <ErrorAlert
      v-if="showErrorAlert && errorInfo"
      :show="showErrorAlert"
      :error-type="errorInfo.type"
      :error-message="friendlyErrorMessage"
      :error-code="errorInfo.code"
      :can-retry="errorInfo.canRetry"
      :show-help-button="true"
      :is-fallback-mode="learningStore.workflowState.metadata?.isFallbackMode || false"
      @close="hideError"
      @retry="handleErrorRetry"
      @help="handleErrorHelp"
    />
    
    <!-- 진행률 표시기 -->
    <div class="progress-indicator">
      <div class="progress-header">
        <h3>학습 진행 상황</h3>
        <span class="progress-percentage">{{ progressPercentage }}%</span>
      </div>
      <div class="progress-steps">
        <div 
          v-for="step in sessionSteps" 
          :key="step.key"
          class="progress-step"
          :class="{
            'step-active': step.active,
            'step-completed': step.completed,
            'step-current': isCurrentStep(step.key)
          }"
        >
          <div class="step-icon">
            <i :class="getStepIcon(step.key)"></i>
          </div>
          <span class="step-name">{{ step.name }}</span>
        </div>
      </div>
    </div>

    <div class="content-header">
      <div class="agent-indicator">
        <div class="agent-icon" :class="agentIconClass">
          <i :class="currentAgentIcon"></i>
        </div>
        <div class="agent-info">
          <h2 class="content-title">{{ sessionTitle }}</h2>
          <p class="content-subtitle">{{ sessionSubtitle }}</p>
          <span class="agent-name">{{ currentAgentName }}</span>
        </div>
      </div>
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

      <!-- 세션 완료 컨텐츠 -->
      <div 
        v-if="shouldShowContent('completion')"
        class="completion-content"
        :class="{ 'content-active': isContentVisible('completion'), 'content-hidden': !isContentVisible('completion') }"
      >
        <SessionCompletion
          :completion-data="completionData"
          :session-info="sessionInfo"
          @proceed-to-next="handleProceedToNext"
          @retry-session="handleRetrySession"
          @go-to-dashboard="handleGoToDashboard"
        />
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
import { computed, defineProps, defineEmits, watch } from 'vue'
import { useLearningStore } from '../../stores/learningStore.js'
import { useTutorStore } from '../../stores/tutorStore.js'
import { useErrorHandler } from '../../composables/useErrorHandler.js'
import SessionCompletion from './SessionCompletion.vue'
import ErrorAlert from '../common/ErrorAlert.vue'

// Store 인스턴스
const learningStore = useLearningStore()
const tutorStore = useTutorStore()

// 에러 핸들러 컴포저블
const {
  showErrorAlert,
  errorInfo,
  friendlyErrorMessage,
  helpInfo,
  hideError,
  retryLastAction
} = useErrorHandler()

// Props 정의 (기존 호환성 유지)
const props = defineProps({
  currentAgent: {
    type: String,
    required: false,
    default: null
  },
  contentData: {
    type: Object,
    required: false,
    default: () => ({})
  },
  currentContentMode: {
    type: String,
    default: 'current'
  },
  completedSteps: {
    type: Object,
    default: () => ({})
  }
})

// Emits 정의
const emit = defineEmits([
  'navigation-click',
  'ui-mode-changed',
  'agent-changed', 
  'progress-stage-changed',
  'proceed-to-next',
  'retry-session',
  'go-to-dashboard'
])

// ===== Store 상태 기반 실시간 컴퓨티드 속성 =====

// 현재 에이전트 (learningStore 우선, props 대체)
const currentAgent = computed(() => {
  return learningStore.workflowState.current_agent || 
         tutorStore.currentAgent || 
         props.currentAgent || 
         'theory_educator'
})

// 현재 UI 모드 (learningStore 우선)
const currentUIMode = computed(() => {
  return learningStore.workflowState.ui_mode || 
         tutorStore.currentUIMode || 
         'chat'
})

// 세션 진행 단계 (learningStore 우선)
const sessionProgressStage = computed(() => {
  return learningStore.workflowState.session_progress_stage || 
         tutorStore.sessionProgressStage || 
         'session_start'
})

// 완료된 단계 (tutorStore 우선)
const completedSteps = computed(() => {
  return Object.keys(tutorStore.completedSteps).length > 0 
    ? tutorStore.completedSteps 
    : props.completedSteps
})

// 컨텐츠 모드 (tutorStore 우선)
const currentContentMode = computed(() => {
  return tutorStore.currentContentMode || props.currentContentMode || 'current'
})

// ===== 에이전트별 테마 및 아이콘 =====

// 에이전트별 테마 클래스
const agentThemeClass = computed(() => {
  const themeMap = {
    'theory_educator': 'theme-theory',
    'quiz_generator': 'theme-quiz', 
    'evaluation_feedback_agent': 'theme-feedback',
    'qna_resolver': 'theme-qna'
  }
  return themeMap[currentAgent.value] || 'theme-theory'
})

// 에이전트별 아이콘 클래스
const agentIconClass = computed(() => {
  const iconClassMap = {
    'theory_educator': 'icon-theory',
    'quiz_generator': 'icon-quiz',
    'evaluation_feedback_agent': 'icon-feedback', 
    'qna_resolver': 'icon-qna'
  }
  return iconClassMap[currentAgent.value] || 'icon-theory'
})

// 에이전트별 아이콘
const currentAgentIcon = computed(() => {
  const iconMap = {
    'theory_educator': 'fas fa-book-open',
    'quiz_generator': 'fas fa-question-circle',
    'evaluation_feedback_agent': 'fas fa-check-circle',
    'qna_resolver': 'fas fa-comments'
  }
  return iconMap[currentAgent.value] || 'fas fa-book-open'
})

// 에이전트별 이름
const currentAgentName = computed(() => {
  const nameMap = {
    'theory_educator': '이론 설명 튜터',
    'quiz_generator': '퀴즈 출제 튜터',
    'evaluation_feedback_agent': '평가 피드백 튜터',
    'qna_resolver': '질문 답변 튜터'
  }
  return nameMap[currentAgent.value] || '학습 튜터'
})

// ===== 세션 정보 =====

// 세션 제목 (learningStore 우선)
const sessionTitle = computed(() => {
  if (learningStore.sessionState.chapter_title && learningStore.sessionState.section_title) {
    return `${learningStore.sessionState.chapter_number}장 ${learningStore.sessionState.section_number}절`
  }
  return tutorStore.sessionInfo.chapter_title || '2장 1절'
})

// 세션 부제목
const sessionSubtitle = computed(() => {
  if (learningStore.sessionState.section_title) {
    return learningStore.sessionState.section_title
  }
  return tutorStore.sessionInfo.section_title || 'LLM이란 무엇인가'
})

// ===== 진행률 표시 =====

// 세션 단계 정보 (tutorStore 기반)
const sessionSteps = computed(() => {
  return tutorStore.sessionSteps || [
    {
      name: '이론',
      key: 'theory',
      active: currentAgent.value === 'theory_educator' || currentAgent.value === 'qna_resolver',
      completed: completedSteps.value.theory || false
    },
    {
      name: '퀴즈',
      key: 'quiz',
      active: currentAgent.value === 'quiz_generator',
      completed: completedSteps.value.quiz || false
    },
    {
      name: '풀이',
      key: 'feedback',
      active: currentAgent.value === 'evaluation_feedback_agent',
      completed: completedSteps.value.feedback || false
    }
  ]
})

// 진행률 퍼센티지
const progressPercentage = computed(() => {
  const steps = sessionSteps.value
  const completedCount = steps.filter(step => step.completed).length
  return Math.round((completedCount / steps.length) * 100)
})

// 현재 활성 단계 확인
const isCurrentStep = (stepKey) => {
  const agentStepMap = {
    'theory_educator': 'theory',
    'quiz_generator': 'quiz',
    'evaluation_feedback_agent': 'feedback',
    'qna_resolver': 'theory' // QnA는 이론 단계로 간주
  }
  return agentStepMap[currentAgent.value] === stepKey
}

// 단계별 아이콘
const getStepIcon = (stepKey) => {
  const iconMap = {
    'theory': 'fas fa-book',
    'quiz': 'fas fa-question',
    'feedback': 'fas fa-check'
  }
  return iconMap[stepKey] || 'fas fa-circle'
}

// ===== 에이전트별 컨텐츠 매핑 =====
const agentContentMap = {
  theory_educator: 'theory',
  quiz_generator: 'quiz',
  evaluation_feedback_agent: 'feedback',
  qna_resolver: 'qna',
  session_completion: 'completion'
}

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

// 세션 완료 데이터
const completionData = computed(() => {
  const workflowContent = learningStore.workflowState.content
  if (workflowContent?.type === 'completion') {
    return workflowContent.completion_data || {}
  }
  return {}
})

// 세션 정보 (SessionCompletion 컴포넌트용)
const sessionInfo = computed(() => ({
  chapter: learningStore.sessionState.chapter_number || tutorStore.sessionInfo.chapter_number || 2,
  section: learningStore.sessionState.section_number || tutorStore.sessionInfo.section_number || 1,
  chapter_title: learningStore.sessionState.chapter_title || tutorStore.sessionInfo.chapter_title || 'LLM 기초',
  section_title: learningStore.sessionState.section_title || tutorStore.sessionInfo.section_title || 'LLM이란 무엇인가'
}))

// ===== 컨텐츠 표시/숨김 로직 (실시간 상태 기반) =====

// 컨텐츠 표시/숨김 로직 (실시간 상태 기반)
const shouldShowContent = (contentType) => {
  // 세션 완료 상태 확인
  if (learningStore.isSessionCompleted && contentType === 'completion') {
    return true
  }
  
  // 세션 완료 상태에서는 completion만 표시
  if (learningStore.isSessionCompleted && contentType !== 'completion') {
    return false
  }
  
  // 현재 에이전트의 컨텐츠 타입 결정
  const currentContentType = agentContentMap[currentAgent.value]
  
  if (currentContentMode.value === 'current') {
    return contentType === currentContentType
  } else if (currentContentMode.value === 'review_theory') {
    return contentType === 'theory'
  } else if (currentContentMode.value === 'review_quiz') {
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

// 네비게이션 버튼 표시 로직 (실시간 상태 기반)
const canShowNavigationButton = (buttonType) => {
  if (buttonType === 'theory') {
    // 피드백 단계에서 이론이 완료된 경우만
    return currentAgent.value === 'evaluation_feedback_agent' && 
           currentContentMode.value === 'current' && 
           completedSteps.value.theory
  }
  
  if (buttonType === 'quiz') {
    // 피드백 단계에서 퀴즈가 완료된 경우만
    return currentAgent.value === 'evaluation_feedback_agent' && 
           currentContentMode.value === 'current' && 
           completedSteps.value.quiz
  }
  
  if (buttonType === 'current') {
    // 리뷰 모드일 때만
    return currentContentMode.value !== 'current'
  }
  
  return false
}

// ===== 실시간 상태 변화 감시 =====

// learningStore 워크플로우 상태 변화 감시
watch(
  () => learningStore.workflowState,
  (newWorkflowState) => {
    if (newWorkflowState && Object.keys(newWorkflowState).length > 0) {
      console.log('MainContentArea: learningStore 워크플로우 상태 변화 감지:', newWorkflowState)
      
      // UI 모드 변경에 따른 컴포넌트 활성화 처리
      if (newWorkflowState.ui_mode) {
        handleUIMode변경(newWorkflowState.ui_mode)
      }
      
      // 에이전트 변경에 따른 테마 업데이트 처리
      if (newWorkflowState.current_agent) {
        handleAgentChange(newWorkflowState.current_agent)
      }
      
      // 진행 단계 변경 처리
      if (newWorkflowState.session_progress_stage) {
        handleProgressStageChange(newWorkflowState.session_progress_stage)
      }
    }
  },
  { deep: true, immediate: true }
)

// tutorStore 상태 변화 감시
watch(
  () => tutorStore.completedSteps,
  (newCompletedSteps) => {
    console.log('MainContentArea: 완료 단계 변화 감지:', newCompletedSteps)
    // 진행률 업데이트는 computed에서 자동 처리됨
  },
  { deep: true, immediate: true }
)

// ===== 상태 변화 핸들러 =====

// UI 모드 변경 핸들러
const handleUIMode변경 = (newUIMode) => {
  console.log(`MainContentArea: UI 모드 변경 - ${currentUIMode.value} → ${newUIMode}`)
  
  // UI 모드에 따른 추가 처리가 필요한 경우 여기에 구현
  if (newUIMode === 'quiz') {
    // 퀴즈 모드로 전환 시 처리
    emit('ui-mode-changed', { mode: 'quiz', agent: currentAgent.value })
  } else if (newUIMode === 'chat') {
    // 채팅 모드로 전환 시 처리
    emit('ui-mode-changed', { mode: 'chat', agent: currentAgent.value })
  }
}

// 에이전트 변경 핸들러
const handleAgentChange = (newAgent) => {
  console.log(`MainContentArea: 에이전트 변경 - ${currentAgent.value} → ${newAgent}`)
  
  // 에이전트 변경에 따른 추가 처리
  emit('agent-changed', { 
    oldAgent: currentAgent.value, 
    newAgent: newAgent,
    theme: agentThemeClass.value
  })
}

// 진행 단계 변경 핸들러
const handleProgressStageChange = (newStage) => {
  console.log(`MainContentArea: 진행 단계 변경 - ${sessionProgressStage.value} → ${newStage}`)
  
  // 진행 단계 변경에 따른 추가 처리
  emit('progress-stage-changed', { 
    stage: newStage, 
    percentage: progressPercentage.value 
  })
}

// ===== 이벤트 핸들러 =====

// 네비게이션 클릭 핸들러
const handleNavigationClick = (navigationType) => {
  console.log('MainContentArea: 네비게이션 클릭:', navigationType)
  
  // tutorStore의 컨텐츠 모드 업데이트
  if (navigationType === 'theory') {
    tutorStore.updateContentMode('review_theory')
  } else if (navigationType === 'quiz') {
    tutorStore.updateContentMode('review_quiz')
  } else if (navigationType === 'current') {
    tutorStore.updateContentMode('current')
  }
  
  emit('navigation-click', navigationType)
}

// ===== 세션 완료 관련 이벤트 핸들러 =====

// 다음 단계로 진행
const handleProceedToNext = (nextStepInfo) => {
  console.log('MainContentArea: 다음 단계로 진행:', nextStepInfo)
  emit('proceed-to-next', nextStepInfo)
}

// 세션 재시도
const handleRetrySession = (sessionInfo) => {
  console.log('MainContentArea: 세션 재시도:', sessionInfo)
  emit('retry-session', sessionInfo)
}

// 대시보드로 이동
const handleGoToDashboard = () => {
  console.log('MainContentArea: 대시보드로 이동')
  emit('go-to-dashboard')
}

// ===== 에러 처리 관련 이벤트 핸들러 =====

// 에러 재시도 핸들러
const handleErrorRetry = async () => {
  if (!errorInfo.value) return
  
  console.log('MainContentArea: 에러 재시도 시도:', errorInfo.value.context)
  
  try {
    // 컨텍스트에 따른 재시도 로직
    const context = errorInfo.value.context
    let result = null
    
    switch (context) {
      case 'startSession':
        // 세션 시작 재시도 - 기본 파라미터로 재시도
        result = await learningStore.startSession(
          learningStore.sessionState.chapter_number || 2,
          learningStore.sessionState.section_number || 1,
          '학습을 다시 시작합니다'
        )
        break
        
      case 'sendMessage':
        // 메시지 전송 재시도 - 마지막 메시지 재전송은 복잡하므로 사용자에게 다시 입력 요청
        console.log('메시지 재전송은 사용자가 직접 다시 입력해야 합니다.')
        hideError()
        return
        
      case 'submitQuiz':
        // 퀴즈 제출 재시도 - 마지막 답안 재제출은 복잡하므로 사용자에게 다시 선택 요청
        console.log('퀴즈 답안 재제출은 사용자가 직접 다시 선택해야 합니다.')
        hideError()
        return
        
      case 'completeSession':
        // 세션 완료 재시도
        result = await learningStore.completeSession('proceed')
        break
        
      default:
        console.warn('알 수 없는 에러 컨텍스트:', context)
        hideError()
        return
    }
    
    if (result && result.success) {
      console.log('에러 재시도 성공:', result)
      hideError()
    } else {
      console.error('에러 재시도 실패:', result)
      // 에러 상태는 learningStore에서 자동으로 업데이트됨
    }
    
  } catch (error) {
    console.error('에러 재시도 중 예외 발생:', error)
    learningStore.handleApiError(error, 'retry_error')
  }
}

// 에러 도움말 핸들러
const handleErrorHelp = () => {
  if (!helpInfo.value) return
  
  console.log('MainContentArea: 에러 도움말 표시:', helpInfo.value)
  
  // 도움말 모달이나 별도 컴포넌트를 표시하는 로직
  // 현재는 콘솔에 도움말 정보를 출력
  alert(`${helpInfo.value.title}\n\n${helpInfo.value.content.join('\n')}`)
}
</script>

<style scoped>
.main-content-area {
  background: white;
  padding: 2rem;
  overflow-y: auto;
  border-right: 1px solid #dee2e6;
  height: 100%;
  transition: all 0.3s ease;
}

/* ===== 에이전트별 테마 스타일 ===== */

.theme-theory {
  background: linear-gradient(135deg, #f8f9ff, #e3f2fd);
  border-right-color: #2196f3;
}

.theme-quiz {
  background: linear-gradient(135deg, #fff8f0, #fff3e0);
  border-right-color: #ff9800;
}

.theme-feedback {
  background: linear-gradient(135deg, #f0fff4, #e8f5e8);
  border-right-color: #4caf50;
}

.theme-qna {
  background: linear-gradient(135deg, #faf0ff, #f3e5f5);
  border-right-color: #9c27b0;
}

/* ===== 진행률 표시기 ===== */

.progress-indicator {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #2c3e50;
  font-weight: 600;
}

.progress-percentage {
  font-size: 1.2rem;
  font-weight: bold;
  color: #4caf50;
  background: rgba(76, 175, 80, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.progress-steps::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 2rem;
  right: 2rem;
  height: 2px;
  background: #e0e0e0;
  z-index: 1;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 2;
  transition: all 0.3s ease;
}

.step-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border: 2px solid #e0e0e0;
  margin-bottom: 0.5rem;
  transition: all 0.3s ease;
}

.step-icon i {
  font-size: 1.2rem;
  color: #9e9e9e;
  transition: all 0.3s ease;
}

.step-name {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
  transition: all 0.3s ease;
}

/* 단계 상태별 스타일 */
.step-completed .step-icon {
  background: #4caf50;
  border-color: #4caf50;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.step-completed .step-icon i {
  color: white;
}

.step-completed .step-name {
  color: #4caf50;
  font-weight: 600;
}

.step-current .step-icon {
  background: #2196f3;
  border-color: #2196f3;
  box-shadow: 0 2px 12px rgba(33, 150, 243, 0.4);
  animation: pulse 2s infinite;
}

.step-current .step-icon i {
  color: white;
}

.step-current .step-name {
  color: #2196f3;
  font-weight: 600;
}

.step-active .step-icon {
  border-color: #ff9800;
  background: rgba(255, 152, 0, 0.1);
}

.step-active .step-icon i {
  color: #ff9800;
}

.step-active .step-name {
  color: #ff9800;
}

@keyframes pulse {
  0% {
    box-shadow: 0 2px 12px rgba(33, 150, 243, 0.4);
  }
  50% {
    box-shadow: 0 2px 20px rgba(33, 150, 243, 0.6);
  }
  100% {
    box-shadow: 0 2px 12px rgba(33, 150, 243, 0.4);
  }
}

/* ===== 컨텐츠 헤더 (에이전트 정보 포함) ===== */

.content-header {
  margin-bottom: 1.5rem;
}

.agent-indicator {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.9);
  padding: 1rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.agent-icon {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.agent-icon i {
  font-size: 1.5rem;
  color: white;
}

/* 에이전트별 아이콘 스타일 */
.icon-theory {
  background: linear-gradient(135deg, #2196f3, #1976d2);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.icon-quiz {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.icon-feedback {
  background: linear-gradient(135deg, #4caf50, #388e3c);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.icon-qna {
  background: linear-gradient(135deg, #9c27b0, #7b1fa2);
  box-shadow: 0 4px 12px rgba(156, 39, 176, 0.3);
}

.agent-info {
  flex: 1;
}

.content-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 0.25rem;
  font-weight: 600;
}

.content-subtitle {
  color: #6c757d;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.agent-name {
  display: inline-block;
  background: rgba(33, 150, 243, 0.1);
  color: #1976d2;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

/* 에이전트별 이름 태그 색상 */
.theme-theory .agent-name {
  background: rgba(33, 150, 243, 0.1);
  color: #1976d2;
}

.theme-quiz .agent-name {
  background: rgba(255, 152, 0, 0.1);
  color: #f57c00;
}

.theme-feedback .agent-name {
  background: rgba(76, 175, 80, 0.1);
  color: #388e3c;
}

.theme-qna .agent-name {
  background: rgba(156, 39, 176, 0.1);
  color: #7b1fa2;
}

.content-body {
  min-height: 400px;
}

/* ===== 에이전트별 컨텐츠 스타일 (테마 연동) ===== */

.theory-content {
  background: rgba(255, 255, 255, 0.8);
  border-left: 4px solid #2196f3;
  padding: 1.5rem;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.theme-theory .theory-content {
  background: rgba(33, 150, 243, 0.05);
  border-left-color: #2196f3;
}

.theme-qna .theory-content {
  background: rgba(156, 39, 176, 0.05);
  border-left-color: #9c27b0;
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
  background: rgba(255, 255, 255, 0.8);
  border-left: 4px solid #ff9800;
  padding: 1.5rem;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.theme-quiz .quiz-content {
  background: rgba(255, 152, 0, 0.05);
  border-left-color: #ff9800;
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
  background: rgba(255, 255, 255, 0.8);
  border-left: 4px solid #4caf50;
  padding: 1.5rem;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.theme-feedback .feedback-content {
  background: rgba(76, 175, 80, 0.05);
  border-left-color: #4caf50;
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
  background: rgba(255, 255, 255, 0.8);
  border-left: 4px solid #9c27b0;
  padding: 1.5rem;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.theme-qna .qna-content {
  background: rgba(156, 39, 176, 0.05);
  border-left-color: #9c27b0;
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

.completion-content {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 0.75rem;
  padding: 0;
  margin-bottom: 1rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  overflow: hidden;
}

.theme-feedback .completion-content {
  background: rgba(76, 175, 80, 0.02);
  border: 2px solid rgba(76, 175, 80, 0.2);
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

/* ===== 반응형 디자인 ===== */

@media (max-width: 768px) {
  .main-content-area {
    padding: 1rem;
  }
  
  .progress-indicator {
    padding: 1rem;
    margin-bottom: 1.5rem;
  }
  
  .progress-steps {
    flex-direction: column;
    gap: 1rem;
  }
  
  .progress-steps::before {
    display: none;
  }
  
  .step-icon {
    width: 2.5rem;
    height: 2.5rem;
  }
  
  .step-icon i {
    font-size: 1rem;
  }
  
  .agent-indicator {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }
  
  .agent-icon {
    width: 3rem;
    height: 3rem;
  }
  
  .agent-icon i {
    font-size: 1.25rem;
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

/* ===== 애니메이션 효과 ===== */

.content-active {
  animation: slideInUp 0.4s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 테마 전환 애니메이션 */
.main-content-area,
.agent-icon,
.progress-step,
.theory-content,
.quiz-content,
.feedback-content,
.qna-content {
  transition: all 0.3s ease;
}

/* 호버 효과 */
.agent-icon:hover {
  transform: scale(1.05);
}

.progress-step:hover .step-icon {
  transform: scale(1.1);
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>