# backend/app/tools/content/theory_tools.py

from typing import Dict, Any, List
import json
import logging

from app.core.external.ai_client_manager import get_ai_client_manager, AIProvider
from app.utils.common.exceptions import ExternalAPIError


def theory_generation_tool(
    chapter_data: Dict[str, Any],
    user_type: str,
    learning_context: Dict[str, Any],
    recent_sessions: List[Dict[str, str]],
    vector_materials: List[Dict[str, Any]] = None
) -> str:
    """
    AI를 활용한 사용자 맞춤형 이론 설명 대본 생성 (1회 LLM 호출)
    현재 섹션의 전체 content와 key_points를 기반으로 LLM이 사용자 유형에 맞게 동적 생성
    
    Args:
        chapter_data: JSON에서 로드한 챕터 데이터
        user_type: 사용자 유형 ("beginner" or "advanced")
        learning_context: 학습 맥락 정보
        recent_sessions: 최근 학습 세션 요약
        vector_materials: 벡터 DB에서 검색한 관련 자료 (추후 활용)
        
    Returns:
        생성된 이론 설명 대본 (JSON 문자열)
    """
    
    logger = logging.getLogger(__name__)
    
    try:
        # AI 클라이언트 관리자 가져오기
        ai_manager = get_ai_client_manager()
        
        # 1. 현재 섹션 데이터 추출
        current_section = _get_current_section_data(chapter_data, learning_context)
        if not current_section:
            raise ValueError("현재 섹션 데이터를 찾을 수 없습니다.")
        
        # 2. 사용자 유형별 시스템 지시사항 생성
        system_instruction = _get_system_instruction_by_user_type(user_type, learning_context)
        
        # 3. 섹션 전체 내용을 포함한 프롬프트 생성
        user_prompt = _build_section_based_prompt(
            chapter_data, 
            current_section, 
            learning_context, 
            recent_sessions
        )
        
        logger.info(f"AI 이론 설명 생성 - 챕터 {chapter_data.get('chapter_number', 1)} 섹션 {current_section.get('section_number', 1)} ({user_type})")
        
        # 4. AI 호출 (1회만)
        generated_response = ai_manager.generate_json_content(
            prompt=user_prompt,
            system_instruction=system_instruction,
            provider=AIProvider.GEMINI,
            temperature=0.7
        )
        
        # 5. 응답 검증 및 보완
        validated_response = _validate_response(
            generated_response, 
            chapter_data, 
            current_section, 
            user_type
        )
        
        logger.info("AI 이론 설명 생성 완료")
        return json.dumps(validated_response, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"AI 이론 설명 생성 실패: {str(e)}")
        return _generate_fallback_response(chapter_data, user_type, str(e))


