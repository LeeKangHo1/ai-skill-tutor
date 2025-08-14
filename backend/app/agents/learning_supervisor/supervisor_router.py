# backend/app/agents/learning_supervisor/supervisor_router.py

from app.core.langraph.state_manager import TutorState


def supervisor_router(state: TutorState) -> str:
    """
    LearningSupervisor에서 다음 노드를 결정하는 LangGraph 라우터 함수
    
    새로운 워크플로우:
    1. session_start → 바로 theory_educator (의도 분석 없음)
    2. theory_completed → 질문 받기 OR 퀴즈 진행
    3. quiz_and_feedback_completed → 질문 받기 OR 새 세션 시작
    
    Args:
        state: 현재 TutorState
        
    Returns:
        다음 노드 이름 ("theory_educator", "quiz_generator", "evaluation_feedback_agent", 
                   "qna_resolver", "session_manager", "END")
    """
    try:
        # State에서 필요한 정보 추출
        user_intent = state.get("user_intent", "next_step")
        session_stage = state.get("session_progress_stage", "session_start")
        current_agent = state.get("current_agent", "")
        
        # 1. 세션 시작 → 바로 이론 설명 (의도 분석 무관)
        if session_stage == "session_start":
            return "theory_educator"
        
        # 2. 퀴즈 답변인 경우 → EvaluationFeedbackAgent
        if user_intent == "quiz_answer":
            return "evaluation_feedback_agent"
        
        # 3. 이론 완료 후 → 질문 OR 퀴즈 진행
        if session_stage == "theory_completed":
            if user_intent == "question":
                return "qna_resolver"
            else:  # next_step
                return "quiz_generator"
        
        # 4. 퀴즈와 피드백 완료 후 → 질문 OR 새 세션 시작
        if session_stage == "quiz_and_feedback_completed":
            if user_intent == "question":
                return "qna_resolver"
            else:  # next_step
                return "session_manager"  # 새 세션 시작
        
        # 5. 현재 에이전트가 learning_supervisor이고 응답이 준비된 경우
        if current_agent == "learning_supervisor":
            # 에이전트 대본이 있으면 최종 응답 생성으로
            if (_has_response_ready(state)):
                return "response_generator"
            
            # 사용자 메시지 입력 요청인 경우 → 워크플로우 종료
            if _is_input_request(state):
                return "END"
        
        # 6. 예외 상황 → 기본적으로 워크플로우 종료
        print(f"supervisor_router: 예상치 못한 상황 - intent: {user_intent}, stage: {session_stage}, agent: {current_agent}")
        return "END"
        
    except Exception as e:
        print(f"supervisor_router 오류: {e}")
        return "END"


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
        available_routes = []
        
        # 항상 가능한 라우트
        available_routes.append("END")  # 종료는 언제든 가능
        
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
        if state.get("user_intent") == "quiz_answer":
            available_routes.append("evaluation_feedback_agent")
        
        # 응답 준비 시 가능한 라우트
        if _has_response_ready(state):
            available_routes.append("response_generator")
        
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
            "evaluation_feedback_agent": "답변 평가 및 피드백",
            "qna_resolver": "질문 답변 처리 (이론 완료 후 또는 피드백 완료 후)",
            "session_manager": "새 세션 시작 처리 (피드백 완료 후)",
            "response_generator": "최종 응답 생성",
            "END": "워크플로우 종료"
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
            "current_agent": state.get("current_agent", ""),
            "has_response_ready": _has_response_ready(state),
            "is_input_request": _is_input_request(state),
            "available_routes": self.get_available_routes(state),
            "selected_route": supervisor_router(state)
        }


# 전역 라우터 인스턴스 (추가 기능 사용 시)
router_manager = SupervisorRouter()