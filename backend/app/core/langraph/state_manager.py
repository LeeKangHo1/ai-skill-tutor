# backend/app/core/langraph/state_manager.py

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
import copy

# TutorState 클래스 정의 (PRD v1.3 기준 + 섹션 관리 + 퀴즈 타입 개선)
class TutorState(TypedDict):
    # === 기본 사용자 정보 ===
    user_id: int
    user_type: str   # "beginner": AI 입문자, "advanced": 실무 응용형
    
    # === 학습 진행 상태 ===
    current_chapter: int
    current_section: int  # 현재 섹션 번호 (1학습 세션 = 1섹션)
    current_agent: str  # 현재 활성화된 에이전트 이름 (스네이크 케이스)
    
    # === 학습 세션 진행 단계 ===
    session_progress_stage: str  # "session_start": 세션 시작, "theory_completed": 이론 완료, "quiz_and_feedback_completed": 퀴즈와 피드백 완료
    
    # === UI 모드 제어 ===
    ui_mode: str  # "chat": 채팅 모드, "quiz": 퀴즈 모드
    
    # === 퀴즈 관련 정보 ===
    current_question_type: str        # 퀴즈 타입 ("multiple_choice" or "subjective") - JSON에서 로드
    current_question_number: int      # 문제 번호 (기본키)
    current_question_content: str     # 현재 문제 내용
    current_question_answer: str      # 사용자 답변
    is_answer_correct: int            # 객관식: 1(정답)/0(오답), 주관식: 0~100(점수)
    evaluation_feedback: str          # 평가 및 피드백 내용
    hint_usage_count: int
    
    # === 에이전트 대본 저장 ===
    theory_draft: str                 # TheoryEducator 생성 대본
    quiz_draft: str                   # QuizGenerator 생성 대본
    feedback_draft: str               # EvaluationFeedbackAgent 생성 대본
    qna_draft: str                    # QnAResolver 생성 대본
    
    # === 라우팅 & 디버깅 ===
    previous_agent: str  # 이전 에이전트 이름 (디버깅 및 복귀 추적용)
    
    # === 학습 세션 제어 (SessionManager 활용) ===
    session_decision_result: str  # "proceed": 다음 단계 진행, "retry": 현재 구간 재학습
    current_session_count: int    # 현재 구간에서 학습 세션 횟수 (3회 제한)
    session_start_time: datetime  # 학습 세션 시작 시간
    
    # === 대화 관리 ===
    current_session_conversations: List[Dict[str, Any]]  # 현재 학습 세션의 대화 내용
    recent_sessions_summary: List[Dict[str, str]]        # 최근 5개 학습 세션 요약


