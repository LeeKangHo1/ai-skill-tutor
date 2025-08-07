# backend/app/agents/base/base_agent.py
"""
기본 에이전트 클래스
모든 LangGraph 에이전트가 상속받는 기본 클래스입니다.
"""


class BaseAgent:
    """
    기본 에이전트 클래스
    모든 에이전트의 공통 기능을 제공합니다.
    """
    
    def __init__(self, name, config=None):
        """
        기본 에이전트 초기화
        
        Args:
            name (str): 에이전트 이름
            config (dict): 에이전트 설정
        """
        self.name = name
        self.config = config or {}
    
    def process(self, state):
        """
        상태 처리 메서드
        각 에이전트에서 오버라이드하여 구현합니다.
        
        Args:
            state: TutorState 객체
            
        Returns:
            dict: 업데이트된 상태 정보
        """
        raise NotImplementedError("각 에이전트에서 구현해야 합니다.")
    
    def validate_input(self, state):
        """
        입력 상태 검증
        향후 구현될 예정입니다.
        """
        pass
    
    def log_activity(self, activity, details=None):
        """
        에이전트 활동 로깅
        향후 구현될 예정입니다.
        """
        pass