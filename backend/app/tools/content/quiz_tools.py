# backend/app/tools/content/quiz_tools.py

from typing import Dict, Any, List
import json
import random


def quiz_generation_tool(
    chapter_data: Dict[str, Any],
    user_type: str,
    quiz_context: Dict[str, Any],
    session_progress: str
) -> str:
    """
    JSON 챕터 데이터를 기반으로 퀴즈 생성
    
    Args:
        chapter_data: JSON에서 로드한 챕터 데이터
        user_type: 사용자 유형 ("beginner" or "advanced")
        quiz_context: 퀴즈 생성 맥락 정보
        session_progress: 세션 진행 단계
        
    Returns:
        생성된 퀴즈 대본 (JSON 문자열)
    """
    
    try:
        # 1. 섹션에서 퀴즈 데이터 추출
        sections = chapter_data.get("sections", [])
        if not sections:
            raise ValueError("챕터에 섹션 데이터가 없습니다.")
        
        # 2. 퀴즈 선택 로직
        selected_quiz = _select_quiz_from_sections(sections, quiz_context)
        if not selected_quiz:
            raise ValueError("선택할 수 있는 퀴즈가 없습니다.")
        
        # 3. 사용자 유형별 맞춤화
        customized_quiz = _customize_quiz_for_user_type(
            selected_quiz, 
            user_type, 
            quiz_context
        )
        
        # 4. 최종 퀴즈 대본 구성
        quiz_draft = {
            "content_type": "quiz",
            "chapter_info": {
                "chapter_number": chapter_data.get("chapter_number", 1),
                "title": chapter_data.get("title", "")
            },
            "quiz_info": {
                "question_type": customized_quiz["type"],
                "question_number": customized_quiz.get("number", 1),
                "question": customized_quiz["question"],
                "options": customized_quiz.get("options", []),
                "correct_answer": customized_quiz.get("correct_answer", 1)
            },
            "explanation": customized_quiz.get("explanation", ""),
            "user_guidance": _generate_quiz_guidance(user_type, quiz_context),
            "hints_available": True if (user_type == "beginner" and quiz_context.get("hint_usage_count", 0) == 0) else False
        }
        
        return json.dumps(quiz_draft, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"[quiz_generation_tool] 오류 발생: {str(e)}")
        # 오류 발생 시 기본 퀴즈 반환
        error_quiz = _create_fallback_quiz(user_type, str(e))
        return json.dumps(error_quiz, ensure_ascii=False, indent=2)


def hint_generation_tool(
    question_content: str,
    question_type: str,
    user_type: str,
    quiz_context: Dict[str, Any]
) -> str:
    """
    문제별 맞춤 힌트 생성 (1회 제공)
    
    Args:
        question_content: 문제 내용
        question_type: 문제 유형
        user_type: 사용자 유형
        quiz_context: 퀴즈 맥락 정보
        
    Returns:
        생성된 힌트 내용 (JSON 문자열)
    """
    
    try:
        # 단일 힌트 제공 (1회만)
        hint_type = "concept_hint"
        hint_message = "핵심 개념을 다시 떠올려보세요!"
        
        # 사용자 유형별 힌트 스타일
        if user_type == "beginner":
            tone = "친근하고 격려하는"
            detail_level = "상세한"
            hint_message = "배운 내용 중에서 핵심 키워드를 생각해보세요! 😊"
        else:
            tone = "간결하고 직접적인"
            detail_level = "핵심만"
            hint_message = "학습한 개념의 핵심 포인트를 다시 확인해보세요."
        
        hint_draft = {
            "content_type": "hint",
            "hint_info": {
                "type": hint_type,
                "content": f"💡 힌트: {hint_message}",
                "is_used": True,
                "remaining_hints": 0  # 1회만 제공하므로 남은 힌트 없음
            },
            "tone": tone,
            "user_guidance": f"{detail_level} 힌트를 참고하여 다시 생각해보세요!"
        }
        
        return json.dumps(hint_draft, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"[hint_generation_tool] 오류 발생: {str(e)}")
        error_hint = {
            "content_type": "hint",
            "hint_info": {
                "type": "error",
                "content": f"힌트 생성 중 오류가 발생했습니다: {str(e)}",
                "is_used": True,
                "remaining_hints": 0
            },
            "user_guidance": "다시 시도해 주세요."
        }
        return json.dumps(error_hint, ensure_ascii=False, indent=2)


