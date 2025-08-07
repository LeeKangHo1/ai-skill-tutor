# backend/app/core/external/vector_db.py
"""
ChromaDB 벡터 데이터베이스 클라이언트 모듈
임베딩 저장, 검색 및 관리 기능을 제공합니다.
"""

import chromadb
from typing import List, Dict, Any, Optional
import os
from chromadb.config import Settings

class VectorDBClient:
    """ChromaDB 벡터 데이터베이스 클라이언트 클래스"""
    
    def __init__(self):
        """벡터 DB 클라이언트 초기화"""
        self.client = None
        self.collections = {}
        self.db_path = os.getenv('CHROMA_DB_PATH', './data/chroma_db')
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """ChromaDB 클라이언트를 초기화합니다."""
        try:
            # 로컬 파일 기반 ChromaDB 클라이언트 생성
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        except Exception as e:
            print(f"ChromaDB 클라이언트 초기화 실패: {e}")
            self.client = None
    
    def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None) -> chromadb.Collection:
        """
        컬렉션을 가져오거나 생성합니다.
        
        Args:
            name (str): 컬렉션 이름
            metadata (Optional[Dict]): 컬렉션 메타데이터
            
        Returns:
            chromadb.Collection: ChromaDB 컬렉션 객체
        """
        if not self.client:
            raise Exception("ChromaDB 클라이언트가 초기화되지 않았습니다.")
        
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata=metadata or {}
            )
        
        return self.collections[name]
    
    def add_documents(self, collection_name: str, documents: List[str], 
                     embeddings: List[List[float]], ids: List[str], 
                     metadatas: Optional[List[Dict]] = None) -> None:
        """
        문서와 임베딩을 컬렉션에 추가합니다.
        
        Args:
            collection_name (str): 컬렉션 이름
            documents (List[str]): 문서 텍스트 목록
            embeddings (List[List[float]]): 임베딩 벡터 목록
            ids (List[str]): 문서 ID 목록
            metadatas (Optional[List[Dict]]): 메타데이터 목록
        """
        collection = self.get_or_create_collection(collection_name)
        
        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas or [{}] * len(documents)
        )
    
    def search_similar(self, collection_name: str, query_embeddings: List[List[float]], 
                      n_results: int = 5, where: Optional[Dict] = None) -> Dict[str, Any]:
        """
        유사한 문서를 검색합니다.
        
        Args:
            collection_name (str): 컬렉션 이름
            query_embeddings (List[List[float]]): 쿼리 임베딩 벡터
            n_results (int): 반환할 결과 수
            where (Optional[Dict]): 필터 조건
            
        Returns:
            Dict[str, Any]: 검색 결과
        """
        collection = self.get_or_create_collection(collection_name)
        
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )
        
        return results
    
    def delete_documents(self, collection_name: str, ids: List[str]) -> None:
        """
        문서를 삭제합니다.
        
        Args:
            collection_name (str): 컬렉션 이름
            ids (List[str]): 삭제할 문서 ID 목록
        """
        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=ids)
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        컬렉션 정보를 가져옵니다.
        
        Args:
            collection_name (str): 컬렉션 이름
            
        Returns:
            Dict[str, Any]: 컬렉션 정보
        """
        collection = self.get_or_create_collection(collection_name)
        
        return {
            'name': collection.name,
            'count': collection.count(),
            'metadata': collection.metadata
        }
    
    def reset_collection(self, collection_name: str) -> None:
        """
        컬렉션을 초기화합니다.
        
        Args:
            collection_name (str): 컬렉션 이름
        """
        if not self.client:
            raise Exception("ChromaDB 클라이언트가 초기화되지 않았습니다.")
        
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
        except Exception:
            # 컬렉션이 존재하지 않는 경우 무시
            pass