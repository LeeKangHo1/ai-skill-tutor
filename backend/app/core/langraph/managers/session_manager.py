# backend/app/core/langraph/managers/session_manager.py
# 세션 진행 관리 전담 모듈

import copy
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from ..state.state_definition import TutorState


class SessionManager:
    """
    학습 세션 진행 관리를 담당하는 클래스
    
    주요 기능:
    - 세션 진행 단계 관리
    - 챕터/섹션 진행 로직
    - 세션 초기화 및 완료
    - 재학습 여부 판단
    - 다음 세션 준비
    - 세션 상태 추적
    """
    
    def __init__(self):
        """SessionManager 초기화"""
        pass
    
    def update_section_progress(self, 
                              state: TutorState, 
                              next_section: Optional[int] = None, 
                              next_chapter: Optional[int] = None) -> TutorState:
        """
        섹션/챕터 진행 업데이트
        
        Args:
            state: 현재 State
            next_section: 다음 섹션 번호 (선택사항)
            next_chapter: 다음 챕터 번호 (선택사항)
        
        Returns:
            업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        if next_chapter is not None:
            updated_state["current_chapter"] = next_chapter
            updated_state["current_section"] = 1  # 새 챕터 시작 시 섹션 1부터
        elif next_section is not None:
            updated_state["current_section"] = next_section
        
        return updated_state
    
    def update_session_progress(self, 
                              state: TutorState, 
                              completed_agent: str) -> TutorState:
        """
        세션 진행 단계 업데이트
        
        Args:
            state: 현재 State
            completed_agent: 완료된 에이전트 이름
        
        Returns:
            업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        if completed_agent == "theory_educator":
            updated_state["session_progress_stage"] = "theory_completed"
        elif completed_agent == "evaluation_feedback_agent":
            updated_state["session_progress_stage"] = "quiz_and_feedback_completed"
        # quiz_generator 완료 후에는 단계 변경 없음 (evaluation_feedback_agent로 자동 연결)
        
        return updated_state
    
    def update_session_decision(self, 
                              state: TutorState, 
                              decision: str) -> TutorState:
        """
        세션 완료 후 사용자 결정 업데이트
        
        Args:
            state: 현재 State
            decision: 사용자 결정 ("proceed" 또는 "retry")
        
        Returns:
            결정이 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state["retry_decision_result"] = decision
        return updated_state
    
    def prepare_next_session(self, 
                           state: TutorState, 
                           next_chapter: Optional[int] = None, 
                           next_section: Optional[int] = None) -> TutorState:
        """
        다음 세션 준비
        
        Args:
            state: 현재 State
            next_chapter: 다음 챕터 번호
            next_section: 다음 섹션 번호
        
        Returns:
            다음 세션이 준비된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 진행 상태 업데이트
        if next_chapter is not None:
            updated_state["current_chapter"] = next_chapter
            updated_state["current_section"] = 1  # 새 챕터 시작 시 섹션 1부터
        elif next_section is not None:
            updated_state["current_section"] = next_section
        
        # 세션 상태 초기화
        updated_state = self.reset_session_state(
            updated_state, 
            new_chapter=(next_chapter is not None)
        )
        
        # 에이전트를 session_manager로 설정
        updated_state["current_agent"] = "session_manager"
        updated_state["previous_agent"] = state.get("current_agent", "")
        
        return updated_state
    
    def reset_session_state(self, 
                          state: TutorState, 
                          new_chapter: bool = False) -> TutorState:
        """
        세션 상태 초기화
        
        Args:
            state: 현재 State
            new_chapter: 새 챕터 시작 여부
        
        Returns:
            초기화된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 공통 초기화
        updated_state.update({
            "session_progress_stage": "session_start",
            "ui_mode": "chat",  # UI 모드를 chat으로 초기화
            "current_session_conversations": [],
            
            # 퀴즈 관련 필드 초기화
            "quiz_content": "",
            "quiz_options": [],
            "quiz_correct_answer": None,
            "quiz_explanation": "",
            "quiz_sample_answer": "",
            "quiz_evaluation_criteria": [],
            "quiz_hint": "",
            "user_answer": "",
            "multiple_answer_correct": False,
            "subjective_answer_score": 0,
            "evaluation_feedback": "",
            "hint_usage_count": 0,
            
            "session_start_time": datetime.now(),
            "theory_draft": "",
            "quiz_draft": "",
            "feedback_draft": "",
            "qna_draft": "",
            
            # 워크플로우 응답 초기화
            "workflow_response": {}
        })
        
        if new_chapter:
            updated_state.update({
                "current_session_count": 0,
                "current_section": 1,
                "quiz_type": "multiple_choice"  # 새 챕터 시작 시 기본값으로 초기화
            })
        
        return updated_state
    
    def calculate_next_progress(self, 
                              state: TutorState, 
                              decision_result: str,
                              chapter_data: Optional[Dict[str, Any]] = None) -> Tuple[int, int]:
        """
        다음 진행 위치 계산
        
        Args:
            state: 현재 State
            decision_result: 사용자 결정 ("proceed" 또는 "retry")
            chapter_data: 챕터 데이터 (섹션 수 확인용)
        
        Returns:
            (다음_챕터, 다음_섹션) 튜플
        """
        current_chapter = state.get("current_chapter", 1)
        current_section = state.get("current_section", 1)
        user_type = state.get("user_type", "beginner")
        
        if decision_result == "proceed":
            # 다음 단계 진행
            if chapter_data:
                max_sections = len(chapter_data.get('sections', []))
            else:
                # 기본값 사용 (일반적으로 4섹션)
                max_sections = 4
            
            if current_section < max_sections:
                # 같은 챕터 내 다음 섹션
                next_chapter = current_chapter
                next_section = current_section + 1
            else:
                # 다음 챕터의 첫 번째 섹션
                next_chapter = current_chapter + 1
                next_section = 1
        
        elif decision_result == "retry":
            # 현재 섹션 유지
            next_chapter = current_chapter
            next_section = current_section
        
        else:
            # 기본값: 현재 위치 유지
            next_chapter = current_chapter
            next_section = current_section
        
        return next_chapter, next_section
    
    def increment_session_count(self, state: TutorState) -> TutorState:
        """
        현재 섹션의 세션 카운트 증가
        
        Args:
            state: 현재 State
        
        Returns:
            세션 카운트가 증가된 State
        """
        updated_state = copy.deepcopy(state)
        current_count = state.get("current_session_count", 0)
        updated_state["current_session_count"] = current_count + 1
        return updated_state
    
    def is_session_limit_reached(self, state: TutorState, max_sessions: int = 1) -> bool:
        """
        세션 제한 도달 여부 확인
        
        Args:
            state: 현재 State
            max_sessions: 최대 세션 수 (기본값: 1)
        
        Returns:
            제한 도달 여부
        """
        current_count = state.get("current_session_count", 0)
        return current_count >= max_sessions
    
    def get_session_duration(self, state: TutorState) -> int:
        """
        현재 세션 지속 시간 계산 (분 단위)
        
        Args:
            state: 현재 State
        
        Returns:
            세션 지속 시간 (분)
        """
        start_time = state.get("session_start_time")
        if not start_time:
            return 0
        
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time)
            except ValueError:
                return 0
        
        duration = datetime.now() - start_time
        return int(duration.total_seconds() / 60)
    
    def is_session_completed(self, state: TutorState) -> bool:
        """
        세션 완료 여부 확인
        
        Args:
            state: 현재 State
        
        Returns:
            세션 완료 여부
        """
        stage = state.get("session_progress_stage", "")
        decision = state.get("retry_decision_result", "")
        
        # quiz_and_feedback_completed 단계이고 사용자 결정이 있으면 완료
        return stage == "quiz_and_feedback_completed" and decision in ["proceed", "retry"]
    
    def get_session_summary(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 세션 상태 요약
        
        Args:
            state: 현재 State
        
        Returns:
            세션 상태 요약
        """
        return {
            "current_chapter": state.get("current_chapter", 1),
            "current_section": state.get("current_section", 1),
            "session_progress_stage": state.get("session_progress_stage", "session_start"),
            "current_agent": state.get("current_agent", ""),
            "session_duration_minutes": self.get_session_duration(state),
            "current_session_count": state.get("current_session_count", 0),
            "retry_decision_result": state.get("retry_decision_result", ""),
            "is_completed": self.is_session_completed(state),
            "conversation_count": len(state.get("current_session_conversations", [])),
            "ui_mode": state.get("ui_mode", "chat")
        }
    
    def validate_chapter_section(self, 
                                chapter: int, 
                                section: int, 
                                user_type: str = "beginner") -> bool:
        """
        챕터/섹션 번호 유효성 검증
        
        Args:
            chapter: 챕터 번호
            section: 섹션 번호
            user_type: 사용자 유형
        
        Returns:
            유효성 여부
        """
        # 기본 범위 검증
        if chapter < 1 or section < 1:
            return False
        
        # 사용자 유형별 최대 챕터 수
        max_chapters = {
            "beginner": 8,
            "advanced": 10
        }
        
        max_chapter = max_chapters.get(user_type, 8)
        if chapter > max_chapter:
            return False
        
        # 섹션은 일반적으로 1-4 범위
        if section > 4:
            return False
        
        return True
    
    def get_progress_percentage(self, 
                              state: TutorState, 
                              total_chapters: Optional[int] = None) -> float:
        """
        전체 진행률 계산 (백분율)
        
        Args:
            state: 현재 State
            total_chapters: 전체 챕터 수 (없으면 사용자 유형별 기본값)
        
        Returns:
            진행률 (0.0 - 100.0)
        """
        current_chapter = state.get("current_chapter", 1)
        current_section = state.get("current_section", 1)
        user_type = state.get("user_type", "beginner")
        
        if total_chapters is None:
            total_chapters = 8 if user_type == "beginner" else 10
        
        # 각 챕터당 4섹션 가정
        sections_per_chapter = 4
        total_sections = total_chapters * sections_per_chapter
        
        # 완료된 섹션 수 계산
        completed_sections = (current_chapter - 1) * sections_per_chapter + (current_section - 1)
        
        # 진행률 계산
        progress = (completed_sections / total_sections) * 100
        return min(100.0, max(0.0, progress))
    
    def get_remaining_content(self, 
                            state: TutorState, 
                            total_chapters: Optional[int] = None) -> Dict[str, int]:
        """
        남은 학습 분량 계산
        
        Args:
            state: 현재 State
            total_chapters: 전체 챕터 수
        
        Returns:
            남은 분량 정보
        """
        current_chapter = state.get("current_chapter", 1)
        current_section = state.get("current_section", 1)
        user_type = state.get("user_type", "beginner")
        
        if total_chapters is None:
            total_chapters = 8 if user_type == "beginner" else 10
        
        sections_per_chapter = 4
        
        # 현재 챕터의 남은 섹션
        remaining_sections_current = sections_per_chapter - current_section
        
        # 남은 전체 챕터
        remaining_chapters = total_chapters - current_chapter
        
        # 남은 전체 섹션
        remaining_sections_total = remaining_sections_current + (remaining_chapters * sections_per_chapter)
        
        return {
            "remaining_chapters": remaining_chapters,
            "remaining_sections_current_chapter": remaining_sections_current,
            "remaining_sections_total": remaining_sections_total,
            "progress_percentage": self.get_progress_percentage(state, total_chapters)
        }
    
    def create_session_transition_summary(self, 
                                        current_state: TutorState, 
                                        next_chapter: int, 
                                        next_section: int) -> Dict[str, Any]:
        """
        세션 전환 요약 생성
        
        Args:
            current_state: 현재 State
            next_chapter: 다음 챕터
            next_section: 다음 섹션
        
        Returns:
            세션 전환 요약
        """
        current_chapter = current_state.get("current_chapter", 1)
        current_section = current_state.get("current_section", 1)
        
        return {
            "completed_session": {
                "chapter": current_chapter,
                "section": current_section,
                "duration_minutes": self.get_session_duration(current_state),
                "decision": current_state.get("retry_decision_result", "")
            },
            "next_session": {
                "chapter": next_chapter,
                "section": next_section,
                "is_new_chapter": next_chapter != current_chapter,
                "is_retry": (next_chapter == current_chapter and next_section == current_section)
            },
            "progress": {
                "progress_percentage": self.get_progress_percentage(current_state),
                "remaining_content": self.get_remaining_content(current_state)
            }
        }


# 전역 SessionManager 인스턴스
session_manager = SessionManager()