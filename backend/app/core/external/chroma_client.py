# backend/app/core/external/chroma_client.py

import os
import logging
from typing import Optional, List, Dict, Any
import chromadb
from chromadb.config import Settings


class ChromaDBClient:
    """
    ChromaDB 클라이언트 관리 클래스
    - ChromaDB 연결 설정 및 관리
    - 컬렉션 생성/조회 기능
    - 싱글톤 패턴으로 전역 클라이언트 인스턴스 제공
    """
    
    _instance = None
    _client = None
    _collections = {}
    
    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(ChromaDBClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """ChromaDB 클라이언트 초기화"""
        if self._client is None:
            self.logger = logging.getLogger(__name__)
            self._initialize_client()
    
    def _initialize_client(self):
        """ChromaDB 클라이언트 연결 설정"""
        try:
            # 프로젝트 루트 경로 기준으로 ChromaDB 저장 경로 설정
            if os.getenv('CHROMA_DB_PATH'):
                chroma_path = os.getenv('CHROMA_DB_PATH')
            else:
                # 현재 파일 기준으로 backend/data/chroma_db 경로 계산
                # 수정 후 (4단계 상위로 수정)
                current_file = os.path.abspath(__file__)
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
                chroma_path = os.path.join(backend_dir, 'data', 'chroma_db')
            
            # 디렉토리가 없으면 생성
            os.makedirs(chroma_path, exist_ok=True)
            
            # ChromaDB 클라이언트 생성 (로컬 파일 기반)
            self._client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(
                    anonymized_telemetry=False,  # 텔레메트리 비활성화
                    allow_reset=True
                )
            )
            
            self.logger.info(f"ChromaDB 클라이언트 초기화 완료: {chroma_path}")
            
        except Exception as e:
            self.logger.error(f"ChromaDB 클라이언트 초기화 실패: {str(e)}")
            raise
    
    def get_client(self):
        """ChromaDB 클라이언트 인스턴스 반환"""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def get_collection(self, collection_name: str, embedding_function=None):
        """
        컬렉션 조회 또는 생성
        
        Args:
            collection_name: 컬렉션 이름
            embedding_function: 임베딩 함수 (None시 ChromaDB 기본 함수 사용)
            
        Returns:
            ChromaDB Collection 객체
        """
        try:
            # 이미 로드된 컬렉션이 있으면 반환
            if collection_name in self._collections:
                return self._collections[collection_name]
            
            client = self.get_client()
            
            # 기존 컬렉션 조회 시도
            try:
                collection = client.get_collection(
                    name=collection_name,
                    embedding_function=embedding_function
                )
                self.logger.info(f"기존 컬렉션 조회: {collection_name}")
                
            except Exception:
                # 컬렉션이 없으면 새로 생성
                collection = client.create_collection(
                    name=collection_name,
                    embedding_function=embedding_function,
                    metadata={"created_by": "ai_tutor_system"}
                )
                self.logger.info(f"새 컬렉션 생성: {collection_name}")
            
            # 메모리에 캐시
            self._collections[collection_name] = collection
            return collection
            
        except Exception as e:
            self.logger.error(f"컬렉션 조회/생성 실패 ({collection_name}): {str(e)}")
            raise
    
    def list_collections(self) -> List[str]:
        """모든 컬렉션 이름 목록 반환"""
        try:
            client = self.get_client()
            collections = client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            self.logger.error(f"컬렉션 목록 조회 실패: {str(e)}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        컬렉션 삭제
        
        Args:
            collection_name: 삭제할 컬렉션 이름
            
        Returns:
            삭제 성공 여부
        """
        try:
            client = self.get_client()
            client.delete_collection(name=collection_name)
            
            # 메모리 캐시에서도 제거
            if collection_name in self._collections:
                del self._collections[collection_name]
            
            self.logger.info(f"컬렉션 삭제 완료: {collection_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"컬렉션 삭제 실패 ({collection_name}): {str(e)}")
            return False
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        컬렉션 정보 조회
        
        Args:
            collection_name: 컬렉션 이름
            
        Returns:
            컬렉션 정보 딕셔너리
        """
        try:
            collection = self.get_collection(collection_name)
            count = collection.count()
            
            return {
                "name": collection_name,
                "document_count": count,
                "metadata": collection.metadata
            }
            
        except Exception as e:
            self.logger.error(f"컬렉션 정보 조회 실패 ({collection_name}): {str(e)}")
            return {}
    
    def reset_database(self) -> bool:
        """
        전체 데이터베이스 초기화 (주의: 모든 데이터 삭제)
        
        Returns:
            초기화 성공 여부
        """
        try:
            client = self.get_client()
            client.reset()
            self._collections.clear()
            self.logger.warning("ChromaDB 전체 데이터베이스 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"데이터베이스 초기화 실패: {str(e)}")
            return False


# 전역 ChromaDB 클라이언트 인스턴스
chroma_client = ChromaDBClient()


def get_chroma_client():
    """전역 ChromaDB 클라이언트 반환"""
    return chroma_client