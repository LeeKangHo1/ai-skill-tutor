# backend/app/core/langraph/managers/quiz_manager.py
# 퀴즈 관련 State 조작 전담 모듈

import copy
import json
from typing import Dict, Any, List, Optional, Union

from ..state.state_definition import TutorState


class QuizManager:
    """
    퀴즈 관련 State 조작을 담당하는 클래스
    
    주요 기능:
    - 퀴즈 타입별 State 설정
    - ChatGPT JSON 파싱 및 State 업데이트
    - 사용자 답변 처리
    - 평가 결과 관리
    - 힌트 시스템 관리
    - 퀴즈 데이터 초기화
    """
    
    def __init__(self):
        """QuizManager 초기화"""
        pass
    
    def update_quiz_type_from_section(self, 
                                    state: TutorState, 
                                    chapter_data: Dict[str, Any]) -> TutorState:
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
        updated_state["quiz_type"] = quiz_type
        
        return updated_state
    
    def get_quiz_type_from_section(self, 
                                 state: TutorState, 
                                 chapter_data: Dict[str, Any]) -> str:
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
    
    def get_current_section_data(self, 
                               state: TutorState, 
                               chapter_data: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def parse_quiz_from_json(self, 
                           state: TutorState, 
                           quiz_json: Dict[str, Any]) -> TutorState:
        """
        ChatGPT에서 생성된 퀴즈 JSON을 State에 파싱
        
        Args:
            state: 현재 State
            quiz_json: ChatGPT에서 생성된 퀴즈 JSON
        
        Returns:
            퀴즈 정보가 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 기본 퀴즈 정보 (올바른 키 사용)
        quiz_type = quiz_json.get("type", "multiple_choice")  # quiz_type → type 수정
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
    
    def parse_quiz_from_draft(self, state: TutorState) -> TutorState:
        """
        quiz_draft 필드에서 JSON을 파싱하여 퀴즈 정보 업데이트
        
        Args:
            state: 현재 State
        
        Returns:
            퀴즈 정보가 업데이트된 State
        """
        quiz_draft = state.get("quiz_draft", "")
        
        if not quiz_draft:
            return copy.deepcopy(state)
        
        try:
            quiz_json = json.loads(quiz_draft)
            return self.parse_quiz_from_json(state, quiz_json)
        except (json.JSONDecodeError, TypeError) as e:
            # JSON 파싱 실패 시 기존 State 반환
            return copy.deepcopy(state)
    
    def update_quiz_info(self, 
                        state: TutorState,
                        quiz_type: Optional[str] = None,
                        quiz_content: Optional[str] = None,
                        quiz_options: Optional[List[str]] = None,
                        quiz_correct_answer: Optional[Union[int, None]] = None,
                        quiz_explanation: Optional[str] = None,
                        quiz_sample_answer: Optional[str] = None,
                        quiz_evaluation_criteria: Optional[List[str]] = None,
                        quiz_hint: Optional[str] = None) -> TutorState:
        """
        퀴즈 기본 정보 업데이트
        
        Args:
            state: 현재 State
            quiz_type: 퀴즈 타입
            quiz_content: 퀴즈 문제 내용
            quiz_options: 객관식 선택지
            quiz_correct_answer: 객관식 정답 번호
            quiz_explanation: 객관식 정답 해설
            quiz_sample_answer: 주관식 모범 답안
            quiz_evaluation_criteria: 주관식 평가 기준
            quiz_hint: 힌트 내용
        
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
        
        return updated_state
    
    def update_user_answer(self, 
                          state: TutorState, 
                          user_answer: str) -> TutorState:
        """
        사용자 답변 업데이트
        
        Args:
            state: 현재 State
            user_answer: 사용자 답변
        
        Returns:
            사용자 답변이 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state["user_answer"] = user_answer
        return updated_state
    
    def update_evaluation_result(self, 
                               state: TutorState,
                               is_correct: Optional[bool] = None,
                               score: Optional[int] = None,
                               feedback: Optional[str] = None) -> TutorState:
        """
        평가 결과 업데이트 (객관식/주관식 분리)
        
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
    
    def evaluate_multiple_choice(self, 
                                state: TutorState, 
                                user_answer: str) -> TutorState:
        """
        객관식 로컬 채점 및 결과 업데이트
        
        Args:
            state: 현재 State
            user_answer: 사용자 답변 (문자열)
        
        Returns:
            채점 결과가 업데이트된 State
        """
        updated_state = copy.deepcopy(state)
        
        # 사용자 답변 업데이트
        updated_state["user_answer"] = user_answer
        
        # 로컬 채점
        try:
            user_choice = int(user_answer)
            correct_answer = state.get("quiz_correct_answer", 1)
            is_correct = (user_choice == correct_answer)
            
            updated_state["multiple_answer_correct"] = is_correct
            updated_state["subjective_answer_score"] = 0  # 객관식에서는 0
            
        except (ValueError, TypeError):
            # 답변을 정수로 변환할 수 없는 경우 오답 처리
            updated_state["multiple_answer_correct"] = False
            updated_state["subjective_answer_score"] = 0
        
        return updated_state
    
    def increment_hint_usage(self, state: TutorState) -> TutorState:
        """
        힌트 사용 횟수 증가
        
        Args:
            state: 현재 State
        
        Returns:
            힌트 사용 횟수가 증가된 State
        """
        updated_state = copy.deepcopy(state)
        current_count = state.get("hint_usage_count", 0)
        updated_state["hint_usage_count"] = current_count + 1
        return updated_state
    
    def reset_hint_usage(self, state: TutorState) -> TutorState:
        """
        힌트 사용 횟수 초기화
        
        Args:
            state: 현재 State
        
        Returns:
            힌트 사용 횟수가 초기화된 State
        """
        updated_state = copy.deepcopy(state)
        updated_state["hint_usage_count"] = 0
        return updated_state
    
    def clear_quiz_data(self, state: TutorState) -> TutorState:
        """
        퀴즈 관련 데이터 초기화
        
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
            "evaluation_feedback": "",
            "hint_usage_count": 0
        })
        
        return updated_state
    
    def prepare_quiz_mode(self, 
                         state: TutorState, 
                         quiz_type: Optional[str] = None) -> TutorState:
        """
        퀴즈 모드로 전환 준비
        
        Args:
            state: 현재 State
            quiz_type: 퀴즈 타입 (기본값: 현재 상태 유지)
        
        Returns:
            퀴즈 모드로 설정된 State
        """
        updated_state = copy.deepcopy(state)
        
        # UI 모드를 퀴즈로 변경
        updated_state["ui_mode"] = "quiz"
        
        # 퀴즈 타입 설정
        if quiz_type:
            updated_state["quiz_type"] = quiz_type
        
        # 사용자 의도를 퀴즈 답변으로 설정
        updated_state["user_intent"] = "quiz_answer"
        
        return updated_state
    
    def finish_quiz_mode(self, state: TutorState) -> TutorState:
        """
        퀴즈 모드 종료 후 채팅 모드로 복귀
        
        Args:
            state: 현재 State
        
        Returns:
            채팅 모드로 복귀된 State
        """
        updated_state = copy.deepcopy(state)
        
        # UI 모드를 채팅으로 변경
        updated_state["ui_mode"] = "chat"
        
        # 사용자 의도를 다음 단계로 설정
        updated_state["user_intent"] = "next_step"
        
        return updated_state
    
    def get_quiz_summary(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 퀴즈 상태 요약 반환
        
        Args:
            state: 현재 State
        
        Returns:
            퀴즈 상태 요약
        """
        quiz_type = state.get("quiz_type", "multiple_choice")
        
        summary = {
            "quiz_type": quiz_type,
            "quiz_content": state.get("quiz_content", ""),
            "user_answer": state.get("user_answer", ""),
            "hint_usage_count": state.get("hint_usage_count", 0),
            "evaluation_feedback": state.get("evaluation_feedback", ""),
            "has_hint": bool(state.get("quiz_hint", "")),
            "is_answered": bool(state.get("user_answer", ""))
        }
        
        if quiz_type == "multiple_choice":
            summary.update({
                "options": state.get("quiz_options", []),
                "correct_answer": state.get("quiz_correct_answer"),
                "is_correct": state.get("multiple_answer_correct", False),
                "explanation": state.get("quiz_explanation", "")
            })
        elif quiz_type == "subjective":
            summary.update({
                "sample_answer": state.get("quiz_sample_answer", ""),
                "evaluation_criteria": state.get("quiz_evaluation_criteria", []),
                "score": state.get("subjective_answer_score", 0)
            })
        
        return summary
    
    def is_quiz_completed(self, state: TutorState) -> bool:
        """
        퀴즈 완료 여부 확인
        
        Args:
            state: 현재 State
        
        Returns:
            퀴즈 완료 여부
        """
        # 사용자 답변이 있고 평가 피드백이 있으면 완료
        has_answer = bool(state.get("user_answer", ""))
        has_feedback = bool(state.get("evaluation_feedback", ""))
        
        return has_answer and has_feedback
    
    def get_quiz_score(self, state: TutorState) -> int:
        """
        퀴즈 점수 반환 (객관식/주관식 통합)
        
        Args:
            state: 현재 State
        
        Returns:
            점수 (0-100)
        """
        quiz_type = state.get("quiz_type", "multiple_choice")
        
        if quiz_type == "multiple_choice":
            # 객관식: 정답이면 100점, 오답이면 0점
            return 100 if state.get("multiple_answer_correct", False) else 0
        elif quiz_type == "subjective":
            # 주관식: 채점된 점수 반환
            return state.get("subjective_answer_score", 0)
        
        return 0
    
    def sync_quiz_types(self, state: TutorState) -> TutorState:
        """
        퀴즈 타입 동기화 (v2.0에서는 quiz_type 하나만 사용)
        
        Args:
            state: 현재 State
        
        Returns:
            동기화된 State (v2.0에서는 변경 없음)
        """
        # v2.0에서는 quiz_type 하나만 사용하므로 동기화 불필요
        return copy.deepcopy(state)


# 전역 QuizManager 인스턴스
quiz_manager = QuizManager()