# backend/app/agents/learning_supervisor/supervisor_router.py

from app.core.langraph.state_manager import TutorState


def supervisor_router(state: TutorState) -> str:
    """
    LearningSupervisor에서 다음 노드를 결정하는 LangGraph 라우터 함수
    
    새로운 워크플로우:
    1. session_start → 바로 theory_educator (의도 분석 없음)
    2. theory_completed → 질문 받기 OR 퀴즈 진행
    3. quiz_answer → evaluation_feedback (의도 분석 없음)
    4. quiz_and_feedback_completed → 질문 받기 OR 새 세션 시작
    
    Args:
        state: 현재 TutorState (user_intent가 설정된 상태)
        
    Returns:
        다음 노드 이름 ("theory_educator", "quiz_generator", "evaluation_feedback", 
                   "qna_resolver", "session_manager", "learning_supervisor_output")
    """
    try:
        user_intent = state.get("user_intent", "next_step")
        session_stage = state.get("session_progress_stage", "session_start")
        session_decision = state.get("session_decision_result", "")
        
        print(f"[Router] 라우팅 결정 - intent: {user_intent}, stage: {session_stage}, decision: {session_decision}")
        
        # 1. 퀴즈 답변 처리 (의도 분석 없이 바로 평가로)
        if user_intent == "quiz_answer":
            print("[Router] → evaluation_feedback (퀴즈 답변 제출)")
            return "evaluation_feedback"
        
        # 2. 질문 답변 요청  
        if user_intent == "question":
            print("[Router] → qna_resolver (질문 답변)")
            return "qna_resolver"
        
        # 3. 세션 완료 처리 (평가 완료 후)
        if session_stage == "quiz_and_feedback_completed" and user_intent == "next_step":
            print("[Router] → session_manager (세션 완료)")
            return "session_manager"
        
        # 4. 다음 단계 진행
        if user_intent == "next_step":
            if session_stage == "session_start":
                print("[Router] → theory_educator (세션 시작)")
                return "theory_educator"
            elif session_stage == "theory_completed":
                print("[Router] → quiz_generator (이론 완료 후)")
                return "quiz_generator"
        
        # 5. 기본값 - 직접 응답 생성
        print(f"[Router] → learning_supervisor_output (직접 응답, intent: {user_intent})")
        return "learning_supervisor_output"
        
    except Exception as e:
        print(f"[Router] 라우팅 오류: {e} - 기본값으로 learning_supervisor_output 반환")
        return "learning_supervisor_output"


def _has_response_ready(state: TutorState) -> bool:
    """
    에이전트 응답이 준비되었는지 확인
    
    Args:
        state: TutorState
        
    Returns:
        응답 준비 여부
    """
    drafts = [
        state.get("theory_draft", ""),
        state.get("quiz_draft", ""),
        state.get("feedback_draft", ""),
        state.get("qna_draft", "")
    ]
    
    # 하나라도 내용이 있으면 응답 준비된 것으로 간주
    for draft in drafts:
        if draft and draft.strip():
            return True
    
    return False


def _is_input_request(state: TutorState) -> bool:
    """
    사용자 입력 요청 상황인지 확인
    
    Args:
        state: TutorState
        
    Returns:
        입력 요청 여부
    """
    # 최근 대화에서 "메시지를 입력해주세요" 또는 "답변을 입력해주세요" 메시지가 있는지 확인
    conversations = state.get("current_session_conversations", [])
    
    if not conversations:
        return False
    
    # 마지막 메시지 확인
    last_conversation = conversations[-1]
    last_message = last_conversation.get("message", "").lower()
    
    # 입력 요청 관련 키워드 확인
    input_keywords = ["메시지를 입력해주세요", "답변을 입력해주세요", "입력해주세요"]
    
    for keyword in input_keywords:
        if keyword in last_message:
            return True
    
    return False


