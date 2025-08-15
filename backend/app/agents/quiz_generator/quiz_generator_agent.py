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
    - 순수 퀴즈 대본만 생성 (사용자 대면 메시지 없음)
    - 힌트도 함께 생성하여 한 번에 처리
    - LearningSupervisor가 대본을 사용자 친화적으로 변환
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
            
            # 1. UI 모드를 quiz로 변경 (퀴즈 생성 시작 시점)
            updated_state = state_manager.update_ui_mode(state, "quiz")
            
            # 2. 특정 섹션 데이터만 로드
            section_data = self._load_section_data(updated_state["current_chapter"], updated_state["current_section"])
            if not section_data:
                raise ValueError(f"챕터 {updated_state['current_chapter']} 섹션 {updated_state['current_section']} 데이터를 찾을 수 없습니다.")
            
            # 3. 재학습 여부 확인
            is_retry_session = updated_state["current_session_count"] > 0
            
            # 4. 퀴즈 타입 확인 및 State 동기화
            quiz_type = self._get_quiz_type_from_section(section_data)
            updated_state = state_manager.update_quiz_info(updated_state, question_type=quiz_type)
            
            # 5. 순수 퀴즈 대본 생성 (힌트 포함, 사용자 대면 메시지 없음)
            quiz_content = quiz_generation_tool(
                section_data=section_data,
                user_type=updated_state["user_type"],
                is_retry_session=is_retry_session,
                theory_content=updated_state.get("theory_draft", "")
            )
            
            # 6. 퀴즈 정보 파싱 및 State 업데이트
            quiz_info = self._parse_quiz_content(quiz_content)
            if quiz_info:
                updated_state = self._update_state_with_quiz_info(updated_state, quiz_info)
            
            # 7. State 업데이트 - 순수 대본만 저장
            updated_state = state_manager.update_agent_draft(
                updated_state, 
                self.agent_name, 
                quiz_content
            )
            
            # 8. 현재 에이전트 설정
            updated_state = state_manager.update_agent_transition(
                updated_state,
                self.agent_name
            )
            
            # 9. 대화 기록 추가 (시스템 로그용)
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
            # 현재 에이전트 설정
            error_state = state_manager.update_agent_transition(
                error_state,
                self.agent_name
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
    
    def _get_quiz_type_from_section(self, section_data: Dict[str, Any]) -> str:
        """
        섹션 데이터에서 퀴즈 타입 추출
        
        Args:
            section_data: 섹션 데이터
            
        Returns:
            퀴즈 타입 ("multiple_choice" or "subjective")
        """
        quiz_data = section_data.get('quiz', {})
        quiz_type = quiz_data.get('type', 'multiple_choice')
        
        # 유효한 타입인지 검증
        valid_types = ['multiple_choice', 'subjective']
        if quiz_type not in valid_types:
            quiz_type = 'multiple_choice'  # 기본값으로 fallback
        
        return quiz_type
    
    def _parse_quiz_content(self, quiz_content: str) -> Dict[str, Any]:
        """
        퀴즈 대본에서 JSON 데이터 파싱
        
        Args:
            quiz_content: 퀴즈 대본 (JSON 형태)
            
        Returns:
            파싱된 퀴즈 정보 딕셔너리
        """
        try:
            # JSON 파싱
            quiz_data = json.loads(quiz_content)
            
            # quiz 필드에서 실제 퀴즈 정보 추출
            quiz_info = quiz_data.get("quiz", {})
            
            if not quiz_info:
                print(f"[{self.agent_name}] 퀴즈 정보가 비어있습니다.")
                return None
            
            print(f"[{self.agent_name}] 퀴즈 정보 파싱 완료")
            return quiz_info
            
        except json.JSONDecodeError as e:
            print(f"[{self.agent_name}] JSON 파싱 오류: {str(e)}")
            return None
        except Exception as e:
            print(f"[{self.agent_name}] 퀴즈 정보 파싱 중 오류: {str(e)}")
            return None
    
    def _update_state_with_quiz_info(self, state: TutorState, quiz_info: Dict[str, Any]) -> TutorState:
        """
        파싱된 퀴즈 정보로 State 업데이트
        
        Args:
            state: 현재 TutorState
            quiz_info: 파싱된 퀴즈 정보
            
        Returns:
            업데이트된 TutorState
        """
        # 퀴즈 기본 정보 업데이트
        question_content = quiz_info.get("question", "")
        question_number = quiz_info.get("question_number", 1)
        question_type = quiz_info.get("type", "multiple_choice")
        
        updated_state = state_manager.update_quiz_info(
            state,
            question_type=question_type,
            question_number=question_number,
            question_content=question_content
        )
        
        return updated_state
    
    def _create_error_response(self, error_message: str) -> str:
        """
        오류 발생 시 기본 대본 생성 (순수 대본)
        
        Args:
            error_message: 오류 메시지
            
        Returns:
            오류 대본 텍스트
        """
        return f"퀴즈를 생성하는 중 문제가 발생했습니다.\n\n오류: {error_message}"
    
    def get_quiz_status(self, state: TutorState) -> Dict[str, Any]:
        """
        현재 퀴즈 상태 정보 반환 (외부에서 호출 가능)
        
        Args:
            state: 현재 TutorState
            
        Returns:
            퀴즈 상태 정보
        """
        return {
            "chapter": state["current_chapter"],
            "section": state["current_section"],
            "question_type": state.get("current_question_type", ""),
            "question_number": state.get("current_question_number", 0),
            "question_content": state.get("current_question_content", ""),
            "user_answer": state.get("current_question_answer", ""),
            "hint_usage_count": state.get("hint_usage_count", 0),
            "quiz_draft_ready": bool(state.get("quiz_draft", "").strip())
        }
    
    def validate_quiz_data(self, quiz_info: Dict[str, Any], quiz_type: str) -> bool:
        """
        퀴즈 데이터 유효성 검증
        
        Args:
            quiz_info: 퀴즈 정보
            quiz_type: 퀴즈 타입
            
        Returns:
            유효성 여부
        """
        # 기본 필드 검증
        required_fields = ["question", "type"]
        for field in required_fields:
            if field not in quiz_info or not quiz_info[field]:
                print(f"[{self.agent_name}] 필수 필드 누락: {field}")
                return False
        
        # 타입별 검증
        if quiz_type == "multiple_choice":
            # 객관식은 선택지와 정답이 필요
            options = quiz_info.get("options", [])
            correct_answer = quiz_info.get("correct_answer")
            
            if not options or len(options) < 2:
                print(f"[{self.agent_name}] 객관식 선택지 부족")
                return False
            
            if correct_answer is None:
                print(f"[{self.agent_name}] 객관식 정답 누락")
                return False
        
        elif quiz_type == "subjective":
            # 주관식은 평가 기준이 있으면 좋음
            evaluation_criteria = quiz_info.get("evaluation_criteria")
            if not evaluation_criteria:
                print(f"[{self.agent_name}] 주관식 평가 기준 권장 (누락되어도 진행 가능)")
        
        return True
    
    def extract_hint_from_quiz(self, quiz_content: str) -> str:
        """
        퀴즈 대본에서 힌트 추출
        
        Args:
            quiz_content: 퀴즈 대본 (JSON 형태)
            
        Returns:
            힌트 텍스트
        """
        try:
            quiz_data = json.loads(quiz_content)
            quiz_info = quiz_data.get("quiz", {})
            hint = quiz_info.get("hint", "")
            
            if hint:
                return hint
            else:
                return "힌트가 준비되어 있지 않습니다. 다시 한번 생각해보세요!"
                
        except Exception as e:
            print(f"[{self.agent_name}] 힌트 추출 중 오류: {str(e)}")
            return "힌트를 불러올 수 없습니다."