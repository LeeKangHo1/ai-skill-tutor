# backend/app/services/learning/session_service.py
# 세션 관리 비즈니스 로직 서비스

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.utils.database.connection import fetch_one
from app.config.db_config import DatabaseQueryError
from app.core.langraph.workflow import execute_tutor_workflow_sync
from app.core.langraph.state_manager import state_manager

# 로깅 설정
logger = logging.getLogger(__name__)

class SessionService:
    """
    학습 세션 관리 서비스 클래스
    
    LangGraph 워크플로우 관리, 세션 초기화, 세션 완료 등을 담당합니다.
    """
    
    def __init__(self):
        """SessionService 초기화"""
        pass
    
    def start_session(
        self, 
        user_id: int, 
        chapter_number: int, 
        section_number: int, 
        user_message: str = "학습을 시작하겠습니다"
    ) -> Optional[Dict[str, Any]]:
        """
        학습 세션 시작 처리
        
        Args:
            user_id (int): 사용자 ID
            chapter_number (int): 챕터 번호
            section_number (int): 섹션 번호
            user_message (str): 사용자 시작 메시지
            
        Returns:
            Optional[Dict[str, Any]]: 세션 시작 결과 또는 None
            
        Raises:
            DatabaseQueryError: 데이터베이스 조회 오류 시
            ValueError: 유효하지 않은 챕터/섹션인 경우
        """
        try:
            logger.info(f"세션 시작 처리 시작 - 사용자 ID: {user_id}, 챕터: {chapter_number}, 섹션: {section_number}")
            
            # 사용자 정보 조회
            user_info = self._get_user_info(user_id)
            if not user_info:
                raise ValueError(f"사용자를 찾을 수 없습니다: {user_id}")
            
            # 챕터/섹션 유효성 검증
            self._validate_chapter_section(user_info.get("user_type"), chapter_number, section_number)
            
            # 현재 진행 상태 확인 (접근 권한 체크)
            self._validate_access_permission(user_id, chapter_number, section_number)
            
            # LangGraph State 초기화
            initial_state = state_manager.create_session_state(
                user_id=user_id,
                user_type=user_info.get("user_type"),
                chapter=chapter_number,
                section=section_number
            )
            
            # 사용자 메시지 추가
            initial_state = state_manager.handle_user_message(initial_state, user_message)
            
            # LangGraph 워크플로우 실행 (세션 시작)
            workflow_result = execute_tutor_workflow_sync(initial_state)
            
            if not workflow_result:
                logger.error(f"워크플로우 실행 실패 - 사용자 ID: {user_id}")
                return None
            
            # 세션 정보 구성
            session_info = {
                "chapter_number": chapter_number,
                "section_number": section_number,
                "chapter_title": self._get_chapter_title(chapter_number),
                "estimated_duration": self._get_estimated_duration(chapter_number, section_number)
            }
            
            # 워크플로우 응답 추출
            workflow_response = workflow_result.get("workflow_response", {})
            
            result = {
                "session_info": session_info,
                "workflow_response": workflow_response
            }
            
            logger.info(f"세션 시작 처리 완료 - 사용자 ID: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"세션 시작 처리 오류 - 사용자 ID: {user_id}: {e}")
            raise
    
    def complete_session(self, user_id: int, proceed_decision: str) -> Optional[Dict[str, Any]]:
        """
        학습 세션 완료 처리
        
        Args:
            user_id (int): 사용자 ID
            proceed_decision (str): 진행 결정 ("proceed" 또는 "retry")
            
        Returns:
            Optional[Dict[str, Any]]: 세션 완료 결과
        """
        try:
            logger.info(f"세션 완료 처리 시작 - 사용자 ID: {user_id}, 결정: {proceed_decision}")
            
            # 현재 진행 중인 세션의 State 조회 (실제로는 세션 관리 시스템에서 가져와야 함)
            # 여기서는 간단히 구현
            current_state = self._get_current_session_state(user_id)
            if not current_state:
                raise ValueError("진행 중인 세션을 찾을 수 없습니다.")
            
            # 세션 결정 업데이트
            updated_state = state_manager.update_session_decision(current_state, proceed_decision)
            
            # SessionManager를 통한 세션 완료 및 DB 저장
            workflow_result = execute_tutor_workflow_sync(updated_state)
            
            if not workflow_result:
                logger.error(f"세션 완료 워크플로우 실행 실패 - 사용자 ID: {user_id}")
                return None
            
            logger.info(f"세션 완료 처리 성공 - 사용자 ID: {user_id}")
            return workflow_result
            
        except Exception as e:
            logger.error(f"세션 완료 처리 오류 - 사용자 ID: {user_id}: {e}")
            raise
    
    def _get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        사용자 정보 조회
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Optional[Dict[str, Any]]: 사용자 정보
        """
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
    
    def _validate_chapter_section(self, user_type: str, chapter_number: int, section_number: int) -> None:
        """
        챕터/섹션 유효성 검증
        
        Args:
            user_type (str): 사용자 유형
            chapter_number (int): 챕터 번호
            section_number (int): 섹션 번호
            
        Raises:
            ValueError: 유효하지 않은 챕터/섹션인 경우
        """
        # 사용자 유형별 최대 챕터 수 확인
        max_chapters = 10 if user_type == "advanced" else 8
        
        if chapter_number > max_chapters:
            raise ValueError(f"{user_type} 사용자는 최대 {max_chapters}챕터까지 이용 가능합니다.")
        
        # 섹션 수 확인 (현재는 모든 챕터가 4섹션으로 가정)
        max_sections = 4
        if section_number > max_sections:
            raise ValueError(f"각 챕터는 최대 {max_sections}섹션까지 있습니다.")
    
    def _validate_access_permission(self, user_id: int, chapter_number: int, section_number: int) -> None:
        """
        챕터/섹션 접근 권한 검증
        
        Args:
            user_id (int): 사용자 ID
            chapter_number (int): 챕터 번호
            section_number (int): 섹션 번호
            
        Raises:
            ValueError: 접근 권한이 없는 경우
        """
        try:
            # 현재 사용자 진행 상태 조회
            query = """
                SELECT current_chapter, current_section
                FROM user_progress
                WHERE user_id = %s
            """
            
            result = fetch_one(query, (user_id,))
            
            if not result:
                # 진행 상태가 없으면 1챕터 1섹션만 허용
                if chapter_number != 1 or section_number != 1:
                    raise ValueError("1챕터 1섹션부터 시작해주세요.")
                return
            
            current_chapter = result.get("current_chapter", 1)
            current_section = result.get("current_section", 1)
            
            # 접근 권한 검증 로직
            if chapter_number < current_chapter:
                # 이전 챕터는 항상 접근 가능
                return
            elif chapter_number == current_chapter:
                # 현재 챕터의 현재 섹션까지만 접근 가능
                if section_number <= current_section:
                    return
                else:
                    raise ValueError(f"현재 {current_chapter}챕터 {current_section}섹션까지만 이용 가능합니다.")
            else:
                # 다음 챕터는 현재 챕터를 모두 완료한 경우에만 접근 가능
                raise ValueError(f"현재 {current_chapter}챕터를 먼저 완료해주세요.")
                
        except Exception as e:
            logger.error(f"접근 권한 검증 오류 - 사용자 ID: {user_id}: {e}")
            raise
    
    def _get_chapter_title(self, chapter_number: int) -> str:
        """
        챕터 번호에 따른 챕터 제목 반환
        
        Args:
            chapter_number (int): 챕터 번호
            
        Returns:
            str: 챕터 제목
        """
        chapter_titles = {
            1: "AI는 무엇인가?",
            2: "LLM이란 무엇인가",
            3: "다양한 AI 챗봇들 소개",
            4: "프롬프트란 무엇인가",
            5: "좋은 프롬프트 작성법",
            6: "ChatGPT로 할 수 있는 것들",
            7: "AI와 함께하는 일상업무",
            8: "AI 활용 고급 팁과 주의사항",
            9: "고급 프롬프트 엔지니어링",  # 실무 응용형 전용
            10: "API 연동 및 자동화"        # 실무 응용형 전용
        }
        
        return chapter_titles.get(chapter_number, f"{chapter_number}챕터")
    
    def _get_estimated_duration(self, chapter_number: int, section_number: int) -> str:
        """
        예상 학습 시간 반환
        
        Args:
            chapter_number (int): 챕터 번호
            section_number (int): 섹션 번호
            
        Returns:
            str: 예상 학습 시간
        """
        # 현재는 기본값으로 15분 반환 (추후 세부 조정 가능)
        return "15분"
    
    def _get_current_session_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        현재 진행 중인 세션의 State 조회 (임시 구현)
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Optional[Dict[str, Any]]: 현재 세션 State
        """
        # 실제로는 세션 관리 시스템에서 현재 활성 State를 가져와야 함
        # 여기서는 임시로 기본 State 반환
        logger.warning(f"임시 구현: 현재 세션 State 조회 - 사용자 ID: {user_id}")
        return None