# backend/app/tools/content/theory_tools.py

import json
import logging
from typing import Dict, Any, List

from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.external.ai_client_manager import get_ai_client_manager, AIProvider
from app.utils.common.exceptions import ExternalAPIError


def theory_generation_tool(
    chapter_data: Dict[str, Any],
    user_type: str,
    learning_context: Dict[str, Any],
    vector_materials: List[Dict[str, Any]] = None
) -> str:
    """
    AI를 활용한 사용자 맞춤형 이론 설명 대본 생성 (LangChain + LangSmith 적용)
    AI Client Manager에서 LangSmith 추적 관리
    
    Args:
        chapter_data: JSON에서 로드한 챕터 데이터
        user_type: 사용자 유형 ("beginner" or "advanced")
        learning_context: 학습 맥락 정보
        vector_materials: 벡터 DB에서 검색한 관련 자료 (추후 활용)
        
    Returns:
        생성된 이론 설명 대본 (JSON 문자열)
    """
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("이론 생성 도구 시작")
        
        # 1. AI 클라이언트 관리자 가져오기
        ai_manager = get_ai_client_manager()
        
        # 2. 현재 섹션 데이터 추출
        current_section = _get_current_section_data(chapter_data, learning_context)
        if not current_section:
            raise ValueError("현재 섹션 데이터를 찾을 수 없습니다.")
        
        # 3. LangChain 프롬프트 템플릿 생성
        system_template, user_template = _create_prompt_templates(user_type, learning_context)
        
        # 4. 프롬프트 데이터 준비
        prompt_data = _prepare_prompt_data(chapter_data, current_section, learning_context)
        
        # 5. Messages 생성
        system_message = SystemMessage(content=system_template.format(**prompt_data))
        user_message = HumanMessage(content=user_template.format(
            chapter_number=prompt_data["chapter_number"],
            chapter_title=prompt_data["chapter_title"],
            section_number=prompt_data["section_number"],
            section_title=prompt_data["section_title"]
        ))
        
        # 6. AI 컨텐츠 생성 (AI Client Manager가 LangSmith 추적 관리)
        generated_response = ai_manager.generate_json_content_with_messages(
            messages=[system_message, user_message]
        )
        
        # 7. 응답 검증 및 표준화
        if isinstance(generated_response, str):
            try:
                generated_response = json.loads(generated_response)
            except json.JSONDecodeError:
                logger.warning("JSON 파싱 실패, 기본 응답 생성")
                raise ValueError("AI 응답을 JSON으로 파싱할 수 없습니다.")
        
        validated_response = _validate_response(generated_response, chapter_data, current_section, user_type)
        
        logger.info("이론 생성 도구 완료")
        return json.dumps(validated_response, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"AI 이론 설명 생성 실패: {str(e)}")
        
        # Fallback 응답 생성
        return _generate_fallback_response(chapter_data, user_type, str(e))


