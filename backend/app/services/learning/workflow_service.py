# backend/app/services/learning/workflow_service.py
# LangGraph 워크플로우 관리 비즈니스 로직 서비스

import logging
from typing import Dict, Any, Optional

from app.core.langraph.workflow import execute_tutor_workflow_sync, workflow_executor
from app.core.langraph.state_manager import state_manager
from app.utils.database.connection import fetch_one
from app.config.db_config import DatabaseQueryError

# 로깅 설정
logger = logging.getLogger(__name__)

class WorkflowService:
    """
    LangGraph 워크플로우 관리 서비스 클래스
    
    State 관리 및 세션 생명주기 관리를 담당합니다.
    실제 라우팅과 의도분석은 LangGraph 내부에서 처리됩니다.
    """
    
    def __init__(self):
        """WorkflowService 초기화"""
        # 활성 세션 State를 메모리에 저장 (임시 구현)
        # 실제로는 Redis나 다른 세션 스토어 사용 권장
        self._active_sessions = {}
    
    def process_message(
        self, 
        user_id: int, 
        user_message: str, 
        message_type: str = "user"
    ) -> Optional[Dict[str, Any]]:
        """
        통합 메시지 처리
        
        현재 활성 세션의 State에 메시지를 추가하고 LangGraph가 처리하도록 합니다.
        
        Args:
            user_id (int): 사용자 ID
            user_message (str): 사용자 메시지
            message_type (str): 메시지 타입
            
        Returns:
            Optional[Dict[str, Any]]: 처리 결과
        """
        try:
            logger.info(f"메시지 처리 - 사용자 ID: {user_id}, 타입: {message_type}")
            
            # 현재 활성 세션 State 조회
            current_state = self._get_active_session_state(user_id)
            if not current_state:
                raise ValueError("활성 세션을 찾을 수 없습니다. 새로운 세션을 시작해주세요.")
            
            # 사용자 메시지를 State에 추가 (LangGraph가 자동으로 처리)
            updated_state = state_manager.handle_user_message(current_state, user_message, message_type)
            
            # 퀴즈 답변인 경우 답변 정보 업데이트
            if message_type == "quiz_answer":
                updated_state = state_manager.update_user_answer(updated_state, user_message)
            
            # 활성 세션 State 업데이트
            self._update_active_session_state(user_id, updated_state)
            
            # LangGraph 내부에서 자동으로 처리 (라우팅, 의도분석, 응답생성)
            workflow_result = execute_tutor_workflow_sync(updated_state)
            
            if not workflow_result:
                logger.error(f"워크플로우 실행 실패 - 사용자 ID: {user_id}")
                return None
            
            # 업데이트된 State를 세션에 저장
            self._update_active_session_state(user_id, workflow_result)
            
            # workflow_response 추출
            result = self._extract_workflow_response(workflow_result)
            
            logger.info(f"메시지 처리 완료 - 사용자 ID: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"메시지 처리 오류 - 사용자 ID: {user_id}: {e}")
            raise
    
    def submit_quiz_answer(
        self, 
        user_id: int, 
        user_answer: str
    ) -> Optional[Dict[str, Any]]:
        """
        퀴즈 답변 제출 처리
        
        Args:
            user_id (int): 사용자 ID
            user_answer (str): 사용자 답변
            
        Returns:
            Optional[Dict[str, Any]]: 평가 결과
        """
        try:
            logger.info(f"퀴즈 답변 제출 - 사용자 ID: {user_id}")
            
            # quiz_answer 타입으로 메시지 처리
            result = self.process_message(user_id, user_answer, "quiz_answer")
            
            logger.info(f"퀴즈 답변 처리 완료 - 사용자 ID: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"퀴즈 답변 제출 오류 - 사용자 ID: {user_id}: {e}")
            raise
    
    def start_session(
        self, 
        user_id: int, 
        chapter_number: int, 
        section_number: int, 
        user_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        새로운 학습 세션 시작
        
        Args:
            user_id (int): 사용자 ID
            chapter_number (int): 챕터 번호
            section_number (int): 섹션 번호
            user_message (str): 시작 메시지
            
        Returns:
            Optional[Dict[str, Any]]: 세션 시작 결과
        """
        try:
            logger.info(f"새 세션 시작 - 사용자 ID: {user_id}, 챕터: {chapter_number}, 섹션: {section_number}")
            
            # 사용자 정보 조회
            user_info = self._get_user_info(user_id)
            if not user_info:
                raise ValueError(f"사용자를 찾을 수 없습니다: {user_id}")
            
            # 새로운 세션 State 생성
            session_state = state_manager.create_session_state(
                user_id=user_id,
                user_type=user_info.get("user_type"),
                chapter=chapter_number,
                section=section_number
            )
            
            # 시작 메시지 추가
            session_state = state_manager.handle_user_message(session_state, user_message)
            
            # LangGraph 워크플로우 시작 (최초 1회)
            workflow_result = execute_tutor_workflow_sync(session_state)
            
            if not workflow_result:
                logger.error(f"세션 시작 실패 - 사용자 ID: {user_id}")
                return None
            
            # 활성 세션으로 등록
            self._register_active_session(user_id, workflow_result)
            
            # 응답 추출
            result = self._extract_workflow_response(workflow_result)
            
            logger.info(f"새 세션 시작 완료 - 사용자 ID: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"세션 시작 오류 - 사용자 ID: {user_id}: {e}")
            raise
    
    def complete_session(self, user_id: int, proceed_decision: str) -> Optional[Dict[str, Any]]:
        """
        학습 세션 완료 처리
        
        세션을 DB에 저장하고 다음 챕터/섹션으로 State를 업데이트합니다.
        세션은 제거되지 않고 계속 사용됩니다.
        
        Args:
            user_id (int): 사용자 ID
            proceed_decision (str): 진행 결정
            
        Returns:
            Optional[Dict[str, Any]]: 세션 완료 결과
        """
        try:
            logger.info(f"세션 완료 처리 - 사용자 ID: {user_id}, 결정: {proceed_decision}")
            
            # 현재 활성 세션 State 조회
            current_state = self._get_active_session_state(user_id)
            if not current_state:
                raise ValueError("완료할 활성 세션을 찾을 수 없습니다.")
            
            # 세션 결정 업데이트
            updated_state = state_manager.update_session_decision(current_state, proceed_decision)
            
            # SessionManager를 통한 DB 저장 및 다음 세션 준비
            workflow_result = execute_tutor_workflow_sync(updated_state)
            
            if not workflow_result:
                logger.error(f"세션 완료 실패 - 사용자 ID: {user_id}")
                return None
            
            # 업데이트된 State로 활성 세션 갱신 (제거하지 않음)
            self._update_active_session_state(user_id, workflow_result)
            
            # 응답 추출
            result = self._extract_workflow_response(workflow_result)
            
            logger.info(f"세션 완료 처리 성공 - 사용자 ID: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"세션 완료 처리 오류 - 사용자 ID: {user_id}: {e}")
            raise
    
    def get_workflow_health(self) -> Dict[str, Any]:
        """
        워크플로우 상태 검증
        
        Returns:
            Dict[str, Any]: 워크플로우 상태 정보
        """
        try:
            logger.info("워크플로우 상태 검증")
            
            # WorkflowExecutor 상태 검증
            health_status = workflow_executor.validate_workflow_health()
            
            # 활성 세션 정보 추가
            health_status["active_sessions_count"] = len(self._active_sessions)
            health_status["execution_stats"] = workflow_executor.get_execution_stats()
            
            return health_status
            
        except Exception as e:
            logger.error(f"워크플로우 상태 검증 오류: {e}")
            return {"health_status": "error", "error": str(e)}
    
    def _get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """사용자 정보 조회"""
        try:
            query = """
                SELECT user_id, user_type, diagnosis_completed
                FROM users
                WHERE user_id = %s
            """
            
            result = fetch_one(query, (user_id,))
            
            if result and not result.get("diagnosis_completed"):
                raise ValueError("진단을 먼저 완료해주세요.")
            
            return result
            
        except Exception as e:
            logger.error(f"사용자 정보 조회 오류 - 사용자 ID: {user_id}: {e}")
            raise
    
    def _register_active_session(self, user_id: int, session_state: Dict[str, Any]) -> None:
        """활성 세션 등록"""
        self._active_sessions[user_id] = session_state
        logger.debug(f"활성 세션 등록 - 사용자 ID: {user_id}")
    
    def _get_active_session_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """활성 세션 State 조회"""
        return self._active_sessions.get(user_id)
    
    def _update_active_session_state(self, user_id: int, updated_state: Dict[str, Any]) -> None:
        """활성 세션 State 업데이트"""
        self._active_sessions[user_id] = updated_state
        logger.debug(f"활성 세션 업데이트 - 사용자 ID: {user_id}")
    
    def _remove_active_session(self, user_id: int) -> None:
        """활성 세션 제거 (일반적으로 사용하지 않음 - 로그아웃 시에만)"""
        if user_id in self._active_sessions:
            del self._active_sessions[user_id]
            logger.debug(f"활성 세션 제거 - 사용자 ID: {user_id}")
    
    def _extract_workflow_response(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        워크플로우 실행 결과에서 응답 데이터 추출
        
        Args:
            workflow_result (Dict[str, Any]): LangGraph 실행 결과
            
        Returns:
            Dict[str, Any]: API 응답용 데이터
        """
        try:
            # workflow_response 필드가 이미 LangGraph에서 생성됨
            workflow_response = workflow_result.get("workflow_response", {})
            
            # 필요한 필드들만 추출하여 API 응답 구성
            response = {
                "current_agent": workflow_result.get("current_agent", "unknown"),
                "session_progress_stage": workflow_result.get("session_progress_stage", "unknown"),
                "ui_mode": workflow_result.get("ui_mode", "chat"),
                "content": workflow_response.get("content", {}),
                "user_intent": workflow_result.get("user_intent", "unknown")
            }
            
            # 추가 정보가 있는 경우 포함
            if "evaluation_result" in workflow_result:
                response["evaluation_result"] = workflow_result["evaluation_result"]
            
            if "session_completion" in workflow_result:
                response["session_completion"] = workflow_result["session_completion"]
            
            return response
            
        except Exception as e:
            logger.error(f"워크플로우 응답 추출 오류: {e}")
            return {
                "current_agent": "error",
                "session_progress_stage": "error",
                "ui_mode": "chat",
                "content": {
                    "type": "error",
                    "message": "응답 처리 중 오류가 발생했습니다."
                },
                "error": str(e)
            }