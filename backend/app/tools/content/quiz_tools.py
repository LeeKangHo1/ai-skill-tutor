# backend/app/tools/content/quiz_tools.py

from typing import Dict, Any, List
import json
import logging

from app.core.external.ai_client_manager import get_ai_client_manager, AIProvider
from app.utils.common.exceptions import ExternalAPIError


def quiz_generation_tool(
    chapter_data: Dict[str, Any],
    user_type: str,
    learning_context: Dict[str, Any],
    recent_sessions: List[Dict[str, str]],
    theory_content: str = ""
) -> str:
    """
    AI를 활용한 사용자 맞춤형 퀴즈 생성 (1회 LLM 호출)
    State에서 퀴즈 타입을 읽어와 객관식/주관식 함수 분기 처리
    
    Args:
        chapter_data: JSON에서 로드한 챕터 데이터
        user_type: 사용자 유형 ("beginner" or "advanced")
        learning_context: 학습 맥락 정보 (current_question_type 포함)
        recent_sessions: 최근 학습 세션 요약
        theory_content: 이론 설명 내용 (참고용)
        
    Returns:
        생성된 퀴즈 대본 (JSON 문자열)
    """
    
    logger = logging.getLogger(__name__)
    
    try:
        # 1. State에서 퀴즈 타입 추출
        quiz_type = learning_context.get("current_question_type", "multiple_choice")
        
        logger.info(f"퀴즈 생성 시작 - 타입: {quiz_type}, 사용자: {user_type}")
        
        # 2. 퀴즈 타입별 함수 분기
        if quiz_type == "subjective":
            return _generate_subjective_quiz(
                chapter_data, user_type, learning_context, recent_sessions, theory_content
            )
        else:  # multiple_choice
            return _generate_multiple_choice_quiz(
                chapter_data, user_type, learning_context, recent_sessions, theory_content
            )
            
    except Exception as e:
        logger.error(f"퀴즈 생성 실패: {str(e)}")
        return _generate_quiz_fallback_response(chapter_data, user_type, str(e))


def _generate_multiple_choice_quiz(
    chapter_data: Dict[str, Any],
    user_type: str,
    learning_context: Dict[str, Any],
    recent_sessions: List[Dict[str, str]],
    theory_content: str
) -> str:
    """객관식 퀴즈 생성"""
    
    logger = logging.getLogger(__name__)
    
    try:
        ai_manager = get_ai_client_manager()
        
        # 현재 섹션 데이터 추출
        current_section = _get_current_section_data(chapter_data, learning_context)
        if not current_section:
            raise ValueError("현재 섹션 데이터를 찾을 수 없습니다.")
        
        # 객관식 전용 시스템 지시사항
        system_instruction = _get_multiple_choice_system_instruction(user_type, learning_context)
        
        # 객관식 전용 프롬프트
        user_prompt = _build_multiple_choice_prompt(
            chapter_data, current_section, learning_context, recent_sessions, theory_content
        )
        
        logger.info(f"객관식 퀴즈 생성 - 챕터 {chapter_data.get('chapter_number', 1)}")
        
        # AI 호출
        generated_response = ai_manager.generate_json_content(
            prompt=user_prompt,
            system_instruction=system_instruction,
            provider=AIProvider.GEMINI,
            temperature=0.8
        )
        
        # 응답 검증
        validated_response = _validate_multiple_choice_response(
            generated_response, chapter_data, current_section, user_type
        )
        
        logger.info("객관식 퀴즈 생성 완료")
        return json.dumps(validated_response, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"객관식 퀴즈 생성 실패: {str(e)}")
        raise