def _create_prompt_templates(user_type: str, learning_context: Dict[str, Any]) -> tuple:
    """
    사용자 유형과 학습 맥락에 따른 프롬프트 템플릿 생성
    
    Args:
        user_type: 사용자 유형 ("beginner" or "advanced")
        learning_context: 학습 맥락 정보
        
    Returns:
        (system_template, user_template) 튜플
    """
    
    # 재학습 여부에 따른 추가 지시사항
    retry_instruction = ""
    if learning_context.get('is_retry_session', False):
        retry_instruction = "이전 학습에서 어려움을 겪었으므로 더욱 쉽고 친근하게 설명해주세요. "
    
    # JSON 형식 정의 (중괄호 이스케이프 처리)
    json_format = """
**응답 형식** (반드시 JSON으로만 응답):
{{
  "content_type": "theory",
  "chapter_info": {{
    "chapter_number": {chapter_number},
    "title": "{chapter_title}",
    "user_type": "{user_type}"
  }},
  "section_info": {{
    "section_number": {section_number},
    "title": "{section_title}"
  }},
  "main_content": "상세한 이론 설명 (200-400자)",
  "key_points": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
  "analogy": "이해하기 쉬운 비유 설명",
  "examples": ["실제 사례 1", "실제 사례 2"],
  "user_guidance": "학습자를 위한 가이드",
  "next_step_preview": "다음 단계 미리보기"
}}"""
    
    # 사용자 유형별 시스템 프롬프트 (학습 내용 포함)
    if user_type == "beginner":
        system_template = PromptTemplate(
            input_variables=[
                "chapter_number", "chapter_title", "user_type", "section_number", "section_title",
                "learning_objectives", "full_content", "key_points", "analogy", 
                "session_count", "is_retry_session"
            ],
            template=f"""당신은 AI 학습을 처음 시작하는 사용자를 위한 친근한 튜터입니다. {retry_instruction}

**학습 내용 정보**:
- 챕터 {{chapter_number}}: {{chapter_title}}
- 섹션 {{section_number}}: {{section_title}}
- 학습 목표: {{learning_objectives}}
- 세션 {{session_count}}회차 (재학습: {{is_retry_session}})

**참고할 기존 내용**:
{{full_content}}

**핵심 포인트**:
{{key_points}}

**기존 비유**: {{analogy}}

**생성 지침**:
- 친근하고 쉬운 언어 사용 (이모지 활용)
- 일상생활 비유 중심 설명
- "~해보겠습니다", "~할게요" 친근한 톤
- 기술 용어는 반드시 쉬운 말로 풀어서 설명
- 기존 내용을 바탕으로 완전히 새로운 방식으로 재구성

{json_format}"""
        )
    else:  # advanced
        system_template = PromptTemplate(
            input_variables=[
                "chapter_number", "chapter_title", "user_type", "section_number", "section_title",
                "learning_objectives", "full_content", "key_points", "analogy", 
                "session_count", "is_retry_session"
            ],
            template=f"""당신은 실무 응용형 사용자를 위한 효율적인 튜터입니다. {retry_instruction}

**학습 내용 정보**:
- 챕터 {{chapter_number}}: {{chapter_title}}
- 섹션 {{section_number}}: {{section_title}}
- 학습 목표: {{learning_objectives}}
- 세션 {{session_count}}회차 (재학습: {{is_retry_session}})

**참고할 기존 내용**:
{{full_content}}

**핵심 포인트**:
{{key_points}}

**기존 비유**: {{analogy}}

**생성 지침**:
- 효율적이고 핵심적인 설명
- 기술적 배경을 고려한 논리적 구조
- 실무 활용 관점 중심
- "핵심 포인트", "실무에서는" 표현 활용
- 기존 내용을 바탕으로 실무적 관점에서 재구성

{json_format}"""
        )
    
    # 사용자 프롬프트 템플릿 (간단한 요청으로 변경)
    user_template = PromptTemplate(
        input_variables=[
            "chapter_number", "chapter_title", "section_number", "section_title"
        ],
        template="""챕터 {chapter_number}의 섹션 {section_number}번 '{section_title}'에 대한 이론 설명을 생성해주세요."""
    )
    
    return system_template, user_template


def _prepare_prompt_data(
    chapter_data: Dict[str, Any],
    current_section: Dict[str, Any],
    learning_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    프롬프트 템플릿에 사용할 데이터 준비
    
    Args:
        chapter_data: 챕터 데이터
        current_section: 현재 섹션 데이터
        learning_context: 학습 맥락
        
    Returns:
        프롬프트 데이터 딕셔너리
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
    analogy = theory_data.get('analogy', '')
    
    return {
        "chapter_number": chapter_number,
        "chapter_title": chapter_title,
        "section_number": section_number,
        "section_title": section_title,
        "user_type": learning_context.get("user_type", "beginner"),
        "learning_objectives": ', '.join(learning_objectives) if learning_objectives else '없음',
        "full_content": full_content,
        "key_points": '\n'.join([f"- {point}" for point in key_points]) if key_points else '없음',
        "analogy": f"**기존 비유**: {analogy}" if analogy else "",
        "session_count": learning_context.get('session_count', 0) + 1,
        "is_retry_session": '예' if learning_context.get('is_retry_session', False) else '아니오'
    }


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