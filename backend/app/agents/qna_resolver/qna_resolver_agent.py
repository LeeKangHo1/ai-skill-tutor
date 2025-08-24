# backend/app/agents/qna_resolver/qna_resolver_agent.py

from typing import Dict, Any, List
import json
import os

from app.core.langraph.state_manager import TutorState, state_manager


class QnAResolverAgent:
    """
    QnA 답변 에이전트 v2.0 - 벡터 DB 기반 RAG 시스템
    - 사용자 질문을 분석하여 벡터 검색 기반 답변 생성
    - 이론 생성 에이전트의 워크플로우 패턴을 참고하여 구현
    - 순수 답변 대본만 생성 (사용자 대면 메시지 없음)
    """
    
    def __init__(self):
        self.agent_name = "qna_resolver"
        # 현재 파일 기준으로 backend/data/chapters 경로 설정
        current_dir = os.path.dirname(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        self.chapter_data_path = os.path.join(backend_dir, "data", "chapters")
    
    def process(self, state: TutorState) -> TutorState:
        """
        벡터 DB 기반 QnA 답변 생성 메인 프로세스
        
        Args:
            state: 현재 TutorState
            
        Returns:
            업데이트된 TutorState (qna_draft 포함)
        """
        try:
            print(f"[{self.agent_name}] 벡터 DB 기반 QnA 답변 생성 시작")
            
            # 1. 사용자 질문 추출
            user_question = self._extract_user_question(state)
            if not user_question:
                print(f"[{self.agent_name}] 사용자 질문을 찾을 수 없음")
                # 기본 안내 메시지 생성
                qna_response = self._create_default_guide_message()
                # 질문이 없을 때의 로그 메시지
                log_message = "QnA 답변 생성 완료 - 기본 안내 메시지 제공"
            else:
                print(f"[{self.agent_name}] 사용자 질문 추출 완료: {user_question[:100]}...")
                
                # 2. QnA 답변 생성 (벡터 검색 기반)
                qna_response = self._generate_qna_response(user_question)
                # 질문이 있을 때의 로그 메시지
                log_message = f"QnA 답변 생성 완료 - 질문: {user_question[:50]}{'...' if len(user_question) > 50 else ''}"
            
            # 3. State 업데이트 - 이론 생성 에이전트와 동일한 패턴 적용
            # 3-1. 에이전트 draft 업데이트 (qna_draft에 답변 저장)
            updated_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                qna_response
            )
            
            # 3-2. 현재 에이전트 전환 설정
            updated_state = state_manager.update_agent_transition(
                updated_state,
                self.agent_name
            )
            
            # 3-3. 대화 기록 추가 (시스템 메시지로 처리 완료 기록)
            updated_state = state_manager.add_conversation(
                updated_state,
                agent_name=self.agent_name,
                message=log_message,
                message_type="system"
            )
            
            print(f"[{self.agent_name}] QnA 답변 생성 완료")
            return updated_state
            
        except Exception as e:
            print(f"[{self.agent_name}] 오류 발생: {str(e)}")
            # 오류 시에도 State는 반환 (오류 메시지 대본으로) - 이론 생성 에이전트와 동일한 패턴
            # 오류 시 State 업데이트 순서
            # 1. 에이전트 draft 업데이트 (오류 메시지 대본)
            error_state = state_manager.update_agent_draft(
                state, 
                self.agent_name, 
                self._create_error_response(str(e))
            )
            # 2. 현재 에이전트 전환 설정
            error_state = state_manager.update_agent_transition(
                error_state,
                self.agent_name
            )
            # 3. 오류 대화 기록 추가 (선택사항이지만 일관성을 위해 추가)
            error_state = state_manager.add_conversation(
                error_state,
                agent_name=self.agent_name,
                message=f"QnA 답변 생성 중 오류 발생: {str(e)}",
                message_type="system"
            )
            return error_state
    
    def _extract_user_question(self, state: TutorState) -> str:
        """
        State의 current_session_conversations에서 최근 사용자 질문 추출
        
        Args:
            state: 현재 TutorState
            
        Returns:
            사용자 질문 텍스트 (없으면 빈 문자열)
        """
        try:
            conversations = state.get("current_session_conversations", [])
            
            if not conversations:
                print(f"[{self.agent_name}] 대화 기록이 없음")
                return ""
            
            print(f"[{self.agent_name}] 총 {len(conversations)}개의 대화 기록 확인 중...")
            
            # 가장 최근 사용자 메시지부터 역순으로 검색
            user_messages_found = 0
            for i, conv in enumerate(reversed(conversations)):
                message_type = conv.get("message_type", "")
                agent_name = conv.get("agent_name", "")
                message = conv.get("message", "").strip()
                
                print(f"[{self.agent_name}] 대화 {len(conversations)-i}: type={message_type}, agent={agent_name}, message_length={len(message)}")
                
                # 사용자 메시지 타입 필터링
                if message_type == "user":
                    user_messages_found += 1
                    
                    # 메시지 유효성 검증
                    if self._is_valid_user_question(message):
                        print(f"[{self.agent_name}] 유효한 사용자 질문 발견: {message[:100]}...")
                        return message
                    else:
                        print(f"[{self.agent_name}] 유효하지 않은 사용자 메시지 (너무 짧거나 의미 없음): {message[:50]}...")
                        continue
                
                # 최대 5개의 사용자 메시지까지만 확인 (성능 최적화)
                if user_messages_found >= 5:
                    break
            
            print(f"[{self.agent_name}] 총 {user_messages_found}개의 사용자 메시지를 확인했지만 유효한 질문을 찾을 수 없음")
            return ""
            
        except Exception as e:
            print(f"[{self.agent_name}] 질문 추출 중 오류 발생: {str(e)}")
            return ""
    
    def _is_valid_user_question(self, message: str) -> bool:
        """
        사용자 메시지가 유효한 질문인지 검증
        
        Args:
            message: 사용자 메시지
            
        Returns:
            유효한 질문 여부
        """
        if not message or len(message.strip()) < 3:
            return False
        
        # 너무 짧은 메시지 필터링
        if len(message.strip()) < 5:
            return False
        
        # 단순한 인사말이나 의미 없는 메시지 필터링
        simple_greetings = [
            "안녕", "hi", "hello", "ㅎㅇ", "ㅎㅣ", "하이", "헬로",
            "네", "예", "아니오", "아니", "no", "yes", "ok", "okay", "ㅇㅋ",
            "ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "ㅜㅜ", ".", "..", "...", "?", "??", "???"
        ]
        
        message_lower = message.lower().strip()
        if message_lower in simple_greetings:
            return False
        
        # 숫자만 있는 메시지 (퀴즈 답변일 가능성) 필터링
        if message.strip().isdigit():
            return False
        
        # 단일 문자나 기호만 있는 메시지 필터링
        if len(message.strip()) == 1:
            return False
        
        return True
    
    def _generate_qna_response(self, user_question: str) -> str:
        """
        사용자 질문에 대한 답변 생성 (벡터 검색 기반 - Function Calling 방식)
        
        Args:
            user_question: 사용자 질문
            
        Returns:
            생성된 답변 텍스트
        """
        try:
            print(f"[{self.agent_name}] Function Calling 기반 답변 생성 시작")
            
            # qna_tools_chatgpt.py의 Function Calling 방식 사용
            from app.tools.content.qna_tools_chatgpt import qna_generation_tool
            
            # 현재 학습 컨텍스트 준비 (State에서 추출)
            current_context = {
                "chapter": None,  # 현재 State에서 추출하지 않음 (QnA는 범용적)
                "section": None,
                "theory_draft": None  # 필요시 추후 추가
            }
            
            # Function Calling 방식으로 답변 생성
            qna_response = qna_generation_tool(user_question, current_context)
            
            print(f"[{self.agent_name}] Function Calling 기반 답변 생성 완료")
            return qna_response
            
        except Exception as e:
            print(f"[{self.agent_name}] 답변 생성 실패: {str(e)}")
            return self._create_error_response(str(e))
    
    def _create_default_guide_message(self) -> str:
        """
        질문이 없을 때 기본 안내 메시지 생성
        
        Returns:
            기본 안내 메시지
        """
        return """안녕하세요! 무엇이 궁금하신가요?

다음과 같은 질문을 도와드릴 수 있습니다:

📚 **학습 내용 관련 질문**
- "방금 배운 내용을 다시 설명해주세요"
- "이 개념을 실제로 어떻게 활용하나요?"
- "더 자세한 예시를 알려주세요"

💡 **일반적인 궁금증**
- AI와 관련된 모든 질문에 답변해드립니다!

구체적인 질문을 해주시면 더 정확하고 유용한 답변을 드릴 수 있습니다."""
    
    def _create_error_response(self, error_message: str) -> str:
        """
        오류 발생 시 기본 대본 생성 (순수 대본)
        
        Args:
            error_message: 오류 메시지
            
        Returns:
            오류 대본 텍스트
        """
        return f"""답변을 생성하는 중 문제가 발생했습니다.

오류: {error_message}

죄송합니다. 잠시 후 다시 질문해주세요."""