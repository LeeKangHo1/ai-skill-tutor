# backend/app/agents/learning_supervisor/learning_supervisor_agent.py
"""
학습 감독 에이전트
사용자 대면 인터페이스 역할과 다른 에이전트들의 라우팅을 담당합니다.
"""

from ..base import BaseAgent


class LearningSupervisorAgent(BaseAgent):
    """
    학습 감독 에이전트 클래스
    사용자와의 상호작용 및 다른 에이전트들의 조율을 담당합니다.
    """
    
    def __init__(self, config=None):
        """학습 감독 에이전트 초기화"""
        super().__init__("LearningSupervisor", config)
    
    def process(self, state):
        """
        학습 감독 처리
        향후 LangGraph 워크플로우와 연동하여 구현될 예정입니다.
        
        Args:
            state: TutorState 객체
            
        Returns:
            dict: 업데이트된 상태 정보
        """
        # 향후 구현될 예정
        return {"message": "LearningSupervisor processing - to be implemented"}
    
    def route_to_agent(self, user_input, context):
        """
        적절한 에이전트로 라우팅
        향후 구현될 예정입니다.
        """
        pass
    
    def generate_response(self, agent_output):
        """
        최종 응답 생성
        향후 구현될 예정입니다.
        """
        pass