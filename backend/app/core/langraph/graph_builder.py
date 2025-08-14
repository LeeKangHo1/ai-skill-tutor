# backend/app/core/langraph/graph_builder.py

import os
from typing import Any
from langgraph import StateGraph, END

from app.core.langraph.state_manager import TutorState
from app.agents.learning_supervisor.supervisor_router import supervisor_router
from app.agents import agent_nodes
from app.utils.common.graph_visualizer import save_tutor_workflow_graph


class TutorGraphBuilder:
    """
    AI 학습 튜터 LangGraph 워크플로우 빌더
    
    워크플로우 구조:
    learning_supervisor_input → supervisor_router → [agents] → learning_supervisor_output → END
    
    통합된 워크플로우:
    - 모든 에이전트가 learning_supervisor_output으로 연결
    - 퀴즈 답변 제출 시 evaluation_feedback으로 자동 라우팅
    - 일관된 응답 생성 프로세스
    """
    
    def __init__(self):
        pass
        
    def build_graph(self) -> StateGraph:
        """
        LangGraph 워크플로우 그래프 구성
        
        Returns:
            컴파일된 StateGraph 객체
        """
        # StateGraph 생성 (TutorState 타입 지정)
        workflow = StateGraph(TutorState)
        
        # === 노드 등록 (agent_nodes 딕셔너리에서 자동 등록) ===
        for name, node_func in agent_nodes.items():
            workflow.add_node(name, node_func)
        
        # === 엔트리 포인트 (START 노드 자동 생성) ===
        workflow.set_entry_point("learning_supervisor_input")
        
        # === 조건부 라우팅 간선 (기존 supervisor_router 사용) ===
        workflow.add_conditional_edges(
            "learning_supervisor_input",
            supervisor_router,
            {
                "theory_educator": "theory_educator",
                "quiz_generator": "quiz_generator",
                "evaluation_feedback": "evaluation_feedback", 
                "qna_resolver": "qna_resolver",
                "session_manager": "session_manager",
                "learning_supervisor_output": "learning_supervisor_output"
            }
        )
        
        # === 단순 간선 (에이전트 → 최종 응답) ===
        workflow.add_edge("theory_educator", "learning_supervisor_output")
        workflow.add_edge("quiz_generator", "learning_supervisor_output")
        workflow.add_edge("evaluation_feedback", "learning_supervisor_output")
        workflow.add_edge("qna_resolver", "learning_supervisor_output")
        workflow.add_edge("session_manager", "learning_supervisor_output")
        
        # === 최종 종료 ===
        workflow.add_edge("learning_supervisor_output", END)
        
        return workflow
    
    def compile_graph(self) -> Any:
        """
        그래프 컴파일 및 시각화 저장
        
        Returns:
            실행 가능한 컴파일된 그래프
        """
        workflow = self.build_graph()
        compiled_graph = workflow.compile()
        
        # 그래프 시각화 이미지 저장
        save_tutor_workflow_graph(compiled_graph)
        
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

def rebuild_graph():
    """
    그래프 재빌드 (개발/테스트용)
    
    Returns:
        새로 컴파일된 그래프
    """
    global compiled_tutor_graph
    compiled_tutor_graph = graph_builder.compile_graph()
    return compiled_tutor_graph