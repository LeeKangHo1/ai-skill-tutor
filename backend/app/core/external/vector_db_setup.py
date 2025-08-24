# backend/app/core/external/vector_db_setup.py

import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# Python 경로에 backend 폴더 추가
current_file = os.path.abspath(__file__)
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from openai import OpenAI
from chromadb.utils import embedding_functions
from app.core.external.chroma_client import get_chroma_client


class VectorDBSetup:
    """
    벡터 데이터베이스 초기 구축 및 데이터 삽입 클래스
    - JSON 파일들을 읽어서 ChromaDB에 벡터화하여 저장
    - OpenAI text-embedding-3-large 모델 사용
    - 삽입 기록을 별도 파일에 저장
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.chroma_client = get_chroma_client()
        
        # 경로 설정
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        self.chapters_vec_path = os.path.join(backend_dir, 'data', 'chapters_vec')
        self.chapters_metadata_path = os.path.join(backend_dir, 'data', 'chapters', 'chapters_metadata.json')
        self.insertion_log_path = os.path.join(backend_dir, 'data', 'vector_insertion_log.json')
        
        # OpenAI 임베딩 함수 설정
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv('OPENAI_API_KEY'),
            model_name="text-embedding-3-large"
        )
        
        # 컬렉션 이름
        self.collection_name = "ai_tutor_contents"
        
    def setup_database(self) -> bool:
        """
        전체 벡터 데이터베이스 구축 프로세스
        
        Returns:
            구축 성공 여부
        """
        try:
            self.logger.info("벡터 데이터베이스 구축 시작")
            
            # 1. 기존 컬렉션 삭제 (초기화)
            self._reset_collection()
            
            # 2. 새 컬렉션 생성
            collection = self._create_collection()
            
            # 3. JSON 파일들 로드
            chapter_data_list = self._load_all_chapter_data()
            
            # 4. 섹션 메타데이터 로드
            section_metadata = self._load_section_metadata()
            if not section_metadata:  # ← 이 체크 추가
                self.logger.error("섹션 메타데이터 로드에 실패했습니다. 임베딩을 중단합니다.")
                return False
            
            # 5. 벡터 데이터 삽입
            insertion_results = self._insert_vector_data(collection, chapter_data_list, section_metadata)
            
            # 6. 삽입 기록 저장
            self._save_insertion_log(insertion_results)
            
            self.logger.info(f"벡터 데이터베이스 구축 완료 - 총 {len(insertion_results)}개 청크 삽입")
            return True
            
        except Exception as e:
            self.logger.error(f"벡터 데이터베이스 구축 실패: {str(e)}")
            return False
    
    def _reset_collection(self):
        """기존 컬렉션 삭제"""
        try:
            self.chroma_client.delete_collection(self.collection_name)
            self.logger.info(f"기존 컬렉션 삭제: {self.collection_name}")
        except Exception:
            # 컬렉션이 없어도 괜찮음
            self.logger.info(f"삭제할 컬렉션 없음: {self.collection_name}")
    
    def _create_collection(self):
        """새 컬렉션 생성"""
        collection = self.chroma_client.get_collection(
            collection_name=self.collection_name,
            embedding_function=self.embedding_function
        )
        self.logger.info(f"새 컬렉션 생성 완료: {self.collection_name}")
        return collection
    
    def _load_all_chapter_data(self) -> List[Dict[str, Any]]:
        """chapters_vec 폴더의 모든 JSON 파일 로드"""
        all_chunks = []
        
        if not os.path.exists(self.chapters_vec_path):
            raise FileNotFoundError(f"chapters_vec 폴더가 존재하지 않음: {self.chapters_vec_path}")
        
        # JSON 파일들 찾기
        json_files = list(Path(self.chapters_vec_path).glob("*.json"))
        
        if not json_files:
            raise FileNotFoundError(f"chapters_vec 폴더에 JSON 파일이 없음: {self.chapters_vec_path}")
        
        # 각 JSON 파일 로드
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)
                    
                # 파일이 리스트인지 단일 객체인지 확인
                if isinstance(chunk_data, list):
                    all_chunks.extend(chunk_data)
                else:
                    all_chunks.append(chunk_data)
                    
                self.logger.info(f"JSON 파일 로드 완료: {json_file.name}")
                
            except Exception as e:
                self.logger.error(f"JSON 파일 로드 실패 ({json_file.name}): {str(e)}")
                continue
        
        self.logger.info(f"총 {len(all_chunks)}개 청크 로드 완료")
        return all_chunks
    
    def _load_section_metadata(self) -> Dict[str, str]:
        """섹션 제목 메타데이터 로드"""
        section_titles = {}
        
        try:
            with open(self.chapters_metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 챕터별 섹션 제목 추출
            for chapter in metadata.get('chapters', []):
                chapter_num = chapter['chapter_number']
                for section in chapter.get('sections', []):
                    section_num = section['section_number']
                    section_title = section['section_title']
                    key = f"chapter_{chapter_num}_section_{section_num}"
                    section_titles[key] = section_title
            
            self.logger.info(f"섹션 메타데이터 로드 완료: {len(section_titles)}개")
            return section_titles
            
        except Exception as e:
            self.logger.error(f"섹션 메타데이터 로드 실패: {str(e)}")
            return {}
    
    def _insert_vector_data(self, collection, chunks: List[Dict], section_metadata: Dict) -> List[Dict]:
        """벡터 데이터 삽입"""
        insertion_results = []
        
        for i, chunk in enumerate(chunks):
            try:
                # 청크 검증
                if not self._validate_chunk(chunk):
                    self.logger.warning(f"유효하지 않은 청크 스킵: {chunk.get('id', 'unknown')}")
                    continue
                
                # 메타데이터 준비
                metadata = {
                    "id": chunk["id"],
                    "chunk_type": chunk["chunk_type"],
                    "chapter": chunk["chapter"],
                    "section": chunk["section"],
                    "user_type": ",".join(chunk["user_type"]),  # 리스트를 쉼표로 연결
                    "primary_keywords": ",".join(chunk["primary_keywords"]),  # 리스트를 쉼표로 연결
                    "content_category": chunk["content_category"],
                    "content_quality_score": chunk["content_quality_score"],
                    "source_url": chunk["source_url"],
                    "generated_by_llm_name": chunk["generated_by_llm_name"]
                }
                
                # 섹션 제목 추가
                section_key = f"chapter_{chunk['chapter']}_section_{chunk['section']}"
                section_title = section_metadata.get(section_key, "제목 없음")
                
                # ChromaDB에 삽입
                collection.add(
                    documents=[chunk["content"]],  # 벡터화될 텍스트
                    metadatas=[metadata],          # 메타데이터
                    ids=[chunk["id"]]              # 고유 ID
                )
                
                # 삽입 기록 저장
                insertion_results.append({
                    "id": chunk["id"],
                    "chunk_type": chunk["chunk_type"],
                    "user_type": chunk["user_type"],
                    "section_title": section_title,
                    "chapter": chunk["chapter"],
                    "section": chunk["section"],
                    "inserted_at": datetime.now().isoformat(),
                    "status": "success"
                })
                
                self.logger.debug(f"청크 삽입 완료 [{i+1}/{len(chunks)}]: {chunk['id']}")
                
            except Exception as e:
                self.logger.error(f"청크 삽입 실패: {chunk.get('id', 'unknown')} - {str(e)}")
                
                # 실패 기록도 저장
                insertion_results.append({
                    "id": chunk.get("id", "unknown"),
                    "chunk_type": chunk.get("chunk_type", "unknown"),
                    "user_type": chunk.get("user_type", []),
                    "section_title": "삽입 실패",
                    "chapter": chunk.get("chapter", 0),
                    "section": chunk.get("section", 0),
                    "inserted_at": datetime.now().isoformat(),
                    "status": "failed",
                    "error": str(e)
                })
                continue
        
        return insertion_results
    
    def _validate_chunk(self, chunk: Dict[str, Any]) -> bool:
        """청크 데이터 유효성 검증"""
        required_fields = [
            "id", "chunk_type", "chapter", "section", 
            "user_type", "content", "primary_keywords"
        ]
        
        for field in required_fields:
            if field not in chunk or not chunk[field]:
                self.logger.warning(f"필수 필드 누락: {field}")
                return False
        
        # content 길이 검증 (너무 짧거나 긴 것 제외)
        content_length = len(chunk["content"])
        if content_length < 100 or content_length > 3000:
            self.logger.warning(f"부적절한 content 길이: {content_length}")
            return False
        
        return True
    
    def _save_insertion_log(self, insertion_results: List[Dict]):
        """삽입 기록을 JSON 파일로 저장"""
        try:
            log_data = {
                "insertion_date": datetime.now().isoformat(),
                "total_chunks": len(insertion_results),
                "successful_insertions": len([r for r in insertion_results if r["status"] == "success"]),
                "failed_insertions": len([r for r in insertion_results if r["status"] == "failed"]),
                "results": insertion_results
            }
            
            with open(self.insertion_log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"삽입 기록 저장 완료: {self.insertion_log_path}")
            
        except Exception as e:
            self.logger.error(f"삽입 기록 저장 실패: {str(e)}")
    
    def get_insertion_status(self) -> Dict[str, Any]:
        """마지막 삽입 기록 조회"""
        try:
            if os.path.exists(self.insertion_log_path):
                with open(self.insertion_log_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"status": "no_insertion_log"}
                
        except Exception as e:
            self.logger.error(f"삽입 기록 조회 실패: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def verify_database(self) -> Dict[str, Any]:
        """벡터 데이터베이스 상태 확인"""
        try:
            collection = self.chroma_client.get_collection(
                collection_name=self.collection_name,
                embedding_function=self.embedding_function
            )
            
            total_count = collection.count()
            
            # chunk_type별 통계
            chunk_type_stats = {}
            for chunk_type in ["core_concept", "analogy", "practical_example", "technical_detail"]:
                results = collection.get(where={"chunk_type": chunk_type})  
                count = len(results["ids"]) if results["ids"] else 0
                chunk_type_stats[chunk_type] = count

            # 챕터별 통계
            chapter_stats = {}
            for chapter in range(1, 9):  # 1~8챕터
                results = collection.get(where={"chapter": chapter})
                count = len(results["ids"]) if results["ids"] else 0
                chapter_stats[f"chapter_{chapter}"] = count
            
            return {
                "status": "success",
                "total_documents": total_count,
                "chunk_type_statistics": chunk_type_stats,
                "chapter_statistics": chapter_stats,
                "collection_name": self.collection_name,
                "embedding_model": "text-embedding-3-large"
            }
            
        except Exception as e:
            self.logger.error(f"데이터베이스 상태 확인 실패: {str(e)}")
            return {
                "status": "error", 
                "message": str(e)
            }


def main():
    """벡터 DB 구축 실행 함수"""
    print("=== AI 튜터 벡터 데이터베이스 구축 시작 ===")
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # VectorDBSetup 인스턴스 생성
    db_setup = VectorDBSetup()
    
    # 데이터베이스 구축 실행
    success = db_setup.setup_database()
    
    if success:
        print("✅ 벡터 데이터베이스 구축 성공!")
        
        # 구축 결과 확인
        verification = db_setup.verify_database()
        print(f"📊 총 문서 수: {verification.get('total_documents', 0)}")
        print(f"📈 청크 타입별 통계: {verification.get('chunk_type_statistics', {})}")
        
    else:
        print("❌ 벡터 데이터베이스 구축 실패!")
        return False
    
    print("=== 벡터 데이터베이스 구축 완료 ===")
    return True


if __name__ == "__main__":
    main()