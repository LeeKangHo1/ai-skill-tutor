# backend/app/agents/base/agent_config.py
"""
에이전트 설정 클래스
에이전트들의 공통 설정을 관리합니다.
"""


class AgentConfig:
    """
    에이전트 설정 클래스
    모든 에이전트의 공통 설정을 관리합니다.
    """
    
    def __init__(self):
        """에이전트 설정 초기화"""
        self.model_settings = {
            'temperature': 0.7,
            'max_tokens': 1000,
            'model_name': 'gemini-2.5-flash'
        }
        
        self.timeout_settings = {
            'default_timeout': 30,
            'max_retries': 3
        }
        
        self.logging_settings = {
            'log_level': 'INFO',
            'log_activities': True
        }
    
    def get_model_config(self, agent_type=None):
        """
        모델 설정 조회
        향후 에이전트별 특화 설정을 위해 구현될 예정입니다.
        """
        return self.model_settings
    
    def get_timeout_config(self):
        """
        타임아웃 설정 조회
        """
        return self.timeout_settings