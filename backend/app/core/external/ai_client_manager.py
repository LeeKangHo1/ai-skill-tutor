# backend/app/core/external/ai_client_manager.py

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

from langchain_core.messages import BaseMessage

from app.core.external.gemini_client import GeminiClient
from app.core.external.openai_client import OpenAIClient
from app.core.langsmith.langsmith_client import is_langsmith_enabled
from app.utils.common.exceptions import ExternalAPIError


class AIProvider(Enum):
    """AI 제공자 열거형"""
    GEMINI = "gemini"
    OPENAI = "openai"


class AIClientManager:
    """
    AI 클라이언트 통합 관리자
    - 여러 AI 제공자 통합 관리
    - 클라이언트 인스턴스 생성 및 캐싱
    - 공통 인터페이스 제공
    - 장애 시 대체 제공자 활용
    - LangChain Messages 지원
    - LangSmith 추적 통합
    - 409 Conflict 오류 해결
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._clients: Dict[AIProvider, Any] = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """모든 AI 클라이언트 초기화"""
        try:
            # Gemini 클라이언트 초기화
            try:
                self._clients[AIProvider.GEMINI] = GeminiClient()
                self.logger.info("Gemini 클라이언트 초기화 성공")
            except Exception as e:
                self.logger.warning(f"Gemini 클라이언트 초기화 실패: {str(e)}")
            
            # OpenAI 클라이언트 초기화
            try:
                self._clients[AIProvider.OPENAI] = OpenAIClient()
                self.logger.info("OpenAI 클라이언트 초기화 성공")
            except Exception as e:
                self.logger.warning(f"OpenAI 클라이언트 초기화 실패: {str(e)}")
            
            # 최소 하나의 클라이언트는 초기화되어야 함
            if not self._clients:
                raise ExternalAPIError("사용 가능한 AI 클라이언트가 없습니다.")
            
            self.logger.info(f"AI 클라이언트 관리자 초기화 완료 - 활성 클라이언트: {list(self._clients.keys())}")
            
        except Exception as e:
            self.logger.error(f"AI 클라이언트 관리자 초기화 실패: {str(e)}")
            raise
    
    def get_text_client(self, provider: AIProvider = AIProvider.GEMINI) -> Any:
        """
        텍스트 생성용 클라이언트 반환
        
        Args:
            provider: 원하는 AI 제공자
            
        Returns:
            AI 클라이언트 인스턴스
            
        Raises:
            ExternalAPIError: 클라이언트를 찾을 수 없을 때
        """
        try:
            if provider in self._clients:
                return self._clients[provider]
            
            # 요청한 제공자가 없으면 사용 가능한 첫 번째 클라이언트 반환
            if self._clients:
                fallback_provider = next(iter(self._clients.keys()))
                self.logger.warning(f"요청한 제공자 {provider}가 없어서 {fallback_provider}로 대체")
                return self._clients[fallback_provider]
            
            raise ExternalAPIError("사용 가능한 텍스트 생성 클라이언트가 없습니다.")
            
        except Exception as e:
            self.logger.error(f"텍스트 클라이언트 반환 실패: {str(e)}")
            raise
    
    def get_embedding_client(self) -> OpenAIClient:
        """
        임베딩 생성용 클라이언트 반환 (OpenAI 고정)
        
        Returns:
            OpenAI 클라이언트 인스턴스
            
        Raises:
            ExternalAPIError: OpenAI 클라이언트를 찾을 수 없을 때
        """
        try:
            if AIProvider.OPENAI not in self._clients:
                raise ExternalAPIError("OpenAI 클라이언트가 초기화되지 않았습니다.")
            
            return self._clients[AIProvider.OPENAI]
            
        except Exception as e:
            self.logger.error(f"임베딩 클라이언트 반환 실패: {str(e)}")
            raise
    
    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        provider: AIProvider = AIProvider.GEMINI,
        **kwargs
    ) -> str:
        """
        텍스트 컨텐츠 생성 (통합 인터페이스)
        
        Args:
            prompt: 사용자 프롬프트
            system_instruction: 시스템 지시사항
            provider: AI 제공자
            **kwargs: 추가 파라미터
            
        Returns:
            생성된 텍스트
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            client = self.get_text_client(provider)
            
            # Gemini 클라이언트인 경우
            if isinstance(client, GeminiClient):
                return client.generate_content(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    **kwargs
                )
            
            # 다른 클라이언트 추가 시 여기에 구현
            else:
                raise ExternalAPIError(f"지원하지 않는 클라이언트 타입: {type(client)}")
                
        except Exception as e:
            self.logger.error(f"컨텐츠 생성 실패: {str(e)}")
            raise ExternalAPIError(f"컨텐츠 생성 실패: {str(e)}")
    
    def generate_content_with_messages(
        self,
        messages: List[BaseMessage],
        provider: AIProvider = AIProvider.GEMINI,
        **kwargs
    ) -> str:
        """
        LangChain Messages를 사용한 컨텐츠 생성
        
        Args:
            messages: LangChain 메시지 리스트
            provider: AI 제공자
            **kwargs: 추가 파라미터
            
        Returns:
            생성된 텍스트
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            client = self.get_text_client(provider)
            
            # Gemini 클라이언트인 경우
            if isinstance(client, GeminiClient):
                return client.generate_content_with_messages(
                    messages=messages,
                    **kwargs
                )
            
            # OpenAI 클라이언트인 경우 (추후 구현)
            elif isinstance(client, OpenAIClient):
                return client.generate_content_with_messages(
                    messages=messages,
                    **kwargs
                )
            
            else:
                raise ExternalAPIError(f"지원하지 않는 클라이언트 타입: {type(client)}")
                
        except Exception as e:
            self.logger.error(f"Messages 기반 컨텐츠 생성 실패: {str(e)}")
            raise ExternalAPIError(f"Messages 기반 컨텐츠 생성 실패: {str(e)}")
    
    def generate_json_content_with_messages(
        self,
        messages: List[BaseMessage],
        provider: AIProvider = AIProvider.GEMINI,
        **kwargs
    ) -> Dict[str, Any]:
        """
        LangChain Messages를 사용한 JSON 컨텐츠 생성
        LangChain 자동 추적 활용 (완전 자동화)
        
        Args:
            messages: LangChain 메시지 리스트
            provider: AI 제공자
            **kwargs: 추가 파라미터
            
        Returns:
            JSON 형태로 파싱된 응답
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        
        try:
            self.logger.info(f"LangChain JSON 컨텐츠 생성 시작 - Provider: {provider.value}")
            
            # 클라이언트 직접 호출 (LangChain 자동 추적)
            client = self.get_text_client(provider)
            
            if isinstance(client, GeminiClient):
                json_content = client.generate_json_content_with_messages(
                    messages=messages,
                    **kwargs
                )
            elif isinstance(client, OpenAIClient):
                json_content = client.generate_json_content_with_messages(
                    messages=messages,
                    **kwargs
                )
            else:
                raise ExternalAPIError(f"지원하지 않는 클라이언트 타입: {type(client)}")
            
            self.logger.info("LangChain JSON 컨텐츠 생성 완료")
            return json_content
            
        except Exception as e:
            self.logger.error(f"LangChain JSON 컨텐츠 생성 실패: {str(e)}")
            
            # 기본 오류 응답 반환 (시스템 중단 방지)
            return self._create_fallback_json_response(str(e))



    
    def _create_fallback_json_response(self, error_message: str) -> Dict[str, Any]:
        """
        JSON 생성 실패 시 기본 응답 생성
        - 시스템 중단 방지
        - 사용자에게 유용한 메시지 제공
        """
        fallback_content = {
            "content_type": "theory",
            "chapter_info": {
                "chapter_number": 1,
                "title": "AI는 무엇인가?",
                "user_type": "beginner"
            },
            "section_info": {
                "section_number": 1,
                "title": "이론 학습"
            },
            "main_content": f"일시적인 문제가 발생했습니다. 질문을 통해 학습을 진행해주세요.\n오류: {error_message}",
            "key_points": [
                "일시적인 시스템 문제",
                "질문으로 학습 계속 가능",
                "잠시 후 재시도"
            ],
            "analogy": "",
            "examples": [],
            "user_guidance": "시스템 문제로 설명이 생성되지 않았습니다. 궁금한 점을 질문해주세요.",
            "next_step_preview": "질문이 있으시면 언제든 말씀해주세요."
        }
        
        return fallback_content
    
    def generate_embedding(
        self,
        text: str
    ) -> List[float]:
        """
        LangChain을 사용한 텍스트 임베딩 생성 (자동 LangSmith 추적)
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
            
        Raises:
            ExternalAPIError: 임베딩 생성 실패 시
        """
        try:
            client = self.get_embedding_client()
            return client.generate_embedding(text)
            
        except Exception as e:
            self.logger.error(f"LangChain 임베딩 생성 실패: {str(e)}")
            raise ExternalAPIError(f"LangChain 임베딩 생성 실패: {str(e)}")
    
    def test_all_connections(self) -> Dict[str, bool]:
        """
        모든 클라이언트의 연결 상태 테스트
        
        Returns:
            제공자별 연결 상태
        """
        results = {}
        
        for provider, client in self._clients.items():
            try:
                if hasattr(client, 'test_connection'):
                    results[provider.value] = client.test_connection()
                else:
                    results[provider.value] = False
            except Exception as e:
                self.logger.error(f"{provider.value} 연결 테스트 실패: {str(e)}")
                results[provider.value] = False
        
        return results
    
    def get_available_providers(self) -> List[str]:
        """
        사용 가능한 AI 제공자 목록 반환
        
        Returns:
            제공자 이름 리스트
        """
        return [provider.value for provider in self._clients.keys()]
    
    def get_client_info(self) -> Dict[str, Dict[str, Any]]:
        """
        모든 클라이언트의 정보 반환
        
        Returns:
            클라이언트별 정보
        """
        info = {}
        
        for provider, client in self._clients.items():
            try:
                if hasattr(client, 'get_model_info'):
                    client_info = client.get_model_info()
                    # LangSmith 추적 상태 추가
                    client_info["langsmith_enabled"] = is_langsmith_enabled()
                    info[provider.value] = client_info
                else:
                    info[provider.value] = {
                        "status": "initialized",
                        "langsmith_enabled": is_langsmith_enabled()
                    }
            except Exception as e:
                self.logger.error(f"{provider.value} 정보 조회 실패: {str(e)}")
                info[provider.value] = {"error": str(e)}
        
        return info


# 글로벌 인스턴스 생성 (싱글톤 패턴)
_ai_client_manager = None

def get_ai_client_manager() -> AIClientManager:
    """
    AI 클라이언트 관리자 싱글톤 인스턴스 반환
    
    Returns:
        AIClientManager 인스턴스
    """
    global _ai_client_manager
    
    if _ai_client_manager is None:
        _ai_client_manager = AIClientManager()
    
    return _ai_client_manager