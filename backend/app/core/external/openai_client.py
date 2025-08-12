# backend/app/core/external/openai_client.py

import os
import logging
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import JsonOutputParser

from app.utils.common.exceptions import ExternalAPIError


class OpenAIClient:
    """
    LangChain OpenAI 클라이언트
    - LangChain ChatOpenAI 및 OpenAIEmbeddings 사용
    - 자동 LangSmith 추적 지원
    - JSON 출력 파서 통합
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_client()
    
    def _initialize_client(self):
        """LangChain OpenAI 클라이언트 초기화"""
        try:
            # 환경변수에서 API 키 로드
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            
            # 모델 설정
            self.chat_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            self.embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
            self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
            self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
            
            # LangChain ChatOpenAI 모델 생성
            self.llm = ChatOpenAI(
                model=self.chat_model,
                openai_api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # LangChain OpenAI 임베딩 모델 생성
            self.embeddings = OpenAIEmbeddings(
                model=self.embedding_model,
                openai_api_key=api_key
            )
            
            # JSON 출력 파서
            self.json_parser = JsonOutputParser()
            
            self.logger.info(f"LangChain OpenAI 클라이언트 초기화 완료 - 채팅: {self.chat_model}, 임베딩: {self.embedding_model}")
            
        except Exception as e:
            self.logger.error(f"LangChain OpenAI 클라이언트 초기화 실패: {str(e)}")
            raise ExternalAPIError(f"LangChain OpenAI API 초기화 오류: {str(e)}")
    
    def generate_content_with_messages(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        LangChain Messages를 사용한 컨텐츠 생성 (자동 LangSmith 추적)
        
        Args:
            messages: LangChain 메시지 리스트
            temperature: 창의성 수준
            max_tokens: 최대 토큰 수
            **kwargs: 추가 파라미터
            
        Returns:
            생성된 텍스트 응답
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            self.logger.info(f"LangChain OpenAI 호출 시작 - 메시지 수: {len(messages)}")
            
            # 동적으로 temperature 설정
            if temperature is not None:
                original_temp = self.llm.temperature
                self.llm.temperature = temperature
                
                try:
                    response = self.llm.invoke(messages)
                finally:
                    self.llm.temperature = original_temp
            else:
                response = self.llm.invoke(messages)
            
            if not response.content:
                raise ExternalAPIError("LangChain OpenAI에서 빈 응답을 반환했습니다.")
            
            self.logger.info(f"LangChain OpenAI 응답 수신 완료 - 길이: {len(response.content)}")
            return response.content
                
        except Exception as e:
            error_msg = f"LangChain OpenAI 컨텐츠 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def generate_json_content_with_messages(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        LangChain Messages를 사용한 JSON 컨텐츠 생성 (자동 LangSmith 추적)
        
        Args:
            messages: LangChain 메시지 리스트
            temperature: 창의성 수준
            max_tokens: 최대 토큰 수
            **kwargs: 추가 파라미터
            
        Returns:
            JSON 형태로 파싱된 응답
            
        Raises:
            ExternalAPIError: 생성 실패 시
        """
        try:
            from langchain_core.messages import SystemMessage
            
            # JSON 출력을 위한 시스템 메시지 추가/수정
            enhanced_messages = []
            system_found = False
            
            for message in messages:
                if isinstance(message, SystemMessage):
                    json_instruction = (
                        f"{message.content}\n\n"
                        "**중요**: 반드시 유효한 JSON 형식으로만 응답해주세요. "
                        "추가적인 설명이나 마크다운 포맷팅은 사용하지 마세요."
                    )
                    enhanced_messages.append(SystemMessage(content=json_instruction))
                    system_found = True
                else:
                    enhanced_messages.append(message)
            
            if not system_found:
                json_system_msg = SystemMessage(
                    content="반드시 유효한 JSON 형식으로만 응답해주세요. "
                           "추가적인 설명이나 마크다운 포맷팅은 사용하지 마세요."
                )
                enhanced_messages.insert(0, json_system_msg)
            
            self.logger.info(f"LangChain OpenAI JSON 생성 시작 - 메시지 수: {len(enhanced_messages)}")
            
            # 동적으로 temperature 설정
            if temperature is not None:
                original_temp = self.llm.temperature
                self.llm.temperature = temperature
                
                try:
                    chain = self.llm | self.json_parser
                    response = chain.invoke(enhanced_messages)
                finally:
                    self.llm.temperature = original_temp
            else:
                chain = self.llm | self.json_parser
                response = chain.invoke(enhanced_messages)
            
            self.logger.info("LangChain OpenAI JSON 생성 완료")
            return response
                
        except Exception as e:
            error_msg = f"LangChain OpenAI JSON 컨텐츠 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        LangChain을 사용한 임베딩 생성 (자동 LangSmith 추적)
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터 (실수 리스트)
            
        Raises:
            ExternalAPIError: API 호출 실패 시
        """
        try:
            if not text or not text.strip():
                raise ValueError("임베딩할 텍스트가 비어있습니다.")
            
            self.logger.debug(f"LangChain 임베딩 생성 시작 - 텍스트 길이: {len(text)}")
            
            # LangChain OpenAI 임베딩 호출 (자동 LangSmith 추적)
            embedding_vector = self.embeddings.embed_query(text)
            
            self.logger.debug(f"LangChain 임베딩 생성 성공 - 벡터 차원: {len(embedding_vector)}")
            return embedding_vector
            
        except Exception as e:
            error_msg = f"LangChain 임베딩 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        LangChain을 사용한 배치 임베딩 생성 (자동 LangSmith 추적)
        
        Args:
            texts: 임베딩할 텍스트 리스트
            
        Returns:
            임베딩 벡터들의 리스트
            
        Raises:
            ExternalAPIError: API 호출 실패 시
        """
        try:
            if not texts:
                raise ValueError("임베딩할 텍스트 리스트가 비어있습니다.")
            
            # 빈 텍스트 필터링
            valid_texts = [text for text in texts if text and text.strip()]
            if not valid_texts:
                raise ValueError("유효한 텍스트가 없습니다.")
            
            self.logger.info(f"LangChain 배치 임베딩 생성 시작 - 텍스트 수: {len(valid_texts)}")
            
            # LangChain OpenAI 배치 임베딩 호출 (자동 LangSmith 추적)
            embeddings = self.embeddings.embed_documents(valid_texts)
            
            self.logger.info(f"LangChain 배치 임베딩 생성 완료 - 총 {len(embeddings)}개")
            return embeddings
            
        except Exception as e:
            error_msg = f"LangChain 배치 임베딩 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def test_connection(self) -> bool:
        """
        LangChain OpenAI 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            # 간단한 텍스트로 임베딩 테스트
            test_embedding = self.generate_embedding("테스트")
            
            # 임베딩 벡터가 올바른 형태인지 확인
            success = (
                isinstance(test_embedding, list) and 
                len(test_embedding) > 0 and 
                isinstance(test_embedding[0], float)
            )
            
            self.logger.info(f"LangChain OpenAI 연결 테스트 {'성공' if success else '실패'}")
            return success
            
        except Exception as e:
            self.logger.error(f"LangChain OpenAI 연결 테스트 실패: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        현재 설정된 모델 정보 반환
        
        Returns:
            모델 설정 정보
        """
        return {
            "chat_model": self.chat_model,
            "embedding_model": self.embedding_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "provider": "LangChain OpenAI",
            "langsmith_tracing": "자동 추적 활성화"
        }
    
    def get_embedding_dimension(self) -> int:
        """
        현재 임베딩 모델의 차원 수 반환
        
        Returns:
            임베딩 벡터 차원 수
        """
        # text-embedding-3-large: 3072차원
        # text-embedding-3-small: 1536차원
        # text-embedding-ada-002: 1536차원
        
        dimension_map = {
            'text-embedding-3-large': 3072,
            'text-embedding-3-small': 1536,
            'text-embedding-ada-002': 1536
        }
        
        return dimension_map.get(self.embedding_model, 1536)  # 기본값: 1536