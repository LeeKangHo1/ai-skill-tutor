// frontend/tests/0812/integration_workflow.test.js
// 전체 학습 워크플로우 통합 테스트
// 세션 시작부터 완료까지의 전체 플로우를 검증하고 에이전트 전환, UI 모드 변경, 컨텐츠 표시를 테스트

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useLearningStore } from '@/stores/learningStore'
import { useTutorStore } from '@/stores/tutorStore'
import LearningPage from '@/views/learning/LearningPage.vue'
import MainContentArea from '@/components/learning/MainContentArea.vue'
import ChatInteraction from '@/components/learning/ChatInteraction.vue'
import QuizInteraction from '@/components/learning/QuizInteraction.vue'

// 테스트 유틸리티 함수들
const createTestWrapper = (component, props = {}) => {
  return mount(component, {
    props,
    global: {
      plugins: [createPinia()]
    }
  })
}

const waitForNextTick = () => new Promise(resolve => setTimeout(resolve, 0))
const waitForApiCall = (ms = 100) => new Promise(resolve => setTimeout(resolve, ms))

// 모의 API 응답 데이터
const mockApiResponses = {
  sessionStart: {
    success: true,
    data: {
      session_info: {
        session_id: 'test_session_123',
        chapter_number: 2,
        section_number: 1,
        chapter_title: '2장 - LLM 기초',
        section_title: '1절 - 기본 개념',
        estimated_duration: '15분'
      },
      workflow_response: {
        current_agent: 'theory_educator',
        session_progress_stage: 'session_start',
        ui_mode: 'chat',
        content: {
          type: 'theory',
          title: 'LLM 기본 개념',
          content: '대규모 언어 모델(LLM)에 대해 학습해보겠습니다.',
          key_points: ['대규모 데이터 학습', '언어 이해 능력', '텍스트 생성']
        }
      }
    }
  },
  
  messageToQuiz: {
    success: true,
    data: {
      workflow_response: {
        current_agent: 'quiz_generator',
        session_progress_stage: 'theory_completed',
        ui_mode: 'quiz',
        content: {
          type: 'quiz',
          question: 'LLM의 정의는 무엇인가요?',
          quiz_type: 'multiple_choice',
          options: ['대규모 언어 모델', '작은 언어 모델', '번역 모델', '이미지 모델'],
          hint: 'Large Language Model의 줄임말입니다.'
        }
      }
    }
  },
  
  quizSubmit: {
    success: true,
    data: {
      evaluation_result: {
        is_correct: true,
        score: 100,
        feedback: '정답입니다! 잘 이해하고 계시네요.',
        explanation: 'LLM은 Large Language Model의 줄임말로 대규모 언어 모델을 의미합니다.'
      },
      workflow_response: {
        current_agent: 'evaluation_feedback_agent',
        session_progress_stage: 'quiz_and_feedback_completed',
        ui_mode: 'chat',
        content: {
          type: 'feedback',
          title: '평가 완료',
          content: '이번 섹션을 성공적으로 완료했습니다!',
          next_step_decision: 'proceed'
        }
      }
    }
  },
  
  sessionComplete: {
    success: true,
    data: {
      session_completion: {
        completed_at: new Date().toISOString(),
        final_score: 100,
        session_summary: {
          chapter_number: 2,
          section_number: 1,
          total_duration: '12분',
          concepts_learned: ['LLM 기본 개념', '언어 모델의 특징']
        },
        next_chapter: 2,
        next_section: 2,
        next_chapter_title: '2장 - LLM 기초',
        next_section_title: '2절 - LLM 활용 방법',
        proceed_options: {
          can_proceed: true,
          can_retry: true,
          can_dashboard: true
        }
      }
    }
  }
}

