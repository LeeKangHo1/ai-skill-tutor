# backend/app/models/learning/quiz.py
"""
세션 퀴즈 모델
학습 세션 중 출제되는 퀴즈 정보를 관리합니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class SessionQuiz:
    """세션 퀴즈 정보를 관리하는 모델 클래스"""
    
    def __init__(self, quiz_id: Optional[int] = None, session_id: str = "",
                 question_number: Optional[int] = None, question_type: Optional[str] = None,
                 question_content: Optional[str] = None, user_answer: Optional[str] = None,
                 is_answer_correct: Optional[int] = None, evaluation_feedback: Optional[str] = None,
                 hint_usage_count: int = 0, created_at: Optional[datetime] = None):
        self.quiz_id = quiz_id
        self.session_id = session_id
        self.question_number = question_number
        self.question_type = question_type
        self.question_content = question_content
        self.user_answer = user_answer
        self.is_answer_correct = is_answer_correct  # 0: 틀림, 1: 맞음, None: 미평가
        self.evaluation_feedback = evaluation_feedback
        self.hint_usage_count = hint_usage_count
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'quiz_id': self.quiz_id,
            'session_id': self.session_id,
            'question_number': self.question_number,
            'question_type': self.question_type,
            'question_content': self.question_content,
            'user_answer': self.user_answer,
            'is_answer_correct': self.is_answer_correct,
            'evaluation_feedback': self.evaluation_feedback,
            'hint_usage_count': self.hint_usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionQuiz':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        created_at = None
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        return cls(
            quiz_id=data.get('quiz_id'),
            session_id=data.get('session_id', ''),
            question_number=data.get('question_number'),
            question_type=data.get('question_type'),
            question_content=data.get('question_content'),
            user_answer=data.get('user_answer'),
            is_answer_correct=data.get('is_answer_correct'),
            evaluation_feedback=data.get('evaluation_feedback'),
            hint_usage_count=data.get('hint_usage_count', 0),
            created_at=created_at
        )