def _select_quiz_from_sections(sections: List[Dict[str, Any]], quiz_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    섹션들에서 적절한 퀴즈 선택
    
    Args:
        sections: 챕터의 모든 섹션
        quiz_context: 퀴즈 선택 맥락
        
    Returns:
        선택된 퀴즈 데이터
    """
    available_quizzes = []
    
    for section in sections:
        quiz_data = section.get("quiz", {})
        if quiz_data:
            quiz_data["section_number"] = section.get("section_number", 1)
            quiz_data["section_title"] = section.get("title", "")
            available_quizzes.append(quiz_data)
    
    if not available_quizzes:
        return None
    
    # 재학습 세션인 경우 다른 섹션 선택, 아니면 첫 번째 섹션
    if quiz_context.get("is_retry_session", False):
        return random.choice(available_quizzes)
    else:
        return available_quizzes[0]


def _customize_quiz_for_user_type(
    quiz_data: Dict[str, Any], 
    user_type: str, 
    quiz_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    사용자 유형에 맞게 퀴즈 맞춤화
    
    Args:
        quiz_data: 원본 퀴즈 데이터
        user_type: 사용자 유형
        quiz_context: 퀴즈 맥락
        
    Returns:
        맞춤화된 퀴즈
    """
    
    customized_quiz = quiz_data.copy()
    
    if user_type == "beginner":
        # AI 입문자용: 친근한 톤, 격려 메시지 추가
        if quiz_context.get("is_retry_session", False):
            question_prefix = "이번에는 조금 더 쉽게 문제를 내볼게요! 😊\n\n"
        else:
            question_prefix = "배운 내용을 확인해볼까요? 😊\n\n"
        
        customized_quiz["question"] = question_prefix + quiz_data.get("question", "")
        
    else:  # advanced
        # 실무 응용형: 효율적이고 직접적인 톤
        if quiz_context.get("is_retry_session", False):
            question_prefix = "핵심 개념을 다시 확인해보겠습니다.\n\n"
        else:
            question_prefix = "이해도를 확인해보겠습니다.\n\n"
        
        customized_quiz["question"] = question_prefix + quiz_data.get("question", "")
    
    return customized_quiz


def _generate_quiz_guidance(user_type: str, quiz_context: Dict[str, Any]) -> str:
    """
    퀴즈 안내 메시지 생성
    
    Args:
        user_type: 사용자 유형
        quiz_context: 퀴즈 맥락
        
    Returns:
        안내 메시지
    """
    if quiz_context.get("is_retry_session", False):
        if user_type == "beginner":
            return "천천히 생각해보세요. 힌트가 필요하면 언제든 말씀해주세요!"
        else:
            return "핵심 개념을 중심으로 다시 생각해보세요."
    
    if user_type == "beginner":
        return "배운 내용을 떠올리며 답을 선택해보세요. 어려우면 힌트를 요청하세요! (1회만 제공)"
    else:
        return "학습한 내용을 바탕으로 정답을 선택해주세요."


def _create_fallback_quiz(user_type: str, error_message: str) -> Dict[str, Any]:
    """
    오류 시 기본 퀴즈 생성
    
    Args:
        user_type: 사용자 유형
        error_message: 오류 메시지
        
    Returns:
        기본 퀴즈 딕셔너리
    """
    return {
        "content_type": "quiz",
        "chapter_info": {"chapter_number": 1, "title": "오류"},
        "quiz_info": {
            "question_type": "multiple_choice",
            "question_number": 1,
            "question": f"퀴즈 생성 중 문제가 발생했습니다. 어떻게 하시겠어요?",
            "options": [
                "다시 시도하기",
                "다음으로 넘어가기", 
                "이전 단계로 돌아가기",
                "도움말 보기"
            ],
            "correct_answer": 1
        },
        "explanation": f"시스템 오류: {error_message}",
        "user_guidance": "선택지 중 하나를 선택해주세요.",
        "hints_available": False
    }