describe('통합 워크플로우 테스트', () => {
  let learningStore
  let tutorStore
  let pinia

  beforeEach(() => {
    // Pinia 설정
    pinia = createPinia()
    setActivePinia(pinia)
    
    // Store 인스턴스 생성
    learningStore = useLearningStore()
    tutorStore = useTutorStore()
    
    // learningService 모킹
    vi.mock('@/services/learningService', () => ({
      default: {
        startLearningSession: vi.fn(),
        sendSessionMessage: vi.fn(),
        submitQuizAnswer: vi.fn(),
        completeSession: vi.fn()
      }
    }))
  })

  afterEach(() => {
    vi.clearAllMocks()
    learningStore.resetSessionState()
    tutorStore.resetSession()
  })

  describe('1. 전체 학습 워크플로우 테스트', () => {
    it('세션 시작부터 완료까지 전체 플로우가 정상 동작해야 함', async () => {
      // learningService 모킹 설정
      const { default: learningService } = await import('@/services/learningService')
      
      learningService.startLearningSession.mockResolvedValue(mockApiResponses.sessionStart)
      learningService.sendSessionMessage.mockResolvedValue(mockApiResponses.messageToQuiz)
      learningService.submitQuizAnswer.mockResolvedValue(mockApiResponses.quizSubmit)
      learningService.completeSession.mockResolvedValue(mockApiResponses.sessionComplete)

      // 1단계: 세션 시작
      console.log('🚀 1단계: 세션 시작 테스트')
      const startResult = await learningStore.startSession(2, 1, '학습을 시작합니다')
      
      expect(startResult.success).toBe(true)
      expect(learningStore.isSessionActive).toBe(true)
      expect(learningStore.sessionState.session_id).toBe('test_session_123')
      expect(learningStore.workflowState.current_agent).toBe('theory_educator')
      expect(learningStore.workflowState.ui_mode).toBe('chat')
      expect(tutorStore.currentAgent).toBe('theory_educator')
      expect(tutorStore.currentUIMode).toBe('chat')

      await waitForNextTick()

      // 2단계: 메시지 전송 (이론 → 퀴즈 전환)
      console.log('💬 2단계: 메시지 전송 및 퀴즈 모드 전환 테스트')
      const messageResult = await learningStore.sendMessage('다음 단계로 넘어가주세요')
      
      expect(messageResult.success).toBe(true)
      expect(learningStore.workflowState.current_agent).toBe('quiz_generator')
      expect(learningStore.workflowState.ui_mode).toBe('quiz')
      expect(learningStore.workflowState.session_progress_stage).toBe('theory_completed')
      expect(tutorStore.currentAgent).toBe('quiz_generator')
      expect(tutorStore.currentUIMode).toBe('quiz')
      expect(tutorStore.completedSteps.theory).toBe(true)

      await waitForNextTick()

      // 3단계: 퀴즈 답안 제출
      console.log('📝 3단계: 퀴즈 답안 제출 및 피드백 테스트')
      const quizResult = await learningStore.submitQuiz('대규모 언어 모델')
      
      expect(quizResult.success).toBe(true)
      expect(learningStore.workflowState.current_agent).toBe('evaluation_feedback_agent')
      expect(learningStore.workflowState.ui_mode).toBe('chat')
      expect(learningStore.workflowState.session_progress_stage).toBe('quiz_and_feedback_completed')
      expect(learningStore.workflowState.evaluation_result.is_correct).toBe(true)
      expect(tutorStore.currentAgent).toBe('evaluation_feedback_agent')
      expect(tutorStore.currentUIMode).toBe('chat')
      expect(tutorStore.completedSteps.quiz).toBe(true)
      expect(tutorStore.completedSteps.feedback).toBe(true)

      await waitForNextTick()

      // 4단계: 세션 완료
      console.log('✅ 4단계: 세션 완료 테스트')
      const completeResult = await learningStore.completeSession('proceed')
      
      expect(completeResult.success).toBe(true)
      expect(learningStore.sessionState.is_active).toBe(false)
      expect(learningStore.isSessionCompleted).toBe(true)
      expect(learningStore.sessionState.final_score).toBe(100)
      expect(learningStore.sessionState.next_chapter).toBe(2)
      expect(learningStore.sessionState.next_section).toBe(2)

      console.log('🎉 전체 워크플로우 테스트 완료!')
    })

    it('에러 발생 시 적절한 에러 처리가 되어야 함', async () => {
      const { default: learningService } = await import('@/services/learningService')
      
      // 네트워크 에러 시뮬레이션
      learningService.startLearningSession.mockResolvedValue({
        success: false,
        error: '네트워크 연결을 확인해주세요.',
        type: 'network',
        retry: true
      })

      const result = await learningStore.startSession(2, 1, '테스트')
      
      expect(result.success).toBe(false)
      expect(learningStore.hasError).toBe(true)
      expect(learningStore.errorState.network_error).toBe(true)
      expect(learningStore.errorState.can_retry).toBe(true)
      expect(learningStore.isSessionActive).toBe(false)
    })
  })

  describe('2. 에이전트 전환 및 UI 상태 동기화 테스트', () => {
    it('에이전트 변경 시 tutorStore와 learningStore가 동기화되어야 함', async () => {
      // 초기 상태 설정
      learningStore.updateWorkflowState({
        current_agent: 'theory_educator',
        ui_mode: 'chat',
        session_progress_stage: 'session_start'
      })

      await waitForNextTick()

      // tutorStore가 자동으로 동기화되었는지 확인
      expect(tutorStore.currentAgent).toBe('theory_educator')
      expect(tutorStore.currentUIMode).toBe('chat')
      expect(tutorStore.sessionProgressStage).toBe('session_start')

      // 에이전트 변경 테스트
      const agentTransitions = [
        { agent: 'quiz_generator', expectedUIMode: 'quiz', expectedProgress: 'theory_completed' },
        { agent: 'evaluation_feedback_agent', expectedUIMode: 'chat', expectedProgress: 'quiz_and_feedback_completed' },
        { agent: 'qna_resolver', expectedUIMode: 'chat', expectedProgress: 'quiz_and_feedback_completed' }
      ]

      for (const transition of agentTransitions) {
        learningStore.updateWorkflowState({
          current_agent: transition.agent,
          ui_mode: transition.expectedUIMode,
          session_progress_stage: transition.expectedProgress
        })

        await waitForNextTick()

        expect(tutorStore.currentAgent).toBe(transition.agent)
        expect(tutorStore.currentUIMode).toBe(transition.expectedUIMode)
        
        // 완료 단계 확인
        if (transition.agent === 'quiz_generator') {
          expect(tutorStore.completedSteps.theory).toBe(true)
        }
        if (transition.agent === 'evaluation_feedback_agent') {
          expect(tutorStore.completedSteps.quiz).toBe(true)
          expect(tutorStore.completedSteps.feedback).toBe(true)
        }
      }
    })

    it('UI 모드 변경이 올바르게 반영되어야 함', async () => {
      const uiModeTests = [
        { mode: 'chat', expectedQuizMode: false, expectedChatMode: true },
        { mode: 'quiz', expectedQuizMode: true, expectedChatMode: false }
      ]

      for (const test of uiModeTests) {
        learningStore.updateWorkflowState({
          ui_mode: test.mode
        })

        await waitForNextTick()

        expect(tutorStore.currentUIMode).toBe(test.mode)
        expect(tutorStore.isQuizMode).toBe(test.expectedQuizMode)
        expect(tutorStore.isChatMode).toBe(test.expectedChatMode)
      }
    })
  })

  describe('3. 컨텐츠 표시 및 처리 테스트', () => {
    it('이론 컨텐츠가 올바르게 처리되어야 함', async () => {
      const theoryContent = {
        type: 'theory',
        title: 'LLM 기본 개념',
        content: '대규모 언어 모델에 대해 학습합니다.',
        key_points: ['대규모 데이터', '언어 이해', '텍스트 생성']
      }

      learningStore.updateWorkflowState({
        current_agent: 'theory_educator',
        ui_mode: 'chat',
        content: theoryContent
      })

      await waitForNextTick()

      // tutorStore의 메인 컨텐츠 확인
      expect(tutorStore.mainContent.content_type).toBe('theory')
      expect(tutorStore.mainContent.title).toBe('LLM 기본 개념')
      expect(tutorStore.mainContent.content).toBe('대규모 언어 모델에 대해 학습합니다.')

      // 채팅 히스토리에 추가되었는지 확인
      const lastMessage = tutorStore.chatHistory[tutorStore.chatHistory.length - 1]
      expect(lastMessage.type).toBe('theory')
      expect(lastMessage.message).toBe('대규모 언어 모델에 대해 학습합니다.')
    })

    it('퀴즈 컨텐츠가 올바르게 처리되어야 함', async () => {
      const quizContent = {
        type: 'quiz',
        question: 'LLM의 정의는?',
        quiz_type: 'multiple_choice',
        options: ['대규모 언어 모델', '작은 언어 모델'],
        hint: 'Large Language Model의 줄임말입니다.'
      }

      learningStore.updateWorkflowState({
        current_agent: 'quiz_generator',
        ui_mode: 'quiz',
        content: quizContent
      })

      await waitForNextTick()

      // tutorStore의 퀴즈 데이터 확인
      expect(tutorStore.quizData.question).toBe('LLM의 정의는?')
      expect(tutorStore.quizData.type).toBe('multiple_choice')
      expect(tutorStore.quizData.options).toEqual(['대규모 언어 모델', '작은 언어 모델'])
      expect(tutorStore.quizData.hint).toBe('Large Language Model의 줄임말입니다.')
      expect(tutorStore.currentQuizInfo.is_quiz_active).toBe(true)
    })

    it('평가 결과가 올바르게 처리되어야 함', async () => {
      const evaluationResult = {
        is_correct: true,
        score: 100,
        feedback: '정답입니다!',
        explanation: '올바른 답변입니다.'
      }

      learningStore.workflowState.evaluation_result = evaluationResult
      tutorStore.processEvaluationResult(evaluationResult)

      await waitForNextTick()

      // 퀴즈 상태 업데이트 확인
      expect(tutorStore.currentQuizInfo.is_answer_submitted).toBe(true)
      expect(tutorStore.currentQuizInfo.score).toBe(100)

      // 피드백 메시지가 채팅에 추가되었는지 확인
      const lastMessage = tutorStore.chatHistory[tutorStore.chatHistory.length - 1]
      expect(lastMessage.type).toBe('evaluation')
      expect(lastMessage.message).toBe('정답입니다!')
      expect(lastMessage.metadata.is_correct).toBe(true)
    })

    it('QnA 컨텐츠가 올바르게 처리되어야 함', async () => {
      const qnaContent = {
        type: 'qna',
        content: '질문에 대한 답변입니다.',
        question: '사용자의 질문',
        answer: '상세한 답변'
      }

      learningStore.updateWorkflowState({
        current_agent: 'qna_resolver',
        ui_mode: 'chat',
        content: qnaContent
      })

      await waitForNextTick()

      // QnA 응답이 채팅에 추가되었는지 확인
      const lastMessage = tutorStore.chatHistory[tutorStore.chatHistory.length - 1]
      expect(lastMessage.type).toBe('qna')
      expect(lastMessage.message).toBe('질문에 대한 답변입니다.')
    })
  })

  describe('4. 컴포넌트 통합 테스트', () => {
    it('LearningPage가 store와 올바르게 연동되어야 함', async () => {
      const wrapper = createTestWrapper(LearningPage)
      
      // Store 인스턴스 확인
      expect(wrapper.vm.learningStore).toBeDefined()
      expect(wrapper.vm.tutorStore).toBeDefined()

      // 초기 상태 확인
      expect(wrapper.vm.learningStore.isSessionActive).toBe(false)
      expect(wrapper.vm.tutorStore.currentAgent).toBe('theory_educator')
    })

    it('MainContentArea가 에이전트 변경에 따라 UI를 업데이트해야 함', async () => {
      const wrapper = createTestWrapper(MainContentArea)

      // 에이전트별 테마 변경 테스트
      const agentThemes = [
        { agent: 'theory_educator', expectedClass: 'theory-educator' },
        { agent: 'quiz_generator', expectedClass: 'quiz-generator' },
        { agent: 'evaluation_feedback_agent', expectedClass: 'evaluation-feedback' },
        { agent: 'qna_resolver', expectedClass: 'qna-resolver' }
      ]

      for (const theme of agentThemes) {
        tutorStore.updateAgent(theme.agent)
        await waitForNextTick()

        // 에이전트별 CSS 클래스가 적용되었는지 확인
        expect(wrapper.classes()).toContain(theme.expectedClass)
      }
    })

    it('ChatInteraction과 QuizInteraction이 UI 모드에 따라 전환되어야 함', async () => {
      const wrapper = createTestWrapper(MainContentArea)

      // 채팅 모드 테스트
      tutorStore.updateUIMode('chat')
      await waitForNextTick()

      expect(wrapper.findComponent(ChatInteraction).exists()).toBe(true)
      expect(wrapper.findComponent(QuizInteraction).exists()).toBe(false)

      // 퀴즈 모드 테스트
      tutorStore.updateUIMode('quiz')
      await waitForNextTick()

      expect(wrapper.findComponent(ChatInteraction).exists()).toBe(false)
      expect(wrapper.findComponent(QuizInteraction).exists()).toBe(true)
    })
  })

  describe('5. 세션 완료 및 다음 단계 처리 테스트', () => {
    it('세션 완료 조건 확인이 올바르게 동작해야 함', async () => {
      // 모든 단계 완료 설정
      tutorStore.updateCompletedSteps({
        theory: true,
        quiz: true,
        feedback: true
      })
      tutorStore.updateSessionProgress('quiz_and_feedback_completed')

      await waitForNextTick()

      expect(tutorStore.isSessionReadyToComplete).toBe(true)
    })

    it('다음 단계 정보가 올바르게 제공되어야 함', async () => {
      // 세션 완료 상태 설정
      learningStore.sessionState.is_active = false
      learningStore.sessionState.completed_at = new Date().toISOString()
      learningStore.sessionState.next_chapter = 2
      learningStore.sessionState.next_section = 2

      await waitForNextTick()

      const nextStepInfo = learningStore.nextStepInfo
      expect(nextStepInfo.has_next_step).toBe(true)
      expect(nextStepInfo.next_chapter).toBe(2)
      expect(nextStepInfo.next_section).toBe(2)
    })
  })

  describe('6. 에러 처리 및 복구 테스트', () => {
    it('API 에러 발생 시 적절한 에러 상태가 설정되어야 함', async () => {
      const errorTypes = [
        { type: 'network', expectedState: 'network_error' },
        { type: 'auth', expectedState: 'auth_error' },
        { type: 'server', expectedState: 'server_error' },
        { type: 'validation', expectedState: 'validation_error' }
      ]

      for (const errorTest of errorTypes) {
        learningStore.clearErrors()
        
        const mockError = {
          success: false,
          error: `${errorTest.type} 에러 발생`,
          type: errorTest.type,
          retry: true
        }

        learningStore.handleApiError(mockError, 'test')

        expect(learningStore.hasError).toBe(true)
        expect(learningStore.errorState[errorTest.expectedState]).toBe(true)
        expect(learningStore.errorState.can_retry).toBe(true)
      }
    })

    it('재시도 기능이 올바르게 동작해야 함', async () => {
      const { default: learningService } = await import('@/services/learningService')
      
      // 첫 번째 호출은 실패, 두 번째 호출은 성공
      learningService.startLearningSession
        .mockResolvedValueOnce({
          success: false,
          error: '네트워크 에러',
          type: 'network',
          retry: true
        })
        .mockResolvedValueOnce(mockApiResponses.sessionStart)

      // 첫 번째 시도 (실패)
      const firstResult = await learningStore.startSession(2, 1, '테스트')
      expect(firstResult.success).toBe(false)
      expect(learningStore.canRetry).toBe(true)

      // 재시도 (성공)
      const retryResult = await learningStore.retryLastAction('startSession', 2, 1, '테스트')
      expect(retryResult.success).toBe(true)
      expect(learningStore.isSessionActive).toBe(true)
    })
  })

  describe('7. 성능 및 메모리 테스트', () => {
    it('대량의 채팅 메시지 처리 시 성능이 유지되어야 함', async () => {
      const startTime = Date.now()
      
      // 100개의 메시지 추가
      for (let i = 0; i < 100; i++) {
        tutorStore.addChatMessage({
          sender: '튜터',
          message: `테스트 메시지 ${i}`,
          type: 'system'
        })
      }

      const endTime = Date.now()
      const processingTime = endTime - startTime

      expect(tutorStore.chatHistory.length).toBe(101) // 초기 메시지 1개 + 100개
      expect(processingTime).toBeLessThan(1000) // 1초 이내 처리
    })

    it('Store 상태 리셋이 메모리 누수 없이 동작해야 함', async () => {
      // 대량의 데이터 설정
      for (let i = 0; i < 50; i++) {
        tutorStore.addChatMessage({
          sender: '튜터',
          message: `대량 메시지 ${i}`,
          type: 'system'
        })
      }

      learningStore.updateWorkflowState({
        current_agent: 'theory_educator',
        content: { type: 'theory', content: '대량 컨텐츠'.repeat(100) }
      })

      // 리셋 실행
      learningStore.resetSessionState()
      tutorStore.resetSession()

      // 상태가 초기화되었는지 확인
      expect(learningStore.sessionState.session_id).toBeNull()
      expect(learningStore.workflowState.current_agent).toBeNull()
      expect(tutorStore.chatHistory.length).toBe(1) // 초기 메시지만 남음
      expect(tutorStore.currentAgent).toBe('theory_educator')
    })
  })
})