def _get_current_section_data(chapter_data: Dict[str, Any], learning_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    현재 섹션 데이터 추출
    
    Args:
        chapter_data: 챕터 데이터
        learning_context: 학습 맥락 (current_section 포함)
        
    Returns:
        현재 섹션 데이터
    """
    sections = chapter_data.get('sections', [])
    current_section_number = learning_context.get('current_section', 1)
    
    # 섹션 번호로 현재 섹션 찾기
    for section in sections:
        if section.get('section_number') == current_section_number:
            return section
    
    # 찾지 못한 경우 첫 번째 섹션 반환
    return sections[0] if sections else {}


def _get_system_instruction_by_user_type(user_type: str, learning_context: Dict[str, Any]) -> str:
    """사용자 유형별 시스템 지시사항 생성"""
    
    # 기본 JSON 형식 지시사항
    base_json_format = """
반드시 아래 JSON 구조로만 응답하세요:
{
    "content_type": "theory",
    "chapter_info": {"chapter_number": 숫자, "title": "제목", "user_type": "유형"},
    "section_info": {"section_number": 숫자, "title": "섹션제목"},
    "main_content": "설명 내용",
    "key_points": ["핵심1", "핵심2", "핵심3"],
    "analogy": "비유 설명",
    "examples": ["예시1", "예시2"],
    "user_guidance": "안내 메시지",
    "next_step_preview": "다음 단계 안내"
}
"""
    
    # 재학습 처리
    retry_instruction = ""
    if learning_context.get("is_retry_session", False):
        retry_instruction = "이전에 어려워했을 수 있으니 더 쉽고 자세하게 설명하세요. "
    
    # 사용자 유형별 스타일
    if user_type == "beginner":
        return f"""
당신은 AI 입문자를 위한 친근한 튜터입니다. {retry_instruction}
- 친근하고 쉬운 언어 사용 (이모지 활용)
- 일상생활 비유 중심 설명
- "~해보겠습니다", "~할게요" 친근한 톤
- 기술 용어는 반드시 쉬운 말로 풀어서 설명
- 주어진 내용을 바탕으로 완전히 새로운 방식으로 재구성

{base_json_format}
"""
    else:  # advanced
        return f"""
당신은 실무 응용형 사용자를 위한 효율적인 튜터입니다. {retry_instruction}
- 효율적이고 핵심적인 설명
- 기술적 배경을 고려한 논리적 구조
- 실무 활용 관점 중심
- "핵심 포인트", "실무에서는" 표현 활용
- 주어진 내용을 바탕으로 실무적 관점에서 재구성

{base_json_format}
"""


def _build_section_based_prompt(
    chapter_data: Dict[str, Any],
    current_section: Dict[str, Any],
    learning_context: Dict[str, Any],
    recent_sessions: List[Dict[str, str]]
) -> str:
    """
    현재 섹션의 전체 내용을 포함한 프롬프트 생성
    
    Args:
        chapter_data: 챕터 데이터
        current_section: 현재 섹션 데이터
        learning_context: 학습 맥락
        recent_sessions: 최근 세션 요약
        
    Returns:
        생성된 프롬프트
    """
    
    # 챕터 기본 정보
    chapter_number = chapter_data.get('chapter_number', 1)
    chapter_title = chapter_data.get('title', '')
    
    # 섹션 기본 정보
    section_number = current_section.get('section_number', 1)
    section_title = current_section.get('title', '')
    learning_objectives = current_section.get('learning_objectives', [])
    
    # 섹션의 이론 내용 전체 추출
    theory_data = current_section.get('theory', {})
    full_content = theory_data.get('content', '')
    key_points = theory_data.get('key_points', [])
    analogy = theory_data.get('analogy', '')  # 선택적 필드
    
    # 학습 이력 (최대 2개만)
    history = ""
    if recent_sessions:
        recent = recent_sessions[-2:]
        history = f"최근 학습: {', '.join([s.get('summary', '')[:30] for s in recent])}"
    
    # 섹션 전체 내용을 포함한 프롬프트 구성
    prompt = f"""
**챕터 정보**:
- 챕터 {chapter_number}: {chapter_title}
- 섹션 {section_number}: {section_title}
- 학습 목표: {', '.join(learning_objectives) if learning_objectives else '없음'}

**섹션 전체 내용** (이 내용을 바탕으로 사용자 맞춤형 설명을 재구성해주세요):

**주요 내용**:
{full_content}

**핵심 포인트**:
{chr(10).join([f"- {point}" for point in key_points]) if key_points else '없음'}

{f"**기존 비유**: {analogy}" if analogy else ""}

**학습 맥락**:
- 세션 {learning_context.get('session_count', 0) + 1}회차
- 재학습: {'예' if learning_context.get('is_retry_session', False) else '아니오'}
{history}

**요청사항**:
위의 섹션 전체 내용을 참고하여, 사용자 유형에 맞는 완전히 새로운 설명을 생성해주세요.
기존 내용을 단순 복사하지 말고, 창의적이고 이해하기 쉬운 방식으로 재구성해주세요.
"""
    
    return prompt


def _validate_response(
    response: Dict[str, Any], 
    chapter_data: Dict[str, Any], 
    current_section: Dict[str, Any],
    user_type: str
) -> Dict[str, Any]:
    """AI 응답 검증 및 필수 필드 보완"""
    
    return {
        "content_type": "theory",
        "chapter_info": {
            "chapter_number": chapter_data.get("chapter_number", 1),
            "title": chapter_data.get("title", ""),
            "user_type": user_type
        },
        "section_info": {
            "section_number": current_section.get("section_number", 1),
            "title": current_section.get("title", "")
        },
        "main_content": response.get("main_content", "설명을 생성하는 중 문제가 발생했습니다."),
        "key_points": response.get("key_points", ["핵심 내용을 정리 중입니다."]),
        "analogy": response.get("analogy", ""),
        "examples": response.get("examples", []),
        "user_guidance": response.get("user_guidance") or (
            "천천히 읽어보시고 질문해주세요!" if user_type == "beginner" 
            else "개념을 파악하셨다면 다음 단계로 진행하겠습니다."
        ),
        "next_step_preview": response.get("next_step_preview", "이제 퀴즈를 풀어보겠습니다.")
    }


def _generate_fallback_response(chapter_data: Dict[str, Any], user_type: str, error_msg: str) -> str:
    """오류 발생 시 기본 응답 생성"""
    
    fallback = {
        "content_type": "theory",
        "chapter_info": {
            "chapter_number": chapter_data.get("chapter_number", 1),
            "title": chapter_data.get("title", ""),
            "user_type": user_type
        },
        "section_info": {
            "section_number": 1,
            "title": "이론 학습"
        },
        "main_content": f"일시적인 문제가 발생했습니다. 질문을 통해 학습을 진행해주세요.\n오류: {error_msg}",
        "key_points": ["일시적인 시스템 문제", "질문으로 학습 계속 가능", "잠시 후 재시도"],
        "analogy": "",
        "examples": [],
        "user_guidance": "시스템 문제로 설명이 생성되지 않았습니다. 궁금한 점을 질문해주세요.",
        "next_step_preview": "질문이 있으시면 언제든 말씀해주세요."
    }
    
    return json.dumps(fallback, ensure_ascii=False, indent=2)