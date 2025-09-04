# backend/tests/terminal_tester_by_claude/display_utils.py
# 터미널 출력 및 포맷팅 유틸리티

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from config import config


class DisplayUtils:
    """터미널 출력 관련 유틸리티 클래스"""
    
    @staticmethod
    def clear_screen():
        """화면 지우기"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_welcome():
        """환영 메시지 출력"""
        print(config.colorize(config.MESSAGES["welcome"], "cyan"))
    
    @staticmethod
    def print_colored(text: str, color: str = "white", end: str = "\n"):
        """컬러 텍스트 출력"""
        print(config.colorize(text, color), end=end)
    
    @staticmethod
    def print_success(message: str):
        """성공 메시지 출력"""
        print(config.colorize(f"✅ {message}", "green"))
    
    @staticmethod
    def print_error(message: str):
        """에러 메시지 출력"""
        print(config.colorize(f"❌ {message}", "red"))
    
    @staticmethod
    def print_warning(message: str):
        """경고 메시지 출력"""
        print(config.colorize(f"⚠️ {message}", "yellow"))
    
    @staticmethod
    def print_info(message: str):
        """정보 메시지 출력"""
        print(config.colorize(f"ℹ️ {message}", "blue"))
    
    @staticmethod
    def print_separator(char: str = "=", length: int = 60):
        """구분선 출력"""
        print(config.colorize(char * length, "purple"))
    
    @staticmethod
    def print_json_response(response_data: Dict[str, Any], title: str = "API 응답"):
        """JSON 응답 데이터 예쁘게 출력"""
        try:
            # 제목 출력
            DisplayUtils.print_separator()
            DisplayUtils.print_colored(f"📡 {title}", "bold")
            DisplayUtils.print_separator("-", 60)
            
            # JSON 포맷팅
            json_str = json.dumps(response_data, ensure_ascii=False, indent=config.JSON_INDENT)
            
            # 길이 제한 체크
            if len(json_str) > config.MAX_DISPLAY_LENGTH:
                DisplayUtils.print_warning(f"응답이 너무 깁니다 ({len(json_str)}자). 일부만 표시합니다.")
                json_str = json_str[:config.MAX_DISPLAY_LENGTH] + "\n... (생략됨)"
            
            # JSON 출력
            print(json_str)
            DisplayUtils.print_separator()
            
        except Exception as e:
            DisplayUtils.print_error(f"JSON 출력 중 오류: {str(e)}")
            print(f"Raw 데이터: {response_data}")
    
    @staticmethod
    def print_api_error(error_response: Dict[str, Any], endpoint: str = ""):
        """API 에러 응답 상세 출력"""
        try:
            DisplayUtils.print_separator()
            DisplayUtils.print_error(f"API 호출 실패: {endpoint}")
            DisplayUtils.print_separator("-", 60)
            
            # HTTP 상태 코드 출력
            if "status_code" in error_response:
                DisplayUtils.print_colored(f"Status Code: {error_response['status_code']}", "red")
            
            # 에러 세부 정보 출력
            if "error" in error_response:
                error_info = error_response["error"]
                if isinstance(error_info, dict):
                    if "code" in error_info:
                        DisplayUtils.print_colored(f"Error Code: {error_info['code']}", "yellow")
                    if "message" in error_info:
                        DisplayUtils.print_colored(f"Error Message: {error_info['message']}", "red")
                    if "details" in error_info:
                        DisplayUtils.print_colored("Error Details:", "yellow")
                        print(json.dumps(error_info["details"], ensure_ascii=False, indent=2))
                else:
                    DisplayUtils.print_colored(f"Error: {error_info}", "red")
            
            # 전체 응답 출력
            DisplayUtils.print_colored("\n전체 응답 데이터:", "purple")
            print(json.dumps(error_response, ensure_ascii=False, indent=2))
            DisplayUtils.print_separator()
            
        except Exception as e:
            DisplayUtils.print_error(f"에러 출력 중 오류: {str(e)}")
            print(f"Raw 에러 데이터: {error_response}")
    
    @staticmethod
    def print_help():
        """명령어 도움말 출력"""
        DisplayUtils.print_separator()
        DisplayUtils.print_colored("📖 사용 가능한 명령어", "bold")
        DisplayUtils.print_separator("-", 60)
        
        for command, description in config.COMMANDS_HELP.items():
            DisplayUtils.print_colored(f"{command:12}", "cyan", end="")
            print(f" : {description}")
        
        DisplayUtils.print_separator("-", 60)
        DisplayUtils.print_info("학습 세션 진행 순서:")
        print(config.MESSAGES["session_flow"])
    
    @staticmethod
    def print_state_info(state_data: Dict[str, Any]):
        """TutorState 정보 보기 좋게 출력"""
        try:
            DisplayUtils.print_separator()
            DisplayUtils.print_colored("🧠 현재 TutorState 정보", "bold")
            DisplayUtils.print_separator("-", 60)
            
            # 기본 정보
            basic_info = {
                "사용자 ID": state_data.get("user_id", "N/A"),
                "사용자 타입": state_data.get("user_type", "N/A"),
                "현재 챕터": state_data.get("current_chapter", "N/A"),
                "현재 섹션": state_data.get("current_section", "N/A"),
                "현재 에이전트": state_data.get("current_agent", "N/A"),
                "세션 진행 단계": state_data.get("session_progress_stage", "N/A"),
                "UI 모드": state_data.get("ui_mode", "N/A"),
                "사용자 의도": state_data.get("user_intent", "N/A")
            }
            
            DisplayUtils.print_colored("📋 기본 정보:", "green")
            for key, value in basic_info.items():
                print(f"  {key}: {value}")
            
            # 퀴즈 정보
            if state_data.get("quiz_content"):
                DisplayUtils.print_colored("\n❓ 퀴즈 정보:", "yellow")
                quiz_info = {
                    "퀴즈 타입": state_data.get("quiz_type", "N/A"),
                    "문제": state_data.get("quiz_content", "N/A")[:100] + "..." if len(str(state_data.get("quiz_content", ""))) > 100 else state_data.get("quiz_content", "N/A"),
                    "사용자 답변": state_data.get("user_answer", "N/A"),
                    "힌트 사용 횟수": state_data.get("hint_usage_count", 0)
                }
                for key, value in quiz_info.items():
                    print(f"  {key}: {value}")
            
            # 에이전트 대본 정보
            drafts = {
                "Theory Draft": state_data.get("theory_draft", ""),
                "Quiz Draft": state_data.get("quiz_draft", ""),
                "Feedback Draft": state_data.get("feedback_draft", ""),
                "QnA Draft": state_data.get("qna_draft", "")
            }
            
            active_drafts = {k: v for k, v in drafts.items() if v}
            if active_drafts:
                DisplayUtils.print_colored("\n📝 활성 에이전트 대본:", "purple")
                for draft_name, content in active_drafts.items():
                    content_preview = content[:50] + "..." if len(content) > 50 else content
                    print(f"  {draft_name}: {content_preview}")
            
            # 대화 기록 수
            conversations = state_data.get("current_session_conversations", [])
            if conversations:
                DisplayUtils.print_colored(f"\n💬 현재 세션 대화 수: {len(conversations)}개", "blue")
            
            DisplayUtils.print_separator()
            
            # 전체 State 출력 옵션
            DisplayUtils.print_colored("전체 State 데이터를 보시겠습니까? (y/n): ", "cyan", end="")
            user_input = input().strip().lower()
            if user_input == 'y':
                DisplayUtils.print_json_response(state_data, "전체 TutorState")
                
        except Exception as e:
            DisplayUtils.print_error(f"State 정보 출력 중 오류: {str(e)}")
            DisplayUtils.print_json_response(state_data, "TutorState (Raw)")
    
    @staticmethod
    def print_login_prompt():
        """로그인 프롬프트 출력"""
        DisplayUtils.print_separator()
        DisplayUtils.print_colored("🔐 사용자 로그인", "bold")
        DisplayUtils.print_separator("-", 60)
    
    @staticmethod
    def print_timestamp():
        """현재 시간 출력"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        DisplayUtils.print_colored(f"⏰ {now}", "purple")
    
    @staticmethod
    def get_user_input(prompt: str = None) -> str:
        """사용자 입력 받기 (프롬프트 포함)"""
        if prompt is None:
            prompt = config.PROMPTS["main"]
        
        try:
            return input(config.colorize(prompt, "cyan")).strip()
        except KeyboardInterrupt:
            print(f"\n{config.MESSAGES['goodbye']}")
            sys.exit(0)
        except EOFError:
            print(f"\n{config.MESSAGES['goodbye']}")
            sys.exit(0)
    
    # display_utils.py의 get_password_input 함수 수정
    @staticmethod
    def get_password_input(prompt: str = None) -> str:
        """비밀번호 입력 받기"""
        if prompt is None:
            prompt = config.PROMPTS["password"]
        
        try:
            # getpass 대신 일반 input 사용 (보안이 떨어지지만 터미널 테스트용)
            DisplayUtils.print_warning("주의: 비밀번호가 화면에 표시됩니다 (테스트용)")
            return input(prompt)
        except KeyboardInterrupt:
            print(f"\n{config.MESSAGES['goodbye']}")
            sys.exit(0)
    
    @staticmethod
    def confirm_action(message: str) -> bool:
        """사용자 확인 입력 받기"""
        while True:
            DisplayUtils.print_colored(f"{message} (y/n): ", "yellow", end="")
            response = input().strip().lower()
            
            if response in ['y', 'yes', '예', 'ㅇ']:
                return True
            elif response in ['n', 'no', '아니오', 'ㄴ']:
                return False
            else:
                DisplayUtils.print_warning("y 또는 n을 입력해주세요.")
    
    @staticmethod
    def print_loading(message: str = "처리 중..."):
        """로딩 메시지 출력"""
        print(config.colorize(f"⏳ {message}", "yellow"), end="", flush=True)
    
    @staticmethod
    def clear_loading():
        """로딩 메시지 지우기"""
        print("\r" + " " * 50 + "\r", end="", flush=True)


# 편의를 위한 전역 함수들
def print_success(message: str):
    """성공 메시지 출력 (전역 함수)"""
    DisplayUtils.print_success(message)

def print_error(message: str):
    """에러 메시지 출력 (전역 함수)"""
    DisplayUtils.print_error(message)

def print_info(message: str):
    """정보 메시지 출력 (전역 함수)"""
    DisplayUtils.print_info(message)

def print_json(data: Dict[str, Any], title: str = "응답"):
    """JSON 출력 (전역 함수)"""
    DisplayUtils.print_json_response(data, title)