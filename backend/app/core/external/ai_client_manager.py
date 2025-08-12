# backend/app/core/external/ai_client_manager.py

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

from app.core.external.gemini_client import GeminiClient
from app.core.external.openai_client import OpenAIClient
from app.core.langsmith.langsmith_client import get_langsmith_client, is_langsmith_enabled
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
        langsmith_run_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        텍스트 컨텐츠 생성 (통합 인터페이스)
        
        Args:
            prompt: 사용자 프롬프트
            system_instruction: 시스템 지시사항
            provider: AI 제공자
            langsmith_run_id: LangSmith 추적 ID
            **kwargs: 추가 파라미터
            
        Returns:
            생성된 텍스트
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            # LangSmith 추적 정보 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    outputs={"ai_provider": provider.value, "method": "generate_content"}
                )
            
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
            
            # LangSmith에 오류 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    error=f"generate_content 실패: {str(e)}"
                )
            
            raise
    
    def generate_json_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        provider: AIProvider = AIProvider.GEMINI,
        langsmith_run_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        JSON 형태 컨텐츠 생성 (통합 인터페이스)
        
        Args:
            prompt: 사용자 프롬프트
            system_instruction: 시스템 지시사항
            provider: AI 제공자
            langsmith_run_id: LangSmith 추적 ID
            **kwargs: 추가 파라미터
            
        Returns:
            JSON 형태로 파싱된 응답
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            # LangSmith 추적 정보 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    outputs={"ai_provider": provider.value, "method": "generate_json_content"}
                )
            
            client = self.get_text_client(provider)
            
            # Gemini 클라이언트인 경우
            if isinstance(client, GeminiClient):
                return client.generate_json_content(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    **kwargs
                )
            
            # 다른 클라이언트 추가 시 여기에 구현
            else:
                raise ExternalAPIError(f"지원하지 않는 클라이언트 타입: {type(client)}")
                
        except Exception as e:
            self.logger.error(f"JSON 컨텐츠 생성 실패: {str(e)}")
            
            # LangSmith에 오류 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    error=f"generate_json_content 실패: {str(e)}"
                )
            
            raise
    
    def generate_json_content_with_messages(
        self,
        messages: List[BaseMessage],
        provider: AIProvider = AIProvider.GEMINI,
        langsmith_run_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        LangChain Messages를 사용한 JSON 컨텐츠 생성
        
        Args:
            messages: LangChain 메시지 리스트 (SystemMessage, HumanMessage 등)
            provider: AI 제공자
            langsmith_run_id: LangSmith 추적 ID
            **kwargs: 추가 파라미터 (temperature 등)
            
        Returns:
            JSON 형태로 파싱된 응답
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            # LangSmith 추적 정보 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    outputs={
                        "ai_provider": provider.value, 
                        "method": "generate_json_content_with_messages",
                        "message_count": len(messages)
                    }
                )
            
            # Messages를 기존 인터페이스로 변환
            system_instruction = None
            user_prompt = ""
            
            for message in messages:
                if isinstance(message, SystemMessage):
                    system_instruction = message.content
                elif isinstance(message, HumanMessage):
                    user_prompt = message.content
                # 필요시 다른 메시지 타입 추가 가능
            
            if not user_prompt:
                raise ExternalAPIError("유효한 사용자 메시지가 없습니다.")
            
            # 기존 generate_json_content 메서드 활용
            return self.generate_json_content(
                prompt=user_prompt,
                system_instruction=system_instruction,
                provider=provider,
                langsmith_run_id=langsmith_run_id,
                **kwargs
            )
                
        except Exception as e:
            self.logger.error(f"Messages 기반 JSON 컨텐츠 생성 실패: {str(e)}")
            
            # LangSmith에 오류 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    error=f"generate_json_content_with_messages 실패: {str(e)}"
                )
            
            raise
    
    def generate_content_with_messages(
        self,
        messages: List[BaseMessage],
        provider: AIProvider = AIProvider.GEMINI,
        langsmith_run_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        LangChain Messages를 사용한 텍스트 컨텐츠 생성
        
        Args:
            messages: LangChain 메시지 리스트 (SystemMessage, HumanMessage 등)
            provider: AI 제공자
            langsmith_run_id: LangSmith 추적 ID
            **kwargs: 추가 파라미터
            
        Returns:
            생성된 텍스트
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            # LangSmith 추적 정보 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    outputs={
                        "ai_provider": provider.value,
                        "method": "generate_content_with_messages",
                        "message_count": len(messages)
                    }
                )
            
            # Messages를 기존 인터페이스로 변환
            system_instruction = None
            user_prompt = ""
            
            for message in messages:
                if isinstance(message, SystemMessage):
                    system_instruction = message.content
                elif isinstance(message, HumanMessage):
                    user_prompt = message.content
            
            if not user_prompt:
                raise ExternalAPIError("유효한 사용자 메시지가 없습니다.")
            
            # 기존 generate_content 메서드 활용
            return self.generate_content(
                prompt=user_prompt,
                system_instruction=system_instruction,
                provider=provider,
                langsmith_run_id=langsmith_run_id,
                **kwargs
            )
                
        except Exception as e:
            self.logger.error(f"Messages 기반 컨텐츠 생성 실패: {str(e)}")
            
            # LangSmith에 오류 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    error=f"generate_content_with_messages 실패: {str(e)}"
                )
            
            raise
    
    def create_embedding(
        self,
        text: str,
        langsmith_run_id: Optional[str] = None,
        **kwargs
    ) -> List[float]:
        """
        텍스트 임베딩 생성 (통합 인터페이스)
        
        Args:
            text: 임베딩할 텍스트
            langsmith_run_id: LangSmith 추적 ID
            **kwargs: 추가 파라미터
            
        Returns:
            임베딩 벡터
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            # LangSmith 추적 정보 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    outputs={"method": "create_embedding", "text_length": len(text)}
                )
            
            client = self.get_embedding_client()
            return client.create_embedding(text, **kwargs)
            
        except Exception as e:
            self.logger.error(f"임베딩 생성 실패: {str(e)}")
            
            # LangSmith에 오류 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    error=f"create_embedding 실패: {str(e)}"
                )
            
            raise
    
    def create_batch_embeddings(
        self,
        texts: List[str],
        langsmith_run_id: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        배치 임베딩 생성 (통합 인터페이스)
        
        Args:
            texts: 임베딩할 텍스트 리스트
            langsmith_run_id: LangSmith 추적 ID
            **kwargs: 추가 파라미터
            
        Returns:
            임베딩 벡터들의 리스트
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            # LangSmith 추적 정보 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    outputs={"method": "create_batch_embeddings", "batch_size": len(texts)}
                )
            
            client = self.get_embedding_client()
            return client.create_batch_embeddings(texts, **kwargs)
            
        except Exception as e:
            self.logger.error(f"배치 임베딩 생성 실패: {str(e)}")
            
            # LangSmith에 오류 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    error=f"create_batch_embeddings 실패: {str(e)}"
                )
            
            raise
    
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
                    info[provider.value] = client.get_model_info()
                else:
                    info[provider.value] = {"status": "initialized"}
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