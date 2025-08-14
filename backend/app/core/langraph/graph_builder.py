# backend/app/core/langraph/graph_builder.py

from typing import Dict, Any, Literal
from langgraph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from app.core.langraph.state_manager import TutorState
from app.agents.learning_supervisor.learning_supervisor_agent import LearningSupervisor
from app.agents.theory_educator.theory_educator_agent import TheoryEducator
from app.agents.quiz_generator.quiz_generator_agent import QuizGenerator
from app.agents.evaluation_feedback.evaluation_feedback_agent import EvaluationFeedbackAgent
from app.agents.qna_resolver.qna_resolver_agent import qna_resolver_agent
from app.agents.session_manager.session_manager_agent import SessionManager


class TutorGraphBuilder:
    """
    AI 학습 튜터 LangGraph 워크플로우 빌더
    
    워크플로우 구조:
    START → learning_supervisor (입력처리) 
    → supervisor_router (라우팅 결정)
    → [theory_educator | quiz_generator | evaluation_feedback | qna_resolver | session_manager]
    → learning_supervisor (최종응답) 
    → END
    """
    
    def __init__(self):
        self.learning_supervisor = LearningSupervisor()
        self.theory_educator = TheoryEducator()
        self.quiz_generator = QuizGenerator()
        self.evaluation_feedback = EvaluationFeedbackAgent()
        self.session_manager = SessionManager()
        
    def build_graph(self) -> StateGraph:
        """
        LangGraph 워크플로우 그래프 구성
        
        Returns:
            컴파일된 StateGraph 객체
        """
        # StateGraph 생성 (TutorState 타입 지정)
        workflow = StateGraph(TutorState)
        
        # === 노드 등록 ===
        workflow.add_node("learning_supervisor_input", self._supervisor_input_node)
        workflow.add_node("theory_educator", self._theory_educator_node)
        workflow.add_node("quiz_generator", self._quiz_generator_node)
        workflow.add_node("evaluation_feedback", self._evaluation_feedback_node)
        workflow.add_node("qna_resolver", self._qna_resolver_node)
        workflow.add_node("session_manager", self._session_manager_node)
        workflow.add_node("learning_supervisor_output", self._supervisor_output_node)
        
        # === 엔트리 포인트 ===
        workflow.set_entry_point("learning_supervisor_input")
        
        # === 조건부 라우팅 간선 ===
        workflow.add_conditional_edges(
            "learning_supervisor_input",
            self._supervisor_router,
            {
                "theory_educator": "theory_educator",
                "quiz_generator": "quiz_generator", 
                "qna_resolver": "qna_resolver",
                "session_manager": "session_manager",
                "end": "learning_supervisor_output"
            }
        )
        
        # === 단순 간선 (에이전트 → 감독자) ===
        workflow.add_edge("theory_educator", "learning_supervisor_output")
        workflow.add_edge("qna_resolver", "learning_supervisor_output")
        workflow.add_edge("session_manager", "learning_supervisor_output")
        
        # === 퀴즈 → 평가 자동 연결 ===
        workflow.add_edge("quiz_generator", "evaluation_feedback")
        workflow.add_edge("evaluation_feedback", "learning_supervisor_output")
        
        # === 최종 종료 ===
        workflow.add_edge("learning_supervisor_output", END)
        
        return workflow
    
    def _supervisor_input_node(self, state: TutorState, config: RunnableConfig = None) -> TutorState:
        """
        LearningSupervisor 입력 처리 노드
        사용자 메시지 분석 및 의도 파악
        """
        print(f"[GraphBuilder] supervisor_input_node 실행")
        try:
            # 세션 단계에 따라 다른 처리
            session_stage = state.get("session_progress_stage", "session_start")
            
            if session_stage == "session_start":
                # 세션 시작 - 의도 분석 없이 바로 처리
                return self.learning_supervisor.process_user_input(state)
            else:
                # 질문 가능 단계 - 의도 분석 필요
                return self.learning_supervisor.process_user_input(state)
                
        except Exception as e:
            print(f"[GraphBuilder] supervisor_input_node 오류: {e}")
            # 오류 시 기본 처리
            state["user_intent"] = "next_step"
            return state
    
    def _theory_educator_node(self, state: TutorState, config: RunnableConfig = None) -> TutorState:
        """TheoryEducator 에이전트 노드 - 이론 설명 대본 생성"""
        print(f"[GraphBuilder] theory_educator_node 실행")
        try:
            return self.theory_educator.process(state)
        except Exception as e:
            print(f"[GraphBuilder] theory_educator_node 오류: {e}")
            return state
    
    def _quiz_generator_node(self, state: TutorState, config: RunnableConfig = None) -> TutorState:
        """QuizGenerator 에이전트 노드 - 퀴즈 생성 대본 생성"""
        print(f"[GraphBuilder] quiz_generator_node 실행")
        try:
            return self.quiz_generator.process(state)
        except Exception as e:
            print(f"[GraphBuilder] quiz_generator_node 오류: {e}")
            return state
    
    def _evaluation_feedback_node(self, state: TutorState, config: RunnableConfig = None) -> TutorState:
        """EvaluationFeedbackAgent 노드 - 평가 및 피드백 생성"""
        print(f"[GraphBuilder] evaluation_feedback_node 실행")
        try:
            return self.evaluation_feedback.process(state)
        except Exception as e:
            print(f"[GraphBuilder] evaluation_feedback_node 오류: {e}")
            return state
    
    def _qna_resolver_node(self, state: TutorState, config: RunnableConfig = None) -> TutorState:
        """QnAResolver 에이전트 노드 - 질문 답변 대본 생성"""
        print(f"[GraphBuilder] qna_resolver_node 실행")
        try:
            return qna_resolver_agent(state)
        except Exception as e:
            print(f"[GraphBuilder] qna_resolver_node 오류: {e}")
            return state
    
    def _session_manager_node(self, state: TutorState, config: RunnableConfig = None) -> TutorState:
        """SessionManager 에이전트 노드 - 세션 완료 처리"""
        print(f"[GraphBuilder] session_manager_node 실행")
        try:
            return self.session_manager.process(state)
        except Exception as e:
            print(f"[GraphBuilder] session_manager_node 오류: {e}")
            return state
    
    def _supervisor_output_node(self, state: TutorState, config: RunnableConfig = None) -> TutorState:
        """
        LearningSupervisor 출력 처리 노드
        에이전트 대본을 기반으로 최종 사용자 응답 생성
        """
        print(f"[GraphBuilder] supervisor_output_node 실행")
        try:
            return self.learning_supervisor.generate_final_response(state)
        except Exception as e:
            print(f"[GraphBuilder] supervisor_output_node 오류: {e}")
            return state
    
    def _supervisor_router(self, state: TutorState) -> Literal["theory_educator", "quiz_generator", "qna_resolver", "session_manager", "end"]:
        """
        Supervisor 라우터 - 다음 실행할 에이전트 결정
        
        Args:
            state: 현재 TutorState (user_intent가 설정된 상태)
            
        Returns:
            다음 노드 이름
        """
        try:
            user_intent = state.get("user_intent", "next_step")
            session_stage = state.get("session_progress_stage", "session_start")
            session_decision = state.get("session_decision_result", "")
            
            print(f"[Router] 라우팅 결정 - intent: {user_intent}, stage: {session_stage}, decision: {session_decision}")
            
            # 1. 퀴즈 답변 처리
            if user_intent == "quiz_answer":
                print("[Router] → evaluation_feedback (퀴즈 답변)")
                return "evaluation_feedback"
            
            # 2. 질문 답변 요청  
            if user_intent == "question":
                print("[Router] → qna_resolver (질문 답변)")
                return "qna_resolver"
            
            # 3. 세션 완료 처리 (평가 완료 후)
            if session_stage == "quiz_and_feedback_completed" and user_intent == "next_step":
                print("[Router] → session_manager (세션 완료)")
                return "session_manager"
            
            # 4. 다음 단계 진행
            if user_intent == "next_step":
                if session_stage == "session_start":
                    print("[Router] → theory_educator (세션 시작)")
                    return "theory_educator"
                elif session_stage == "theory_completed":
                    print("[Router] → quiz_generator (이론 완료 후)")
                    return "quiz_generator"
            
            # 5. 힌트 요청 (현재는 퀴즈 재생성으로 처리)
            if user_intent == "hint":
                print("[Router] → quiz_generator (힌트 요청)")
                return "quiz_generator"
            
            # 6. 기본값 - 직접 응답 생성
            print(f"[Router] → end (직접 응답, intent: {user_intent})")
            return "end"
            
        except Exception as e:
            print(f"[Router] 라우팅 오류: {e} - 기본값으로 end 반환")
            return "end"
    
    def compile_graph(self) -> Any:
        """
        그래프 컴파일 및 반환
        
        Returns:
            실행 가능한 컴파일된 그래프
        """
        workflow = self.build_graph()
        compiled_graph = workflow.compile()
        
        print("[GraphBuilder] LangGraph 워크플로우 컴파일 완료")
        return compiled_graph


# 전역 그래프 빌더 인스턴스
graph_builder = TutorGraphBuilder()

# 컴파일된 그래프 (앱 시작 시 한 번만 컴파일)
compiled_tutor_graph = None

def get_compiled_graph():
    """
    컴파일된 그래프 반환 (지연 로딩)
    
    Returns:
        컴파일된 LangGraph 워크플로우
    """
    global compiled_tutor_graph
    
    if compiled_tutor_graph is None:
        compiled_tutor_graph = graph_builder.compile_graph()
    
    return compiled_tutor_graph