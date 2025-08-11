# backend/app/tools/content/theory_tools.py

from typing import Dict, Any, List
import json
import random


def theory_generation_tool(
    chapter_data: Dict[str, Any],
    user_type: str,
    learning_context: Dict[str, Any],
    recent_sessions: List[Dict[str, str]],
    vector_materials: List[Dict[str, Any]] = None
) -> str:
    """
    JSON 챕터 데이터를 기반으로 사용자 맞춤형 이론 설명 대본 생성
    
    Args:
        chapter_data: JSON에서 로드한 챕터 데이터
        user_type: 사용자 유형 ("beginner" or "advanced")
        learning_context: 학습 맥락 정보
        recent_sessions: 최근 학습 세션 요약
        vector_materials: 벡터 DB에서 검색한 관련 자료 (추후 활용)
        
    Returns:
        생성된 이론 설명 대본 (JSON 문자열)
    """
    
    try:
        # 1. 챕터 기본 정보 추출
        chapter_info = {
            "chapter_number": chapter_data.get("chapter_number", 1),
            "title": chapter_data.get("title", ""),
            "user_type": chapter_data.get("user_type", user_type)
        }
        
        # 2. 섹션 선택 로직
        sections = chapter_data.get("sections", [])
        if not sections:
            raise ValueError("챕터에 섹션 데이터가 없습니다.")
        
        # 재학습인 경우 특정 섹션 선택, 아니면 순차 진행
        if learning_context.get("is_retry_session", False):
            # 재학습 시에는 랜덤하게 다른 섹션 선택하거나 어려웠던 부분 중심
            selected_section = _select_retry_section(sections, learning_context)
        else:
            # 첫 학습 시에는 첫 번째 섹션부터 시작
            selected_section = sections[0] if sections else {}
        
        # 3. 선택된 섹션의 이론 내용 추출
        theory_data = selected_section.get("theory", {})
        
        # 4. 사용자 유형별 맞춤 처리 (벡터 자료 고려)
        customized_content = _customize_content_for_user_type(
            theory_data, 
            user_type, 
            learning_context,
            vector_materials
        )
        
        # 5. 최종 대본 구성
        theory_draft = {
            "content_type": "theory",
            "chapter_info": chapter_info,
            "section_info": {
                "section_number": selected_section.get("section_number", 1),
                "title": selected_section.get("title", ""),
            },
            "main_content": customized_content["content"],
            "key_points": customized_content["key_points"],
            "analogy": customized_content.get("analogy", ""),
            "user_guidance": _generate_user_guidance(learning_context),
            "next_step_preview": "이제 학습한 내용을 바탕으로 퀴즈를 풀어보겠습니다."
        }
        
        return json.dumps(theory_draft, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"[theory_generation_tool] 오류 발생: {str(e)}")
        # 오류 발생 시 기본 대본 반환
        error_draft = {
            "content_type": "theory",
            "chapter_info": {"chapter_number": 1, "title": "오류", "user_type": user_type},
            "section_info": {"section_number": 1, "title": "오류 발생"},
            "main_content": f"이론 설명 생성 중 오류가 발생했습니다: {str(e)}",
            "key_points": ["오류 발생으로 인한 기본 메시지"],
            "analogy": "",
            "user_guidance": "다시 시도해 주세요.",
            "next_step_preview": ""
        }
        return json.dumps(error_draft, ensure_ascii=False, indent=2)


def _select_retry_section(sections: List[Dict[str, Any]], learning_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    재학습 시 섹션 선택 로직
    
    Args:
        sections: 챕터의 모든 섹션
        learning_context: 학습 맥락
        
    Returns:
        선택된 섹션 데이터
    """
    # 현재는 랜덤 선택, 추후 학습 이력 기반으로 개선 가능
    if sections:
        return random.choice(sections)
    return {}


def _customize_content_for_user_type(
    theory_data: Dict[str, Any], 
    user_type: str, 
    learning_context: Dict[str, Any],
    vector_materials: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    사용자 유형에 맞게 이론 내용 맞춤화
    
    Args:
        theory_data: 원본 이론 데이터
        user_type: 사용자 유형
        learning_context: 학습 맥락
        vector_materials: 벡터 DB 검색 자료 (추후 활용)
        
    Returns:
        맞춤화된 컨텐츠
    """
    
    base_content = theory_data.get("content", "")
    base_key_points = theory_data.get("key_points", [])
    analogy = theory_data.get("analogy", "")
    
    if user_type == "beginner":
        # AI 입문자용: 친근하고 쉬운 설명
        if learning_context.get("is_retry_session", False):
            content_prefix = "이번에는 조금 더 쉽게 설명해드릴게요! 😊\n\n"
        else:
            content_prefix = "안녕하세요! 차근차근 알아보겠습니다. 😊\n\n"
        
        customized_content = content_prefix + base_content
        
        # 비유가 있다면 강조해서 추가
        if analogy:
            customized_content += f"\n\n💡 **쉬운 비유로 이해하기**: {analogy}"
        
    else:  # advanced
        # 실무 응용형: 효율적이고 기술적인 설명
        if learning_context.get("is_retry_session", False):
            content_prefix = "핵심 포인트를 중심으로 다시 정리해드리겠습니다.\n\n"
        else:
            content_prefix = "핵심 개념을 효율적으로 학습해보겠습니다.\n\n"
        
        customized_content = content_prefix + base_content
        
        # 기술적 배경이 있는 사용자를 위한 추가 설명
        customized_content += "\n\n🔧 **기술적 배경**: 이러한 개념들은 실무에서 AI 도구를 선택하고 활용할 때 중요한 판단 기준이 됩니다."
        
        # 벡터 자료가 있을 경우 추가 정보 제공 (추후 구현)
        if vector_materials:
            customized_content += f"\n\n📚 **추가 참고자료**: {len(vector_materials)}개의 관련 자료를 참고했습니다."
    
    return {
        "content": customized_content,
        "key_points": base_key_points,
        "analogy": analogy
    }


def _generate_user_guidance(learning_context: Dict[str, Any]) -> str:
    """
    학습 맥락에 따른 사용자 안내 메시지 생성
    
    Args:
        learning_context: 학습 맥락 정보
        
    Returns:
        안내 메시지
    """
    if learning_context.get("is_retry_session", False):
        return "이전보다 더 자세히 설명해드렸어요. 이해가 안 되는 부분이 있으면 언제든 질문해주세요!"
    
    if learning_context.get("user_type") == "beginner":
        return "천천히 읽어보시고, 궁금한 점이 있으면 편하게 질문해주세요!"
    else:
        return "개념을 파악하셨다면 다음 단계로 진행하겠습니다."