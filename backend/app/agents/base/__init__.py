# app/agents/base/__init__.py

"""
Base Agent 모듈

모든 에이전트의 기반이 되는 추상 클래스와 설정 클래스를 제공합니다.
각 에이전트는 BaseAgent를 상속받아 일관된 인터페이스로 구현됩니다.

주요 구성요소:
- BaseAgent: 모든 에이전트의 추상 기본 클래스
- AgentConfig: 에이전트별 설정 및 프롬프트 관리
- ModelType: 지원하는 AI 모델 타입 정의
- AgentRole: 에이전트 역할 정의

사용 예시:
    from app.agents.base import BaseAgent, AgentConfig, AgentRole, ModelType
    from app.agents.base import create_theory_educator_config
    
    config = create_theory_educator_config()
    # 또는
    config = AgentConfig(
        agent_role=AgentRole.THEORY_EDUCATOR,
        model_type=ModelType.GEMINI_FLASH
    )
"""

from .base_agent import BaseAgent
from .agent_config import (
    AgentConfig,
    ModelType,
    AgentRole,
    create_session_manager_config,
    create_learning_supervisor_config,
    create_theory_educator_config,
    create_quiz_generator_config,
    create_evaluation_feedback_config,
    create_qna_resolver_config
)

# 모듈 버전 정보
__version__ = "1.0.0"
__author__ = "AI Skill Tutor Development Team"

# 외부에서 import할 수 있는 주요 클래스 및 함수
__all__ = [
    # 기본 클래스
    "BaseAgent",
    "AgentConfig",
    
    # 열거형
    "ModelType", 
    "AgentRole",
    
    # 설정 팩토리 함수들
    "create_session_manager_config",
    "create_learning_supervisor_config", 
    "create_theory_educator_config",
    "create_quiz_generator_config",
    "create_evaluation_feedback_config",
    "create_qna_resolver_config"
]


def get_available_agents():
    """사용 가능한 모든 에이전트 역할 목록 반환"""
    return [role.value for role in AgentRole]


def get_available_models():
    """사용 가능한 모든 AI 모델 목록 반환"""
    return [model.value for model in ModelType]


def create_default_config(agent_role: AgentRole) -> AgentConfig:
    """
    에이전트 역할에 따른 기본 설정 생성
    
    Args:
        agent_role: 에이전트 역할
        
    Returns:
        해당 에이전트의 기본 설정
        
    Example:
        config = create_default_config(AgentRole.THEORY_EDUCATOR)
    """
    config_factories = {
        AgentRole.SESSION_MANAGER: create_session_manager_config,
        AgentRole.LEARNING_SUPERVISOR: create_learning_supervisor_config,
        AgentRole.THEORY_EDUCATOR: create_theory_educator_config,
        AgentRole.QUIZ_GENERATOR: create_quiz_generator_config,
        AgentRole.EVALUATION_FEEDBACK: create_evaluation_feedback_config,
        AgentRole.QNA_RESOLVER: create_qna_resolver_config
    }
    
    factory = config_factories.get(agent_role)
    if not factory:
        raise ValueError(f"지원하지 않는 에이전트 역할: {agent_role}")
        
    return factory()


def validate_agent_compatibility(agent_role: AgentRole, model_type: ModelType) -> bool:
    """
    에이전트와 모델의 호환성 검증
    
    Args:
        agent_role: 에이전트 역할
        model_type: AI 모델 타입
        
    Returns:
        호환성 여부
    """
    # 기본적으로 모든 조합 허용, 특수한 제약사항이 있다면 여기서 확인
    
    # 예: QnAResolver는 더 강력한 모델을 권장
    if agent_role == AgentRole.QNA_RESOLVER:
        lightweight_models = [ModelType.GEMINI_FLASH, ModelType.GPT_4O_MINI]
        if model_type in lightweight_models:
            # 경고는 하지만 허용
            return True
    
    return True


# 모듈 로딩 시 기본 검증
def _validate_module():
    """모듈 로딩 시 기본 검증"""
    try:
        # 각 에이전트별 기본 설정이 정상적으로 생성되는지 확인
        for agent_role in AgentRole:
            config = create_default_config(agent_role)
            assert isinstance(config, AgentConfig), f"{agent_role} 설정 생성 실패"
            
    except Exception as e:
        raise ImportError(f"Base Agent 모듈 초기화 실패: {e}")


# 모듈 로딩 시 검증 실행
_validate_module()