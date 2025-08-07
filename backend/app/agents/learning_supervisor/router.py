# backend/app/agents/learning_supervisor/router.py
"""
감독 에이전트 라우터
사용자 입력을 분석하여 적절한 에이전트로 라우팅합니다.
"""


class SupervisorRouter:
    """
    감독 에이전트 라우터 클래스
    사용자 의도를 분석하여 적절한 에이전트를 선택합니다.
    """
    
    def __init__(self):
        """라우터 초기화"""
        self.agent_mapping = {
            'theory': 'TheoryEducator',
            'quiz': 'QuizGenerator',
            'evaluation': 'EvaluationFeedbackAgent',
            'question': 'QnAResolver'
        }
    
    def analyze_intent(self, user_input):
        """
        사용자 의도 분석
        향후 구현될 예정입니다.
        """
        pass
    
    def select_agent(self, intent, context):
        """
        적절한 에이전트 선택
        향후 구현될 예정입니다.
        """
        pass