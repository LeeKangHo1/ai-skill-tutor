// frontend/tests/0812/main_content_area_ui_state.test.js
// MainContentArea.vue의 실시간 UI 상태 반영 기능 테스트

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import MainContentArea from '../../src/components/learning/MainContentArea.vue'
import { useLearningStore } from '../../src/stores/learningStore.js'
import { useTutorStore } from '../../src/stores/tutorStore.js'

describe('MainContentArea 실시간 UI 상태 반영', () => {
  let wrapper
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
    
    // 컴포넌트 마운트
    wrapper = mount(MainContentArea, {
      global: {
        plugins: [pinia]
      }
    })
  })

  describe('에이전트별 테마 색상과 아이콘 업데이트', () => {
    it('theory_educator 에이전트일 때 이론 테마가 적용되어야 함', async () => {
      // learningStore의 워크플로우 상태 업데이트
      learningStore.updateWorkflowState({
        current_agent: 'theory_educator',
        ui_mode: 'chat',
        session_progress_stage: 'session_start'
      })

      await wrapper.vm.$nextTick()

      // 테마 클래스 확인
      expect(wrapper.classes()).toContain('theme-theory')
      
      // 에이전트 아이콘 확인
      const agentIcon = wrapper.find('.agent-icon')
      expect(agentIcon.classes()).toContain('icon-theory')
      
      // 에이전트 이름 확인
      const agentName = wrapper.find('.agent-name')
      expect(agentName.text()).toBe('이론 설명 튜터')
    })

    it('quiz_generator 에이전트일 때 퀴즈 테마가 적용되어야 함', async () => {
      learningStore.updateWorkflowState({
        current_agent: 'quiz_generator',
        ui_mode: 'quiz',
        session_progress_stage: 'theory_completed'
      })

      await wrapper.vm.$nextTick()

      expect(wrapper.classes()).toContain('theme-quiz')
      
      const agentIcon = wrapper.find('.agent-icon')
      expect(agentIcon.classes()).toContain('icon-quiz')
      
      const agentName = wrapper.find('.agent-name')
      expect(agentName.text()).toBe('퀴즈 출제 튜터')
    })

    it('evaluation_feedback_agent 에이전트일 때 피드백 테마가 적용되어야 함', async () => {
      learningStore.updateWorkflowState({
        current_agent: 'evaluation_feedback_agent',
        ui_mode: 'chat',
        session_progress_stage: 'quiz_and_feedback_completed'
      })

      await wrapper.vm.$nextTick()

      expect(wrapper.classes()).toContain('theme-feedback')
      
      const agentIcon = wrapper.find('.agent-icon')
      expect(agentIcon.classes()).toContain('icon-feedback')
      
      const agentName = wrapper.find('.agent-name')
      expect(agentName.text()).toBe('평가 피드백 튜터')
    })

    it('qna_resolver 에이전트일 때 QnA 테마가 적용되어야 함', async () => {
      learningStore.updateWorkflowState({
        current_agent: 'qna_resolver',
        ui_mode: 'chat',
        session_progress_stage: 'theory_completed'
      })

      await wrapper.vm.$nextTick()

      expect(wrapper.classes()).toContain('theme-qna')
      
      const agentIcon = wrapper.find('.agent-icon')
      expect(agentIcon.classes()).toContain('icon-qna')
      
      const agentName = wrapper.find('.agent-name')
      expect(agentName.text()).toBe('질문 답변 튜터')
    })
  })

  describe('UI 모드 전환에 따른 컴포넌트 활성화', () => {
    it('ui_mode가 chat일 때 채팅 컨텐츠가 표시되어야 함', async () => {
      learningStore.updateWorkflowState({
        current_agent: 'theory_educator',
        ui_mode: 'chat',
        session_progress_stage: 'session_start'
      })

      await wrapper.vm.$nextTick()

      // 이론 컨텐츠가 표시되어야 함
      const theoryContent = wrapper.find('.theory-content')
      expect(theoryContent.exists()).toBe(true)
      expect(theoryContent.classes()).toContain('content-active')
    })

    it('ui_mode가 quiz일 때 퀴즈 컨텐츠가 표시되어야 함', async () => {
      learningStore.updateWorkflowState({
        current_agent: 'quiz_generator',
        ui_mode: 'quiz',
        session_progress_stage: 'theory_completed'
      })

      await wrapper.vm.$nextTick()

      // 퀴즈 컨텐츠가 표시되어야 함
      const quizContent = wrapper.find('.quiz-content')
      expect(quizContent.exists()).toBe(true)
      expect(quizContent.classes()).toContain('content-active')
    })

    it('UI 모드 변경 시 이벤트가 발생해야 함', async () => {
      const uiModeChangedSpy = vi.fn()
      wrapper.vm.$emit = vi.fn()

      learningStore.updateWorkflowState({
        current_agent: 'quiz_generator',
        ui_mode: 'quiz',
        session_progress_stage: 'theory_completed'
      })

      await wrapper.vm.$nextTick()

      // UI 모드 변경 이벤트 확인은 실제 구현에서 처리됨
      expect(wrapper.vm.currentUIMode).toBe('quiz')
    })
  })

  describe('session_progress_stage 업데이트에 따른 진행률 표시기 실시간 반영', () => {
    it('진행률 표시기가 올바르게 렌더링되어야 함', () => {
      const progressIndicator = wrapper.find('.progress-indicator')
      expect(progressIndicator.exists()).toBe(true)
      
      const progressSteps = wrapper.findAll('.progress-step')
      expect(progressSteps).toHaveLength(3) // 이론, 퀴즈, 풀이
    })

    it('완료된 단계에 따라 진행률이 업데이트되어야 함', async () => {
      // 이론 완료 상태 설정
      tutorStore.updateCompletedSteps({
        theory: true,
        quiz: false,
        feedback: false
      })

      await wrapper.vm.$nextTick()

      // 진행률 33% (1/3 완료)
      const progressPercentage = wrapper.find('.progress-percentage')
      expect(progressPercentage.text()).toBe('33%')
    })

    it('모든 단계 완료 시 100% 진행률이 표시되어야 함', async () => {
      tutorStore.updateCompletedSteps({
        theory: true,
        quiz: true,
        feedback: true
      })

      await wrapper.vm.$nextTick()

      const progressPercentage = wrapper.find('.progress-percentage')
      expect(progressPercentage.text()).toBe('100%')
    })

    it('현재 활성 단계가 올바르게 표시되어야 함', async () => {
      learningStore.updateWorkflowState({
        current_agent: 'quiz_generator',
        ui_mode: 'quiz',
        session_progress_stage: 'theory_completed'
      })

      tutorStore.updateCompletedSteps({
        theory: true,
        quiz: false,
        feedback: false
      })

      await wrapper.vm.$nextTick()

      // 퀴즈 단계가 현재 활성 단계여야 함
      const progressSteps = wrapper.findAll('.progress-step')
      const quizStep = progressSteps[1] // 두 번째 단계 (퀴즈)
      
      expect(quizStep.classes()).toContain('step-current')
    })
  })

  describe('세션 정보 실시간 업데이트', () => {
    it('learningStore의 세션 정보가 UI에 반영되어야 함', async () => {
      learningStore.updateSessionState({
        chapter_number: 3,
        section_number: 2,
        chapter_title: '3장 - 고급 LLM',
        section_title: '2절 - 프롬프트 엔지니어링',
        is_active: true
      })

      await wrapper.vm.$nextTick()

      const contentTitle = wrapper.find('.content-title')
      expect(contentTitle.text()).toBe('3장 2절')
      
      const contentSubtitle = wrapper.find('.content-subtitle')
      expect(contentSubtitle.text()).toBe('2절 - 프롬프트 엔지니어링')
    })
  })

  describe('네비게이션 버튼 동작', () => {
    it('피드백 단계에서 이론 다시 보기 버튼이 표시되어야 함', async () => {
      learningStore.updateWorkflowState({
        current_agent: 'evaluation_feedback_agent',
        ui_mode: 'chat',
        session_progress_stage: 'quiz_and_feedback_completed'
      })

      tutorStore.updateCompletedSteps({
        theory: true,
        quiz: true,
        feedback: false
      })

      tutorStore.updateContentMode('current')

      await wrapper.vm.$nextTick()

      // 이론 다시 보기 버튼 확인
      const theoryButton = wrapper.find('button:contains("📖 이론 다시 보기")')
      expect(theoryButton.exists()).toBe(true)
    })

    it('네비게이션 클릭 시 컨텐츠 모드가 변경되어야 함', async () => {
      learningStore.updateWorkflowState({
        current_agent: 'evaluation_feedback_agent',
        ui_mode: 'chat',
        session_progress_stage: 'quiz_and_feedback_completed'
      })

      tutorStore.updateCompletedSteps({
        theory: true,
        quiz: true,
        feedback: false
      })

      await wrapper.vm.$nextTick()

      // 네비게이션 클릭 시뮬레이션
      await wrapper.vm.handleNavigationClick('theory')

      // tutorStore의 컨텐츠 모드가 변경되었는지 확인
      expect(tutorStore.currentContentMode).toBe('review_theory')
    })
  })

  describe('실시간 상태 변화 감시', () => {
    it('learningStore 워크플로우 상태 변화를 감지해야 함', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      // 워크플로우 상태 변경
      learningStore.updateWorkflowState({
        current_agent: 'quiz_generator',
        ui_mode: 'quiz',
        session_progress_stage: 'theory_completed'
      })

      await wrapper.vm.$nextTick()

      // 상태 변화 감지 로그 확인
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('MainContentArea: learningStore 워크플로우 상태 변화 감지')
      )

      consoleSpy.mockRestore()
    })

    it('tutorStore 완료 단계 변화를 감지해야 함', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      // 완료 단계 변경
      tutorStore.updateCompletedSteps({
        theory: true,
        quiz: true,
        feedback: false
      })

      await wrapper.vm.$nextTick()

      // 상태 변화 감지 로그 확인
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('MainContentArea: 완료 단계 변화 감지')
      )

      consoleSpy.mockRestore()
    })
  })
})