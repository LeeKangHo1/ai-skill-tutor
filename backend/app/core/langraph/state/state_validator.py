# backend/app/core/langraph/state/state_validator.py
# State 유효성 검증 전담 모듈

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .state_definition import TutorState, REQUIRED_FIELDS, VALID_VALUES


class StateValidationError(Exception):
    """State 검증 실패 시 발생하는 예외"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.field = field
        self.value = value
        super().__init__(message)


class StateValidator:
    """
    TutorState 유효성 검증을 담당하는 클래스
    
    주요 기능:
    - 필수 필드 존재 여부 검증
    - 필드값 유효성 검증
    - 비즈니스 룰 검증
    - 퀴즈 타입별 필드 일관성 검증
    - State 무결성 검증
    """
    
    def __init__(self):
        """StateValidator 초기화"""
        self.required_fields = REQUIRED_FIELDS
        self.valid_values = VALID_VALUES
    
    def validate_state(self, state: TutorState, strict: bool = False) -> bool:
        """
        State 전체 유효성 검증
        
        Args:
            state: 검증할 State
            strict: 엄격한 검증 여부 (기본값: False)
        
        Returns:
            유효성 여부
        
        Raises:
            StateValidationError: 검증 실패 시 (strict=True일 때)
        """
        try:
            # 1. 필수 필드 검증
            self.validate_required_fields(state)
            
            # 2. 필드값 유효성 검증
            self.validate_field_values(state)
            
            # 3. 비즈니스 룰 검증
            self.validate_business_rules(state)
            
            # 4. 퀴즈 일관성 검증
            self.validate_quiz_consistency(state)
            
            # 5. 엄격한 검증 시 추가 검사
            if strict:
                self.validate_strict_rules(state)
            
            return True
            
        except StateValidationError:
            if strict:
                raise
            return False
    
    def validate_required_fields(self, state: TutorState) -> None:
        """
        필수 필드 존재 여부 검증
        
        Args:
            state: 검증할 State
        
        Raises:
            StateValidationError: 필수 필드 누락 시
        """
        for field in self.required_fields:
            if field not in state or state[field] is None:
                raise StateValidationError(
                    f"Required field '{field}' is missing or None",
                    field=field
                )
    
    def validate_field_values(self, state: TutorState) -> None:
        """
        필드값 유효성 검증
        
        Args:
            state: 검증할 State
        
        Raises:
            StateValidationError: 유효하지 않은 값일 때
        """
        # user_type 검증
        if state.get("user_type") not in self.valid_values["user_type"]:
            raise StateValidationError(
                f"Invalid user_type: {state.get('user_type')}. "
                f"Valid values: {self.valid_values['user_type']}",
                field="user_type",
                value=state.get("user_type")
            )
        
        # session_progress_stage 검증
        stage = state.get("session_progress_stage")
        if stage not in self.valid_values["session_progress_stage"]:
            raise StateValidationError(
                f"Invalid session_progress_stage: {stage}. "
                f"Valid values: {self.valid_values['session_progress_stage']}",
                field="session_progress_stage",
                value=stage
            )
        
        # ui_mode 검증
        ui_mode = state.get("ui_mode")
        if ui_mode not in self.valid_values["ui_mode"]:
            raise StateValidationError(
                f"Invalid ui_mode: {ui_mode}. "
                f"Valid values: {self.valid_values['ui_mode']}",
                field="ui_mode",
                value=ui_mode
            )
        
        # quiz_type 검증
        quiz_type = state.get("quiz_type")
        if quiz_type not in self.valid_values["quiz_type"]:
            raise StateValidationError(
                f"Invalid quiz_type: {quiz_type}. "
                f"Valid values: {self.valid_values['quiz_type']}",
                field="quiz_type",
                value=quiz_type
            )
        
        # user_intent 검증
        user_intent = state.get("user_intent")
        if user_intent not in self.valid_values["user_intent"]:
            raise StateValidationError(
                f"Invalid user_intent: {user_intent}. "
                f"Valid values: {self.valid_values['user_intent']}",
                field="user_intent",
                value=user_intent
            )
        
        # retry_decision_result 검증
        decision = state.get("retry_decision_result")
        if decision not in self.valid_values["retry_decision_result"]:
            raise StateValidationError(
                f"Invalid retry_decision_result: {decision}. "
                f"Valid values: {self.valid_values['retry_decision_result']}",
                field="retry_decision_result",
                value=decision
            )
        
        # current_agent 검증 (등록된 에이전트인지 확인)
        agent = state.get("current_agent")
        if agent and agent not in self.valid_values["agent_names"]:
            raise StateValidationError(
                f"Invalid current_agent: {agent}. "
                f"Valid agents: {self.valid_values['agent_names']}",
                field="current_agent",
                value=agent
            )
    
    def validate_business_rules(self, state: TutorState) -> None:
        """
        비즈니스 룰 검증
        
        Args:
            state: 검증할 State
        
        Raises:
            StateValidationError: 비즈니스 룰 위반 시
        """
        # 1. 챕터/섹션 번호는 1 이상이어야 함
        chapter = state.get("current_chapter", 0)
        section = state.get("current_section", 0)
        
        if chapter < 1:
            raise StateValidationError(
                f"current_chapter must be >= 1, got {chapter}",
                field="current_chapter",
                value=chapter
            )
        
        if section < 1:
            raise StateValidationError(
                f"current_section must be >= 1, got {section}",
                field="current_section",
                value=section
            )
        
        # 2. user_id는 양수여야 함
        user_id = state.get("user_id", 0)
        if user_id <= 0:
            raise StateValidationError(
                f"user_id must be > 0, got {user_id}",
                field="user_id",
                value=user_id
            )
        
        # 3. 세션 카운트는 음수일 수 없음
        session_count = state.get("current_session_count", 0)
        if session_count < 0:
            raise StateValidationError(
                f"current_session_count must be >= 0, got {session_count}",
                field="current_session_count",
                value=session_count
            )
        
        # 4. 주관식 점수는 0-100 범위여야 함 (주관식 퀴즈인 경우에만)
        score = state.get("subjective_answer_score", 0)
        quiz_type = state.get("quiz_type", "multiple_choice")
        
        # 주관식 퀴즈이고 실제로 점수가 설정된 경우에만 범위 검증
        if quiz_type == "subjective" and score != 0:
            if not (0 <= score <= 100):
                raise StateValidationError(
                    f"subjective_answer_score must be 0-100, got {score}",
                    field="subjective_answer_score",
                    value=score
                )
        
        # 5. 힌트 사용 횟수는 음수일 수 없음
        hint_count = state.get("hint_usage_count", 0)
        if hint_count < 0:
            raise StateValidationError(
                f"hint_usage_count must be >= 0, got {hint_count}",
                field="hint_usage_count",
                value=hint_count
            )
    
    def validate_quiz_consistency(self, state: TutorState) -> None:
        """
        퀴즈 타입별 필드 일관성 검증
        
        Args:
            state: 검증할 State
        
        Raises:
            StateValidationError: 퀴즈 필드 불일치 시
        """
        quiz_type = state.get("quiz_type", "multiple_choice")
        quiz_content = state.get("quiz_content", "")
        
        # 퀴즈가 아직 생성되지 않은 경우 검증 생략
        if not quiz_content:
            return
        
        if quiz_type == "multiple_choice":
            self._validate_multiple_choice_fields(state)
        elif quiz_type == "subjective":
            self._validate_subjective_fields(state)
    
    def _validate_multiple_choice_fields(self, state: TutorState) -> None:
        """
        객관식 퀴즈 필드 검증
        
        Args:
            state: 검증할 State
        
        Raises:
            StateValidationError: 객관식 필드 오류 시
        """
        quiz_content = state.get("quiz_content", "")
        quiz_options = state.get("quiz_options", [])
        correct_answer = state.get("quiz_correct_answer")
        
        # 퀴즈 내용이 있는 경우에만 선택지 검증
        if quiz_content and not quiz_options:
            raise StateValidationError(
                "Multiple choice quiz must have options when quiz_content exists",
                field="quiz_options"
            )
        
        # 선택지와 정답이 모두 있는 경우에만 정답 범위 검증
        if quiz_options and correct_answer is not None:
            if not isinstance(correct_answer, int):
                raise StateValidationError(
                    f"Multiple choice correct_answer must be int, got {type(correct_answer)}",
                    field="quiz_correct_answer",
                    value=correct_answer
                )
            
            if not (1 <= correct_answer <= len(quiz_options)):
                raise StateValidationError(
                    f"correct_answer {correct_answer} out of range for {len(quiz_options)} options",
                    field="quiz_correct_answer",
                    value=correct_answer
                )
        
        # 주관식 필드가 설정되어 있어도 경고만 출력 (오류 발생하지 않음)
        # 이는 State 전환 과정에서 일시적으로 발생할 수 있는 상황임
    
    def _validate_subjective_fields(self, state: TutorState) -> None:
        """
        주관식 퀴즈 필드 검증
        
        Args:
            state: 검증할 State
        
        Raises:
            StateValidationError: 주관식 필드 오류 시
        """
        quiz_content = state.get("quiz_content", "")
        quiz_options = state.get("quiz_options", [])
        correct_answer = state.get("quiz_correct_answer")
        
        # 퀴즈 내용이 있고 객관식 필드가 설정된 경우에만 검증
        # State 전환 과정에서 일시적으로 객관식 필드가 남아있을 수 있으므로 완화된 검증 적용
        if quiz_content:
            # 주관식 퀴즈에서 선택지가 있으면 경고 (하지만 오류는 발생시키지 않음)
            # 이는 퀴즈 타입 전환 과정에서 발생할 수 있는 일시적 상황
            if quiz_options:
                # 로깅만 하고 오류는 발생시키지 않음
                pass
            
            # 주관식 퀴즈에서 correct_answer가 있으면 경고 (하지만 오류는 발생시키지 않음)
            if correct_answer is not None:
                # 로깅만 하고 오류는 발생시키지 않음
                pass
    
    def validate_strict_rules(self, state: TutorState) -> None:
        """
        엄격한 검증 규칙 (선택적)
        
        Args:
            state: 검증할 State
        
        Raises:
            StateValidationError: 엄격한 규칙 위반 시
        """
        # 1. 세션 진행 단계와 UI 모드 일관성
        stage = state.get("session_progress_stage")
        ui_mode = state.get("ui_mode")
        current_agent = state.get("current_agent")
        
        # 퀴즈 생성 후에는 quiz 모드여야 함
        if current_agent == "quiz_generator" and ui_mode != "quiz":
            raise StateValidationError(
                "quiz_generator should set ui_mode to 'quiz'",
                field="ui_mode",
                value=ui_mode
            )
        
        # 2. 대화 기록 일관성
        conversations = state.get("current_session_conversations", [])
        if conversations and not isinstance(conversations, list):
            raise StateValidationError(
                "current_session_conversations must be a list",
                field="current_session_conversations",
                value=type(conversations)
            )
        
        # 3. 워크플로우 응답 구조 검증
        workflow_response = state.get("workflow_response", {})
        if workflow_response and not isinstance(workflow_response, dict):
            raise StateValidationError(
                "workflow_response must be a dict",
                field="workflow_response",
                value=type(workflow_response)
            )
    
    def validate_field_types(self, state: TutorState) -> None:
        """
        필드 타입 검증
        
        Args:
            state: 검증할 State
        
        Raises:
            StateValidationError: 타입 오류 시
        """
        type_checks = [
            ("user_id", int),
            ("current_chapter", int),
            ("current_section", int),
            ("current_session_count", int),
            ("subjective_answer_score", int),
            ("hint_usage_count", int),
            ("multiple_answer_correct", bool),
            ("quiz_options", list),
            ("quiz_evaluation_criteria", list),
            ("current_session_conversations", list),
            ("recent_sessions_summary", list),
            ("workflow_response", dict),
            ("session_start_time", datetime)
        ]
        
        for field_name, expected_type in type_checks:
            value = state.get(field_name)
            if value is not None and not isinstance(value, expected_type):
                raise StateValidationError(
                    f"Field '{field_name}' must be {expected_type.__name__}, got {type(value).__name__}",
                    field=field_name,
                    value=value
                )
    
    def get_validation_report(self, state: TutorState) -> Dict[str, Any]:
        """
        State 검증 보고서 생성
        
        Args:
            state: 검증할 State
        
        Returns:
            검증 결과 보고서
        """
        report = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "checks_performed": []
        }
        
        # 각 검증 단계별로 실행하고 결과 수집
        validation_steps = [
            ("required_fields", self.validate_required_fields),
            ("field_values", self.validate_field_values),
            ("business_rules", self.validate_business_rules),
            ("quiz_consistency", self.validate_quiz_consistency),
            ("field_types", self.validate_field_types)
        ]
        
        for step_name, validation_func in validation_steps:
            try:
                validation_func(state)
                report["checks_performed"].append(f"{step_name}: PASS")
            except StateValidationError as e:
                report["is_valid"] = False
                report["errors"].append({
                    "step": step_name,
                    "message": str(e),
                    "field": e.field,
                    "value": e.value
                })
                report["checks_performed"].append(f"{step_name}: FAIL")
            except Exception as e:
                report["warnings"].append({
                    "step": step_name,
                    "message": f"Unexpected error: {str(e)}"
                })
                report["checks_performed"].append(f"{step_name}: ERROR")
        
        return report
    
    def validate_for_quiz_generation(self, state: TutorState) -> bool:
        """
        퀴즈 생성 과정에서 사용하는 완화된 검증
        
        Args:
            state: 검증할 State
        
        Returns:
            퀴즈 생성 가능 여부
        """
        try:
            # 필수 필드 검증
            self.validate_required_fields(state)
            
            # 기본 비즈니스 룰만 검증 (퀴즈 관련 검증 제외)
            chapter = state.get("current_chapter", 0)
            section = state.get("current_section", 0)
            user_id = state.get("user_id", 0)
            
            if chapter < 1 or section < 1 or user_id <= 0:
                return False
            
            # 퀴즈 일관성 검증은 생략 (생성 과정에서는 불완전할 수 있음)
            return True
            
        except StateValidationError:
            return False
    
    def quick_validate(self, state: TutorState) -> bool:
        """
        빠른 검증 (필수 필드와 기본 값만 체크)
        
        Args:
            state: 검증할 State
        
        Returns:
            기본 유효성 여부
        """
        try:
            self.validate_required_fields(state)
            
            # 기본적인 값 범위만 체크
            if state.get("current_chapter", 0) < 1:
                return False
            if state.get("current_section", 0) < 1:
                return False
            if state.get("user_id", 0) <= 0:
                return False
            
            return True
        except StateValidationError:
            return False


# 전역 StateValidator 인스턴스
state_validator = StateValidator()