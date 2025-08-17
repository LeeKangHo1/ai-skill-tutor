# backend/app/models/__init__.py
"""
데이터 모델 통합 모듈
모든 모델들을 도메인별로 분리하여 관리합니다.

사용 방법:
1. 통합 import (권장):
   from app.models import User, LearningSession, SessionConversation

2. 도메인별 import:
   from app.models.user import User, UserAuthToken, UserProgress, UserStatistics
   from app.models.learning import LearningSession, SessionConversation, SessionQuiz

3. 특정 모델만 import:
   from app.models.user import User
   from app.models.learning import LearningSession

도메인 구조:
- user/: 사용자 관련 모델 (User, UserAuthToken, UserProgress, UserStatistics)
- learning/: 학습 관련 모델 (LearningSession, SessionConversation, SessionQuiz)
- chapter/: 챕터 관련 모델 (향후 추가 예정)
"""

# 사용자 관련 모델들
from .user import User, UserAuthToken, UserProgress, UserStatistics

# 학습 관련 모델들
from .learning import LearningSession, SessionConversation, SessionQuiz

# 챕터 관련 모델들 (향후 추가 예정)
# from .chapter import Chapter, ChapterContent

__all__ = [
    # 사용자 관련 모델
    'User', 'UserAuthToken', 'UserProgress', 'UserStatistics',
    # 학습 관련 모델
    'LearningSession', 'SessionConversation', 'SessionQuiz'
]