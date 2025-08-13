# backend/app/core/external/vector_db.py

import os
import logging
from typing import List, Dict, Any

from langchain_openai import OpenAIEmbeddings

from app.utils.common.exceptions import ExternalAPIError


class VectorDBClient:
    """
    벡터 데이터베이스 관련 클라이언트
    - OpenAI 임베딩 생성 기능
    - ChromaDB와의 연동을 위한 임베딩 처리
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_client()
    
    def _initialize_client(self):
        """벡터 DB 클라이언트 초기화"""
        try:
            # 환경변수에서 API 키 로드
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            
            # 임베딩 모델 설정
            self.embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
            
            # LangChain OpenAI 임베딩 모델 생성
            self.embeddings = OpenAIEmbeddings(
                model=self.embedding_model,
                openai_api_key=api_key
            )
            
            self.logger.info(f"벡터 DB 클라이언트 초기화 완료 - 임베딩 모델: {self.embedding_model}")
            
        except Exception as e:
            self.logger.error(f"벡터 DB 클라이언트 초기화 실패: {str(e)}")
            raise ExternalAPIError(f"벡터 DB 초기화 오류: {str(e)}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        텍스트 임베딩 생성
        
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
            
            self.logger.debug(f"임베딩 생성 시작 - 텍스트 길이: {len(text)}")
            
            # OpenAI 임베딩 호출
            embedding_vector = self.embeddings.embed_query(text)
            
            self.logger.debug(f"임베딩 생성 성공 - 벡터 차원: {len(embedding_vector)}")
            return embedding_vector
            
        except Exception as e:
            error_msg = f"임베딩 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        배치 임베딩 생성
        
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
            
            self.logger.info(f"배치 임베딩 생성 시작 - 텍스트 수: {len(valid_texts)}")
            
            # OpenAI 배치 임베딩 호출
            embeddings = self.embeddings.embed_documents(valid_texts)
            
            self.logger.info(f"배치 임베딩 생성 완료 - 총 {len(embeddings)}개")
            return embeddings
            
        except Exception as e:
            error_msg = f"배치 임베딩 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
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
    
    def test_connection(self) -> bool:
        """
        벡터 DB 연결 테스트
        
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
            
            self.logger.info(f"벡터 DB 연결 테스트 {'성공' if success else '실패'}")
            return success
            
        except Exception as e:
            self.logger.error(f"벡터 DB 연결 테스트 실패: {str(e)}")
            return False