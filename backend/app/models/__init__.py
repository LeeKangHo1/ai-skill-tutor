# backend/app/models/__init__.py
"""
데이터 모델 통합 모듈
모든 모델들을 도메인별로 분리하여 관리합니다.

⚠️ 현재 상태: 이 폴더 내의 모든 파일들은 사용 중이지 않습니다.
현재 프로젝트에서는 직접 SQL 쿼리를 사용하고 있으며, ORM 모델은 비활성화 상태입니다.

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

📝 참고: 향후 ORM 모델 사용이 필요할 경우 이 구조를 활용할 수 있습니다.
"""

# 사용자 관련 모델들 (현재 미사용)
# from .user import User, UserAuthToken, UserProgress, UserStatistics

# 학습 관련 모델들 (현재 미사용)
# from .learning import LearningSession, SessionConversation, SessionQuiz

# 챕터 관련 모델들 (향후 추가 예정)
# from .chapter import Chapter, ChapterContent

__all__ = [
    # 현재 모든 모델이 비활성화 상태
    # 사용자 관련 모델
    # 'User', 'UserAuthToken', 'UserProgress', 'UserStatistics',
    # 학습 관련 모델
    # 'LearningSession', 'SessionConversation', 'SessionQuiz'
]