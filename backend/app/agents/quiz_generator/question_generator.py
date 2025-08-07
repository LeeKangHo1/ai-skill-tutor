# backend/app/agents/quiz_generator/question_generator.py
"""
문제 생성기
다양한 유형의 퀴즈 문제를 생성합니다.
"""


class QuestionGenerator:
    """
    문제 생성기 클래스
    다양한 형태의 퀴즈 문제를 생성합니다.
    """
    
    def __init__(self):
        """문제 생성기 초기화"""
        self.question_types = ['multiple_choice', 'short_answer', 'true_false']
    
    def generate_multiple_choice(self, content, difficulty):
        """
        객관식 문제 생성
        향후 구현될 예정입니다.
        """
        pass
    
    def generate_short_answer(self, content, difficulty):
        """
        주관식 문제 생성
        향후 구현될 예정입니다.
        """
        pass
    
    def generate_true_false(self, content):
        """
        참/거짓 문제 생성
        향후 구현될 예정입니다.
        """
        pass