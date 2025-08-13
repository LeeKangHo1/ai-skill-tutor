# backend/app/agents/theory_educator/theory_educator_agent.py

from typing import Dict, Any, List
import json
import os

from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.content.theory_tools_chatgpt import theory_generation_tool


class TheoryEducator:
    """
    이론 설명 에이전트
    - 특정 섹션 데이터만 로드하여 효율적 처리
    - 사용자와 직접 소통하지 않고 대본만 생성
    """
    
    def __init__(self):
        self.agent_name = "theory_educator"
        # 현재 파일 기준으로 backend/data/chapters 경로 설정
        current_dir = os.path.dirname(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        self.chapter_data_path = os.path.join(backend_dir, "data", "chapters")
    
    def process(self, state: TutorState) -> TutorState:
        """
        이론 설명 대본 생성 메인 프로세스
        
        Args:
            state: 현재 TutorState
            
        Returns:
            업데이트된 TutorState (theory_draft 포함)
        """
        try:
            print(f"[{self.agent_name}] 이론 설명 생성 시작 - 챕터 {state['current_chapter']} 섹션 {state['current_section']}")
            
            # 1. 특정 섹션 데이터만 로드
            section_data = self._load_section_data(state["current_chapter"], state["current_section"])
            if not section_data:
                raise ValueError(f"챕터 {state['current_chapter']} 섹션 {state['current_section']} 데이터를 찾을 수 없습니다.")
            
            # 2. 재학습 여부 확인
            is_retry_session = state["current_session_count"] > 0
            
            # 3. 벡터 DB에서 관련 자료 검색 (추후 활용)
            vector_materials = []  # 현재는 빈 리스트
            
            # 4. 이론 설명 대본 생성
            theory_content = theory_generation_tool(
                section_data=section_data,
                user_type=state["user_type"],
                vector_materials=vector_materials,
                is_retry_session=is_retry_session
            )
            
            # 5. State 업데이트 - 대본 저장
            updated_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                theory_content
            )
            
            # 6. 세션 진행 단계 업데이트
            updated_state = state_manager.update_session_progress(
                updated_state, 
                self.agent_name
            )
            
            # 7. 대화 기록 추가
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=f"챕터 {state['current_chapter']} 섹션 {state['current_section']} 이론 설명 대본 생성 완료",
                message_type="system"
            )
            
            print(f"[{self.agent_name}] 이론 설명 생성 완료")
            return updated_state
            
        except Exception as e:
            print(f"[{self.agent_name}] 오류 발생: {str(e)}")
            # 오류 시에도 State는 반환 (오류 메시지 대본으로)
            error_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                self._create_error_response(str(e))
            )
            return error_state
    
    def _load_section_data(self, chapter_number: int, section_number: int) -> Dict[str, Any]:
        """
        JSON 파일에서 특정 섹션 데이터만 로드
        
        Args:
            chapter_number: 챕터 번호
            section_number: 섹션 번호
            
        Returns:
            섹션 데이터 딕셔너리
        """
        try:
            chapter_file = os.path.join(
                self.chapter_data_path, 
                f"chapter_{chapter_number:02d}.json"
            )
            
            if not os.path.exists(chapter_file):
                print(f"[{self.agent_name}] 챕터 파일이 존재하지 않음: {chapter_file}")
                return None
            
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            # 특정 섹션만 찾아서 반환
            sections = chapter_data.get('sections', [])
            for section in sections:
                if section.get('section_number') == section_number:
                    print(f"[{self.agent_name}] 섹션 {section_number} 데이터 로드 완료")
                    return section
            
            print(f"[{self.agent_name}] 섹션 {section_number}를 찾을 수 없음")
            return None
            
        except Exception as e:
            print(f"[{self.agent_name}] 섹션 데이터 로드 실패: {str(e)}")
            return None
    
    def _create_error_response(self, error_message: str) -> str:
        """
        오류 발생 시 기본 응답 생성
        
        Args:
            error_message: 오류 메시지
            
        Returns:
            오류 응답 텍스트
        """
        return f"""죄송합니다. 이론 설명을 생성하는 중 문제가 발생했습니다.

궁금한 점이 있으시면 언제든 질문해주세요!

오류: {error_message}"""