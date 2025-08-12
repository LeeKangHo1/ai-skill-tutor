# backend/app/core/external/ai_client_manager.py

import logging
import time
import uuid
import json
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
                    error=f"컨텐츠 생성 실패: {str(e)}"
                )
            
            raise ExternalAPIError(f"컨텐츠 생성 실패: {str(e)}")
    
    def generate_content_with_messages(
        self,
        messages: List[BaseMessage],
        provider: AIProvider = AIProvider.GEMINI,
        langsmith_run_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        LangChain Messages를 사용한 컨텐츠 생성
        
        Args:
            messages: LangChain 메시지 리스트
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
            
            # LangSmith에 오류 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    error=f"Messages 기반 컨텐츠 생성 실패: {str(e)}"
                )
            
            raise ExternalAPIError(f"Messages 기반 컨텐츠 생성 실패: {str(e)}")
    
    # backend/app/core/external/ai_client_manager.py (generate_json_content_with_messages 메서드 수정)

    def generate_json_content_with_messages(
        self,
        messages: List[BaseMessage],
        provider: AIProvider = AIProvider.GEMINI,
        langsmith_run_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        LangChain Messages를 사용한 JSON 컨텐츠 생성
        중복 LangSmith 추적 방지 버전
        
        Args:
            messages: LangChain 메시지 리스트
            provider: AI 제공자
            langsmith_run_id: LangSmith 추적 ID (None이면 새로 생성하지 않음)
            **kwargs: 추가 파라미터
            
        Returns:
            JSON 형태로 파싱된 응답
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        
        # ✅ langsmith_run_id가 None이면 LangSmith 추적하지 않음 (중복 방지)
        should_create_run = langsmith_run_id is not None and is_langsmith_enabled()
        
        unique_run_id = None
        langsmith_client = None
        
        try:
            # ✅ 1. LangSmith 추적 시작 (필요한 경우에만)
            if should_create_run:
                # 고유 run_id 생성 (409 Conflict 방지)
                import time
                import uuid
                unique_run_id = f"ai_json_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
                
                langsmith_client = get_langsmith_client()
                try:
                    # 새로운 run 생성
                    langsmith_client.create_run(
                        name="ai_json_content_generation",
                        run_type="llm",
                        run_id=unique_run_id,
                        inputs={
                            "messages": [{"role": msg.type, "content": msg.content} for msg in messages],
                            "timestamp": time.time(),
                            "provider": provider.value
                        }
                    )
                    self.logger.info(f"LangSmith run 생성: {unique_run_id}")
                except Exception as langsmith_error:
                    self.logger.warning(f"LangSmith run 생성 실패 (계속 진행): {langsmith_error}")
                    langsmith_client = None
            
            # ✅ 2. AI 클라이언트로 JSON 컨텐츠 생성 (LangSmith ID 전달하지 않음)
            json_content = self._generate_json_content_with_retry(messages, provider, **kwargs)
            
            # ✅ 3. LangSmith run 성공으로 업데이트 및 종료
            if langsmith_client and unique_run_id:
                try:
                    langsmith_client.update_run(
                        unique_run_id,
                        outputs={"status": "success", "generated_json": True}
                    )
                    # run 종료는 status를 completed로 설정
                    langsmith_client.update_run(
                        unique_run_id,
                        status="completed"
                    )
                    self.logger.info(f"LangSmith run 완료: {unique_run_id}")
                except Exception as update_error:
                    self.logger.warning(f"LangSmith run 업데이트 실패: {update_error}")
            
            return json_content
            
        except Exception as e:
            self.logger.error(f"JSON 컨텐츠 생성 실패: {str(e)}")
            
            # ✅ 4. LangSmith run 실패로 업데이트
            if langsmith_client and unique_run_id:
                try:
                    langsmith_client.update_run(
                        unique_run_id,
                        error=f"JSON 컨텐츠 생성 실패: {str(e)}",
                        status="error"
                    )
                    self.logger.info(f"LangSmith run 오류 기록: {unique_run_id}")
                except Exception as update_error:
                    self.logger.warning(f"LangSmith 오류 기록 실패: {update_error}")
            
            # 기본 오류 응답 반환 (시스템 중단 방지)
            return self._create_fallback_json_response(str(e))


    def _generate_json_content_with_retry(
        self,
        messages: List[BaseMessage],
        provider: AIProvider,
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        재시도 로직이 포함된 JSON 컨텐츠 생성
        LangSmith 추적 제거 버전
        """
        for attempt in range(max_retries):
            try:
                client = self.get_text_client(provider)
                
                # ✅ Gemini 클라이언트인 경우 (LangSmith 추적 없이)
                if isinstance(client, GeminiClient):
                    result = client.generate_json_content_with_messages(
                        messages=messages,
                        **kwargs
                    )
                    
                    # JSON 파싱 검증
                    if isinstance(result, str):
                        import json
                        result = json.loads(result)
                    
                    return result
                
                # ✅ OpenAI 클라이언트인 경우 (추후 구현)
                elif isinstance(client, OpenAIClient):
                    result = client.generate_json_content_with_messages(
                        messages=messages,
                        **kwargs
                    )
                    
                    # JSON 파싱 검증
                    if isinstance(result, str):
                        import json
                        result = json.loads(result)
                    
                    return result
                
                else:
                    raise ExternalAPIError(f"지원하지 않는 클라이언트 타입: {type(client)}")
                    
            except Exception as e:
                if attempt == max_retries - 1:  # 마지막 시도
                    raise e
                
                self.logger.warning(f"JSON 생성 실패 (재시도 {attempt + 1}/{max_retries}): {str(e)}")
                import time
                time.sleep(1)  # 1초 대기 후 재시도
    
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
        text: str,
        langsmith_run_id: Optional[str] = None
    ) -> List[float]:
        """
        텍스트 임베딩 생성
        
        Args:
            text: 임베딩할 텍스트
            langsmith_run_id: LangSmith 추적 ID
            
        Returns:
            임베딩 벡터
            
        Raises:
            ExternalAPIError: 임베딩 생성 실패 시
        """
        try:
            # LangSmith 추적 정보 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    outputs={"method": "generate_embedding", "text_length": len(text)}
                )
            
            client = self.get_embedding_client()
            return client.generate_embedding(text)
            
        except Exception as e:
            self.logger.error(f"임베딩 생성 실패: {str(e)}")
            
            # LangSmith에 오류 로깅
            if langsmith_run_id and is_langsmith_enabled():
                langsmith_client = get_langsmith_client()
                langsmith_client.update_run(
                    langsmith_run_id,
                    error=f"임베딩 생성 실패: {str(e)}"
                )
            
            raise ExternalAPIError(f"임베딩 생성 실패: {str(e)}")
    
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