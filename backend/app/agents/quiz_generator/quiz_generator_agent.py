# backend/app/agents/quiz_generator/quiz_generator_agent.py
# v2.0 업데이트: State 필드명 변경 대응, parse_quiz_from_json 활용

from typing import Dict, Any
import json
import os

from app.core.langraph.state_manager import TutorState, state_manager
from app.tools.content.quiz_tools_chatgpt import quiz_generation_tool


class QuizGenerator:
    """
    퀴즈 생성 에이전트 (v2.0)
    - 특정 섹션 데이터만 로드하여 효율적 처리
    - 순수 퀴즈 대본만 생성 (사용자 대면 메시지 없음)
    - 힌트도 함께 생성하여 한 번에 처리
    - LearningSupervisor가 대본을 사용자 친화적으로 변환
    - v2.0: 객관식/주관식 분리된 State 필드 지원
    - v2.0: state_manager.parse_quiz_from_json() 활용
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
            
            # 2. theory_draft 우선 확인
            theory_draft = self._get_theory_draft_from_state(updated_state)
            
            # 3. 메타데이터 로드 (항상 필요)
            section_metadata = self._load_section_metadata(updated_state["current_chapter"], updated_state["current_section"])
            if not section_metadata:
                raise ValueError(f"챕터 {updated_state['current_chapter']} 섹션 {updated_state['current_section']} 메타데이터를 찾을 수 없습니다.")
            
            # 4. 데이터 소스 결정 및 로드
            if theory_draft:
                print(f"[{self.agent_name}] theory_draft 기반 퀴즈 생성 모드")
                section_data = section_metadata  # 메타데이터만 사용
                content_source = "theory_draft"
            else:
                print(f"[{self.agent_name}] 폴백 전략: 기존 JSON 파일 사용")
                section_data = self._load_section_data(updated_state["current_chapter"], updated_state["current_section"])
                if not section_data:
                    raise ValueError(f"폴백 데이터도 찾을 수 없습니다.")
                content_source = "fallback"
            
            # 5. 재학습 여부 확인
            is_retry_session = updated_state["current_session_count"] > 0
            
            # 6. 순수 퀴즈 대본 생성 (힌트 포함, 사용자 대면 메시지 없음)
            quiz_content = quiz_generation_tool(
                section_data=section_data,
                user_type=updated_state["user_type"],
                is_retry_session=is_retry_session,
                theory_content=theory_draft,
                content_source=content_source
            )
            
            # 5. 퀴즈 정보 파싱 및 State 업데이트 (v2.0 새로운 메서드 사용)
            quiz_info = self._parse_quiz_content(quiz_content)
            if quiz_info:
                updated_state = state_manager.parse_quiz_from_json(updated_state, quiz_info)
            
            # 6. State 업데이트 - 순수 대본만 저장
            updated_state = state_manager.update_agent_draft(
                updated_state, 
                self.agent_name, 
                quiz_content
            )
            
            # 7. 현재 에이전트 설정
            updated_state = state_manager.update_agent_transition(
                updated_state,
                self.agent_name
            )
            
            # 8. 대화 기록 추가 (데이터 소스 정보 포함)
            source_info = "theory_draft 기반" if content_source == "theory_draft" else "폴백 JSON 파일"
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=f"챕터 {state['current_chapter']} 섹션 {state['current_section']} 퀴즈 생성 완료 (출처: {source_info})",
                message_type="system"
            )
            
            print(f"[{self.agent_name}] 퀴즈 생성 완료 (출처: {source_info})")
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

    def _load_section_data(self, chapter_number: int, section_number: int) -> Dict[str, Any]:
        """
        JSON 파일에서 특정 섹션 데이터만 로드 (폴백 전략용)
        
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
                    print(f"[{self.agent_name}] 폴백 섹션 {section_number} 데이터 로드 완료")
                    return section
            
            print(f"[{self.agent_name}] 섹션 {section_number}를 찾을 수 없음")
            return None
            
        except Exception as e:
            print(f"[{self.agent_name}] 섹션 데이터 로드 실패: {str(e)}")
            return None
    
    def _get_theory_draft_from_state(self, state: TutorState) -> str:
        """
        State에서 theory_draft 내용을 추출
        
        Args:
            state: 현재 TutorState
            
        Returns:
            theory_draft 내용 (없으면 빈 문자열)
        """
        try:
            theory_draft = state.get("theory_draft", "")
            
            if theory_draft and theory_draft.strip():
                print(f"[{self.agent_name}] theory_draft 발견 - 길이: {len(theory_draft)}자")
                return theory_draft.strip()
            else:
                print(f"[{self.agent_name}] theory_draft가 비어있거나 없음")
                return ""
                
        except Exception as e:
            print(f"[{self.agent_name}] theory_draft 추출 실패: {str(e)}")
            return ""
    
    def _get_quiz_type_from_section(self, section_data: Dict[str, Any]) -> str:
        """
        섹션 데이터에서 퀴즈 타입 추출 (v2.0에서는 사용하지 않음 - 호환성 유지)
        ChatGPT가 섹션 데이터를 보고 자동으로 퀴즈 타입을 결정하므로 불필요
        
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
        퀴즈 대본에서 JSON 데이터 파싱 (v2.0 검증 강화)
        
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
            
            # v2.0: JSON 구조 유효성 검증
            if not self.validate_quiz_json_structure(quiz_info):
                print(f"[{self.agent_name}] 퀴즈 JSON 구조가 유효하지 않습니다.")
                return None
            
            print(f"[{self.agent_name}] 퀴즈 정보 파싱 및 검증 완료")
            return quiz_info
            
        except json.JSONDecodeError as e:
            print(f"[{self.agent_name}] JSON 파싱 오류: {str(e)}")
            return None
        except Exception as e:
            print(f"[{self.agent_name}] 퀴즈 정보 파싱 중 오류: {str(e)}")
            return None
    
    def _update_state_with_quiz_info(self, state: TutorState, quiz_info: Dict[str, Any]) -> TutorState:
        """
        파싱된 퀴즈 정보로 State 업데이트 (v2.0에서는 parse_quiz_from_json 사용)
        이 메서드는 호환성을 위해 유지하지만 실제로는 state_manager.parse_quiz_from_json을 사용
        
        Args:
            state: 현재 TutorState
            quiz_info: 파싱된 퀴즈 정보
            
        Returns:
            업데이트된 TutorState
        """
        # v2.0에서는 state_manager.parse_quiz_from_json을 직접 사용
        return state_manager.parse_quiz_from_json(state, quiz_info)
    
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
        현재 퀴즈 상태 정보 반환 (v2.0 필드명 업데이트)
        
        Args:
            state: 현재 TutorState
            
        Returns:
            퀴즈 상태 정보
        """
        return {
            "chapter": state["current_chapter"],
            "section": state["current_section"],
            "quiz_type": state.get("quiz_type", ""),  # current_question_type → quiz_type
            "quiz_content": state.get("quiz_content", ""),  # current_question_content → quiz_content
            "quiz_options": state.get("quiz_options", []),  # 새로운 필드
            "quiz_correct_answer": state.get("quiz_correct_answer"),  # 새로운 필드
            "quiz_hint": state.get("quiz_hint", ""),  # 새로운 필드
            "user_answer": state.get("user_answer", ""),  # current_question_answer → user_answer
            "multiple_answer_correct": state.get("multiple_answer_correct", False),  # 새로운 필드
            "subjective_answer_score": state.get("subjective_answer_score", 0),  # 새로운 필드
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
    
    def validate_quiz_json_structure(self, quiz_info: Dict[str, Any]) -> bool:
        """
        ChatGPT에서 생성된 퀴즈 JSON 구조 유효성 검증 (v2.0 신규)
        
        Args:
            quiz_info: 파싱된 퀴즈 정보
            
        Returns:
            유효성 여부
        """
        try:
            # 기본 필드 검증
            required_fields = ["type", "question"]
            for field in required_fields:
                if field not in quiz_info:
                    print(f"[{self.agent_name}] 필수 필드 누락: {field}")
                    return False
            
            quiz_type = quiz_info.get("type")
            
            # 객관식 필드 검증
            if quiz_type == "multiple_choice":
                mc_fields = ["options", "correct_answer", "explanation"]
                for field in mc_fields:
                    if field not in quiz_info:
                        print(f"[{self.agent_name}] 객관식 필수 필드 누락: {field}")
                        return False
                
                # 선택지 개수 검증
                options = quiz_info.get("options", [])
                if not isinstance(options, list) or len(options) < 2:
                    print(f"[{self.agent_name}] 객관식 선택지 부족: {len(options)}개")
                    return False
                
                # 정답 번호 검증
                correct_answer = quiz_info.get("correct_answer")
                if not isinstance(correct_answer, int) or correct_answer < 1 or correct_answer > len(options):
                    print(f"[{self.agent_name}] 객관식 정답 번호 오류: {correct_answer}")
                    return False
            
            # 주관식 필드 검증
            elif quiz_type == "subjective":
                subj_fields = ["sample_answer", "evaluation_criteria"]
                for field in subj_fields:
                    if field not in quiz_info:
                        print(f"[{self.agent_name}] 주관식 권장 필드 누락: {field}")
                        # 주관식은 경고만 출력하고 계속 진행
            
            else:
                print(f"[{self.agent_name}] 알 수 없는 퀴즈 타입: {quiz_type}")
                return False
            
            print(f"[{self.agent_name}] 퀴즈 JSON 구조 검증 통과: {quiz_type}")
            return True
            
        except Exception as e:
            print(f"[{self.agent_name}] 퀴즈 JSON 구조 검증 중 오류: {str(e)}")
            return False
    
    def get_quiz_field_mapping(self) -> Dict[str, str]:
        """
        ChatGPT JSON 필드와 State 필드 매핑 정보 반환 (v2.0 신규)
        
        Returns:
            필드 매핑 딕셔너리
        """
        return {
            # ChatGPT JSON → State 필드
            "type": "quiz_type",
            "question": "quiz_content", 
            "options": "quiz_options",
            "correct_answer": "quiz_correct_answer",
            "explanation": "quiz_explanation",
            "sample_answer": "quiz_sample_answer",
            "evaluation_criteria": "quiz_evaluation_criteria",
            "hint": "quiz_hint"
        }