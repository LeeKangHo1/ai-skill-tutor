# backend/tests/terminal_tester_by_claude/main.py
# AI 튜터 터미널 테스터 메인 실행 파일

import sys
import os
import signal
from typing import Optional

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from config import config
from display_utils import DisplayUtils
from api_client import APIClient
from auth_manager import AuthManager
from command_handler import CommandHandler


class TerminalTester:
    """AI 튜터 터미널 테스터 메인 클래스"""
    
    def __init__(self):
        """터미널 테스터 초기화"""
        self.running = False
        self.api_client = None
        self.auth_manager = None
        self.command_handler = None
        
        # 시그널 핸들러 등록 (Ctrl+C 처리)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러 (Ctrl+C 등)"""
        print(f"\n{config.MESSAGES['goodbye']}")
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """정리 작업"""
        try:
            if self.auth_manager and self.auth_manager.is_logged_in:
                DisplayUtils.print_info("로그아웃 처리 중...")
                self.auth_manager.logout()
        except Exception:
            pass  # 정리 중 오류는 무시
    
    def initialize(self) -> bool:
        """
        컴포넌트 초기화
        
        Returns:
            bool: 초기화 성공 여부
        """
        try:
            DisplayUtils.print_info("🔧 시스템 초기화 중...")
            
            # 1. 인증 관리자 초기화
            self.auth_manager = AuthManager()
            DisplayUtils.print_info("✅ 인증 관리자 초기화 완료")
            
            # 2. API 클라이언트 초기화
            self.api_client = APIClient()
            DisplayUtils.print_info("✅ API 클라이언트 초기화 완료")
            
            # 3. 상호 참조 설정 (순환 참조 방지)
            self.api_client.set_auth_manager(self.auth_manager)
            self.auth_manager.set_api_client(self.api_client)
            DisplayUtils.print_info("✅ 컴포넌트 연결 완료")
            
            # 4. 명령어 핸들러 초기화
            self.command_handler = CommandHandler(self.api_client, self.auth_manager)
            DisplayUtils.print_info("✅ 명령어 핸들러 초기화 완료")
            
            DisplayUtils.print_success("🎉 시스템 초기화 완료!")
            return True
            
        except Exception as e:
            DisplayUtils.print_error(f"초기화 실패: {str(e)}")
            return False
    
    def check_server_connection(self) -> bool:
        """
        서버 연결 상태 확인
        
        Returns:
            bool: 연결 성공 여부
        """
        DisplayUtils.print_info("🌐 서버 연결 확인 중...")
        
        try:
            success, response = self.api_client.check_health()
            
            if success:
                DisplayUtils.print_success("✅ 서버 연결 성공!")
                
                # 서버 정보 출력
                data = response.get('data', {})
                if 'status' in data:
                    DisplayUtils.print_info(f"서버 상태: {data['status']}")
                
                return True
            else:
                DisplayUtils.print_error("❌ 서버 연결 실패")
                DisplayUtils.print_api_error(response, "Health Check")
                
                # 연결 실패 시 도움말 제공
                DisplayUtils.print_separator("-", 60)
                DisplayUtils.print_warning("서버 연결 문제 해결 방법:")
                DisplayUtils.print_info("1. 백엔드 서버가 실행 중인지 확인하세요")
                DisplayUtils.print_info("2. 서버 주소가 올바른지 확인하세요 (현재: http://localhost:5000)")
                DisplayUtils.print_info("3. 방화벽이나 네트워크 설정을 확인하세요")
                DisplayUtils.print_separator("-", 60)
                
                return False
                
        except Exception as e:
            DisplayUtils.print_error(f"연결 확인 중 오류: {str(e)}")
            return False
    
    def run(self):
        """메인 실행 루프"""
        try:
            # 환영 메시지 출력
            DisplayUtils.clear_screen()
            DisplayUtils.print_welcome()
            
            # 시스템 초기화
            if not self.initialize():
                DisplayUtils.print_error("시스템 초기화에 실패했습니다.")
                return
            
            # 서버 연결 확인
            if not self.check_server_connection():
                if not DisplayUtils.confirm_action("서버 연결에 실패했습니다. 계속 진행하시겠습니까?"):
                    return
            
            DisplayUtils.print_separator()
            DisplayUtils.print_info("터미널 테스터가 준비되었습니다!")
            DisplayUtils.print_info("'help' 명령어로 사용법을 확인하거나 'login' 명령어로 시작하세요.")
            DisplayUtils.print_separator()
            
            # 메인 루프 시작
            self.running = True
            self._main_loop()
            
        except KeyboardInterrupt:
            print(f"\n{config.MESSAGES['goodbye']}")
        except Exception as e:
            DisplayUtils.print_error(f"실행 중 오류 발생: {str(e)}")
        finally:
            self._cleanup()
    
    def _main_loop(self):
        """메인 명령어 처리 루프"""
        while self.running:
            try:
                # 사용자 입력 받기
                user_input = DisplayUtils.get_user_input()
                
                # 빈 입력 처리
                if not user_input:
                    continue
                
                # 명령어 처리
                should_continue = self.command_handler.process_command(user_input)
                
                if not should_continue:
                    self.running = False
                    break
                
            except KeyboardInterrupt:
                # Ctrl+C 처리
                self.running = False
                break
            except EOFError:
                # EOF 처리 (Ctrl+D)
                self.running = False
                break
            except Exception as e:
                DisplayUtils.print_error(f"명령어 처리 중 오류: {str(e)}")
                DisplayUtils.print_info("계속 진행하려면 아무 키나 누르세요.")
        
        print(f"\n{config.MESSAGES['goodbye']}")
    
    def run_interactive_setup(self):
        """대화형 초기 설정"""
        DisplayUtils.print_separator()
        DisplayUtils.print_colored("🚀 초기 설정", "bold")
        DisplayUtils.print_separator("-", 60)
        
        # 자동 로그인 옵션
        if DisplayUtils.confirm_action("바로 로그인하시겠습니까?"):
            if self.auth_manager.login():
                DisplayUtils.print_success("로그인이 완료되었습니다!")
                
                # 테스트 세션 시작 옵션
                if DisplayUtils.confirm_action("테스트 세션을 시작하시겠습니까? (1챕터 1섹션)"):
                    self.command_handler.handle_start_session(["1", "1", "테스트 세션 시작"])
        
        DisplayUtils.print_separator()


