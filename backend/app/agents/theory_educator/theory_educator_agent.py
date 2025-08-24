# backend/app/agents/theory_educator/theory_educator_agent.py

from typing import Dict, Any, List
import json
import os

from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.content.theory_tools_chatgpt import theory_generation_tool
from app.tools.external.vector_search_tools import search_theory_materials


class TheoryEducator:
    """
    이론 설명 에이전트 v2.0 - 벡터 DB 기반 + 폴백 전략
    - 우선: chapters_metadata.json + 벡터 검색 결과로 이론 생성
    - 폴백: 벡터 검색 실패 시 기존 chapter_xx.json 파일 활용
    - 순수 이론 설명 대본만 생성 (사용자 대면 메시지 없음)
    """
    
    def __init__(self):
        self.agent_name = "theory_educator"
        # 현재 파일 기준으로 backend/data/chapters 경로 설정
        current_dir = os.path.dirname(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        self.chapter_data_path = os.path.join(backend_dir, "data", "chapters")
    
    def process(self, state: TutorState) -> TutorState:
        """
        벡터 DB 기반 이론 설명 대본 생성 메인 프로세스
        
        Args:
            state: 현재 TutorState
            
        Returns:
            업데이트된 TutorState (theory_draft 포함)
        """
        try:
            print(f"[{self.agent_name}] 벡터 DB 기반 이론 설명 생성 시작 - 챕터 {state['current_chapter']} 섹션 {state['current_section']}")
            
            # 1. 메타데이터에서 챕터/섹션 기본 정보 로드
            section_metadata = self._load_section_metadata(state["current_chapter"], state["current_section"])
            if not section_metadata:
                raise ValueError(f"챕터 {state['current_chapter']} 섹션 {state['current_section']} 메타데이터를 찾을 수 없습니다.")
            
            # 2. 벡터 DB에서 관련 자료 검색
            print(f"[{self.agent_name}] 벡터 DB에서 이론 생성용 자료 검색 중...")
            vector_materials = search_theory_materials(state["current_chapter"], state["current_section"])
            
            # 3. 벡터 검색 결과 확인 및 폴백 전략 적용
            if vector_materials and len(vector_materials) > 0:
                print(f"[{self.agent_name}] 벡터 검색 성공 - {len(vector_materials)}개 자료 발견")

                # 벡터 DB 데이터 내용 터미널 출력
                print(f"[{self.agent_name}] === 벡터 DB 검색 결과 상세 ===")
                for i, material in enumerate(vector_materials, 1):
                    chunk_type = material.get('chunk_type', 'unknown')
                    quality_score = material.get('content_quality_score', 0)
                    keywords = material.get('primary_keywords', [])
                    content = material.get('content', '')[:200]  # 처음 200자만
                    
                    print(f"[{self.agent_name}] 자료 {i}:")
                    print(f"  - 타입: {chunk_type}")
                    print(f"  - 품질점수: {quality_score}")
                    print(f"  - 키워드: {', '.join(keywords) if keywords else '없음'}")
                    print(f"  - 내용: {content}...")
                    print()
                print(f"[{self.agent_name}] === 벡터 DB 검색 결과 끝 ===")

                content_source = "vector"
                section_data = section_metadata  # 메타데이터만 사용
            else:
                print(f"[{self.agent_name}] 벡터 검색 실패 또는 결과 없음 - 폴백 전략 활성화")
                section_data = self._load_section_data_fallback(state["current_chapter"], state["current_section"])
                if not section_data:
                    raise ValueError(f"폴백 데이터도 찾을 수 없습니다.")
                content_source = "fallback"
                vector_materials = []  # 폴백 시에는 빈 리스트
            
            # 4. 재학습 여부 확인
            is_retry_session = state["current_session_count"] > 0
            
            # 5. 벡터 기반 또는 폴백 기반으로 이론 설명 대본 생성
            theory_content = theory_generation_tool(
                section_metadata=section_metadata,  # 항상 메타데이터 전달
                section_data=section_data if content_source == "fallback" else None,  # 폴백 시에만 상세 데이터 전달
                vector_materials=vector_materials,  # 벡터 검색 결과
                user_type=state["user_type"],
                is_retry_session=is_retry_session,
                content_source=content_source  # "vector" or "fallback"
            )
            
            # 6. State 업데이트 - 순수 대본만 저장
            updated_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                theory_content
            )
            
            # 7. 세션 진행 단계 업데이트
            updated_state = state_manager.update_session_progress(
                updated_state, 
                self.agent_name
            )
            
            # 8. 현재 에이전트 설정
            updated_state = state_manager.update_agent_transition(
                updated_state,
                self.agent_name
            )
            
            # 9. 대화 기록 추가 (벡터 사용 여부 기록)
            source_info = f"벡터 DB ({len(vector_materials)}개 자료)" if content_source == "vector" else "폴백 JSON 파일"
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=f"챕터 {state['current_chapter']} 섹션 {state['current_section']} 이론 설명 생성 완료 (출처: {source_info})",
                message_type="system"
            )
            
            print(f"[{self.agent_name}] 이론 설명 생성 완료 (출처: {source_info})")
            return updated_state
            
        except Exception as e:
            print(f"[{self.agent_name}] 오류 발생: {str(e)}")
            # 오류 시에도 State는 반환 (오류 메시지 대본으로)
            error_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                self._create_error_response(str(e))
            )
            # 현재 에이전트 설정
            error_state = state_manager.update_agent_transition(
                error_state,
                self.agent_name
            )
            return error_state
    
    def _load_section_metadata(self, chapter_number: int, section_number: int) -> Dict[str, Any]:
        """
        chapters_metadata.json에서 특정 섹션의 메타데이터만 로드
        
        Args:
            chapter_number: 챕터 번호
            section_number: 섹션 번호
            
        Returns:
            섹션 메타데이터 딕셔너리 (제목 정보만)
        """
        try:
            metadata_file = os.path.join(self.chapter_data_path, "chapters_metadata.json")
            
            if not os.path.exists(metadata_file):
                print(f"[{self.agent_name}] 메타데이터 파일이 존재하지 않음: {metadata_file}")
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 특정 챕터 찾기
            for chapter in metadata.get('chapters', []):
                if chapter.get('chapter_number') == chapter_number:
                    chapter_title = chapter.get('chapter_title', '')
                    
                    # 특정 섹션 찾기
                    for section in chapter.get('sections', []):
                        if section.get('section_number') == section_number:
                            section_title = section.get('section_title', '')
                            
                            print(f"[{self.agent_name}] 메타데이터 로드 완료 - {chapter_title} > {section_title}")
                            
                            return {
                                "chapter_number": chapter_number,
                                "chapter_title": chapter_title,
                                "section_number": section_number,
                                "section_title": section_title,
                                "estimated_duration": chapter.get('estimated_duration_minutes', 0)
                            }
            
            print(f"[{self.agent_name}] 챕터 {chapter_number} 섹션 {section_number} 메타데이터를 찾을 수 없음")
            return None
            
        except Exception as e:
            print(f"[{self.agent_name}] 메타데이터 로드 실패: {str(e)}")
            return None
    
    def _load_section_data_fallback(self, chapter_number: int, section_number: int) -> Dict[str, Any]:
        """
        폴백 전략: 기존 chapter_xx.json 파일에서 특정 섹션 데이터 로드
        
        Args:
            chapter_number: 챕터 번호
            section_number: 섹션 번호
            
        Returns:
            섹션 상세 데이터 딕셔너리
        """
        try:
            chapter_file = os.path.join(
                self.chapter_data_path, 
                f"chapter_{chapter_number:02d}.json"
            )
            
            if not os.path.exists(chapter_file):
                print(f"[{self.agent_name}] 폴백 파일이 존재하지 않음: {chapter_file}")
                return None
            
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            # 특정 섹션만 찾아서 반환
            sections = chapter_data.get('sections', [])
            for section in sections:
                if section.get('section_number') == section_number:
                    print(f"[{self.agent_name}] 폴백 데이터 로드 완료 - 섹션 {section_number}")
                    return section
            
            print(f"[{self.agent_name}] 폴백 데이터에서 섹션 {section_number}를 찾을 수 없음")
            return None
            
        except Exception as e:
            print(f"[{self.agent_name}] 폴백 데이터 로드 실패: {str(e)}")
            return None
    
    def _create_error_response(self, error_message: str) -> str:
        """
        오류 발생 시 기본 대본 생성 (순수 대본)
        
        Args:
            error_message: 오류 메시지
            
        Returns:
            오류 대본 텍스트
        """
        return f"이론 설명을 생성하는 중 문제가 발생했습니다.\n\n오류: {error_message}\n\n죄송합니다. 잠시 후 다시 시도해주세요."
    
    def get_section_info(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 섹션 정보 반환 (외부에서 호출 가능) - 메타데이터 기반
        
        Args:
            state: 현재 TutorState
            
        Returns:
            섹션 정보 딕셔너리
        """
        section_metadata = self._load_section_metadata(state["current_chapter"], state["current_section"])
        
        if section_metadata:
            return {
                "chapter": state["current_chapter"],
                "section": state["current_section"],
                "chapter_title": section_metadata.get("chapter_title", ""),
                "section_title": section_metadata.get("section_title", ""),
                "estimated_duration": section_metadata.get("estimated_duration", 0),
                "data_source": "metadata"
            }
        else:
            # 폴백으로 상세 데이터 시도
            section_data = self._load_section_data_fallback(state["current_chapter"], state["current_section"])
            if section_data:
                return {
                    "chapter": state["current_chapter"],
                    "section": state["current_section"],
                    "section_title": section_data.get("title", ""),
                    "description": section_data.get("description", ""),
                    "learning_objectives": section_data.get("learning_objectives", []),
                    "estimated_duration": section_data.get("estimated_duration_minutes", 0),
                    "data_source": "fallback"
                }
            else:
                return {
                    "chapter": state["current_chapter"],
                    "section": state["current_section"],
                    "error": "섹션 데이터를 찾을 수 없습니다."
                }
    
    def validate_section_data(self, chapter_number: int, section_number: int) -> bool:
        """
        섹션 데이터 유효성 검증 (메타데이터 + 벡터 또는 폴백)
        
        Args:
            chapter_number: 챕터 번호
            section_number: 섹션 번호
            
        Returns:
            유효성 여부
        """
        # 1. 메타데이터 검증
        section_metadata = self._load_section_metadata(chapter_number, section_number)
        if not section_metadata:
            print(f"[{self.agent_name}] 메타데이터 검증 실패")
            return False
        
        # 2. 벡터 검색 또는 폴백 데이터 검증
        vector_materials = search_theory_materials(chapter_number, section_number)
        
        if vector_materials and len(vector_materials) > 0:
            print(f"[{self.agent_name}] 벡터 데이터 검증 성공 - {len(vector_materials)}개 자료")
            return True
        else:
            # 폴백 검증
            section_data = self._load_section_data_fallback(chapter_number, section_number)
            if not section_data:
                print(f"[{self.agent_name}] 폴백 데이터 검증 실패")
                return False
            
            # 필수 필드 검증
            required_fields = ["title", "theory"]
            for field in required_fields:
                if field not in section_data or not section_data[field]:
                    print(f"[{self.agent_name}] 폴백 데이터 필수 필드 누락: {field}")
                    return False
            
            print(f"[{self.agent_name}] 폴백 데이터 검증 성공")
            return True
    
    def get_content_source_info(self, chapter_number: int, section_number: int) -> Dict[str, Any]:
        """
        특정 섹션의 콘텐츠 소스 정보 반환 (디버깅용)
        
        Args:
            chapter_number: 챕터 번호
            section_number: 섹션 번호
            
        Returns:
            콘텐츠 소스 정보
        """
        try:
            # 메타데이터 확인
            metadata_available = self._load_section_metadata(chapter_number, section_number) is not None
            
            # 벡터 검색 결과 확인
            vector_materials = search_theory_materials(chapter_number, section_number)
            vector_available = vector_materials and len(vector_materials) > 0
            
            # 폴백 데이터 확인
            fallback_data = self._load_section_data_fallback(chapter_number, section_number)
            fallback_available = fallback_data is not None
            
            # 실제 사용될 소스 결정
            if metadata_available and vector_available:
                primary_source = "vector"
            elif metadata_available and fallback_available:
                primary_source = "fallback"
            else:
                primary_source = "none"
            
            return {
                "chapter": chapter_number,
                "section": section_number,
                "metadata_available": metadata_available,
                "vector_materials_count": len(vector_materials) if vector_materials else 0,
                "fallback_available": fallback_available,
                "primary_source": primary_source,
                "vector_materials": vector_materials if vector_available else None
            }
            
        except Exception as e:
            return {
                "chapter": chapter_number,
                "section": section_number,
                "error": str(e)
            }