@dataclass
class StateManager:
    """
    LangGraph State 관리 클래스
    TutorState의 생성, 업데이트, 저장을 담당
    """
    
    def __init__(self):
        self._default_state = self._create_default_state()
    
    def _create_default_state(self) -> TutorState:
        """기본 State 템플릿 생성"""
        return TutorState(
            # 기본 사용자 정보
            user_id=0,
            user_type="unassigned",
            
            # 학습 진행 상태
            current_chapter=1,
            current_section=1,
            current_agent="session_manager",
            
            # 학습 세션 진행 단계
            session_progress_stage="session_start",
            
            # UI 모드 제어
            ui_mode="chat",
            
            # 퀴즈 관련 정보
            current_question_type="multiple_choice",  # 기본값: 객관식
            current_question_number=0,
            current_question_content="",
            current_question_answer="",
            is_answer_correct=0,
            evaluation_feedback="",
            hint_usage_count=0,
            
            # 에이전트 대본 저장
            theory_draft="",
            quiz_draft="",
            feedback_draft="",
            qna_draft="",
            
            # 라우팅 & 디버깅
            previous_agent="",
            
            # 학습 세션 제어
            session_decision_result="",
            current_session_count=0,
            session_start_time=datetime.now(),
            
            # 대화 관리
            current_session_conversations=[],
            recent_sessions_summary=[]
        )
    
    def initialize_state(self, user_id: int, user_type: str, current_chapter: int = 1, current_section: int = 1) -> TutorState:
        """
        새로운 사용자 State 초기화
        
        Args:
            user_id: 사용자 ID
            user_type: 사용자 유형 ("beginner" or "advanced")
            current_chapter: 시작할 챕터 번호 (기본값: 1)
            current_section: 시작할 섹션 번호 (기본값: 1)
        
        Returns:
            초기화된 TutorState
        """
        state = copy.deepcopy(self._default_state)
        state.update({
            "user_id": user_id,
            "user_type": user_type,
            "current_chapter": current_chapter,
            "current_section": current_section,
            "session_start_time": datetime.now()
        })
        return state
    
    def update_section_progress(self, state: TutorState, next_section: int = None, next_chapter: int = None) -> TutorState:
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
    
    def update_agent_transition(self, state: TutorState, new_agent: str) -> TutorState:
        """
        에이전트 전환 시 State 업데이트
        
        Args:
            state: 현재 State
            new_agent: 새로운 에이전트 이름
        
        Returns:
            업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state["previous_agent"] = state["current_agent"]
        updated_state["current_agent"] = new_agent
        return updated_state
    
    def update_session_progress(self, state: TutorState, completed_agent: str) -> TutorState:
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
    
    def update_ui_mode(self, state: TutorState, mode: str) -> TutorState:
        """
        UI 모드 업데이트
        
        Args:
            state: 현재 State
            mode: UI 모드 ("chat" or "quiz")
        
        Returns:
            업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state["ui_mode"] = mode
        return updated_state
    
    def update_quiz_info(self, state: TutorState, 
                        question_type: str = None,
                        question_number: int = None,
                        question_content: str = None,
                        user_answer: str = None,
                        is_correct: int = None,
                        feedback: str = None,
                        hint_count: int = None) -> TutorState:
        """
        퀴즈 관련 정보 업데이트
        
        Args:
            state: 현재 State
            question_type: 퀴즈 타입 ("multiple_choice" or "subjective")
            question_number: 문제 번호
            question_content: 문제 내용
            user_answer: 사용자 답변
            is_correct: 정답 여부/점수
            feedback: 피드백 내용
            hint_count: 힌트 사용 횟수
        
        Returns:
            업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        if question_type is not None:
            updated_state["current_question_type"] = question_type
        if question_number is not None:
            updated_state["current_question_number"] = question_number
        if question_content is not None:
            updated_state["current_question_content"] = question_content
        if user_answer is not None:
            updated_state["current_question_answer"] = user_answer
        if is_correct is not None:
            updated_state["is_answer_correct"] = is_correct
        if feedback is not None:
            updated_state["evaluation_feedback"] = feedback
        if hint_count is not None:
            updated_state["hint_usage_count"] = hint_count
            
        return updated_state
    
    def update_agent_draft(self, state: TutorState, agent_name: str, draft_content: str) -> TutorState:
        """
        에이전트 대본 업데이트
        
        Args:
            state: 현재 State
            agent_name: 에이전트 이름
            draft_content: 대본 내용
        
        Returns:
            업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        draft_field_map = {
            "theory_educator": "theory_draft",
            "quiz_generator": "quiz_draft",
            "evaluation_feedback_agent": "feedback_draft",
            "qna_resolver": "qna_draft"
        }
        
        if agent_name in draft_field_map:
            field_name = draft_field_map[agent_name]
            updated_state[field_name] = draft_content
        
        return updated_state
    
    def add_conversation(self, state: TutorState, 
                        agent_name: str,
                        message: str,
                        message_type: str = "system") -> TutorState:
        """
        현재 세션에 대화 내용 추가
        
        Args:
            state: 현재 State
            agent_name: 에이전트 이름
            message: 메시지 내용
            message_type: 메시지 유형 ("user", "system", "tool")
        
        Returns:
            업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        conversation_item = {
            "agent_name": agent_name,
            "message": message,
            "timestamp": datetime.now(),
            "message_type": message_type,
            "session_stage": state["session_progress_stage"]
        }
        
        updated_state["current_session_conversations"].append(conversation_item)
        return updated_state
    
    def clear_agent_drafts(self, state: TutorState) -> TutorState:
        """
        에이전트 대본 필드 초기화
        
        Args:
            state: 현재 State
        
        Returns:
            업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state.update({
            "theory_draft": "",
            "quiz_draft": "",
            "feedback_draft": "",
            "qna_draft": ""
        })
        return updated_state
    
    def reset_session_state(self, state: TutorState, new_chapter: bool = False) -> TutorState:
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
            "current_session_conversations": [],
            "current_question_answer": "",
            "evaluation_feedback": "",
            "hint_usage_count": 0,
            "session_start_time": datetime.now(),
            "theory_draft": "",
            "quiz_draft": "",
            "feedback_draft": "",
            "qna_draft": ""
        })
        
        if new_chapter:
            updated_state.update({
                "current_session_count": 0,
                "current_section": 1,
                "current_question_content": "",
                "current_question_type": "multiple_choice"  # 새 챕터 시작 시 기본값으로 초기화
            })
        
        return updated_state
    
    def get_quiz_type_from_section(self, state: TutorState, chapter_data: Dict[str, Any]) -> str:
        """
        현재 섹션의 퀴즈 타입 반환
        
        Args:
            state: 현재 State
            chapter_data: 전체 챕터 데이터
        
        Returns:
            퀴즈 타입 ("multiple_choice" or "subjective")
        """
        current_section = self.get_current_section_data(state, chapter_data)
        quiz_data = current_section.get('quiz', {})
        
        # JSON에서 type 필드를 읽어옴 (기본값: multiple_choice)
        quiz_type = quiz_data.get('type', 'multiple_choice')
        
        # 유효한 타입인지 검증
        valid_types = ['multiple_choice', 'subjective']
        if quiz_type not in valid_types:
            quiz_type = 'multiple_choice'  # 기본값으로 fallback
        
        return quiz_type
    
    def update_quiz_type_from_section(self, state: TutorState, chapter_data: Dict[str, Any]) -> TutorState:
        """
        현재 섹션의 퀴즈 타입으로 State 업데이트
        
        Args:
            state: 현재 State
            chapter_data: 전체 챕터 데이터
        
        Returns:
            퀴즈 타입이 업데이트된 State
        """
        quiz_type = self.get_quiz_type_from_section(state, chapter_data)
        
        updated_state = copy.deepcopy(state)
        updated_state["current_question_type"] = quiz_type
        
        return updated_state
    
    def get_current_section_data(self, state: TutorState, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        현재 섹션 데이터 반환
        
        Args:
            state: 현재 State
            chapter_data: 전체 챕터 데이터
        
        Returns:
            현재 섹션 데이터
        """
        sections = chapter_data.get('sections', [])
        current_section_index = state["current_section"] - 1  # 0-based index
        
        if 0 <= current_section_index < len(sections):
            return sections[current_section_index]
        
        # 섹션을 찾을 수 없으면 첫 번째 섹션 반환
        return sections[0] if sections else {}
    
    def sync_quiz_types(self, state: TutorState) -> TutorState:
        """
        현재 섹션의 퀴즈 타입을 State에 동기화
        quiz_generator 호출 전에 사용하여 JSON과 State 간 일관성 보장
        
        Args:
            state: 현재 State
        
        Returns:
            동기화된 State
        """
        # 이제 current_question_type 하나만 사용하므로 동기화 로직이 단순해짐
        return copy.deepcopy(state)
    
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
                serialized[key] = value.isoformat()
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
        state = copy.deepcopy(self._default_state)
        
        for key, value in state_dict.items():
            if key == "session_start_time" and isinstance(value, str):
                state[key] = datetime.fromisoformat(value)
            elif key in state:
                state[key] = value
        
        return state
    
    def validate_state(self, state: TutorState) -> bool:
        """
        State 유효성 검증
        
        Args:
            state: 검증할 State
        
        Returns:
            유효성 여부
        """
        required_fields = [
            "user_id", "user_type", "current_chapter", "current_section", "current_agent",
            "session_progress_stage", "ui_mode", "current_question_type"
        ]
        
        for field in required_fields:
            if field not in state or state[field] is None:
                return False
        
        # 유효한 값 범위 검증
        valid_user_types = ["beginner", "advanced", "unassigned"]
        valid_progress_stages = ["session_start", "theory_completed", "quiz_and_feedback_completed"]
        valid_ui_modes = ["chat", "quiz"]
        valid_quiz_types = ["multiple_choice", "subjective"]
        
        if state["user_type"] not in valid_user_types:
            return False
        if state["session_progress_stage"] not in valid_progress_stages:
            return False
        if state["ui_mode"] not in valid_ui_modes:
            return False
        if state["current_question_type"] not in valid_quiz_types:
            return False
        if state["current_chapter"] < 1 or state["current_section"] < 1:
            return False
        
        return True


# 전역 State Manager 인스턴스
state_manager = StateManager()