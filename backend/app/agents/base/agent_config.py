# app/agents/base/agent_config.py

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ModelType(Enum):
    """AI 모델 타입 정의"""
    GEMINI_FLASH = "gemini-2.5-flash"
    GEMINI_PRO = "gemini-2.5-pro"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"


class AgentRole(Enum):
    """에이전트 역할 정의"""
    SESSION_MANAGER = "session_manager"
    LEARNING_SUPERVISOR = "learning_supervisor"
    THEORY_EDUCATOR = "theory_educator"
    QUIZ_GENERATOR = "quiz_generator"
    EVALUATION_FEEDBACK = "evaluation_feedback_agent"
    QNA_RESOLVER = "qna_resolver"


@dataclass
class AgentConfig:
    """
    에이전트 설정 클래스
    각 에이전트의 동작 방식, 모델 설정, 프롬프트 등을 관리
    """
    
    # 기본 설정
    agent_role: AgentRole
    model_type: ModelType = ModelType.GEMINI_FLASH
    log_level: int = logging.INFO
    max_retry_count: int = 3
    timeout_seconds: int = 30
    
    # 프롬프트 설정
    system_prompt: str = ""
    prompt_templates: Dict[str, str] = field(default_factory=dict)
    
    # 도구 설정
    allowed_tools: List[str] = field(default_factory=list)
    tool_timeout: int = 10
    
    # 출력 설정
    max_output_length: int = 2000
    output_format: str = "text"  # "text", "json", "markdown"
    
    # 사용자 유형별 설정
    user_type_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """초기화 후 설정 검증 및 기본값 설정"""
        self._load_default_prompts()
        self._load_default_tools()
        self._load_user_type_configs()
    
    def _load_default_prompts(self) -> None:
        """에이전트별 기본 프롬프트 로딩"""
        
        base_system_prompt = """
당신은 AI 활용법 학습 튜터의 {agent_role} 에이전트입니다.
사용자의 학습 목표 달성을 위해 전문적이고 친근한 방식으로 도움을 제공합니다.

핵심 원칙:
1. 사용자 유형({user_type})에 맞는 적절한 설명 수준 유지
2. 학습 진행 단계({session_progress_stage})를 고려한 맥락적 응답
3. 정확하고 유용한 정보 제공
4. 격려와 동기부여를 통한 학습 의욕 향상
"""
        
        # 에이전트별 전용 프롬프트
        agent_prompts = {
            AgentRole.SESSION_MANAGER: {
                "system": base_system_prompt + """
당신의 역할: 학습 세션의 시작과 완료를 관리하고, 다음 단계 진행 여부를 판단합니다.
- 세션 초기화 및 완료 분석
- 학습 진도 추적 및 다음 단계 결정
- 세션 품질 평가 및 개선점 제안
""",
                "completion_analysis": "현재 학습 세션의 완료 여부를 분석하고 다음 단계를 결정해주세요.",
                "session_init": "새로운 학습 세션을 시작합니다. 사용자 상태를 확인하고 적절한 시작점을 설정해주세요."
            },
            
            AgentRole.LEARNING_SUPERVISOR: {
                "system": base_system_prompt + """
당신의 역할: 사용자와 직접 소통하며, 적절한 에이전트로 라우팅하고 최종 응답을 생성합니다.
- 사용자 의도 파악 및 분석
- 적절한 전문 에이전트로 라우팅
- 에이전트 대본을 사용자 친화적 응답으로 변환
""",
                "routing": "사용자의 요청을 분석하고 가장 적절한 처리 방향을 결정해주세요.",
                "response_generation": "전문 에이전트의 대본을 바탕으로 사용자에게 친근하고 이해하기 쉬운 응답을 생성해주세요."
            },
            
            AgentRole.THEORY_EDUCATOR: {
                "system": base_system_prompt + """
당신의 역할: AI 관련 개념과 이론을 사용자 수준에 맞게 설명하는 대본을 생성합니다.
- 복잡한 개념의 단계별 설명
- 실생활 예시 및 비유 활용
- 핵심 포인트 강조 및 요약
""",
                "concept_explanation": "다음 개념을 사용자가 이해하기 쉽게 설명하는 대본을 작성해주세요:",
                "example_generation": "설명한 개념에 대한 구체적이고 이해하기 쉬운 예시를 제공해주세요."
            },
            
            AgentRole.QUIZ_GENERATOR: {
                "system": base_system_prompt + """
당신의 역할: 학습한 내용을 바탕으로 적절한 난이도의 문제를 출제하는 대본을 생성합니다.
- 객관식 및 주관식 문제 생성
- 단계별 힌트 시스템 구현
- 실제 AI API 연동 실습 문제 제공
""",
                "quiz_generation": "학습한 내용을 바탕으로 적절한 문제를 출제해주세요:",
                "hint_generation": "현재 문제에 대한 단계별 힌트를 생성해주세요."
            },
            
            AgentRole.EVALUATION_FEEDBACK: {
                "system": base_system_prompt + """
당신의 역할: 사용자의 답변을 평가하고 건설적인 피드백을 제공하는 대본을 생성합니다.
- 정확한 답변 평가 및 점수 산정
- 개인화된 학습 피드백 제공
- 추가 학습 방향 제안
""",
                "answer_evaluation": "사용자의 답변을 평가하고 상세한 피드백을 제공해주세요:",
                "improvement_suggestion": "학습 개선을 위한 구체적인 제안사항을 제공해주세요."
            },
            
            AgentRole.QNA_RESOLVER: {
                "system": base_system_prompt + """
당신의 역할: 사용자의 즉석 질문에 대해 정확하고 유용한 답변을 제공하는 대본을 생성합니다.
- 벡터 검색 및 웹 검색을 통한 정보 수집
- 현재 학습 맥락과 연결된 답변 제공
- 추가 학습 자료 및 참고 링크 제안
""",
                "question_analysis": "사용자의 질문을 분석하고 가장 적절한 답변 방향을 결정해주세요:",
                "answer_generation": "수집된 정보를 바탕으로 정확하고 유용한 답변을 생성해주세요."
            }
        }
        
        if self.agent_role in agent_prompts:
            self.system_prompt = agent_prompts[self.agent_role]["system"]
            self.prompt_templates.update(agent_prompts[self.agent_role])
        else:
            self.system_prompt = base_system_prompt
    
    def _load_default_tools(self) -> None:
        """에이전트별 기본 도구 설정"""
        
        tool_mappings = {
            AgentRole.SESSION_MANAGER: [
                "session_initialization_tool",
                "session_completion_analysis_tool"
            ],
            AgentRole.LEARNING_SUPERVISOR: [
                "user_intent_analysis_tool",
                "response_generation_tool"
            ],
            AgentRole.THEORY_EDUCATOR: [
                "theory_generation_tool",
                "vector_search_tool"
            ],
            AgentRole.QUIZ_GENERATOR: [
                "quiz_generation_tool",
                "hint_generation_tool",
                "prompt_practice_tool",
                "vector_search_tool"
            ],
            AgentRole.EVALUATION_FEEDBACK: [
                "answer_evaluation_tool",
                "feedback_generation_tool"
            ],
            AgentRole.QNA_RESOLVER: [
                "vector_search_tool",
                "web_search_tool",
                "context_integration_tool"
            ]
        }
        
        if self.agent_role in tool_mappings:
            self.allowed_tools = tool_mappings[self.agent_role]
    
    def _load_user_type_configs(self) -> None:
        """사용자 유형별 설정 로딩"""
        
        self.user_type_configs = {
            "beginner": {
                "explanation_level": "basic",
                "use_analogies": True,
                "step_by_step": True,
                "max_concept_depth": 2,
                "preferred_examples": "daily_life",
                "feedback_style": "encouraging"
            },
            "advanced": {
                "explanation_level": "technical",
                "use_analogies": False,
                "step_by_step": False,
                "max_concept_depth": 4,
                "preferred_examples": "technical_case",
                "feedback_style": "analytical"
            }
        }
    
    def get_prompt_template(self, template_name: str) -> str:
        """프롬프트 템플릿 조회"""
        return self.prompt_templates.get(template_name, "")
    
    def get_user_config(self, user_type: str) -> Dict[str, Any]:
        """사용자 유형별 설정 조회"""
        return self.user_type_configs.get(user_type, self.user_type_configs["beginner"])
    
    def is_tool_allowed(self, tool_name: str) -> bool:
        """도구 사용 권한 확인"""
        return tool_name in self.allowed_tools
    
    def get_model_config(self) -> Dict[str, Any]:
        """모델 설정 반환"""
        model_configs = {
            ModelType.GEMINI_FLASH: {
                "provider": "google",
                "model_name": "gemini-2.5-flash",
                "max_tokens": 1000,
                "temperature": 0.2,
                "top_p": 0.4
            },
            ModelType.GEMINI_PRO: {
                "provider": "google", 
                "model_name": "gemini-2.5-pro",
                "max_tokens": 1000,
                "temperature": 0.2,
                "top_p": 0.4
            },
            ModelType.GPT_4O_MINI: {
                "provider": "openai",
                "model_name": "gpt-4o-mini",
                "max_tokens": 1000,
                "temperature": 0.2,
                "top_p": 0.4
            }
        }
        
        return model_configs.get(self.model_type, model_configs[ModelType.GEMINI_FLASH])


