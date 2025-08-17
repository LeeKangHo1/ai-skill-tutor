# backend/app/core/langraph/state_manager.py
# v2.0 업데이트: 퀴즈 필드 완전 재설계, 객관식/주관식 분리, AUTO_INCREMENT 세션 ID 지원

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
import copy

# TutorState 클래스 정의 (PRD v2.0 기준 - 퀴즈 필드 완전 재설계)
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
    
    # === 퀴즈 관련 정보 (v2.0 완전 재설계) ===
    quiz_type: str                        # "multiple_choice" 또는 "subjective"
    quiz_content: str                     # 퀴즈 문제 내용
    quiz_options: List[str]               # 객관식: ["선택지1", "선택지2", "선택지3", "선택지4"], 주관식: []
    quiz_correct_answer: Any              # 객관식: 정답 번호(int), 주관식: None
    quiz_explanation: str                 # 객관식: 정답 해설, 주관식: ""
    quiz_sample_answer: str               # 객관식: "", 주관식: 모범 답안 예시
    quiz_evaluation_criteria: List[str]   # 객관식: [], 주관식: ["평가기준1", "평가기준2", "평가기준3"]
    quiz_hint: str                        # 힌트 내용 (공통)
    user_answer: str                      # 사용자 답변
    multiple_answer_correct: bool         # 객관식 정답 여부 (True/False)
    subjective_answer_score: int          # 주관식 점수 (0~100점)
    evaluation_feedback: str              # 평가 및 피드백 내용
    
    # === 에이전트 대본 저장 ===
    theory_draft: str                 # TheoryEducator 생성 대본
    quiz_draft: str                   # QuizGenerator 생성 대본
    feedback_draft: str               # EvaluationFeedbackAgent 생성 대본
    qna_draft: str                    # QnAResolver 생성 대본
    
    # === 라우팅 & 디버깅 ===
    user_intent: str  # 사용자 의도 ("next_step", "question", "quiz_answer")
    previous_agent: str  # 이전 에이전트 이름 (디버깅 및 복귀 추적용)
    
    # === 학습 세션 제어 (SessionManager 활용) ===
    retry_decision_result: str  # "proceed": 다음 단계 진행, "retry": 현재 구간 재학습 (필드명 변경)
    current_session_count: int    # 현재 구간에서 학습 세션 횟수 (1회 제한으로 변경)
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
        """기본 State 템플릿 생성 (v2.0 퀴즈 필드 구조)"""
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
            
            # 퀴즈 관련 정보 (v2.0 완전 재설계)
            quiz_type="multiple_choice",              # 기본값: 객관식
            quiz_content="",                          # 퀴즈 문제 내용
            quiz_options=[],                          # 객관식 선택지 배열
            quiz_correct_answer=None,                 # 객관식 정답 번호
            quiz_explanation="",                      # 객관식 정답 해설
            quiz_sample_answer="",                    # 주관식 모범 답안
            quiz_evaluation_criteria=[],              # 주관식 평가 기준
            quiz_hint="",                             # 힌트 내용
            user_answer="",                           # 사용자 답변
            multiple_answer_correct=False,            # 객관식 정답 여부
            subjective_answer_score=0,                # 주관식 점수
            evaluation_feedback="",                   # 평가 피드백
            
            # 에이전트 대본 저장
            theory_draft="",
            quiz_draft="",
            feedback_draft="",
            qna_draft="",
            
            # 라우팅 & 디버깅
            user_intent="next_step",  # 기본값: 다음 단계 진행
            previous_agent="",
            
            # 학습 세션 제어 (필드명 변경)
            retry_decision_result="",                 # session_decision_result → retry_decision_result
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
                        quiz_type: str = None,
                        quiz_content: str = None,
                        quiz_options: List[str] = None,
                        quiz_correct_answer: Any = None,
                        quiz_explanation: str = None,
                        quiz_sample_answer: str = None,
                        quiz_evaluation_criteria: List[str] = None,
                        quiz_hint: str = None,
                        user_answer: str = None,
                        multiple_answer_correct: bool = None,
                        subjective_answer_score: int = None,
                        feedback: str = None) -> TutorState:
        """
        퀴즈 관련 정보 업데이트 (v2.0 완전 재설계)
        
        Args:
            state: 현재 State
            quiz_type: 퀴즈 타입 ("multiple_choice" or "subjective")
            quiz_content: 퀴즈 문제 내용
            quiz_options: 객관식 선택지 배열
            quiz_correct_answer: 객관식 정답 번호 또는 주관식 None
            quiz_explanation: 객관식 정답 해설
            quiz_sample_answer: 주관식 모범 답안
            quiz_evaluation_criteria: 주관식 평가 기준
            quiz_hint: 힌트 내용
            user_answer: 사용자 답변
            multiple_answer_correct: 객관식 정답 여부
            subjective_answer_score: 주관식 점수
            feedback: 피드백 내용
        
        Returns:
            업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 퀴즈 기본 정보
        if quiz_type is not None:
            updated_state["quiz_type"] = quiz_type
        if quiz_content is not None:
            updated_state["quiz_content"] = quiz_content
        if quiz_hint is not None:
            updated_state["quiz_hint"] = quiz_hint
        
        # 객관식 전용 필드
        if quiz_options is not None:
            updated_state["quiz_options"] = quiz_options
        if quiz_correct_answer is not None:
            updated_state["quiz_correct_answer"] = quiz_correct_answer
        if quiz_explanation is not None:
            updated_state["quiz_explanation"] = quiz_explanation
        
        # 주관식 전용 필드
        if quiz_sample_answer is not None:
            updated_state["quiz_sample_answer"] = quiz_sample_answer
        if quiz_evaluation_criteria is not None:
            updated_state["quiz_evaluation_criteria"] = quiz_evaluation_criteria
        
        # 사용자 답변 및 평가 결과
        if user_answer is not None:
            updated_state["user_answer"] = user_answer
        if multiple_answer_correct is not None:
            updated_state["multiple_answer_correct"] = multiple_answer_correct
        if subjective_answer_score is not None:
            updated_state["subjective_answer_score"] = subjective_answer_score
        if feedback is not None:
            updated_state["evaluation_feedback"] = feedback
            
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
        세션 상태 초기화 (v2.0 퀴즈 필드 구조)
        
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
            
            # 퀴즈 관련 필드 초기화 (v2.0 구조)
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
                "quiz_type": "multiple_choice"  # 새 챕터 시작 시 기본값으로 초기화
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
        현재 섹션의 퀴즈 타입으로 State 업데이트 (v2.0 필드명 변경)
        
        Args:
            state: 현재 State
            chapter_data: 전체 챕터 데이터
        
        Returns:
            퀴즈 타입이 업데이트된 State
        """
        quiz_type = self.get_quiz_type_from_section(state, chapter_data)
        
        updated_state = copy.deepcopy(state)
        updated_state["quiz_type"] = quiz_type  # current_question_type → quiz_type
        
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
        현재 섹션의 퀴즈 타입을 State에 동기화 (v2.0 단순화)
        quiz_generator 호출 전에 사용하여 JSON과 State 간 일관성 보장
        
        Args:
            state: 현재 State
        
        Returns:
            동기화된 State
        """
        # v2.0에서는 quiz_type 하나만 사용하므로 동기화 로직이 단순해짐
        return copy.deepcopy(state)
    
    def parse_quiz_from_json(self, state: TutorState, quiz_json: Dict[str, Any]) -> TutorState:
        """
        ChatGPT에서 생성된 퀴즈 JSON을 State에 파싱 (v2.0 신규 메서드)
        
        Args:
            state: 현재 State
            quiz_json: ChatGPT에서 생성된 퀴즈 JSON
        
        Returns:
            퀴즈 정보가 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 기본 퀴즈 정보
        quiz_type = quiz_json.get("quiz_type", "multiple_choice")
        updated_state["quiz_type"] = quiz_type
        updated_state["quiz_content"] = quiz_json.get("question", "")
        updated_state["quiz_hint"] = quiz_json.get("hint", "")
        
        # 객관식 전용 필드
        if quiz_type == "multiple_choice":
            updated_state["quiz_options"] = quiz_json.get("options", [])
            updated_state["quiz_correct_answer"] = quiz_json.get("correct_answer", 1)
            updated_state["quiz_explanation"] = quiz_json.get("explanation", "")
            # 주관식 필드 초기화
            updated_state["quiz_sample_answer"] = ""
            updated_state["quiz_evaluation_criteria"] = []
        
        # 주관식 전용 필드
        elif quiz_type == "subjective":
            updated_state["quiz_sample_answer"] = quiz_json.get("sample_answer", "")
            updated_state["quiz_evaluation_criteria"] = quiz_json.get("evaluation_criteria", [])
            # 객관식 필드 초기화
            updated_state["quiz_options"] = []
            updated_state["quiz_correct_answer"] = None
            updated_state["quiz_explanation"] = ""
        
        return updated_state
    
    def update_evaluation_result(self, state: TutorState, 
                               is_correct: bool = None,
                               score: int = None,
                               feedback: str = None) -> TutorState:
        """
        평가 결과 업데이트 (v2.0 객관식/주관식 분리)
        
        Args:
            state: 현재 State
            is_correct: 객관식 정답 여부
            score: 주관식 점수 (0-100)
            feedback: 평가 피드백
        
        Returns:
            평가 결과가 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        quiz_type = state.get("quiz_type", "multiple_choice")
        
        if quiz_type == "multiple_choice" and is_correct is not None:
            updated_state["multiple_answer_correct"] = is_correct
            updated_state["subjective_answer_score"] = 0  # 객관식에서는 0으로 초기화
        elif quiz_type == "subjective" and score is not None:
            updated_state["subjective_answer_score"] = score
            updated_state["multiple_answer_correct"] = False  # 주관식에서는 False로 초기화
        
        if feedback is not None:
            updated_state["evaluation_feedback"] = feedback
        
        return updated_state
    
    def clear_quiz_data(self, state: TutorState) -> TutorState:
        """
        퀴즈 관련 데이터 초기화 (v2.0 신규 메서드)
        
        Args:
            state: 현재 State
        
        Returns:
            퀴즈 데이터가 초기화된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 퀴즈 관련 모든 필드 초기화
        updated_state.update({
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
            "evaluation_feedback": ""
        })
        
        return updated_state
    
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
        State 유효성 검증 (v2.0 필드명 변경 반영)
        
        Args:
            state: 검증할 State
        
        Returns:
            유효성 여부
        """
        required_fields = [
            "user_id", "user_type", "current_chapter", "current_section", "current_agent",
            "session_progress_stage", "ui_mode", "quiz_type"  # current_question_type → quiz_type
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
        if state["quiz_type"] not in valid_quiz_types:  # current_question_type → quiz_type
            return False
        if state["current_chapter"] < 1 or state["current_section"] < 1:
            return False
        
        return True
    
    def update_user_answer(self, state: TutorState, user_answer: str) -> TutorState:
        """
        사용자 답변만 업데이트 (v2.0 신규 메서드)
        퀴즈 내용은 QuizGenerator가, 평가 결과는 EvaluationFeedbackAgent가 담당
        
        Args:
            state: 현재 State
            user_answer: 사용자 답변
        
        Returns:
            사용자 답변이 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state["user_answer"] = user_answer
        return updated_state
    
    def update_session_decision(self, state: TutorState, decision: str) -> TutorState:
        """
        세션 완료 후 사용자 결정 업데이트 (v2.0 신규 메서드)
        
        Args:
            state: 현재 State
            decision: 사용자 결정 ("proceed" 또는 "retry")
        
        Returns:
            결정이 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state["retry_decision_result"] = decision
        return updated_state
    
    def prepare_next_session(self, state: TutorState, next_chapter: int = None, next_section: int = None) -> TutorState:
        """
        다음 세션 준비 (v2.0 신규 메서드)
        
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
        updated_state = self.reset_session_state(updated_state, new_chapter=(next_chapter is not None))
        
        # 에이전트를 session_manager로 설정
        updated_state = self.update_agent_transition(updated_state, "session_manager")
        
        return updated_state


# 전역 State Manager 인스턴스
state_manager = StateManager()