def _generate_subjective_quiz(
    chapter_data: Dict[str, Any],
    user_type: str,
    learning_context: Dict[str, Any],
    recent_sessions: List[Dict[str, str]],
    theory_content: str
) -> str:
    """주관식 퀴즈 생성"""
    
    logger = logging.getLogger(__name__)
    
    try:
        ai_manager = get_ai_client_manager()
        
        # 현재 섹션 데이터 추출
        current_section = _get_current_section_data(chapter_data, learning_context)
        if not current_section:
            raise ValueError("현재 섹션 데이터를 찾을 수 없습니다.")
        
        # 주관식 전용 시스템 지시사항
        system_instruction = _get_subjective_system_instruction(user_type, learning_context)
        
        # 주관식 전용 프롬프트
        user_prompt = _build_subjective_prompt(
            chapter_data, current_section, learning_context, recent_sessions, theory_content
        )
        
        logger.info(f"주관식 퀴즈 생성 - 챕터 {chapter_data.get('chapter_number', 1)}")
        
        # AI 호출
        generated_response = ai_manager.generate_json_content(
            prompt=user_prompt,
            system_instruction=system_instruction,
            provider=AIProvider.GEMINI,
            temperature=0.8
        )
        
        # 응답 검증
        validated_response = _validate_subjective_response(
            generated_response, chapter_data, current_section, user_type
        )
        
        logger.info("주관식 퀴즈 생성 완료")
        return json.dumps(validated_response, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"주관식 퀴즈 생성 실패: {str(e)}")
        raise


def _get_current_section_data(chapter_data: Dict[str, Any], learning_context: Dict[str, Any]) -> Dict[str, Any]:
    """현재 섹션 데이터 추출"""
    sections = chapter_data.get('sections', [])
    current_section_number = learning_context.get('current_section', 1)
    
    for section in sections:
        if section.get('section_number') == current_section_number:
            return section
    
    return sections[0] if sections else {}


def _get_multiple_choice_system_instruction(user_type: str, learning_context: Dict[str, Any]) -> str:
    """객관식 전용 시스템 지시사항"""
    
    base_json_format = """
반드시 아래 JSON 구조로만 응답하세요:
{
    "content_type": "quiz",
    "chapter_info": {"chapter_number": 숫자, "title": "제목", "user_type": "유형"},
    "section_info": {"section_number": 숫자, "title": "섹션제목"},
    "quiz_info": {
        "question_type": "multiple_choice",
        "question_number": 1,
        "question": "문제 내용",
        "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
        "correct_answer": 정답번호(1-4),
        "explanation": "정답 해설"
    },
    "hint": "도움이 되는 힌트",
    "user_guidance": "응답 후 안내 메시지",
    "next_step_preview": "다음 단계 안내"
}
"""
    
    retry_instruction = ""
    if learning_context.get("is_retry_session", False):
        retry_instruction = "이전에 틀렸을 수 있으니 더 쉬운 문제와 자세한 힌트를 제공하세요. "
    
    if user_type == "beginner":
        return f"""
당신은 AI 입문자를 위한 친근한 객관식 퀴즈 출제자입니다. {retry_instruction}
- 쉽고 이해하기 쉬운 4지선다 문제 출제
- 일상생활과 연관된 예시 활용
- 친근하고 격려적인 톤 사용
- 힌트는 구체적이고 도움이 되도록 제공
- 그럴듯한 오답 3개와 명확한 정답 1개 구성

{base_json_format}
"""
    else:  # advanced
        return f"""
당신은 실무 응용형 사용자를 위한 효율적인 객관식 퀴즈 출제자입니다. {retry_instruction}
- 실무 적용 관점의 4지선다 문제 출제
- 논리적이고 체계적인 문제 구성
- 핵심을 파악하는 능력 테스트
- 힌트는 핵심 포인트 중심으로 제공

{base_json_format}
"""


def _get_subjective_system_instruction(user_type: str, learning_context: Dict[str, Any]) -> str:
    """주관식 전용 시스템 지시사항"""
    
    base_json_format = """
반드시 아래 JSON 구조로만 응답하세요:
{
    "content_type": "quiz",
    "chapter_info": {"chapter_number": 숫자, "title": "제목", "user_type": "유형"},
    "section_info": {"section_number": 숫자, "title": "섹션제목"},
    "quiz_info": {
        "question_type": "subjective",
        "question_number": 1,
        "question": "프롬프트 작성 문제 내용",
        "sample_answer": "모범 답안 예시",
        "evaluation_criteria": ["평가 기준1", "평가 기준2", "평가 기준3"]
    },
    "hint": "프롬프트 작성에 도움이 되는 힌트",
    "user_guidance": "응답 후 안내 메시지",
    "next_step_preview": "다음 단계 안내"
}
"""
    
    retry_instruction = ""
    if learning_context.get("is_retry_session", False):
        retry_instruction = "이전에 어려워했을 수 있으니 더 간단하고 명확한 문제를 출제하세요. "
    
    if user_type == "beginner":
        return f"""
당신은 AI 입문자를 위한 친근한 프롬프트 작성 퀴즈 출제자입니다. {retry_instruction}
- 간단하고 실용적인 프롬프트 작성 문제 출제
- 일상생활에서 사용할 수 있는 예시 중심
- 친근하고 격려적인 톤 사용
- 힌트는 구체적인 작성 방법 제시
- 예시: "ChatGPT에게 요리 레시피를 요청하는 프롬프트 작성하기"

{base_json_format}
"""
    else:  # advanced
        return f"""
당신은 실무 응용형 사용자를 위한 고급 프롬프트 작성 퀴즈 출제자입니다. {retry_instruction}
- 업무에 활용 가능한 복합적인 프롬프트 작성 문제 출제
- 실무 시나리오 기반 문제 구성
- 효율성과 정확성에 중점
- 힌트는 프롬프트 엔지니어링 기법 제시
- 예시: "업무용 이메일 초안 작성을 위한 효과적인 프롬프트 만들기"

{base_json_format}
"""


