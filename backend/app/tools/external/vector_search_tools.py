# backend/app/tools/external/vector_search_tools.py

import logging
from typing import List, Dict, Any
from chromadb.utils import embedding_functions

from app.core.external.chroma_client import get_chroma_client


def search_theory_materials(chapter: int, section: int) -> List[Dict[str, Any]]:
    """
    이론 생성용 벡터 자료 검색
    - core_concept: content_quality_score 90점 이상, 최대 3개
    - 기타 타입: content_quality_score 높은 순으로 2개
    
    Args:
        chapter: 챕터 번호
        section: 섹션 번호
        
    Returns:
        검색된 청크 데이터 리스트 (최대 5개)
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"이론 생성용 벡터 검색 시작 - 챕터 {chapter} 섹션 {section}")
        
        # ChromaDB 컬렉션 가져오기
        collection = _get_collection()
        if not collection:
            logger.warning("ChromaDB 컬렉션을 찾을 수 없음")
            return []
        
        # 1단계: core_concept 청크 검색 (최대 3개)
        core_chunks = _search_core_concept_chunks(collection, chapter, section)
        logger.info(f"core_concept 청크 {len(core_chunks)}개 발견")
        
        # 2단계: 기타 청크 타입 검색 (2개)
        other_chunks = _search_other_chunks(collection, chapter, section)
        logger.info(f"기타 청크 {len(other_chunks)}개 발견")
        
        # 결과 합치기
        all_chunks = core_chunks + other_chunks
        
        logger.info(f"이론 생성용 벡터 검색 완료 - 총 {len(all_chunks)}개 청크 반환")
        return all_chunks
        
    except Exception as e:
        logger.error(f"이론 생성용 벡터 검색 실패: {str(e)}")
        return []


def search_quiz_materials(chapter: int, section: int) -> List[Dict[str, Any]]:
    """
    퀴즈 생성용 벡터 자료 검색
    - core_concept 제외한 나머지 청크 타입만
    - content_quality_score 높은 순으로 최대 3개
    
    Args:
        chapter: 챕터 번호
        section: 섹션 번호
        
    Returns:
        검색된 청크 데이터 리스트 (최대 3개)
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"퀴즈 생성용 벡터 검색 시작 - 챕터 {chapter} 섹션 {section}")
        
        # ChromaDB 컬렉션 가져오기
        collection = _get_collection()
        if not collection:
            logger.warning("ChromaDB 컬렉션을 찾을 수 없음")
            return []
        
        # core_concept 제외한 모든 타입 검색
        other_chunk_types = ["analogy", "practical_example", "technical_detail"]
        all_chunks = []
        
        for chunk_type in other_chunk_types:
            try:
                results = collection.get(
                    where={
                        "chapter": chapter,
                        "section": section,
                        "chunk_type": chunk_type
                    }
                )
                
                if results["documents"]:
                    documents = results["documents"]
                    metadatas = results["metadatas"]
                    
                    for doc, metadata in zip(documents, metadatas):
                        quality_score = metadata.get("content_quality_score", 0)
                        
                        if quality_score >= 90:  # 90점 이상만
                            chunk_data = {
                                "content": doc,
                                "chunk_type": metadata["chunk_type"],
                                "content_quality_score": quality_score,
                                "primary_keywords": metadata["primary_keywords"],
                                "source_url": metadata["source_url"],
                                "id": metadata["id"]
                            }
                            all_chunks.append(chunk_data)
                            
            except Exception as e:
                logger.warning(f"{chunk_type} 검색 실패: {str(e)}")
                continue
        
        # content_quality_score 높은 순으로 정렬 후 상위 3개 선택
        all_chunks.sort(key=lambda x: x["content_quality_score"], reverse=True)
        result_chunks = all_chunks[:3]
        
        logger.info(f"퀴즈 생성용 벡터 검색 완료 - 총 {len(result_chunks)}개 청크 반환")
        return result_chunks
        
    except Exception as e:
        logger.error(f"퀴즈 생성용 벡터 검색 실패: {str(e)}")
        return []