def print_usage():
    """사용법 출력"""
    print("""
🤖 AI 튜터 터미널 테스터 사용법

실행 방법:
    python main.py              # 일반 실행
    python main.py --setup      # 대화형 설정과 함께 실행
    python main.py --help       # 도움말 출력

기본 명령어:
    login                       # 로그인
    start <챕터> <섹션>         # 학습 세션 시작
    msg "<메시지>"              # 메시지 전송
    quiz "<답변>"               # 퀴즈 답변
    complete <proceed|retry>    # 세션 완료
    help                        # 전체 명령어 도움말
    quit                        # 종료

예시 워크플로우:
    1. login
    2. start 1 1
    3. msg "다음 단계로 가주세요"
    4. quiz "2"
    5. complete proceed

필요 사항:
    - Python 3.7 이상
    - requests 라이브러리
    - 백엔드 서버 실행 (http://localhost:5000)

문제 해결:
    - 연결 오류: 백엔드 서버 실행 상태 확인
    - 토큰 오류: logout 후 다시 login
    - 세션 오류: reset 명령어로 세션 초기화
    """)


def main():
    """메인 함수"""
    # 명령줄 인수 처리
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h', 'help']:
            print_usage()
            return
        elif arg == '--version':
            print("AI 튜터 터미널 테스터 v1.0")
            print(f"Python {sys.version}")
            return
        elif arg not in ['--setup']:
            print(f"알 수 없는 인수: {arg}")
            print("--help를 사용하여 도움말을 확인하세요.")
            return
    
    # 의존성 확인
    try:
        import requests
        import jwt
    except ImportError as e:
        print(f"❌ 필수 라이브러리가 설치되지 않았습니다: {e}")
        print("다음 명령어로 설치하세요:")
        print("pip install requests PyJWT")
        return
    
    # 터미널 테스터 실행
    tester = TerminalTester()
    
    # 대화형 설정 모드
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        tester.run_interactive_setup()
    
    # 메인 실행
    tester.run()


if __name__ == "__main__":
    main()