def _build_multiple_choice_prompt(
    chapter_data: Dict[str, Any],
    current_section: Dict[str, Any],
    learning_context: Dict[str, Any],
    recent_sessions: List[Dict[str, str]],
    theory_content: str
) -> str:
    """객관식 프롬프트 생성"""
    
    return _build_base_prompt(
        chapter_data, current_section, learning_context, recent_sessions, theory_content,
        quiz_type="객관식 4지선다"
    )


def _build_subjective_prompt(
    chapter_data: Dict[str, Any],
    current_section: Dict[str, Any],
    learning_context: Dict[str, Any],
    recent_sessions: List[Dict[str, str]],
    theory_content: str
) -> str:
    """주관식 프롬프트 생성"""
    
    return _build_base_prompt(
        chapter_data, current_section, learning_context, recent_sessions, theory_content,
        quiz_type="주관식 프롬프트 작성"
    )


def _build_base_prompt(
    chapter_data: Dict[str, Any],
    current_section: Dict[str, Any],
    learning_context: Dict[str, Any],
    recent_sessions: List[Dict[str, str]],
    theory_content: str,
    quiz_type: str
) -> str:
    """공통 프롬프트 기반 생성"""
    
    # 챕터/섹션 기본 정보
    chapter_number = chapter_data.get('chapter_number', 1)
    chapter_title = chapter_data.get('title', '')
    section_number = current_section.get('section_number', 1)
    section_title = current_section.get('title', '')
    
    # 기존 퀴즈 템플릿 정보
    existing_quiz = current_section.get('quiz', {})
    quiz_template_info = ""
    if existing_quiz:
        quiz_template_info = f"""
**기존 퀴즈 템플릿** (참고용):
- 문제 유형: {existing_quiz.get('type', '')}
- 문제: {existing_quiz.get('question', '')}
"""
    
    # 이론 내용 요약
    theory_summary = ""
    if theory_content:
        try:
            theory_json = json.loads(theory_content)
            main_content = theory_json.get('main_content', '')
            key_points = theory_json.get('key_points', [])
            theory_summary = f"""
**학습한 이론 내용**:
- 주요 내용: {main_content[:200]}...
- 핵심 포인트: {', '.join(key_points[:3])}
"""
        except:
            theory_summary = f"**학습한 이론**: {theory_content[:100]}..."
    
    # 학습 이력
    history = ""
    if recent_sessions:
        recent = recent_sessions[-2:]
        history = f"최근 학습: {', '.join([s.get('summary', '')[:30] for s in recent])}"
    
    return f"""
**{quiz_type} 퀴즈 생성 요청**:
- 챕터 {chapter_number}: {chapter_title}
- 섹션 {section_number}: {section_title}
- 세션 {learning_context.get('session_count', 0) + 1}회차
- 재학습: {'예' if learning_context.get('is_retry_session', False) else '아니오'}

{quiz_template_info}

{theory_summary}

{history}

**생성 요청사항**:
위 내용을 바탕으로 {quiz_type} 문제 1개를 생성해주세요.
기존 템플릿과 유사하지만 완전히 다른 새로운 문제를 만들어주세요.
학습한 핵심 개념을 제대로 이해했는지 확인할 수 있어야 합니다.
힌트 1개를 함께 생성해주세요.
"""


