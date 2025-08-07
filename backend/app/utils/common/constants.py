# backend/app/utils/common/constants.py
"""
상수 정의
애플리케이션에서 사용하는 상수들을 정의합니다.
"""

# 사용자 레벨 상수
class UserLevel:
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# 세션 상태 상수
class SessionStatus:
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# 퀴즈 타입 상수
class QuizType:
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
    ESSAY = "essay"


# 에이전트 타입 상수
class AgentType:
    SESSION_MANAGER = "session_manager"
    LEARNING_SUPERVISOR = "learning_supervisor"
    THEORY_EDUCATOR = "theory_educator"
    QUIZ_GENERATOR = "quiz_generator"
    EVALUATION_FEEDBACK = "evaluation_feedback"
    QNA_RESOLVER = "qna_resolver"


# 응답 상태 코드
class ResponseStatus:
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


# 학습 챕터 상수
class ChapterType:
    AI_BASICS = "ai_basics"
    PROMPT_ENGINEERING = "prompt_engineering"
    AI_TOOLS = "ai_tools"
    PRACTICAL_APPLICATIONS = "practical_applications"