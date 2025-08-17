# backend/app/core/langraph/__init__.py
"""
LangGraph 관련 핵심 구성 요소들 (v2.0)
워크플로우, 상태 관리, 그래프 빌더 등 LangGraph 시스템의 핵심 기능을 제공합니다.

v2.0 주요 변경사항:
- TutorState 퀴즈 필드 완전 재설계 (객관식/주관식 분리)
- 통합 워크플로우 지원 (하이브리드 UX)
- evaluation_feedback_agent 라우팅 수정
- AUTO_INCREMENT 세션 ID 지원
"""

from .workflow import WorkflowExecutor, workflow_executor, execute_tutor_workflow, execute_tutor_workflow_sync
from .state_manager import StateManager, state_manager, TutorState
from .graph_builder import TutorGraphBuilder, get_compiled_graph, rebuild_graph

__all__ = [
    'WorkflowExecutor', 'workflow_executor', 'execute_tutor_workflow', 'execute_tutor_workflow_sync', 
    'StateManager', 'state_manager', 'TutorState',
    'TutorGraphBuilder', 'get_compiled_graph', 'rebuild_graph'
]