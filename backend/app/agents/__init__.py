# backend/app/agents/__init__.py
# LangGraph 에이전트 모듈

from .session_manager.session_manager_agent import SessionManager
from .learning_supervisor.learning_supervisor_agent import LearningSupervisor
from .theory_educator.theory_educator_agent import TheoryEducator
from .quiz_generator.quiz_generator_agent import QuizGenerator
from .evaluation_feedback.evaluation_feedback_agent import EvaluationFeedbackAgent
from .qna_resolver.qna_resolver_agent import QnAResolverAgent

__all__ = [
    'SessionManager',
    'LearningSupervisor',
    'TheoryEducator',
    'QuizGenerator',
    'EvaluationFeedbackAgent',
    'QnAResolverAgent'
]

# 에이전트 인스턴스 생성 (단일 인스턴스 사용)
learning_supervisor = LearningSupervisor()
theory_educator = TheoryEducator()
quiz_generator = QuizGenerator()
evaluation_feedback_agent = EvaluationFeedbackAgent()
qna_resolver = QnAResolverAgent()
session_manager = SessionManager()

agent_nodes = {
    "learning_supervisor_input": learning_supervisor.process_user_input,
    "learning_supervisor_output": learning_supervisor.generate_final_response,
    "theory_educator": theory_educator.process,
    "quiz_generator": quiz_generator.process,
    "evaluation_feedback_agent": evaluation_feedback_agent.process,
    "qna_resolver": qna_resolver.process,
    "session_manager": session_manager.process,
}