def search_qna_materials(query_text: str) -> List[Dict[str, Any]]:
    """
    QnA용 벡터 자료 검색 (일반 RAG 시스템)
    - 유사도 검색 (confidence 0.9 이상)
    - 최대 5개
    
    Args:
        query_text: 사용자 질문 텍스트
        chapter: 특정 챕터로 제한 (None이면 전체 검색)
        
    Returns:
        검색된 청크 데이터 리스트 (최대 5개)
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"QnA용 벡터 검색 시작 - 질문: {query_text[:50]}...")
        
        # ChromaDB 컬렉션 가져오기
        collection = _get_collection()
        if not collection:
            logger.warning("ChromaDB 컬렉션을 찾을 수 없음")
            return []
        
        # 벡터 유사도 검색 실행
        results = collection.query(
            query_texts=[query_text],
            n_results=10  # 넉넉하게 가져와서 필터링
        )
        
        # confidence 0.9 이상 필터링
        filtered_chunks = []
        
        if results["documents"] and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                # distance를 confidence로 변환 (거리가 작을수록 유사도 높음)
                confidence = 1.0 - distance
                
                if confidence >= 0.9:  # confidence 0.9 이상만
                    chunk_data = {
                        "content": doc,
                        "chunk_type": metadata["chunk_type"],
                        "content_quality_score": metadata["content_quality_score"],
                        "primary_keywords": metadata["primary_keywords"],
                        "source_url": metadata["source_url"],
                        "chapter": metadata["chapter"],
                        "section": metadata["section"],
                        "id": metadata["id"],
                        "confidence": confidence,
                        "search_rank": i + 1
                    }
                    filtered_chunks.append(chunk_data)
                    
                    # 최대 5개까지만
                    if len(filtered_chunks) >= 5:
                        break
        
        logger.info(f"QnA용 벡터 검색 완료 - 총 {len(filtered_chunks)}개 청크 반환")
        return filtered_chunks
        
    except Exception as e:
        logger.error(f"QnA용 벡터 검색 실패: {str(e)}")
        return []


def _get_collection():
    """AI 튜터 컬렉션 조회"""
    try:
        chroma_client = get_chroma_client()
        
        # OpenAI 임베딩 함수 설정
        embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv('OPENAI_API_KEY'),
            model_name="text-embedding-3-large"
        )
        
        collection = chroma_client.get_collection(
            collection_name="ai_tutor_contents",
            embedding_function=embedding_function
        )
        
        return collection
        
    except Exception as e:
        logging.getLogger(__name__).error(f"컬렉션 조회 실패: {str(e)}")
        return None


def _search_core_concept_chunks(collection, chapter: int, section: int) -> List[Dict[str, Any]]:
    """
    core_concept 청크 검색
    - content_quality_score 90점 이상
    - 최대 3개
    """
    try:
        # 벡터 검색 실행 (정확한 메타데이터 매칭)
        results = collection.get(
            where={
                "chapter": chapter,
                "section": section,
                "chunk_type": "core_concept"
            }
        )
        
        # content_quality_score 90점 이상 필터링
        filtered_chunks = []
        
        if results["documents"]:
            documents = results["documents"]
            metadatas = results["metadatas"]
            
            for doc, metadata in zip(documents, metadatas):
                quality_score = metadata.get("content_quality_score", 0)
                
                if quality_score >= 90:  # 90점 이상만
                    chunk_data = {
                        "content": doc,
                        "chunk_type": metadata["chunk_type"],
                        "content_quality_score": quality_score,
                        "primary_keywords": metadata["primary_keywords"],
                        "source_url": metadata["source_url"],
                        "id": metadata["id"]
                    }
                    filtered_chunks.append(chunk_data)
        
        # content_quality_score 높은 순으로 정렬 후 최대 3개
        filtered_chunks.sort(key=lambda x: x["content_quality_score"], reverse=True)
        return filtered_chunks[:3]
        
    except Exception as e:
        logging.getLogger(__name__).error(f"core_concept 검색 실패: {str(e)}")
        return []


def _search_other_chunks(collection, chapter: int, section: int) -> List[Dict[str, Any]]:
    """
    기타 청크 타입 검색 (analogy, practical_example, technical_detail)
    - content_quality_score 높은 순으로 2개
    """
    try:
        # core_concept 제외한 모든 타입의 청크 가져오기
        other_chunk_types = ["analogy", "practical_example", "technical_detail"]
        
        all_other_chunks = []
        
        # 각 청크 타입별로 조회
        for chunk_type in other_chunk_types:
            try:
                results = collection.get(
                    where={
                        "chapter": chapter,
                        "section": section,
                        "chunk_type": chunk_type
                    }
                )
                
                if results["documents"]:
                    documents = results["documents"]
                    metadatas = results["metadatas"]
                    
                    for doc, metadata in zip(documents, metadatas):
                        quality_score = metadata.get("content_quality_score", 0)
                        
                        if quality_score >= 90:  # 90점 이상만
                            chunk_data = {
                                "content": doc,
                                "chunk_type": metadata["chunk_type"],
                                "content_quality_score": quality_score,
                                "primary_keywords": metadata["primary_keywords"],
                                "source_url": metadata["source_url"],
                                "id": metadata["id"]
                            }
                            all_other_chunks.append(chunk_data)
                            
            except Exception as e:
                logging.getLogger(__name__).warning(f"{chunk_type} 검색 실패: {str(e)}")
                continue
        
        # content_quality_score 높은 순으로 정렬 후 상위 2개 선택
        all_other_chunks.sort(key=lambda x: x["content_quality_score"], reverse=True)
        return all_other_chunks[:2]
        
    except Exception as e:
        logging.getLogger(__name__).error(f"기타 청크 검색 실패: {str(e)}")
        return []


def get_vector_search_statistics(chapter: int = None, section: int = None) -> Dict[str, Any]:
    """
    벡터 검색 통계 조회 (디버깅용)
    
    Args:
        chapter: 특정 챕터 (None이면 전체)
        section: 특정 섹션 (None이면 전체)
        
    Returns:
        검색 통계 정보
    """
    try:
        collection = _get_collection()
        if not collection:
            return {"error": "컬렉션을 찾을 수 없음"}
        
        # 검색 조건 설정
        where_condition = {}
        if chapter:
            where_condition["chapter"] = chapter
        if section:
            where_condition["section"] = section
        
        # 청크 타입별 개수 조회
        chunk_type_counts = {}
        for chunk_type in ["core_concept", "analogy", "practical_example", "technical_detail"]:
            type_condition = {**where_condition, "chunk_type": chunk_type}
            count = collection.count(where=type_condition)
            chunk_type_counts[chunk_type] = count
        
        total_count = collection.count(where=where_condition)
        
        return {
            "total_chunks": total_count,
            "chunk_type_distribution": chunk_type_counts,
            "search_scope": {
                "chapter": chapter if chapter else "전체",
                "section": section if section else "전체"
            }
        }
        
    except Exception as e:
        logging.getLogger(__name__).error(f"통계 조회 실패: {str(e)}")
        return {"error": str(e)}


# 임포트 누락 추가
import os