def _validate_multiple_choice_response(
    response: Dict[str, Any], 
    chapter_data: Dict[str, Any], 
    current_section: Dict[str, Any],
    user_type: str
) -> Dict[str, Any]:
    """객관식 응답 검증"""
    
    quiz_info = response.get("quiz_info", {})
    hint = response.get("hint", "핵심 개념을 떠올려보세요.")
    
    return {
        "content_type": "quiz",
        "chapter_info": {
            "chapter_number": chapter_data.get("chapter_number", 1),
            "title": chapter_data.get("title", ""),
            "user_type": user_type
        },
        "section_info": {
            "section_number": current_section.get("section_number", 1),
            "title": current_section.get("title", "")
        },
        "quiz_info": {
            "question_type": "multiple_choice",
            "question_number": 1,
            "question": quiz_info.get("question", "퀴즈를 생성하는 중 문제가 발생했습니다."),
            "options": quiz_info.get("options", ["선택지 1", "선택지 2", "선택지 3", "선택지 4"]),
            "correct_answer": quiz_info.get("correct_answer", 1),
            "explanation": quiz_info.get("explanation", "정답 해설을 생성하는 중 문제가 발생했습니다.")
        },
        "hint": hint,
        "user_guidance": response.get("user_guidance") or (
            "차근차근 생각해보시고, 어려우면 힌트를 사용해보세요!" if user_type == "beginner"
            else "문제를 분석해보시고, 필요하면 힌트를 참고하세요."
        ),
        "next_step_preview": response.get("next_step_preview", "답변을 제출하면 결과를 확인할 수 있습니다.")
    }


def _validate_subjective_response(
    response: Dict[str, Any], 
    chapter_data: Dict[str, Any], 
    current_section: Dict[str, Any],
    user_type: str
) -> Dict[str, Any]:
    """주관식 응답 검증"""
    
    quiz_info = response.get("quiz_info", {})
    hint = response.get("hint", "구체적이고 명확한 프롬프트를 작성해보세요.")
    
    return {
        "content_type": "quiz",
        "chapter_info": {
            "chapter_number": chapter_data.get("chapter_number", 1),
            "title": chapter_data.get("title", ""),
            "user_type": user_type
        },
        "section_info": {
            "section_number": current_section.get("section_number", 1),
            "title": current_section.get("title", "")
        },
        "quiz_info": {
            "question_type": "subjective",
            "question_number": 1,
            "question": quiz_info.get("question", "프롬프트 작성 문제를 생성하는 중 문제가 발생했습니다."),
            "sample_answer": quiz_info.get("sample_answer", "모범답안을 생성하는 중 문제가 발생했습니다."),
            "evaluation_criteria": quiz_info.get("evaluation_criteria", ["구체성", "명확성", "완성도"])
        },
        "hint": hint,
        "user_guidance": response.get("user_guidance") or (
            "창의적으로 프롬프트를 작성해보세요!" if user_type == "beginner"
            else "효과적인 프롬프트 엔지니어링 기법을 활용해보세요."
        ),
        "next_step_preview": response.get("next_step_preview", "작성한 프롬프트를 제출하면 평가를 받을 수 있습니다.")
    }


def _generate_quiz_fallback_response(chapter_data: Dict[str, Any], user_type: str, error_msg: str) -> str:
    """오류 발생 시 기본 퀴즈 응답 생성"""
    
    fallback = {
        "content_type": "quiz",
        "chapter_info": {
            "chapter_number": chapter_data.get("chapter_number", 1),
            "title": chapter_data.get("title", ""),
            "user_type": user_type
        },
        "section_info": {
            "section_number": 1,
            "title": "퀴즈"
        },
        "quiz_info": {
            "question_type": "multiple_choice",
            "question_number": 1,
            "question": "일시적인 문제로 퀴즈를 생성할 수 없습니다. 어떻게 하시겠습니까?",
            "options": [
                "다시 시도하기",
                "이론 설명 다시 보기", 
                "질문하기",
                "다음 단계로 넘어가기"
            ],
            "correct_answer": 1,
            "explanation": "시스템 문제가 발생했습니다. 다시 시도해주세요."
        },
        "hint": "시스템에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
        "user_guidance": "시스템 문제로 퀴즈가 생성되지 않았습니다. 다른 방법으로 학습을 진행해보세요.",
        "next_step_preview": "문제가 해결되면 정상적인 퀴즈를 진행할 수 있습니다."
    }
    
    return json.dumps(fallback, ensure_ascii=False, indent=2)