# backend/tests/terminal_tester_by_claude/command_handler.py
# 터미널 명령어 처리 및 비즈니스 로직

import json
from typing import Dict, Any, List, Optional, Tuple
from config import config
from display_utils import DisplayUtils


class CommandHandler:
    """터미널 명령어 처리 클래스"""
    
    def __init__(self, api_client, auth_manager):
        """
        명령어 핸들러 초기화
        
        Args:
            api_client: API 클라이언트 인스턴스
            auth_manager: 인증 관리자 인스턴스
        """
        self.api_client = api_client
        self.auth_manager = auth_manager
        
        # 현재 세션 상태 추적
        self.current_session_state = {
            "active": False,
            "chapter": None,
            "section": None,
            "stage": None,  # session_start, theory_completed, quiz_and_feedback_completed
            "ui_mode": None,  # chat, quiz
            "current_agent": None
        }
        
        # TutorState 캐시 (마지막으로 받은 State)
        self.cached_tutor_state = None
        
        # 명령어 매핑
        self.commands = {
            "login": self.handle_login,
            "logout": self.handle_logout,
            "start": self.handle_start_session,
            "msg": self.handle_send_message,
            "quiz": self.handle_quiz_answer,
            "complete": self.handle_complete_session,
            "state": self.handle_show_state,
            "auth": self.handle_auth_status,
            "health": self.handle_health_check,
            "version": self.handle_version_check,
            "help": self.handle_help,
            "clear": self.handle_clear_screen,
            "status": self.handle_session_status,
            "reset": self.handle_reset_session
        }
    
    def process_command(self, command_line: str) -> bool:
        """
        명령어 처리
        
        Args:
            command_line: 사용자가 입력한 명령어 라인
            
        Returns:
            bool: 계속 실행 여부 (False면 프로그램 종료)
        """
        if not command_line.strip():
            return True
        
        # 명령어 파싱
        parts = command_line.strip().split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # 종료 명령어 체크
        if command in ["quit", "exit", "q"]:
            return False
        
        # 명령어 실행
        if command in self.commands:
            try:
                self.commands[command](args)
            except Exception as e:
                DisplayUtils.print_error(f"명령어 실행 중 오류: {str(e)}")
        else:
            DisplayUtils.print_error(f"알 수 없는 명령어: {command}")
            DisplayUtils.print_info("'help'를 입력하여 사용 가능한 명령어를 확인하세요.")
        
        return True
    
    # === 인증 관련 명령어 ===
    
    def handle_login(self, args: List[str]):
        """로그인 명령어 처리"""
        if self.auth_manager.is_logged_in:
            if not DisplayUtils.confirm_action("이미 로그인되어 있습니다. 다시 로그인하시겠습니까?"):
                return
            
            self.auth_manager.logout()
        
        # 로그인 실행
        success = self.auth_manager.login()
        
        if success:
            # 로그인 성공 시 세션 상태 초기화
            self._reset_session_state()
            DisplayUtils.print_info("학습 세션을 시작하려면 'start <챕터> <섹션>' 명령어를 사용하세요.")
            DisplayUtils.print_info("예: start 1 1")
    
    def handle_logout(self, args: List[str]):
        """로그아웃 명령어 처리"""
        if not self.auth_manager.is_logged_in:
            DisplayUtils.print_warning("로그인 상태가 아닙니다.")
            return
        
        if self.current_session_state["active"]:
            if not DisplayUtils.confirm_action("진행 중인 세션이 있습니다. 정말 로그아웃하시겠습니까?"):
                return
        
        success = self.auth_manager.logout()
        if success:
            self._reset_session_state()
    
    def handle_auth_status(self, args: List[str]):
        """인증 상태 확인 명령어"""
        self.auth_manager.print_auth_status()
    
    # === 학습 세션 관련 명령어 ===
    
    def handle_start_session(self, args: List[str]):
        """학습 세션 시작 명령어"""
        if not self.auth_manager.require_login():
            return
        
        # 인수 확인
        if len(args) < 2:
            DisplayUtils.print_error("사용법: start <챕터> <섹션> [메시지]")
            DisplayUtils.print_info("예: start 1 1")
            DisplayUtils.print_info("예: start 2 3 \"2챕터 3섹션 시작할게요\"")
            return
        
        try:
            chapter = int(args[0])
            section = int(args[1])
            user_message = " ".join(args[2:]) if len(args) > 2 else None
        except ValueError:
            DisplayUtils.print_error("챕터와 섹션은 숫자여야 합니다.")
            return
        
        # 유효성 검사
        if chapter < 1 or chapter > 8:
            DisplayUtils.print_error("챕터는 1-8 사이의 숫자여야 합니다.")
            return
        
        if section < 1:
            DisplayUtils.print_error("섹션은 1 이상의 숫자여야 합니다.")
            return
        
        # 진행 중인 세션 확인
        if self.current_session_state["active"]:
            if not DisplayUtils.confirm_action("진행 중인 세션이 있습니다. 새 세션을 시작하시겠습니까?"):
                return
        
        # 세션 시작 요청
        DisplayUtils.print_loading("세션 시작 중...")
        success, response = self.api_client.start_session(chapter, section, user_message)
        DisplayUtils.clear_loading()
        
        if success:
            DisplayUtils.print_success(f"{chapter}챕터 {section}섹션 세션이 시작되었습니다!")
            DisplayUtils.print_json_response(response, "세션 시작 응답")
            
            # 세션 상태 업데이트
            self._update_session_state_from_response(response, chapter, section)
            self._print_next_action_guide()
        else:
            DisplayUtils.print_api_error(response, "세션 시작")
    
    def handle_send_message(self, args: List[str]):
        """메시지 전송 명령어"""
        if not self.auth_manager.require_login():
            return
        
        if not self.current_session_state["active"]:
            DisplayUtils.print_error("활성 세션이 없습니다. 'start <챕터> <섹션>' 명령어로 세션을 시작하세요.")
            return
        
        if not args:
            DisplayUtils.print_error("사용법: msg <메시지 내용>")
            DisplayUtils.print_info("예: msg \"다음 단계로 가주세요\"")
            DisplayUtils.print_info("예: msg \"AI와 머신러닝의 차이가 뭐예요?\"")
            return
        
        message = " ".join(args)
        
        # 메시지 전송
        DisplayUtils.print_loading("메시지 전송 중...")
        success, response = self.api_client.send_message(message)
        DisplayUtils.clear_loading()
        
        if success:
            DisplayUtils.print_success("메시지가 처리되었습니다!")
            DisplayUtils.print_json_response(response, "메시지 응답")
            
            # 세션 상태 업데이트
            self._update_session_state_from_response(response)
            self._print_next_action_guide()
        else:
            DisplayUtils.print_api_error(response, "메시지 전송")
    
    def handle_quiz_answer(self, args: List[str]):
        """퀴즈 답변 제출 명령어"""
        if not self.auth_manager.require_login():
            return
        
        if not self.current_session_state["active"]:
            DisplayUtils.print_error("활성 세션이 없습니다.")
            return
        
        if not args:
            DisplayUtils.print_error("사용법: quiz <답변>")
            DisplayUtils.print_info("객관식 예: quiz 2")
            DisplayUtils.print_info("주관식 예: quiz \"대규모 언어 모델입니다\"")
            return
        
        answer = " ".join(args)
        
        # 퀴즈 답변 제출
        DisplayUtils.print_loading("답변 제출 중...")
        success, response = self.api_client.submit_quiz_answer(answer)
        DisplayUtils.clear_loading()
        
        if success:
            DisplayUtils.print_success("답변이 제출되고 평가되었습니다!")
            DisplayUtils.print_json_response(response, "퀴즈 평가 응답")
            
            # 세션 상태 업데이트
            self._update_session_state_from_response(response)
            self._print_next_action_guide()
        else:
            DisplayUtils.print_api_error(response, "퀴즈 답변 제출")
    
    def handle_complete_session(self, args: List[str]):
        """세션 완료 명령어"""
        if not self.auth_manager.require_login():
            return
        
        if not self.current_session_state["active"]:
            DisplayUtils.print_error("활성 세션이 없습니다.")
            return
        
        if not args or args[0].lower() not in ["proceed", "retry"]:
            DisplayUtils.print_error("사용법: complete <proceed|retry>")
            DisplayUtils.print_info("proceed: 다음 섹션으로 진행")
            DisplayUtils.print_info("retry: 현재 섹션 재학습")
            return
        
        decision = args[0].lower()
        
        # 확인 메시지
        action_msg = "다음 섹션으로 진행" if decision == "proceed" else "현재 섹션 재학습"
        if not DisplayUtils.confirm_action(f"정말 {action_msg}하시겠습니까?"):
            return
        
        # 세션 완료 요청
        DisplayUtils.print_loading("세션 완료 처리 중...")
        success, response = self.api_client.complete_session(decision)
        DisplayUtils.clear_loading()
        
        if success:
            DisplayUtils.print_success("세션이 완료되었습니다!")
            DisplayUtils.print_json_response(response, "세션 완료 응답")
            
            # 세션 상태 업데이트
            self._update_session_state_from_response(response)
            
            # 다음 세션 안내
            if decision == "proceed":
                DisplayUtils.print_info("다음 세션을 시작하려면 적절한 챕터/섹션으로 'start' 명령어를 사용하세요.")
            else:
                DisplayUtils.print_info("재학습을 위해 동일한 챕터/섹션으로 'start' 명령어를 사용하세요.")
        else:
            DisplayUtils.print_api_error(response, "세션 완료")
    
    # === 상태 확인 명령어 ===
    
    def handle_show_state(self, args: List[str]):
        """TutorState 조회 명령어"""
        if not self.auth_manager.require_login():
            return
        
        if not self.cached_tutor_state:
            DisplayUtils.print_warning("캐시된 State가 없습니다.")
            DisplayUtils.print_info("학습 세션을 시작하거나 명령어를 실행한 후 다시 시도하세요.")
            return
        
        # State 정보 출력
        DisplayUtils.print_state_info(self.cached_tutor_state)
    
    def handle_session_status(self, args: List[str]):
        """현재 세션 상태 출력"""
        DisplayUtils.print_separator()
        DisplayUtils.print_colored("📚 현재 세션 상태", "bold")
        DisplayUtils.print_separator("-", 60)
        
        if self.current_session_state["active"]:
            DisplayUtils.print_success("세션 활성화됨")
            DisplayUtils.print_info(f"챕터/섹션: {self.current_session_state['chapter']}/{self.current_session_state['section']}")
            DisplayUtils.print_info(f"진행 단계: {self.current_session_state['stage']}")
            DisplayUtils.print_info(f"UI 모드: {self.current_session_state['ui_mode']}")
            DisplayUtils.print_info(f"현재 에이전트: {self.current_session_state['current_agent']}")
        else:
            DisplayUtils.print_warning("활성 세션 없음")
            DisplayUtils.print_info("'start <챕터> <섹션>' 명령어로 세션을 시작하세요.")
        
        DisplayUtils.print_separator()
    
    def handle_reset_session(self, args: List[str]):
        """세션 상태 초기화"""
        if self.current_session_state["active"]:
            if not DisplayUtils.confirm_action("진행 중인 세션을 초기화하시겠습니까?"):
                return
        
        self._reset_session_state()
        DisplayUtils.print_success("세션 상태가 초기화되었습니다.")
    
    # === 시스템 명령어 ===
    
    def handle_health_check(self, args: List[str]):
        """서버 상태 확인"""
        DisplayUtils.print_loading("서버 상태 확인 중...")
        success, response = self.api_client.check_health()
        DisplayUtils.clear_loading()
        
        if success:
            DisplayUtils.print_success("서버가 정상 동작 중입니다!")
            DisplayUtils.print_json_response(response, "서버 상태")
        else:
            DisplayUtils.print_error("서버 상태 확인 실패")
            DisplayUtils.print_api_error(response, "Health Check")
    
    def handle_version_check(self, args: List[str]):
        """서버 버전 확인"""
        DisplayUtils.print_loading("버전 정보 확인 중...")
        success, response = self.api_client.get_version()
        DisplayUtils.clear_loading()
        
        if success:
            DisplayUtils.print_success("버전 정보를 가져왔습니다!")
            DisplayUtils.print_json_response(response, "버전 정보")
        else:
            DisplayUtils.print_error("버전 정보 확인 실패")
            DisplayUtils.print_api_error(response, "Version Check")
    
    def handle_help(self, args: List[str]):
        """도움말 출력"""
        DisplayUtils.print_help()
    
    def handle_clear_screen(self, args: List[str]):
        """화면 지우기"""
        DisplayUtils.clear_screen()
        DisplayUtils.print_colored("🤖 AI 튜터 터미널 테스터", "cyan")
        
        if self.auth_manager.is_logged_in:
            user_name = self.auth_manager.user_info.get('username', 'Unknown')
            DisplayUtils.print_info(f"현재 사용자: {user_name}")
    
    # === 내부 헬퍼 메서드 ===
    
    def _update_session_state_from_response(self, response: Dict[str, Any], chapter: int = None, section: int = None):
        """API 응답에서 세션 상태 업데이트"""
        try:
            data = response.get('data', {})
            
            # 세션 정보 업데이트
            if chapter and section:
                self.current_session_state["chapter"] = chapter
                self.current_session_state["section"] = section
                self.current_session_state["active"] = True
            
            # workflow_response에서 상태 정보 추출
            workflow_response = data.get('workflow_response', {})
            if workflow_response:
                self.current_session_state["current_agent"] = workflow_response.get('current_agent')
                self.current_session_state["stage"] = workflow_response.get('session_progress_stage')
                self.current_session_state["ui_mode"] = workflow_response.get('ui_mode')
            
            # 세션 완료 처리
            session_completion = workflow_response.get('session_completion')
            if session_completion:
                # 세션이 완료되면 비활성화
                self.current_session_state["active"] = False
                # 다음 섹션 정보가 있으면 업데이트
                next_chapter = session_completion.get('next_chapter')
                next_section = session_completion.get('next_section')
                if next_chapter and next_section:
                    DisplayUtils.print_info(f"다음 세션: {next_chapter}챕터 {next_section}섹션")
            
            # TutorState 캐시 업데이트 (실제로는 서버에서 받지 않지만 시뮬레이션)
            self._simulate_tutor_state_cache(workflow_response)
            
        except Exception as e:
            DisplayUtils.print_warning(f"세션 상태 업데이트 중 오류: {str(e)}")
    
    def _simulate_tutor_state_cache(self, workflow_response: Dict[str, Any]):
        """TutorState 캐시 시뮬레이션 (실제 State는 서버에만 있음)"""
        if not workflow_response:
            return
        
        # 기본 State 구조 생성
        simulated_state = {
            "user_id": self.auth_manager.user_info.get('user_id'),
            "user_type": self.auth_manager.user_info.get('user_type', 'beginner'),
            "current_chapter": self.current_session_state.get('chapter'),
            "current_section": self.current_session_state.get('section'),
            "current_agent": workflow_response.get('current_agent'),
            "session_progress_stage": workflow_response.get('session_progress_stage'),
            "ui_mode": workflow_response.get('ui_mode'),
            "user_intent": "unknown",  # 클라이언트에서는 알 수 없음
            "quiz_type": "unknown",
            "quiz_content": "",
            "user_answer": "",
            "current_session_conversations": [],
            "session_start_time": None
        }
        
        # 컨텐츠 정보 추가
        content = workflow_response.get('content', {})
        if content.get('type') == 'quiz':
            simulated_state.update({
                "quiz_type": content.get('quiz_type', 'multiple_choice'),
                "quiz_content": content.get('question', ''),
                "quiz_options": content.get('options', []),
                "quiz_hint": content.get('hint', '')
            })
        
        self.cached_tutor_state = simulated_state
    
    def _reset_session_state(self):
        """세션 상태 초기화"""
        self.current_session_state = {
            "active": False,
            "chapter": None,
            "section": None,
            "stage": None,
            "ui_mode": None,
            "current_agent": None
        }
        self.cached_tutor_state = None
    
    def _print_next_action_guide(self):
        """다음 액션 가이드 출력"""
        if not self.current_session_state["active"]:
            return
        
        stage = self.current_session_state.get("stage")
        ui_mode = self.current_session_state.get("ui_mode")
        
        DisplayUtils.print_separator("-", 40)
        DisplayUtils.print_colored("💡 다음 액션 가이드:", "yellow")
        
        if stage == "theory_completed":
            if ui_mode == "quiz":
                DisplayUtils.print_info("퀴즈가 준비되었습니다. 'quiz <답변>' 명령어로 답변하세요.")
                DisplayUtils.print_info("예: quiz 2  (객관식)")
                DisplayUtils.print_info("예: quiz \"답변 내용\"  (주관식)")
            else:
                DisplayUtils.print_info("'msg \"다음 단계로 가주세요\"' 로 퀴즈를 요청하거나")
                DisplayUtils.print_info("'msg \"질문 내용\"' 으로 궁금한 점을 물어보세요.")
        
        elif stage == "quiz_and_feedback_completed":
            DisplayUtils.print_info("'complete proceed' - 다음 섹션으로 진행")
            DisplayUtils.print_info("'complete retry' - 현재 섹션 재학습")
            DisplayUtils.print_info("'msg \"질문 내용\"' - 추가 질문")
        
        elif stage == "session_start":
            DisplayUtils.print_info("'msg \"다음 단계로 가주세요\"' 로 학습을 진행하세요.")
        
        DisplayUtils.print_separator("-", 40)
    
    def get_available_commands(self) -> List[str]:
        """사용 가능한 명령어 목록 반환"""
        return list(self.commands.keys()) + ["quit", "exit", "q"]


# 편의를 위한 전역 함수
def create_command_handler(api_client, auth_manager) -> CommandHandler:
    """명령어 핸들러 생성"""
    return CommandHandler(api_client, auth_manager)