// frontend/tests/0812/test_quiz_interaction_api.js
// QuizInteraction.vue의 API 연동 기능 테스트

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import QuizInteraction from '../../src/components/learning/QuizInteraction.vue'
import { useLearningStore } from '../../src/stores/learningStore.js'
import { useTutorStore } from '../../src/stores/tutorStore.js'

describe('QuizInteraction API 연동 테스트', () => {
  let wrapper
  let learningStore
  let tutorStore
  
  beforeEach(() => {
    // Pinia 설정
    setActivePinia(createPinia())
    
    // Store 인스턴스 생성
    learningStore = useLearningStore()
    tutorStore = useTutorStore()
    
    // 기본 퀴즈 데이터
    const quizData = {
      question: 'LLM의 정의는 무엇인가요?',
      type: 'multiple_choice',
      options: [
        { value: '1', text: '대규모 언어 모델' },
        { value: '2', text: '작은 언어 모델' },
        { value: '3', text: '번역 모델' },
        { value: '4', text: '이미지 모델' }
      ],
      hint: 'Large Language Model의 줄임말입니다.'
    }
    
    // 컴포넌트 마운트
    wrapper = mount(QuizInteraction, {
      props: {
        quizData,
        isLoading: false,
        showProgress: true,
        allowRetry: true
      },
      global: {
        plugins: [createPinia()]
      }
    })
  })
  
  it('객관식 답안 제출 시 learningStore.submitQuiz 호출', async () => {
    // learningStore.submitQuiz 메서드 모킹
    const mockSubmitQuiz = vi.spyOn(learningStore, 'submitQuiz').mockResolvedValue({
      success: true,
      data: {
        evaluation_result: {
          is_correct: true,
          score: 100,
          feedback: '정답입니다!',
          explanation: 'LLM은 Large Language Model의 줄임말입니다.'
        },
        workflow_response: {
          current_agent: 'evaluation_feedback_agent',
          ui_mode: 'chat',
          content: {
            type: 'feedback',
            content: '잘했습니다!'
          }
        }
      }
    })
    
    // tutorStore 메서드 모킹
    const mockProcessEvaluationResult = vi.spyOn(tutorStore, 'processEvaluationResult')
    const mockUpdateFromWorkflowResponse = vi.spyOn(tutorStore, 'updateFromWorkflowResponse')
    
    // 답안 선택
    const firstOption = wrapper.find('.quiz-option')
    await firstOption.trigger('click')
    
    // 제출 버튼 클릭
    const submitButton = wrapper.find('.submit-btn')
    await submitButton.trigger('click')
    
    // API 호출 확인
    expect(mockSubmitQuiz).toHaveBeenCalledWith('1')
    
    // tutorStore 메서드 호출 확인
    expect(mockProcessEvaluationResult).toHaveBeenCalled()
    expect(mockUpdateFromWorkflowResponse).toHaveBeenCalled()
    
    // 평가 결과 표시 확인
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.evaluation-result').exists()).toBe(true)
    expect(wrapper.find('.result-status.correct').exists()).toBe(true)
  })
  
  it('주관식 답안 제출 시 learningStore.submitQuiz 호출', async () => {
    // 주관식 퀴즈 데이터로 변경
    await wrapper.setProps({
      quizData: {
        question: 'LLM에 대해 설명해주세요.',
        type: 'subjective',
        hint: '대규모 언어 모델에 대해 생각해보세요.'
      }
    })
    
    // learningStore.submitQuiz 메서드 모킹
    const mockSubmitQuiz = vi.spyOn(learningStore, 'submitQuiz').mockResolvedValue({
      success: true,
      data: {
        evaluation_result: {
          is_correct: true,
          score: 85,
          feedback: '좋은 답변입니다!',
          explanation: '핵심 개념을 잘 이해하고 있습니다.'
        }
      }
    })
    
    // 주관식 답안 입력
    const subjectiveInput = wrapper.find('.subjective-input')
    await subjectiveInput.setValue('LLM은 대규모 언어 모델로, 자연어 처리에 사용됩니다.')
    
    // 제출 버튼 클릭
    const submitButton = wrapper.find('.submit-btn')
    await submitButton.trigger('click')
    
    // API 호출 확인
    expect(mockSubmitQuiz).toHaveBeenCalledWith('LLM은 대규모 언어 모델로, 자연어 처리에 사용됩니다.')
  })
  
  it('API 에러 발생 시 에러 처리', async () => {
    // learningStore.submitQuiz 메서드가 에러를 반환하도록 모킹
    const mockSubmitQuiz = vi.spyOn(learningStore, 'submitQuiz').mockResolvedValue({
      success: false,
      error: '네트워크 연결을 확인해주세요.'
    })
    
    // tutorStore.addChatMessage 모킹
    const mockAddChatMessage = vi.spyOn(tutorStore, 'addChatMessage')
    
    // 답안 선택 및 제출
    const firstOption = wrapper.find('.quiz-option')
    await firstOption.trigger('click')
    
    const submitButton = wrapper.find('.submit-btn')
    await submitButton.trigger('click')
    
    // 에러 메시지가 채팅에 추가되었는지 확인
    expect(mockAddChatMessage).toHaveBeenCalledWith({
      sender: '시스템',
      message: '퀴즈 제출 중 오류가 발생했습니다: 네트워크 연결을 확인해주세요.',
      type: 'error',
      timestamp: expect.any(Date)
    })
    
    // 제출 상태가 되돌려졌는지 확인
    expect(wrapper.vm.isSubmitted).toBe(false)
  })
  
  it('힌트 요청 시 채팅에 힌트 메시지 추가', async () => {
    // tutorStore.addChatMessage 모킹
    const mockAddChatMessage = vi.spyOn(tutorStore, 'addChatMessage')
    
    // 힌트 버튼 클릭
    const hintButton = wrapper.find('.hint-btn')
    await hintButton.trigger('click')
    
    // 힌트가 채팅에 추가되었는지 확인
    expect(mockAddChatMessage).toHaveBeenCalledWith({
      sender: '튜터',
      message: '💡 힌트: Large Language Model의 줄임말입니다.',
      type: 'hint',
      timestamp: expect.any(Date)
    })
    
    // 힌트 표시 확인
    expect(wrapper.find('.hint-container').exists()).toBe(true)
    expect(wrapper.vm.hintUsed).toBe(true)
  })
  
  it('learningStore 로딩 상태에 따른 UI 비활성화', async () => {
    // learningStore 로딩 상태 설정
    learningStore.setApiLoading(true)
    
    await wrapper.vm.$nextTick()
    
    // 모든 인터랙션 요소가 비활성화되었는지 확인
    expect(wrapper.find('.submit-btn').attributes('disabled')).toBeDefined()
    expect(wrapper.find('.hint-btn').attributes('disabled')).toBeDefined()
    
    // 로딩 스피너 표시 확인
    expect(wrapper.find('.button-spinner').exists()).toBe(true)
  })
  
  it('평가 결과 표시 및 다시 풀기 기능', async () => {
    // 평가 결과 설정
    await wrapper.setData({
      evaluationResult: {
        is_correct: false,
        score: 0,
        feedback: '틀렸습니다. 다시 시도해보세요.',
        explanation: '정답은 1번입니다.'
      },
      showEvaluationResult: true,
      isSubmitted: true
    })
    
    await wrapper.vm.$nextTick()
    
    // 평가 결과 표시 확인
    expect(wrapper.find('.evaluation-result').exists()).toBe(true)
    expect(wrapper.find('.result-status.incorrect').exists()).toBe(true)
    expect(wrapper.find('.feedback-text').text()).toBe('틀렸습니다. 다시 시도해보세요.')
    
    // 다시 풀기 버튼 클릭
    const retryButton = wrapper.find('.result-actions .btn-outline')
    await retryButton.trigger('click')
    
    // 상태 초기화 확인
    expect(wrapper.vm.isSubmitted).toBe(false)
    expect(wrapper.vm.showEvaluationResult).toBe(false)
    expect(wrapper.vm.evaluationResult).toBe(null)
  })
})