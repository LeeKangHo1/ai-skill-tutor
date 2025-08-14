# backend/app/agents/qna_resolver/qna_resolver_agent.py

from app.core.langraph.state_manager import TutorState, state_manager


class QnAResolverAgent:
    """
    QnA Resolver 에이전트 클래스 (임시 구현)
    
    현재는 임시 구현이며, 실제 구현 시 다음 기능들이 추가될 예정:
    1. Vector DB 검색을 통한 학습 컨텍스트 매칭
    2. 웹 검색을 통한 최신 정보 제공
    3. 학습 관련성 판단 및 적절한 응답 생성
    4. 학습 진행으로의 자연스러운 유도
    """
    
    def __init__(self):
        self.agent_name = "qna_resolver"
        self.description = "질문 답변 처리 에이전트 (임시 구현)"
    
    def process(self, state: TutorState) -> TutorState:
        """
        QnA Resolver 메인 처리 메서드
        
        Args:
            state: 현재 TutorState
            
        Returns:
            qna_draft가 업데이트된 TutorState
        """
        try:
            # 현재 사용자 입력 메시지 확인 (최근 대화에서 추출)
            conversations = state.get("current_session_conversations", [])
            user_message = ""
            
            if conversations:
                # 가장 최근 사용자 메시지 찾기
                for conv in reversed(conversations):
                    if conv.get("message_type") == "user":
                        user_message = conv.get("message", "")
                        break
            
            # 임시 응답 메시지 생성
            if not user_message:
                qna_response = "QnAResolver가 호출되었습니다. 무엇이 궁금하신가요?"
            else:
                qna_response = f"QnAResolver가 호출되었습니다. '{user_message}'에 대한 답변을 준비 중입니다. (실제 구현 예정)"
            
            # qna_draft에 응답 저장
            updated_state = state_manager.update_agent_draft(state, self.agent_name, qna_response)
            
            # 현재 에이전트를 qna_resolver로 설정
            updated_state = state_manager.update_agent_transition(updated_state, self.agent_name)
            
            print(f"[{self.agent_name}] 임시 응답: {qna_response}")
            
            return updated_state
            
        except Exception as e:
            print(f"[{self.agent_name}] 에이전트 오류: {e}")
            
            # 오류 시 기본 응답
            error_response = "QnAResolver에서 일시적인 오류가 발생했습니다. 다시 시도해주세요."
            updated_state = state_manager.update_agent_draft(state, self.agent_name, error_response)
            updated_state = state_manager.update_agent_transition(updated_state, self.agent_name)
            
            return updated_state
    
    def get_status(self) -> str:
        """에이전트 상태 반환"""
        return "임시 구현 - 테스트용 응답만 제공"