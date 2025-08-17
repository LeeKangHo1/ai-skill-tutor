# backend/app/core/langraph/workflow.py
# v2.0 업데이트: 통합 워크플로우 지원, 하이브리드 UX 처리

import asyncio
import logging
from typing import Dict, Any, Optional, AsyncIterator
from datetime import datetime

from app.core.langraph.state_manager import TutorState, state_manager
from app.core.langraph.graph_builder import get_compiled_graph
from app.utils.common.graph_visualizer import save_tutor_workflow_graph


class WorkflowExecutor:
    """
    LangGraph 워크플로우 실행 관리자
    
    주요 기능:
    1. 컴파일된 그래프 실행
    2. State 직렬화/역직렬화
    3. 스트리밍 출력 처리
    4. 오류 처리 및 복구
    5. 실행 통계 및 로깅
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0
        }
    
    async def execute_workflow(
        self, 
        state: TutorState,
        stream: bool = False,
        config: Optional[Dict[str, Any]] = None
    ) -> TutorState:
        """
        워크플로우 실행 (비동기)
        
        Args:
            state: 입력 TutorState
            stream: 스트리밍 모드 사용 여부
            config: 실행 설정 (thread_id 등)
            
        Returns:
            실행 완료된 TutorState
        """
        start_time = datetime.now()
        execution_id = f"exec_{int(start_time.timestamp())}"
        
        try:
            self.logger.info(f"[{execution_id}] 워크플로우 실행 시작")
            self._log_execution_start(state, execution_id)
            
            # 컴파일된 그래프 가져오기
            compiled_graph = get_compiled_graph()
            
            # State 유효성 검증
            if not state_manager.validate_state(state):
                raise ValueError("Invalid TutorState provided")
            
            # 실행 설정 준비
            runtime_config = self._prepare_runtime_config(config, execution_id)
            
            # 워크플로우 실행
            if stream:
                final_state = await self._execute_with_streaming(
                    compiled_graph, state, runtime_config
                )
            else:
                final_state = await self._execute_standard(
                    compiled_graph, state, runtime_config
                )
            
            # 실행 통계 업데이트
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(True, execution_time)
            
            self.logger.info(f"[{execution_id}] 워크플로우 실행 완료 ({execution_time:.2f}s)")
            return final_state
            
        except Exception as e:
            # 실행 실패 통계 업데이트
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(False, execution_time)
            
            self.logger.error(f"[{execution_id}] 워크플로우 실행 실패: {str(e)}")
            return self._handle_execution_error(state, str(e))
    
    def execute_workflow_sync(
        self, 
        state: TutorState,
        config: Optional[Dict[str, Any]] = None
    ) -> TutorState:
        """
        워크플로우 동기 실행 (웹 API용)
        
        Args:
            state: 입력 TutorState
            config: 실행 설정
            
        Returns:
            실행 완료된 TutorState
        """
        try:
            # 비동기 실행을 동기로 래핑
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.execute_workflow(state, stream=False, config=config)
                )
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"동기 워크플로우 실행 실패: {str(e)}")
            return self._handle_execution_error(state, str(e))
    
    async def _execute_standard(
        self, 
        compiled_graph: Any, 
        state: TutorState,
        config: Dict[str, Any]
    ) -> TutorState:
        """
        표준 워크플로우 실행
        
        Args:
            compiled_graph: 컴파일된 LangGraph
            state: 입력 State
            config: 실행 설정
            
        Returns:
            실행 완료된 State
        """
        try:
            # LangGraph 실행
            result = await compiled_graph.ainvoke(state, config=config)
            
            # 결과 검증
            if not isinstance(result, dict):
                raise ValueError("워크플로우 실행 결과가 올바르지 않습니다.")
            
            # TutorState로 변환
            final_state = state_manager.from_dict(result) if isinstance(result, dict) else result
            
            return final_state
            
        except Exception as e:
            self.logger.error(f"표준 실행 중 오류: {str(e)}")
            raise
    
    async def _execute_with_streaming(
        self, 
        compiled_graph: Any, 
        state: TutorState,
        config: Dict[str, Any]
    ) -> TutorState:
        """
        스트리밍 워크플로우 실행
        
        Args:
            compiled_graph: 컴파일된 LangGraph
            state: 입력 State
            config: 실행 설정
            
        Returns:
            실행 완료된 State
        """
        try:
            final_state = None
            
            # 스트리밍 실행
            async for chunk in compiled_graph.astream(state, config=config):
                self.logger.debug(f"스트리밍 청크: {chunk}")
                
                # 마지막 청크가 최종 결과
                if chunk:
                    final_state = chunk
            
            if final_state is None:
                raise ValueError("스트리밍 실행에서 결과를 받지 못했습니다.")
            
            # TutorState로 변환
            if isinstance(final_state, dict):
                final_state = state_manager.from_dict(final_state)
            
            return final_state
            
        except Exception as e:
            self.logger.error(f"스트리밍 실행 중 오류: {str(e)}")
            raise
    
    def _prepare_runtime_config(
        self, 
        config: Optional[Dict[str, Any]], 
        execution_id: str
    ) -> Dict[str, Any]:
        """
        런타임 설정 준비
        
        Args:
            config: 사용자 제공 설정
            execution_id: 실행 ID
            
        Returns:
            런타임 설정 딕셔너리
        """
        runtime_config = {
            "recursion_limit": 50,
            "execution_id": execution_id,
            "timeout": 300  # 5분 타임아웃
        }
        
        # 사용자 설정 병합
        if config:
            runtime_config.update(config)
        
        # configurable 설정 (LangGraph 전용)
        if "configurable" not in runtime_config:
            runtime_config["configurable"] = {}
        
        # thread_id 설정 (세션 관리용)
        if "thread_id" not in runtime_config["configurable"]:
            runtime_config["configurable"]["thread_id"] = execution_id
        
        return runtime_config
    
    def _handle_execution_error(self, state: TutorState, error_message: str) -> TutorState:
        """
        실행 오류 처리 (v2.0 업데이트)
        
        Args:
            state: 원본 State
            error_message: 오류 메시지
            
        Returns:
            오류 처리된 State
        """
        try:
            # 오류 상태로 State 업데이트
            error_state = state.copy()
            
            # 오류 메시지를 적절한 draft에 저장
            error_response = f"죄송합니다. 처리 중 오류가 발생했습니다: {error_message}"
            error_state = state_manager.update_agent_draft(
                error_state, 
                "theory_educator", 
                error_response
            )
            
            # 현재 에이전트를 learning_supervisor로 설정
            error_state = state_manager.update_agent_transition(
                error_state, 
                "learning_supervisor"
            )
            
            # UI 모드를 chat으로 설정 (오류 시 안전한 모드)
            error_state = state_manager.update_ui_mode(error_state, "chat")
            
            # 오류 로그를 대화 기록에 추가
            error_state = state_manager.add_conversation(
                error_state,
                agent_name="system",
                message=f"워크플로우 실행 오류: {error_message}",
                message_type="system"
            )
            
            return error_state
            
        except Exception as e:
            self.logger.error(f"오류 처리 중 추가 오류 발생: {str(e)}")
            # 최소한의 기본 State 반환
            return state
    
    def _log_execution_start(self, state: TutorState, execution_id: str) -> None:
        """
        실행 시작 로그
        
        Args:
            state: 입력 State
            execution_id: 실행 ID
        """
        self.logger.info(f"[{execution_id}] 실행 정보:")
        self.logger.info(f"  - 사용자 ID: {state.get('user_id', 'unknown')}")
        self.logger.info(f"  - 챕터/섹션: {state.get('current_chapter', 0)}/{state.get('current_section', 0)}")
        self.logger.info(f"  - 세션 단계: {state.get('session_progress_stage', 'unknown')}")
        self.logger.info(f"  - 사용자 의도: {state.get('user_intent', 'unknown')}")
    
    def _update_execution_stats(self, success: bool, execution_time: float) -> None:
        """
        실행 통계 업데이트
        
        Args:
            success: 성공 여부
            execution_time: 실행 시간(초)
        """
        self.execution_stats["total_executions"] += 1
        
        if success:
            self.execution_stats["successful_executions"] += 1
        else:
            self.execution_stats["failed_executions"] += 1
        
        # 평균 실행 시간 계산
        total_time = (
            self.execution_stats["average_execution_time"] * 
            (self.execution_stats["total_executions"] - 1) + 
            execution_time
        )
        self.execution_stats["average_execution_time"] = total_time / self.execution_stats["total_executions"]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        실행 통계 반환
        
        Returns:
            실행 통계 딕셔너리
        """
        return {
            **self.execution_stats,
            "success_rate": (
                self.execution_stats["successful_executions"] / 
                max(self.execution_stats["total_executions"], 1) * 100
            )
        }
    
    def reset_stats(self) -> None:
        """실행 통계 초기화"""
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0
        }
    
    def validate_workflow_health(self) -> Dict[str, Any]:
        """
        워크플로우 상태 검증
        
        Returns:
            상태 검증 결과
        """
        try:
            # 컴파일된 그래프 확인
            compiled_graph = get_compiled_graph()
            
            # 기본 State로 간단한 검증
            test_state = state_manager.initialize_state(
                user_id=999999,
                user_type="beginner",
                current_chapter=1,
                current_section=1
            )
            
            health_status = {
                "graph_compiled": compiled_graph is not None,
                "state_manager_working": state_manager.validate_state(test_state),
                "execution_stats": self.get_execution_stats(),
                "timestamp": datetime.now().isoformat()
            }
            
            # 그래프 시각화 저장 시도
            try:
                save_tutor_workflow_graph(compiled_graph)
                health_status["graph_visualization"] = True
            except Exception as e:
                health_status["graph_visualization"] = False
                health_status["visualization_error"] = str(e)
            
            return health_status
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "health_status": "unhealthy"
            }


# 전역 워크플로우 실행기 인스턴스
workflow_executor = WorkflowExecutor()

async def execute_tutor_workflow(
    state: TutorState,
    stream: bool = False,
    config: Optional[Dict[str, Any]] = None
) -> TutorState:
    """
    튜터 워크플로우 실행 (편의 함수)
    
    Args:
        state: 입력 TutorState
        stream: 스트리밍 모드 사용 여부
        config: 실행 설정
        
    Returns:
        실행 완료된 TutorState
    """
    return await workflow_executor.execute_workflow(state, stream, config)

def execute_tutor_workflow_sync(
    state: TutorState,
    config: Optional[Dict[str, Any]] = None
) -> TutorState:
    """
    튜터 워크플로우 동기 실행 (편의 함수)
    
    Args:
        state: 입력 TutorState
        config: 실행 설정
        
    Returns:
        실행 완료된 TutorState
    """
    return workflow_executor.execute_workflow_sync(state, config)