class SupervisorRouter:
    """
    라우팅 로직을 관리하는 클래스 (추가 기능용)
    """
    
    def __init__(self):
        pass
    
    def get_available_routes(self, state: TutorState) -> list:
        """
        현재 상태에서 가능한 라우팅 옵션 반환
        
        Args:
            state: TutorState
            
        Returns:
            가능한 라우트 목록
        """
        session_stage = state.get("session_progress_stage", "session_start")
        user_intent = state.get("user_intent", "next_step")
        available_routes = []
        
        # 항상 가능한 라우트
        available_routes.append("learning_supervisor_output")  # 직접 응답은 언제든 가능
        
        # 단계별 가능한 라우트
        if session_stage == "session_start":
            available_routes.append("theory_educator")
        
        elif session_stage == "theory_completed":
            available_routes.append("qna_resolver")   # 질문 가능
            available_routes.append("quiz_generator") # 퀴즈 진행 가능
        
        elif session_stage == "quiz_and_feedback_completed":
            available_routes.append("qna_resolver")     # 질문 가능
            available_routes.append("session_manager")  # 새 세션 시작 가능
        
        # 퀴즈 답변 시 가능한 라우트
        if user_intent == "quiz_answer":
            available_routes.append("evaluation_feedback")
        
        return available_routes
    
    def validate_route(self, state: TutorState, target_route: str) -> bool:
        """
        특정 라우트가 현재 상태에서 유효한지 검증
        
        Args:
            state: TutorState
            target_route: 검증할 라우트 이름
            
        Returns:
            라우트 유효성 여부
        """
        available_routes = self.get_available_routes(state)
        return target_route in available_routes
    
    def get_route_description(self, route_name: str) -> str:
        """
        라우트 설명 반환
        
        Args:
            route_name: 라우트 이름
            
        Returns:
            라우트 설명
        """
        descriptions = {
            "theory_educator": "개념 설명 생성 (세션 시작 시 자동 진행)",
            "quiz_generator": "퀴즈 문제 생성 (이론 완료 후)",
            "evaluation_feedback": "답변 평가 및 피드백 (퀴즈 답변 제출 시)",
            "qna_resolver": "질문 답변 처리 (이론 완료 후 또는 피드백 완료 후)",
            "session_manager": "새 세션 시작 처리 (피드백 완료 후)",
            "learning_supervisor_output": "직접 응답 생성 (기본 경로)"
        }
        
        return descriptions.get(route_name, "알 수 없는 라우트")
    
    def debug_routing_decision(self, state: TutorState) -> dict:
        """
        라우팅 결정 과정을 디버깅용으로 반환
        
        Args:
            state: TutorState
            
        Returns:
            디버깅 정보
        """
        return {
            "user_intent": state.get("user_intent", ""),
            "session_stage": state.get("session_progress_stage", ""),
            "session_decision": state.get("session_decision_result", ""),
            "ui_mode": state.get("ui_mode", ""),
            "has_response_ready": _has_response_ready(state),
            "is_input_request": _is_input_request(state),
            "available_routes": self.get_available_routes(state),
            "selected_route": supervisor_router(state)
        }
    
    def get_intent_priority(self, user_intent: str) -> int:
        """
        사용자 의도 우선순위 반환 (낮을수록 높은 우선순위)
        
        Args:
            user_intent: 사용자 의도
            
        Returns:
            우선순위 숫자
        """
        priority_map = {
            "quiz_answer": 1,     # 최우선 - 퀴즈 답변
            "question": 2,        # 높음 - 질문
            "next_step": 3,       # 보통 - 다음 단계
        }
        
        return priority_map.get(user_intent, 4)  # 기타는 가장 낮은 우선순위
    
    def should_bypass_intent_analysis(self, state: TutorState) -> bool:
        """
        의도 분석을 우회해야 하는지 판단
        
        Args:
            state: TutorState
            
        Returns:
            의도 분석 우회 여부
        """
        session_stage = state.get("session_progress_stage", "session_start")
        ui_mode = state.get("ui_mode", "chat")
        
        # 세션 시작이거나 퀴즈 모드인 경우 의도 분석 우회
        if session_stage == "session_start":
            return True
        
        if ui_mode == "quiz":
            return True
        
        return False


# 전역 라우터 인스턴스 (추가 기능 사용 시)
router_manager = SupervisorRouter()