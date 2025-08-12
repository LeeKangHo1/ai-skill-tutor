# backend/app/core/external/openai_client.py

import os
import logging
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI

from app.utils.common.exceptions import ExternalAPIError


class OpenAIClient:
    """
    OpenAI API 클라이언트 (임베딩 전용)
    - 텍스트 임베딩 생성
    - 벡터 검색을 위한 쿼리 임베딩 처리
    - 에러 처리 및 재시도 로직
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_client()
    
    def _initialize_client(self):
        """OpenAI API 클라이언트 초기화"""
        try:
            # 환경변수에서 API 키 로드
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            
            # OpenAI 클라이언트 생성
            self.client = OpenAI(api_key=api_key)
            
            # 임베딩 모델 설정
            self.embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
            
            self.logger.info(f"OpenAI 클라이언트 초기화 완료 - 임베딩 모델: {self.embedding_model}")
            
        except Exception as e:
            self.logger.error(f"OpenAI 클라이언트 초기화 실패: {str(e)}")
            raise ExternalAPIError(f"OpenAI API 초기화 오류: {str(e)}")
    
    def create_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        단일 텍스트에 대한 임베딩 벡터 생성
        
        Args:
            text: 임베딩할 텍스트
            model: 사용할 임베딩 모델 (선택사항)
            
        Returns:
            임베딩 벡터 (실수 리스트)
            
        Raises:
            ExternalAPIError: API 호출 실패 시
        """
        try:
            if not text or not text.strip():
                raise ValueError("임베딩할 텍스트가 비어있습니다.")
            
            # 사용할 모델 결정
            embedding_model = model if model else self.embedding_model
            
            self.logger.debug(f"임베딩 생성 시작 - 텍스트 길이: {len(text)}")
            
            # OpenAI API 호출
            response = self.client.embeddings.create(
                input=text,
                model=embedding_model
            )
            
            # 응답 검증
            if not response.data or len(response.data) == 0:
                raise ExternalAPIError("OpenAI API에서 빈 임베딩 응답을 반환했습니다.")
            
            embedding_vector = response.data[0].embedding
            
            self.logger.debug(f"임베딩 생성 성공 - 벡터 차원: {len(embedding_vector)}")
            return embedding_vector
            
        except openai.APIError as e:
            error_msg = f"OpenAI API 오류: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
        except Exception as e:
            error_msg = f"임베딩 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def create_batch_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        여러 텍스트에 대한 배치 임베딩 생성
        
        Args:
            texts: 임베딩할 텍스트 리스트
            model: 사용할 임베딩 모델 (선택사항)
            batch_size: 배치 크기 (API 제한 고려)
            
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
            
            # 사용할 모델 결정
            embedding_model = model if model else self.embedding_model
            
            self.logger.info(f"배치 임베딩 생성 시작 - 텍스트 수: {len(valid_texts)}")
            
            all_embeddings = []
            
            # 배치 단위로 처리
            for i in range(0, len(valid_texts), batch_size):
                batch_texts = valid_texts[i:i + batch_size]
                
                self.logger.debug(f"배치 {i//batch_size + 1} 처리 중 - 크기: {len(batch_texts)}")
                
                # OpenAI API 호출
                response = self.client.embeddings.create(
                    input=batch_texts,
                    model=embedding_model
                )
                
                # 응답 검증
                if not response.data or len(response.data) != len(batch_texts):
                    raise ExternalAPIError("배치 임베딩 응답 수가 요청과 일치하지 않습니다.")
                
                # 임베딩 벡터 추출
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            
            self.logger.info(f"배치 임베딩 생성 완료 - 총 {len(all_embeddings)}개")
            return all_embeddings
            
        except openai.APIError as e:
            error_msg = f"OpenAI 배치 API 오류: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
        except Exception as e:
            error_msg = f"배치 임베딩 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def create_query_embedding(self, query: str) -> List[float]:
        """
        검색 쿼리용 임베딩 생성 (단일 텍스트 특화)
        
        Args:
            query: 검색 쿼리 텍스트
            
        Returns:
            쿼리 임베딩 벡터
            
        Raises:
            ExternalAPIError: API 호출 실패 시
        """
        try:
            if not query or not query.strip():
                raise ValueError("검색 쿼리가 비어있습니다.")
            
            # 쿼리 전처리 (필요시)
            processed_query = query.strip()
            
            self.logger.debug(f"쿼리 임베딩 생성: {processed_query[:100]}...")
            
            return self.create_embedding(processed_query)
            
        except Exception as e:
            error_msg = f"쿼리 임베딩 생성 실패: {str(e)}"
            self.logger.error(error_msg)
            raise ExternalAPIError(error_msg)
    
    def test_connection(self) -> bool:
        """
        OpenAI API 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            # 간단한 텍스트로 임베딩 테스트
            test_embedding = self.create_embedding("테스트")
            
            # 임베딩 벡터가 올바른 형태인지 확인
            success = (
                isinstance(test_embedding, list) and 
                len(test_embedding) > 0 and 
                isinstance(test_embedding[0], float)
            )
            
            self.logger.info(f"OpenAI API 연결 테스트 {'성공' if success else '실패'}")
            return success
            
        except Exception as e:
            self.logger.error(f"OpenAI API 연결 테스트 실패: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        현재 설정된 모델 정보 반환
        
        Returns:
            모델 설정 정보
        """
        return {
            "embedding_model": self.embedding_model,
            "provider": "OpenAI",
            "purpose": "text embedding"
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