# backend/app/core/langraph/state/state_factory.py
# State 생성 및 초기화 로직 전담

import copy
import json
from datetime import datetime
from typing import Dict, Any, Optional

from .state_definition import TutorState, DEFAULT_VALUES


class StateFactory:
    """
    TutorState 생성 및 초기화를 담당하는 팩토리 클래스
    
    주요 기능:
    - 기본 State 템플릿 생성
    - 사용자별 State 초기화
    - State 직렬화/역직렬화
    - State 초기화 및 리셋
    """
    
    def __init__(self):
        """StateFactory 초기화"""
        self._default_state = self._create_default_state()
    
    def _create_default_state(self) -> TutorState:
        """
        기본 State 템플릿 생성
        
        Returns:
            기본값으로 초기화된 TutorState
        """
        # DEFAULT_VALUES를 기반으로 기본 State 생성
        default_state = TutorState(**DEFAULT_VALUES)
        
        # datetime 필드는 현재 시간으로 설정
        default_state["session_start_time"] = datetime.now()
        
        return default_state
    
    def create_new_state(self, 
                        user_id: int, 
                        user_type: str,
                        current_chapter: int = 1, 
                        current_section: int = 1) -> TutorState:
        """
        새로운 사용자를 위한 State 생성
        
        Args:
            user_id: 사용자 ID
            user_type: 사용자 유형 ("beginner" or "advanced")
            current_chapter: 시작할 챕터 번호 (기본값: 1)
            current_section: 시작할 섹션 번호 (기본값: 1)
        
        Returns:
            초기화된 TutorState
        """
        state = copy.deepcopy(self._default_state)
        
        # 사용자 정보 설정
        state.update({
            "user_id": user_id,
            "user_type": user_type,
            "current_chapter": current_chapter,
            "current_section": current_section,
            "session_start_time": datetime.now()
        })
        
        return state
    
    def create_session_state(self,
                           user_id: int,
                           user_type: str, 
                           chapter: int,
                           section: int,
                           existing_conversations: Optional[list] = None) -> TutorState:
        """
        학습 세션용 State 생성
        
        Args:
            user_id: 사용자 ID
            user_type: 사용자 유형
            chapter: 진행할 챕터 번호
            section: 진행할 섹션 번호
            existing_conversations: 기존 대화 기록 (선택사항)
        
        Returns:
            세션용으로 초기화된 TutorState
        """
        state = self.create_new_state(user_id, user_type, chapter, section)
        
        # 세션 관련 설정
        state.update({
            "current_agent": "session_manager",
            "session_progress_stage": "session_start",
            "ui_mode": "chat",
            "user_intent": "next_step",
            "current_session_count": 0,
            "session_start_time": datetime.now()
        })
        
        # 기존 대화 기록이 있으면 설정
        if existing_conversations:
            state["current_session_conversations"] = existing_conversations
        
        return state
    
    def reset_session_state(self, 
                          state: TutorState, 
                          new_chapter: bool = False,
                          preserve_user_info: bool = True) -> TutorState:
        """
        세션 상태 초기화
        
        Args:
            state: 현재 State
            new_chapter: 새 챕터 시작 여부
            preserve_user_info: 사용자 정보 보존 여부
        
        Returns:
            초기화된 State
        """
        # 보존할 사용자 정보 백업
        preserved_data = {}
        if preserve_user_info:
            preserved_data = {
                "user_id": state.get("user_id", 0),
                "user_type": state.get("user_type", "unassigned"),
                "current_chapter": state.get("current_chapter", 1),
                "current_section": state.get("current_section", 1)
            }
        
        # 새로운 기본 State 생성
        reset_state = copy.deepcopy(self._default_state)
        reset_state["session_start_time"] = datetime.now()
        
        # 보존된 데이터 복원
        if preserve_user_info:
            reset_state.update(preserved_data)
        
        # 새 챕터 시작 시 추가 초기화
        if new_chapter:
            reset_state.update({
                "current_session_count": 0,
                "current_section": 1,
                "quiz_type": "multiple_choice"  # 새 챕터 시작 시 기본값으로 초기화
            })
        
        # 세션 기본 설정
        reset_state.update({
            "session_progress_stage": "session_start",
            "ui_mode": "chat",
            "current_agent": "session_manager",
            "user_intent": "next_step"
        })
        
        return reset_state
    
    def copy_state(self, state: TutorState) -> TutorState:
        """
        State 깊은 복사
        
        Args:
            state: 복사할 State
        
        Returns:
            복사된 State
        """
        return copy.deepcopy(state)
    
    def merge_states(self, 
                    base_state: TutorState, 
                    updates: Dict[str, Any]) -> TutorState:
        """
        기존 State에 업데이트 병합
        
        Args:
            base_state: 기본 State
            updates: 업데이트할 필드들
        
        Returns:
            병합된 State
        """
        merged_state = copy.deepcopy(base_state)
        merged_state.update(updates)
        return merged_state
    
    def to_dict(self, state: TutorState) -> Dict[str, Any]:
        """
        State를 직렬화 가능한 딕셔너리로 변환
        
        Args:
            state: TutorState 객체
        
        Returns:
            직렬화된 딕셔너리
        """
        serialized = {}
        
        for key, value in state.items():
            if isinstance(value, datetime):
                # datetime을 ISO 형식 문자열로 변환
                serialized[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                # 리스트나 딕셔너리는 JSON 직렬화 가능한지 확인
                try:
                    json.dumps(value)  # 직렬화 테스트
                    serialized[key] = value
                except (TypeError, ValueError):
                    # 직렬화 불가능한 경우 빈 값으로 설정
                    serialized[key] = [] if isinstance(value, list) else {}
            else:
                serialized[key] = value
        
        return serialized
    
    def from_dict(self, state_dict: Dict[str, Any]) -> TutorState:
        """
        딕셔너리에서 State 복원
        
        Args:
            state_dict: 직렬화된 State 딕셔너리
        
        Returns:
            복원된 TutorState
        """
        # 기본 State로 시작
        state = copy.deepcopy(self._default_state)
        
        # 입력 데이터로 업데이트
        for key, value in state_dict.items():
            if key == "session_start_time" and isinstance(value, str):
                # ISO 형식 문자열을 datetime으로 변환
                try:
                    state[key] = datetime.fromisoformat(value)
                except ValueError:
                    state[key] = datetime.now()  # 파싱 실패 시 현재 시간으로 설정
            elif key in state:
                state[key] = value
        
        return state
    
    def to_json(self, state: TutorState) -> str:
        """
        State를 JSON 문자열로 직렬화
        
        Args:
            state: TutorState 객체
        
        Returns:
            JSON 문자열
        """
        serialized_dict = self.to_dict(state)
        return json.dumps(serialized_dict, ensure_ascii=False, indent=2)
    
    def from_json(self, json_str: str) -> TutorState:
        """
        JSON 문자열에서 State 복원
        
        Args:
            json_str: JSON 문자열
        
        Returns:
            복원된 TutorState
        """
        try:
            state_dict = json.loads(json_str)
            return self.from_dict(state_dict)
        except (json.JSONDecodeError, TypeError) as e:
            # JSON 파싱 실패 시 기본 State 반환
            return copy.deepcopy(self._default_state)
    
    def create_quiz_state(self,
                         state: TutorState,
                         quiz_type: str = "multiple_choice") -> TutorState:
        """
        퀴즈 진행을 위한 State 생성
        
        Args:
            state: 현재 State
            quiz_type: 퀴즈 유형 ("multiple_choice" or "subjective")
        
        Returns:
            퀴즈용으로 설정된 State
        """
        quiz_state = copy.deepcopy(state)
        
        # 퀴즈 모드 설정
        quiz_state.update({
            "ui_mode": "quiz",
            "quiz_type": quiz_type,
            "user_intent": "quiz_answer"
        })
        
        # 퀴즈 관련 필드 초기화
        quiz_state.update({
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
            "hint_usage_count": 0
        })
        
        return quiz_state
    
    def clear_agent_drafts(self, state: TutorState) -> TutorState:
        """
        에이전트 대본 필드 초기화
        
        Args:
            state: 현재 State
        
        Returns:
            대본이 초기화된 State
        """
        cleared_state = copy.deepcopy(state)
        cleared_state.update({
            "theory_draft": "",
            "quiz_draft": "",
            "feedback_draft": "",
            "qna_draft": ""
        })
        return cleared_state
    
    def clear_quiz_data(self, state: TutorState) -> TutorState:
        """
        퀴즈 관련 데이터 초기화
        
        Args:
            state: 현재 State
        
        Returns:
            퀴즈 데이터가 초기화된 State
        """
        cleared_state = copy.deepcopy(state)
        
        # 퀴즈 관련 모든 필드 초기화
        cleared_state.update({
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
            "hint_usage_count": 0
        })
        
        return cleared_state
    
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
        next_state = copy.deepcopy(state)
        
        # 진행 상태 업데이트
        if next_chapter is not None:
            next_state["current_chapter"] = next_chapter
            next_state["current_section"] = 1  # 새 챕터 시작 시 섹션 1부터
        elif next_section is not None:
            next_state["current_section"] = next_section
        
        # 세션 상태 초기화
        next_state = self.reset_session_state(
            next_state, 
            new_chapter=(next_chapter is not None)
        )
        
        return next_state
    
    def get_default_state(self) -> TutorState:
        """
        기본 State 템플릿 반환
        
        Returns:
            기본 State 복사본
        """
        return copy.deepcopy(self._default_state)


# 전역 StateFactory 인스턴스
state_factory = StateFactory()