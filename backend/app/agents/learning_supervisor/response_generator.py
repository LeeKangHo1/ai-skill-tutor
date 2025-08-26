# backend/app/agents/learning_supervisor/response_generator.py
# v2.0 업데이트: workflow_response 구조, 하이브리드 UX 지원, 컨텐츠 타입 표준화

from typing import Dict, Any
from app.core.langraph.state_manager import TutorState, state_manager


class ResponseGenerator:
    """
    에이전트 대본을 사용자 친화적인 최종 응답으로 정제하는 클래스 (v2.0)
    
    주요 역할:
    1. 각 에이전트가 생성한 대본(draft) 추출
    2. 사용자 유형(beginner/advanced)에 맞는 톤 체크
    3. 응답 형식 정제 및 표준화
    4. UI 모드에 맞는 응답 구조화
    5. v2.0: workflow_response 구조 생성
    6. v2.0: 하이브리드 UX 지원 (chat/quiz 모드)
    7. v2.0: 컨텐츠 타입 표준화 (theory, quiz, feedback, qna)
    """
    
    def __init__(self):
        pass
    
    def generate_final_response(self, state: TutorState) -> TutorState:
        """
        최종 응답 생성 메인 함수 (v2.0 workflow_response 구조)
        
        Args:
            state: 에이전트 대본이 포함된 TutorState
            
        Returns:
            workflow_response가 포함된 TutorState
        """
        try:
            print(f"[DEBUG] ResponseGenerator.generate_final_response 호출됨")
            
            # 현재 활성 에이전트 확인
            current_agent = state.get("current_agent", "")
            print(f"[DEBUG] ResponseGenerator - current_agent: {current_agent}")
            
            # 에이전트별 workflow_response 생성
            if "theory_educator" in current_agent:
                return self._create_theory_workflow_response(state)
            elif "quiz_generator" in current_agent:
                return self._create_quiz_workflow_response(state)
            elif "evaluation_feedback" in current_agent:
                return self._create_feedback_workflow_response(state)
            elif "qna_resolver" in current_agent:
                return self._create_qna_workflow_response(state)
            elif "session_manager" in current_agent:
                return self._create_session_workflow_response(state)
            else:
                # 기본 처리: 모든 대본 확인해서 가장 최근 내용 처리
                return self._create_default_workflow_response(state)
                
        except Exception as e:
            print(f"ResponseGenerator 처리 중 오류: {e}")
            return self._create_error_workflow_response(state)
    
    def _process_theory_response(self, state: TutorState) -> TutorState:
        """
        이론 설명 응답 정제
        
        Args:
            state: TutorState
            
        Returns:
            정제된 응답이 포함된 TutorState
        """
        theory_draft = state.get("theory_draft", "")
        
        if not theory_draft:
            # 대본이 없으면 기본 응답
            final_response = self._generate_theory_fallback(state)
        else:
            # 이론 설명 대본 정제
            final_response = self._refine_theory_content(theory_draft, state)
        
        # 정제된 응답을 theory_draft에 다시 저장
        updated_state = state_manager.update_agent_draft(state, "theory_educator", final_response)
        
        return updated_state
    
    def _process_quiz_response(self, state: TutorState) -> TutorState:
        """
        퀴즈 문제 응답 정제
        
        Args:
            state: TutorState
            
        Returns:
            정제된 응답이 포함된 TutorState
        """
        quiz_draft = state.get("quiz_draft", "")
        
        if not quiz_draft:
            # 대본이 없으면 기본 응답
            final_response = self._generate_quiz_fallback(state)
        else:
            # 퀴즈 대본 정제
            final_response = self._refine_quiz_content(quiz_draft, state)
        
        # 정제된 응답을 quiz_draft에 다시 저장
        updated_state = state_manager.update_agent_draft(state, "quiz_generator", final_response)
        
        # 퀴즈 모드로 UI 전환
        updated_state = state_manager.update_ui_mode(updated_state, "quiz")
        
        return updated_state
    
    def _process_feedback_response(self, state: TutorState) -> TutorState:
        """
        평가 피드백 응답 정제
        
        Args:
            state: TutorState
            
        Returns:
            정제된 응답이 포함된 TutorState
        """
        feedback_draft = state.get("feedback_draft", "")
        
        if not feedback_draft:
            # 대본이 없으면 기본 응답
            final_response = self._generate_feedback_fallback(state)
        else:
            # 피드백 대본 정제
            final_response = self._refine_feedback_content(feedback_draft, state)
        
        # 정제된 응답을 feedback_draft에 다시 저장
        updated_state = state_manager.update_agent_draft(state, "evaluation_feedback_agent", final_response)
        
        # 채팅 모드로 UI 전환
        updated_state = state_manager.update_ui_mode(updated_state, "chat")
        
        return updated_state
    
    def _process_qna_response(self, state: TutorState) -> TutorState:
        """
        질문 답변 응답 정제
        
        Args:
            state: TutorState
            
        Returns:
            정제된 응답이 포함된 TutorState
        """
        qna_draft = state.get("qna_draft", "")
        
        if not qna_draft:
            # 대본이 없으면 기본 응답
            final_response = self._generate_qna_fallback(state)
        else:
            # QnA 대본 정제
            final_response = self._refine_qna_content(qna_draft, state)
        
        # 정제된 응답을 qna_draft에 다시 저장
        updated_state = state_manager.update_agent_draft(state, "qna_resolver", final_response)
        
        return updated_state
    
    def _process_session_response(self, state: TutorState) -> TutorState:
        """
        세션 완료 응답 정제
        
        Args:
            state: TutorState
            
        Returns:
            처리된 TutorState
        """
        # SessionManager는 이미 완료 메시지를 생성하므로 그대로 사용
        # 필요시 추가 정제 가능
        return state
    
    def _process_default_response(self, state: TutorState) -> TutorState:
        """
        기본 응답 처리 (에이전트가 명확하지 않은 경우)
        
        Args:
            state: TutorState
            
        Returns:
            처리된 TutorState
        """
        # 모든 대본을 확인해서 내용이 있는 것 찾기
        drafts = [
            ("theory_educator", state.get("theory_draft", "")),
            ("quiz_generator", state.get("quiz_draft", "")),
            ("evaluation_feedback_agent", state.get("feedback_draft", "")),
            ("qna_resolver", state.get("qna_draft", ""))
        ]
        
        for agent_name, draft_content in drafts:
            if draft_content and draft_content.strip():
                # 내용이 있는 첫 번째 대본 처리
                if "theory" in agent_name:
                    return self._process_theory_response(state)
                elif "quiz" in agent_name:
                    return self._process_quiz_response(state)
                elif "feedback" in agent_name:
                    return self._process_feedback_response(state)
                elif "qna" in agent_name:
                    return self._process_qna_response(state)
        
        # 모든 대본이 비어있으면 기본 메시지
        return self._generate_error_response(state)
    
    def _refine_theory_content(self, theory_draft: str, state: TutorState) -> str:
        """
        이론 설명 내용 정제
        
        Args:
            theory_draft: 원본 이론 설명 대본
            state: TutorState
            
        Returns:
            정제된 이론 설명
        """
        user_type = state.get("user_type", "beginner")
        current_chapter = state.get("current_chapter", 1)
        current_section = state.get("current_section", 1)
        
        # 원본 내용에서 불필요한 부분 제거
        refined_content = theory_draft.strip()
        
        # Theory Educator 접두사 제거 (있는 경우)
        if refined_content.startswith("🤖 Theory Educator:"):
            refined_content = refined_content.replace("🤖 Theory Educator:", "").strip()
        
        # 중복된 구분선 제거
        refined_content = refined_content.replace("---------------------", "").strip()
        
        # 과도한 줄바꿈 정리
        import re
        refined_content = re.sub(r'\n{3,}', '\n\n', refined_content)
        
        # 챕터/섹션 정보 추가 (간단하게)
        intro = f"📚 {current_chapter}챕터 {current_section}섹션\n\n"
        
        # 사용자 유형별 톤 체크 및 간단한 안내 추가
        if user_type == "beginner":
            # 초보자용: 친근하고 격려하는 톤
            if not any(word in refined_content for word in ["안녕", "환영", "함께"]):
                intro += "차근차근 함께 배워보시죠! 😊\n\n"
        else:
            # 고급자용: 효율적이고 전문적인 톤
            intro += "핵심 내용을 정리해서 설명드리겠습니다.\n\n"
        
        # 마무리 안내 추가 (간단하게)
        outro = "\n\n💡 궁금한 점이 있으시면 언제든 질문해주세요. 이해하셨다면 '다음'이라고 말씀해주시면 퀴즈를 진행하겠습니다."
        
        return intro + refined_content + outro
    
    def _refine_quiz_content(self, quiz_draft: str, state: TutorState) -> str:
        """
        퀴즈 내용 정제
        
        Args:
            quiz_draft: 원본 퀴즈 대본 (JSON 형태)
            state: TutorState
            
        Returns:
            정제된 퀴즈 내용 (사용자 친화적 형태)
        """
        user_type = state.get("user_type", "beginner")
        quiz_type = state.get("quiz_type", "multiple_choice")
        quiz_content = state.get("quiz_content", "")
        quiz_options = state.get("quiz_options", [])
        quiz_hint = state.get("quiz_hint", "")
        
        # 퀴즈 시작 안내
        if quiz_type == "multiple_choice":
            intro = "📝 이제 퀴즈를 풀어보겠습니다! 정답을 선택해주세요.\n\n"
        else:
            intro = "📝 이제 실습 문제를 풀어보겠습니다! 자유롭게 답변해주세요.\n\n"
        
        # 사용자 유형별 격려 메시지
        if user_type == "beginner":
            intro += "천천히 생각해보세요. 틀려도 괜찮으니 편하게 답변해주시면 됩니다! 💪\n\n"
        
        # 퀴즈 문제 내용 구성
        quiz_content_formatted = f"**문제**: {quiz_content}\n\n"
        
        # 객관식인 경우 선택지 추가
        if quiz_type == "multiple_choice" and quiz_options:
            quiz_content_formatted += "**선택지**:\n"
            for i, option in enumerate(quiz_options, 1):
                quiz_content_formatted += f"{i}. {option}\n"
            quiz_content_formatted += "\n"
        
        # 힌트가 있는 경우 추가
        if quiz_hint:
            quiz_content_formatted += f"💡 **힌트**: {quiz_hint}\n\n"
        
        # 답변 입력 안내 추가
        outro = "✏️ 답변을 입력해주세요!"
        
        return intro + quiz_content_formatted + outro
    
    def _refine_feedback_content(self, feedback_draft: str, state: TutorState) -> str:
        """
        피드백 내용 정제
        
        Args:
            feedback_draft: 원본 피드백 대본
            state: TutorState
            
        Returns:
            정제된 피드백 내용
        """
        user_type = state.get("user_type", "beginner")
        quiz_type = state.get("quiz_type", "multiple_choice")
        
        # v2.0 평가 결과 필드 사용
        if quiz_type == "multiple_choice":
            is_correct = state.get("multiple_answer_correct", False)
            score = 100 if is_correct else 0
        else:  # subjective
            score = state.get("subjective_answer_score", 0)
            is_correct = score >= 60
        
        session_decision = state.get("retry_decision_result", "proceed")  # v2.0 필드명
        
        # 기본 정제
        refined_content = feedback_draft.strip()
        
        # 결과에 따른 이모지 및 격려 메시지 추가 (v2.0 수정)
        if is_correct:
            intro = "🎉 "
        else:
            intro = "💪 "
        
        # 객관식 문제의 경우 정답과 사용자 답변 정보 추가
        answer_info_text = ""
        if quiz_type == "multiple_choice":
            quiz_correct_answer = state.get("quiz_correct_answer", "")
            user_answer = state.get("user_answer", "")
            
            if quiz_correct_answer and user_answer:
                answer_info_text = f"""
📋 **답변 정보**
• 정답: {quiz_correct_answer}
• 선택한 답: {user_answer}
"""

        
        # 세션 결정 결과에 따른 상세 안내 추가
        if session_decision == "proceed":
            outro = f"""
🎯 **다음 단계 안내**
• 이 섹션을 성공적으로 완료하셨습니다!
• 추가로 궁금한 점이 있으시면 언제든 질문해주세요
• 다음 학습으로 넘어가려면 다음 학습 버튼을 눌러주세요.
• 이 부분을 다시 학습하고 싶으시면 재학습 버튼을 눌러주세요."""
        elif session_decision == "retry":
            outro = f"""
🎯 **다음 단계 안내**
• 이번 학습은 아쉬운 부분이 있었습니다. 재학습을 추천드립니다.
• 추가로 궁금한 점이 있으시면 언제든 질문해주세요
• 다음 학습으로 넘어가려면 다음 학습 버튼을 눌러주세요.
• 이 부분을 다시 학습하고 싶으시면 재학습 버튼을 눌러주세요."""
        else:
            outro = f"""
💬 **학습 완료**:
• 궁금한 점이 있으시면 언제든 질문해주세요
• 다음 단계로 진행하려면 '다음'이라고 말씀해주세요"""
        
        return answer_info_text + intro + refined_content + outro
    
    def _refine_qna_content(self, qna_draft: str, state: TutorState) -> str:
        """
        QnA 내용 정제
        
        Args:
            qna_draft: 원본 QnA 대본
            state: TutorState
            
        Returns:
            정제된 QnA 내용
        """
        user_type = state.get("user_type", "beginner")
        
        # 기본 정제
        refined_content = qna_draft.strip()
        
        # 답변 시작 표시
        intro = "💬 "
        
        # 추가 도움 안내
        outro = "\n\n📚 더 궁금한 점이 있으시면 언제든 질문해주세요!"
        
        return intro + refined_content + outro
    
    def _create_theory_workflow_response(self, state: TutorState) -> TutorState:
        """
        이론 설명 workflow_response 생성 (v2.0 신규)
        
        Args:
            state: TutorState
            
        Returns:
            workflow_response가 포함된 TutorState
        """
        theory_draft = state.get("theory_draft", "")
        
        # 이론 내용 정제
        if not theory_draft:
            refined_content = self._generate_theory_fallback(state)
        else:
            refined_content = self._refine_theory_content(theory_draft, state)
        
        # workflow_response 구조 생성
        workflow_response = {
            "current_agent": "theory_educator",
            "session_progress_stage": "theory_completed",
            "ui_mode": "chat",
            "content": {
                "type": "theory",
                "title": f"{state.get('current_chapter', 1)}챕터 {state.get('current_section', 1)}섹션",
                "content": refined_content,
                "key_points": self._extract_key_points(refined_content),
                "examples": self._extract_examples(refined_content)
            }
        }
        
        # State 업데이트 - 정제된 내용을 theory_draft에도 저장
        updated_state = state_manager.update_workflow_response(state, workflow_response)
        updated_state = state_manager.update_agent_draft(updated_state, "theory_educator", refined_content)
        updated_state = state_manager.update_ui_mode(updated_state, "chat")
        
        return updated_state
    
    def _create_quiz_workflow_response(self, state: TutorState) -> TutorState:
        """
        퀴즈 workflow_response 생성 (v2.0 신규)
        
        Args:
            state: TutorState
            
        Returns:
            workflow_response가 포함된 TutorState
        """
        quiz_draft = state.get("quiz_draft", "")
        quiz_type = state.get("quiz_type", "multiple_choice")  # v2.0 필드명
        quiz_content = state.get("quiz_content", "")
        quiz_options = state.get("quiz_options", [])
        quiz_hint = state.get("quiz_hint", "")
        
        # 퀴즈 내용 정제
        if not quiz_draft:
            refined_quiz_content = self._generate_quiz_fallback(state)
        else:
            refined_quiz_content = self._refine_quiz_content(quiz_draft, state)
        
        # 퀴즈 내용 구성
        content = {
            "type": "quiz",
            "quiz_type": quiz_type,
            "question": quiz_content,
            "refined_content": refined_quiz_content  # 정제된 퀴즈 내용 추가
        }
        
        # 객관식 전용 필드
        if quiz_type == "multiple_choice":
            content["options"] = quiz_options
        
        # 공통 필드
        if quiz_hint:
            content["hint"] = quiz_hint
        
        # workflow_response 구조 생성
        workflow_response = {
            "current_agent": "quiz_generator",
            "session_progress_stage": "theory_completed",
            "ui_mode": "quiz",
            "content": content
        }
        
        # State 업데이트 - 정제된 내용을 quiz_draft에도 저장
        updated_state = state_manager.update_workflow_response(state, workflow_response)
        updated_state = state_manager.update_agent_draft(updated_state, "quiz_generator", refined_quiz_content)
        updated_state = state_manager.update_ui_mode(updated_state, "quiz")
        
        return updated_state
    
    def _create_feedback_workflow_response(self, state: TutorState) -> TutorState:
        """
        평가 피드백 workflow_response 생성 (v2.0 신규)
        
        Args:
            state: TutorState
            
        Returns:
            workflow_response가 포함된 TutorState
        """
        feedback_draft = state.get("feedback_draft", "")
        quiz_type = state.get("quiz_type", "multiple_choice")
        
        # 평가 결과 추출 (v2.0 필드)
        if quiz_type == "multiple_choice":
            is_correct = state.get("multiple_answer_correct", False)
            score = 100 if is_correct else 0
        else:  # subjective
            score = state.get("subjective_answer_score", 0)
            is_correct = score >= 60  # 60점 이상이면 통과
        
        # 피드백 내용 정제
        if not feedback_draft:
            refined_feedback = self._generate_feedback_fallback(state)
        else:
            refined_feedback = self._refine_feedback_content(feedback_draft, state)
        
        # workflow_response 구조 생성
        workflow_response = {
            "current_agent": "evaluation_feedback_agent",
            "session_progress_stage": "quiz_and_feedback_completed",
            "ui_mode": "chat",
            "evaluation_result": {
                "quiz_type": quiz_type,
                "is_answer_correct": is_correct,
                "score": score,
                "feedback": {
                    "title": "🎉 정답입니다!" if is_correct else "💪 아쉽네요!",
                    "content": refined_feedback,
                    "explanation": state.get("quiz_explanation", ""),
                    "next_step_decision": state.get("retry_decision_result", "proceed")  # v2.0 필드명
                }
            }
        }
        
        # State 업데이트 - 정제된 내용을 feedback_draft에도 저장
        updated_state = state_manager.update_workflow_response(state, workflow_response)
        updated_state = state_manager.update_agent_draft(updated_state, "evaluation_feedback_agent", refined_feedback)
        updated_state = state_manager.update_ui_mode(updated_state, "chat")
        
        return updated_state
    
    def _create_qna_workflow_response(self, state: TutorState) -> TutorState:
        """
        질문 답변 workflow_response 생성 (v2.0 신규)
        
        Args:
            state: TutorState
            
        Returns:
            workflow_response가 포함된 TutorState
        """
        qna_draft = state.get("qna_draft", "")
        
        # QnA 내용 정제
        if not qna_draft:
            refined_content = self._generate_qna_fallback(state)
        else:
            refined_content = self._refine_qna_content(qna_draft, state)
        
        # workflow_response 구조 생성
        workflow_response = {
            "current_agent": "qna_resolver",
            "session_progress_stage": state.get("session_progress_stage", "theory_completed"),
            "ui_mode": "chat",
            "content": {
                "type": "qna",
                "question": self._extract_user_message(state),
                "answer": refined_content,
                "related_topics": self._extract_related_topics(refined_content)
            }
        }
        
        # State 업데이트 - 정제된 내용을 qna_draft에도 저장
        updated_state = state_manager.update_workflow_response(state, workflow_response)
        updated_state = state_manager.update_agent_draft(updated_state, "qna_resolver", refined_content)
        updated_state = state_manager.update_ui_mode(updated_state, "chat")
        
        return updated_state
    
    def _create_session_workflow_response(self, state: TutorState) -> TutorState:
        """
        세션 완료 workflow_response 생성 (v2.0 신규)
        
        Args:
            state: TutorState
            
        Returns:
            workflow_response가 포함된 TutorState
        """
        # workflow_response 구조 생성
        workflow_response = {
            "current_agent": "session_manager",
            "session_progress_stage": "session_start",
            "ui_mode": "chat",
            "session_completion": {
                "completed_chapter": state.get("current_chapter", 1),
                "completed_section": state.get("current_section", 1),
                "next_chapter": state.get("current_chapter", 1),
                "next_section": state.get("current_section", 1) + 1,
                "session_summary": f"{state.get('current_chapter', 1)}챕터 {state.get('current_section', 1)}섹션을 성공적으로 완료했습니다.",
                "study_time_minutes": 15  # 예상 학습 시간
            }
        }
        
        # State 업데이트
        updated_state = state_manager.update_workflow_response(state, workflow_response)
        updated_state = state_manager.update_ui_mode(updated_state, "chat")
        
        return updated_state
    
    def _create_default_workflow_response(self, state: TutorState) -> TutorState:
        """
        기본 workflow_response 생성 (v2.0 신규)
        
        Args:
            state: TutorState
            
        Returns:
            workflow_response가 포함된 TutorState
        """
        # 가장 최근 대본 찾기
        drafts = [
            ("theory_educator", state.get("theory_draft", "")),
            ("quiz_generator", state.get("quiz_draft", "")),
            ("evaluation_feedback_agent", state.get("feedback_draft", "")),
            ("qna_resolver", state.get("qna_draft", ""))
        ]
        
        for agent_name, draft_content in drafts:
            if draft_content and draft_content.strip():
                # 내용이 있는 첫 번째 대본으로 응답 생성
                if "theory" in agent_name:
                    return self._create_theory_workflow_response(state)
                elif "quiz" in agent_name:
                    return self._create_quiz_workflow_response(state)
                elif "feedback" in agent_name:
                    return self._create_feedback_workflow_response(state)
                elif "qna" in agent_name:
                    return self._create_qna_workflow_response(state)
        
        # 모든 대본이 비어있으면 오류 응답
        return self._create_error_workflow_response(state)
    
    def _create_error_workflow_response(self, state: TutorState) -> TutorState:
        """
        오류 workflow_response 생성 (v2.0 신규)
        
        Args:
            state: TutorState
            
        Returns:
            오류 workflow_response가 포함된 TutorState
        """
        error_message = "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요."
        
        # workflow_response 구조 생성
        workflow_response = {
            "current_agent": "learning_supervisor",
            "session_progress_stage": state.get("session_progress_stage", "session_start"),
            "ui_mode": "chat",
            "content": {
                "type": "error",
                "message": error_message
            }
        }
        
        # State 업데이트
        updated_state = state_manager.update_workflow_response(state, workflow_response)
        updated_state = state_manager.update_ui_mode(updated_state, "chat")
        
        return updated_state
    
    def _extract_user_message(self, state: TutorState) -> str:
        """State에서 사용자 메시지 추출"""
        conversations = state.get("current_session_conversations", [])
        
        # 마지막 대화에서 사용자 메시지 찾기
        for conv in reversed(conversations):
            if conv.get("message_type") == "user":
                return conv.get("message", "")
        
        return ""
    
    def _extract_key_points(self, content: str) -> list:
        """이론 내용에서 핵심 포인트 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 로직 필요)
        key_points = []
        lines = content.split('\n')
        for line in lines:
            if '핵심' in line or '중요' in line or '포인트' in line:
                key_points.append(line.strip())
        
        return key_points[:3]  # 최대 3개
    
    def _extract_examples(self, content: str) -> list:
        """이론 내용에서 예시 추출"""
        # 간단한 예시 추출 (실제로는 더 정교한 로직 필요)
        examples = []
        lines = content.split('\n')
        for line in lines:
            if '예시' in line or '예를 들어' in line or '예:' in line:
                examples.append(line.strip())
        
        return examples[:2]  # 최대 2개
    
    def _extract_related_topics(self, content: str) -> list:
        """QnA 내용에서 관련 주제 추출"""
        # 간단한 관련 주제 추출 (실제로는 더 정교한 로직 필요)
        related_topics = []
        if 'AI' in content:
            related_topics.append('인공지능 기초')
        if 'ChatGPT' in content or 'GPT' in content:
            related_topics.append('ChatGPT 활용')
        if '프롬프트' in content:
            related_topics.append('프롬프트 엔지니어링')
        
        return related_topics[:3]  # 최대 3개
    
    def _generate_theory_fallback(self, state: TutorState) -> str:
        """이론 설명 대본이 없을 때 기본 응답"""
        chapter = state.get("current_chapter", 1)
        return f"죄송합니다. {chapter}챕터 이론 내용을 준비 중입니다. 잠시 후 다시 시도해주세요."
    
    def _generate_quiz_fallback(self, state: TutorState) -> str:
        """퀴즈 대본이 없을 때 기본 응답"""
        return "죄송합니다. 퀴즈 문제를 준비 중입니다. 잠시 후 다시 시도해주세요."
    
    def _generate_feedback_fallback(self, state: TutorState) -> str:
        """피드백 대본이 없을 때 기본 응답"""
        return "답변을 확인했습니다. 피드백을 준비 중이니 잠시만 기다려주세요."
    
    def _generate_qna_fallback(self, state: TutorState) -> str:
        """QnA 대본이 없을 때 기본 응답"""
        return "질문을 확인했습니다. 답변을 준비 중이니 잠시만 기다려주세요."
    
    def _generate_error_response(self, state: TutorState) -> TutorState:
        """
        오류 응답 생성
        
        Args:
            state: TutorState
            
        Returns:
            오류 응답이 포함된 TutorState
        """
        error_message = "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요."
        
        # 임시로 theory_draft에 오류 메시지 저장
        updated_state = state_manager.update_agent_draft(state, "theory_educator", error_message)
        
        return updated_state


# 전역 ResponseGenerator 인스턴스
response_generator = ResponseGenerator()