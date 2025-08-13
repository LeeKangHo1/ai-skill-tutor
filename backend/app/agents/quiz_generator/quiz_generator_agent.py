# backend/app/agents/quiz_generator/quiz_generator_agent.py

from typing import Dict, Any
import json
import os

from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.content.quiz_tools_chatgpt import quiz_generation_tool


class QuizGenerator:
    """
    퀴즈 생성 에이전트
    - 특정 섹션 데이터만 로드하여 효율적 처리
    - 사용자와 직접 소통하지 않고 대본만 생성
    """
    
    def __init__(self):
        self.agent_name = "quiz_generator"
        # 현재 파일 기준으로 backend/data/chapters 경로 설정
        current_dir = os.path.dirname(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        self.chapter_data_path = os.path.join(backend_dir, "data", "chapters")
    
    def process(self, state: TutorState) -> TutorState:
        """
        퀴즈 생성 대본 생성 메인 프로세스
        
        Args:
            state: 현재 TutorState
            
        Returns:
            업데이트된 TutorState (quiz_draft 포함)
        """
        try:
            print(f"[{self.agent_name}] 퀴즈 생성 시작 - 챕터 {state['current_chapter']} 섹션 {state['current_section']}")
            
            # 1. 특정 섹션 데이터만 로드
            section_data = self._load_section_data(state["current_chapter"], state["current_section"])
            if not section_data:
                raise ValueError(f"챕터 {state['current_chapter']} 섹션 {state['current_section']} 데이터를 찾을 수 없습니다.")
            
            # 2. 재학습 여부 확인
            is_retry_session = state["current_session_count"] > 0
            
            # 3. 퀴즈 생성
            quiz_content = quiz_generation_tool(
                section_data=section_data,
                user_type=state["user_type"],
                is_retry_session=is_retry_session,
                theory_content=state.get("theory_draft", "")
            )
            
            # 4. State 업데이트 - 대본 저장
            updated_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                quiz_content
            )
            
            # 5. UI 모드를 quiz로 변경
            updated_state = state_manager.update_ui_mode(
                updated_state, 
                "quiz"
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
                message=f"챕터 {state['current_chapter']} 섹션 {state['current_section']} 퀴즈 생성 완료",
                message_type="system"
            )
            
            print(f"[{self.agent_name}] 퀴즈 생성 완료")
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
        return f"""죄송합니다. 퀴즈를 생성하는 중 문제가 발생했습니다.

다른 방법으로 학습을 진행해보시거나, 궁금한 점이 있으시면 언제든 질문해주세요!

오류: {error_message}"""