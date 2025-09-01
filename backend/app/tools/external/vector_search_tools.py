# backend/app/tools/external/vector_search_tools.py

import logging
import os
from typing import List, Dict, Any
from chromadb.utils import embedding_functions
import asyncio
from concurrent.futures import ThreadPoolExecutor

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
                # ChromaDB 최신 문법 사용
                results = collection.get(
                    where={
                        "$and": [
                            {"chapter": {"$eq": chapter}},
                            {"section": {"$eq": section}},
                            {"chunk_type": {"$eq": chunk_type}}
                        ]
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


def search_qna_materials(query_text: str, max_distance: float = 1.2) -> List[Dict[str, Any]]:
    """
    QnA용 벡터 자료 검색 (개선된 RAG 시스템)
    - 거리 기반 필터링 (낮은 거리 = 높은 유사도)
    - 실용적인 거리 임계값 (기본값 1.2)
    - 정규화된 유사도 점수 제공
    
    Args:
        query_text: 사용자 질문 텍스트
        max_distance: 최대 허용 거리 (기본값 1.2)
        
    Returns:
        검색된 청크 데이터 리스트 (최대 5개)
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"QnA용 벡터 검색 시작 - 질문: {query_text[:50]}...")
        logger.info(f"최대 거리 임계값: {max_distance}")
        
        # ChromaDB 컬렉션 가져오기
        collection = _get_collection()
        if not collection:
            logger.warning("ChromaDB 컬렉션을 찾을 수 없음")
            return []
        
        # 벡터 유사도 검색 실행
        results = collection.query(
            query_texts=[query_text],
            n_results=15  # 충분한 후보 확보
        )
        
        filtered_chunks = []
        
        if results["documents"] and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            
            logger.info(f"원시 검색 결과: {len(documents)}개")
            
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                # 거리 기반 필터링
                if distance <= max_distance:
                    # 정규화된 유사도 점수 (0~1 범위)
                    similarity_score = max(0, 1 - (distance / max_distance))
                    
                    chunk_data = {
                        "content": doc,
                        "chunk_type": metadata["chunk_type"],
                        "content_quality_score": metadata["content_quality_score"],
                        "primary_keywords": metadata["primary_keywords"],
                        "source_url": metadata["source_url"],
                        "chapter": metadata["chapter"],
                        "section": metadata["section"],
                        "id": metadata["id"],
                        "distance": distance,
                        "similarity_score": similarity_score,
                        "search_rank": i + 1
                    }
                    filtered_chunks.append(chunk_data)
                    
                    logger.debug(f"순위 {i+1}: 거리={distance:.3f}, 유사도={similarity_score:.3f}")
                    
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
        # ChromaDB 최신 문법 사용
        results = collection.get(
            where={
                "$and": [
                    {"chapter": {"$eq": chapter}},
                    {"section": {"$eq": section}},
                    {"chunk_type": {"$eq": "core_concept"}}
                ]
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
                        "$and": [
                            {"chapter": {"$eq": chapter}},
                            {"section": {"$eq": section}},
                            {"chunk_type": {"$eq": chunk_type}}
                        ]
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

def search_qna_materials_parallel(search_queries: List[str]) -> List[Dict]:
    """
    병렬 벡터 검색 실행 및 결과 통합 (동기 버전)
    
    Args:
        search_queries: 검색 쿼리 리스트 (최대 3개)
        
    Returns:
        통합된 벡터 검색 결과 리스트
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"병렬 벡터 검색 시작 - 쿼리 {len(search_queries)}개")
        
        # ThreadPoolExecutor를 사용한 병렬 실행
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 최대 3개 쿼리로 제한
            limited_queries = search_queries[:3]
            
            # 병렬 검색 실행
            future_to_query = {
                executor.submit(search_qna_materials, query): query 
                for query in limited_queries
            }
            
            # 결과 수집
            all_results = []
            for future in future_to_query:
                query = future_to_query[future]
                try:
                    results = future.result(timeout=10)  # 10초 타임아웃
                    if results:
                        all_results.extend(results)
                        logger.info(f"쿼리 '{query}' 검색 완료: {len(results)}개 결과")
                except Exception as e:
                    logger.warning(f"쿼리 '{query}' 검색 실패: {str(e)}")
        
        # 결과 통합 및 중복 제거
        combined_results = _combine_and_deduplicate_results(all_results)
        
        logger.info(f"병렬 벡터 검색 완료 - 총 {len(combined_results)}개 결과")
        return combined_results
        
    except Exception as e:
        logger.error(f"병렬 벡터 검색 실패: {str(e)}")
        # 오류 시 첫 번째 쿼리로 단일 검색
        if search_queries:
            logger.info(f"단일 검색으로 폴백: '{search_queries[0]}'")
            return search_qna_materials(search_queries[0])
        return []


def _combine_and_deduplicate_results(all_results: List[Dict]) -> List[Dict]:
    """
    벡터 검색 결과 통합 및 중복 제거
    
    Args:
        all_results: 여러 검색 결과의 합집합
        
    Returns:
        중복 제거된 상위 결과 리스트
    """
    if not all_results:
        return []
    
    # 중복 제거 (내용 기준)
    seen_contents = set()
    unique_results = []
    
    for result in all_results:
        content = result.get('content', '')
        if content and content not in seen_contents:
            seen_contents.add(content)
            unique_results.append(result)
    
    # 유사도 점수 기준 정렬 (상위 5개만)
    unique_results.sort(
        key=lambda x: x.get('similarity_score', x.get('content_quality_score', 0)), 
        reverse=True
    )
    
    return unique_results[:5]


async def search_qna_materials_parallel_async(search_queries: List[str]) -> List[Dict]:
    """
    병렬 벡터 검색 실행 및 결과 통합 (비동기 버전)
    
    Args:
        search_queries: 검색 쿼리 리스트 (최대 3개)
        
    Returns:
        통합된 벡터 검색 결과 리스트
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"비동기 병렬 벡터 검색 시작 - 쿼리 {len(search_queries)}개")
        
        # 비동기 검색 작업 생성
        search_tasks = [
            _async_vector_search_wrapper(query) 
            for query in search_queries[:3]  # 최대 3개로 제한
        ]
        
        # 병렬 실행
        all_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # 결과 통합
        combined_results = []
        for i, results in enumerate(all_results):
            if isinstance(results, Exception):
                logger.warning(f"검색 쿼리 '{search_queries[i]}' 실패: {str(results)}")
                continue
                
            if isinstance(results, list) and results:
                combined_results.extend(results)
        
        # 중복 제거 및 정렬
        final_results = _combine_and_deduplicate_results(combined_results)
        
        logger.info(f"비동기 병렬 벡터 검색 완료 - 총 {len(final_results)}개 결과")
        return final_results
        
    except Exception as e:
        logger.error(f"비동기 병렬 벡터 검색 실패: {str(e)}")
        # 오류 시 첫 번째 쿼리로 단일 검색
        if search_queries:
            return search_qna_materials(search_queries[0])
        return []


async def _async_vector_search_wrapper(query: str) -> List[Dict]:
    """
    비동기 벡터 검색 래퍼 함수
    
    Args:
        query: 검색 쿼리
        
    Returns:
        벡터 검색 결과
    """
    logger = logging.getLogger(__name__)
    
    try:
        # search_qna_materials가 동기 함수이므로 asyncio.to_thread 사용
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, search_qna_materials, query)
        return result
    except Exception as e:
        logger.error(f"비동기 벡터 검색 실패 (쿼리: '{query}'): {str(e)}")
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
        where_conditions = []
        if chapter:
            where_conditions.append({"chapter": {"$eq": chapter}})
        if section:
            where_conditions.append({"section": {"$eq": section}})
        
        # 전체 조건
        if where_conditions:
            where_condition = {"$and": where_conditions} if len(where_conditions) > 1 else where_conditions[0]
        else:
            where_condition = None
        
        # 청크 타입별 개수 조회
        chunk_type_counts = {}
        for chunk_type in ["core_concept", "analogy", "practical_example", "technical_detail"]:
            type_conditions = where_conditions + [{"chunk_type": {"$eq": chunk_type}}]
            type_condition = {"$and": type_conditions} if len(type_conditions) > 1 else type_conditions[0]
            
            try:
                type_results = collection.get(where=type_condition)
                count = len(type_results["documents"]) if type_results["documents"] else 0
                chunk_type_counts[chunk_type] = count
            except Exception:
                chunk_type_counts[chunk_type] = 0
        
        # 전체 개수 조회
        if where_condition:
            total_results = collection.get(where=where_condition)
            total_count = len(total_results["documents"]) if total_results["documents"] else 0
        else:
            total_count = collection.count()
        
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