// 추가 유틸리티 테스트
describe('테스트 유틸리티 검증', () => {
  it('Store 연동 상태 확인 기능이 올바르게 동작해야 함', () => {
    const learningStore = useLearningStore()
    const tutorStore = useTutorStore()

    // 동기화된 상태 설정
    learningStore.updateWorkflowState({
      current_agent: 'theory_educator',
      ui_mode: 'chat',
      session_progress_stage: 'session_start'
    })

    const connectionStatus = tutorStore.checkLearningStoreConnection()
    
    expect(connectionStatus.syncStatus.agentSync).toBe(true)
    expect(connectionStatus.syncStatus.uiModeSync).toBe(true)
    expect(connectionStatus.syncStatus.progressSync).toBe(true)
  })

  it('디버그 정보가 올바르게 제공되어야 함', () => {
    const learningStore = useLearningStore()
    const tutorStore = useTutorStore()

    const learningDebugInfo = {
      sessionState: learningStore.sessionState,
      apiState: learningStore.apiState,
      workflowState: learningStore.workflowState,
      errorState: learningStore.errorState
    }

    const tutorDebugInfo = tutorStore.getStateInfo()

    expect(learningDebugInfo.sessionState).toBeDefined()
    expect(learningDebugInfo.apiState).toBeDefined()
    expect(learningDebugInfo.workflowState).toBeDefined()
    expect(learningDebugInfo.errorState).toBeDefined()

    expect(tutorDebugInfo.currentAgent).toBeDefined()
    expect(tutorDebugInfo.currentUIMode).toBeDefined()
    expect(tutorDebugInfo.sessionInfo).toBeDefined()
  })
})