# 에이전트별 기본 설정 팩토리 함수들
def create_session_manager_config() -> AgentConfig:
    """SessionManager 설정 생성"""
    return AgentConfig(
        agent_role=AgentRole.SESSION_MANAGER,
        model_type=ModelType.GEMINI_FLASH,
        max_output_length=1000,
        output_format="json"
    )


def create_learning_supervisor_config() -> AgentConfig:
    """LearningSupervisor 설정 생성"""
    return AgentConfig(
        agent_role=AgentRole.LEARNING_SUPERVISOR,
        model_type=ModelType.GEMINI_FLASH,
        max_output_length=2000,
        output_format="text"
    )


def create_theory_educator_config() -> AgentConfig:
    """TheoryEducator 설정 생성"""
    return AgentConfig(
        agent_role=AgentRole.THEORY_EDUCATOR,
        model_type=ModelType.GEMINI_FLASH,
        max_output_length=3000,
        output_format="markdown"
    )


def create_quiz_generator_config() -> AgentConfig:
    """QuizGenerator 설정 생성"""
    return AgentConfig(
        agent_role=AgentRole.QUIZ_GENERATOR,
        model_type=ModelType.GEMINI_FLASH,
        max_output_length=1500,
        output_format="json",
        tool_timeout=15
    )


def create_evaluation_feedback_config() -> AgentConfig:
    """EvaluationFeedbackAgent 설정 생성"""
    return AgentConfig(
        agent_role=AgentRole.EVALUATION_FEEDBACK,
        model_type=ModelType.GEMINI_FLASH,
        max_output_length=2000,
        output_format="text"
    )


def create_qna_resolver_config() -> AgentConfig:
    """QnAResolver 설정 생성"""
    return AgentConfig(
        agent_role=AgentRole.QNA_RESOLVER,
        model_type=ModelType.GEMINI_FLASH,  # 테스트 후 수준 높은 추론이 필요할 경우 GEMINI_PRO로 전환
        max_output_length=2500,
        output_format="text",
        tool_timeout=20
    )