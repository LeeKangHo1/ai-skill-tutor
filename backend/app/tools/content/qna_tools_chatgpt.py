# backend/app/tools/content/qna_tools_chatgpt.py

import logging
import os
import json
from typing import Dict, Any, List

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool

from app.tools.external.vector_search_tools import search_qna_materials


def qna_generation_tool(user_question: str, current_context: Dict[str, Any] = None) -> str:
    """
    LCEL 파이프라인 기반 QnA 답변 생성
    - PromptTemplate | ChatOpenAI (with tools) | StrOutputParser 구조
    - Function calling 방식으로 벡터 검색 자동 수행
    
    Args:
        user_question: 사용자 질문
        current_context: 현재 학습 컨텍스트
        
    Returns:
        생성된 답변 텍스트
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("QnA 답변 생성 시작 (LCEL 파이프라인)")
        print(f"[QnA 도구] LCEL 파이프라인 기반 답변 생성 시작")
        
        # 1. QnA 컨텍스트 메타데이터 로드
        context_metadata = _load_qna_context_metadata()
        
        # 2. 프롬프트 템플릿 생성
        prompt_template = _create_qna_prompt_template()
        
        # 3. ChatGPT 모델 (벡터 검색 도구 바인딩)
        model = _get_chatgpt_model_with_tools()
        
        # 4. 출력 파서
        output_parser = StrOutputParser()
        
        # 5. LCEL 파이프라인 구성
        qna_chain = prompt_template | model | output_parser
        
        # 6. 파이프라인 실행
        print(f"[QnA 도구] LCEL 파이프라인 실행 중...")
        
        response = qna_chain.invoke({
            "user_question": user_question,
            "learning_context": json.dumps(context_metadata, ensure_ascii=False, indent=2),
            "current_chapter": current_context.get("chapter", "알 수 없음") if current_context else "알 수 없음",
            "current_section": current_context.get("section", "알 수 없음") if current_context else "알 수 없음"
        })
        
        logger.info("QnA 답변 생성 완료 (LCEL 파이프라인)")
        print(f"[QnA 도구] LCEL 파이프라인 답변 생성 완료 - 길이: {len(response)}자")
        
        return response
        
    except Exception as e:
        logger.error(f"QnA 답변 생성 실패: {str(e)}")
        print(f"[QnA 도구] LCEL 파이프라인 오류: {str(e)}")
        return _generate_error_response(user_question, str(e))


@tool
def vector_search_qna_tool(search_query: str) -> List[Dict[str, Any]]:
    """
    QnA용 벡터 검색 도구 (LangChain Tool for Function Calling)
    
    Args:
        search_query: 검색할 쿼리 텍스트
        
    Returns:
        검색된 벡터 자료 리스트
    """
    logger = logging.getLogger(__name__)
    logger.info(f"벡터 검색 도구 호출 - 쿼리: {search_query[:50]}...")
    print(f"[벡터 검색] 검색 시작 - 쿼리: {search_query}")
    
    try:
        # 기존 search_qna_materials() 함수 활용
        search_results = search_qna_materials(search_query)
        
        logger.info(f"벡터 검색 완료 - {len(search_results)}개 결과 반환")
        
        if search_results:
            print(f"[벡터 검색] 성공 - {len(search_results)}개 결과 발견")
            
            # 검색 결과 요약 로그
            for i, result in enumerate(search_results, 1):
                chunk_type = result.get('chunk_type', 'unknown')
                similarity_score = result.get('similarity_score', 0)
                quality_score = result.get('content_quality_score', 0)
                keywords = result.get('primary_keywords', [])
                
                print(f"[벡터 검색] 결과 {i}: {chunk_type} (유사도: {similarity_score:.3f}, 품질: {quality_score})")
                print(f"[벡터 검색]   키워드: {', '.join(keywords) if keywords else '없음'}")
        else:
            print(f"[벡터 검색] 결과 없음")
        
        # Function calling에서 사용하기 위해 간소화된 형태로 반환
        simplified_results = []
        for result in search_results:
            simplified_result = {
                "content": result["content"],
                "type": result["chunk_type"],
                "keywords": result["primary_keywords"],
                "quality": result["content_quality_score"],
                "similarity": round(result["similarity_score"], 3),
                "source": f"챕터 {result['chapter']}-{result['section']}"
            }
            simplified_results.append(simplified_result)
        
        return simplified_results
        
    except Exception as e:
        logger.error(f"벡터 검색 도구 실패: {str(e)}")
        print(f"[벡터 검색] 오류: {str(e)}")
        return []


def _load_qna_context_metadata() -> Dict[str, Any]:
    """
    QnA용 컨텍스트 메타데이터 로드
    
    Returns:
        로드된 메타데이터 딕셔너리
    """
    try:
        # 현재 파일 기준으로 backend/data 경로 설정
        current_dir = os.path.dirname(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        metadata_path = os.path.join(backend_dir, "data", "qna_context_metadata.json")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"[QnA 도구] 컨텍스트 메타데이터 로드 완료 - {len(metadata.get('chapters', []))}개 챕터")
        return metadata
        
    except Exception as e:
        logging.getLogger(__name__).error(f"QnA 컨텍스트 메타데이터 로드 실패: {str(e)}")
        print(f"[QnA 도구] 메타데이터 로드 실패: {str(e)}")
        
        # 폴백: 기본 컨텍스트 반환
        return {
            "learning_context": {
                "curriculum_overview": "AI 활용법 학습 과정"
            },
            "chapters": []
        }


def _create_qna_prompt_template() -> PromptTemplate:
    """
    QnA용 프롬프트 템플릿 생성 (Function Calling 지원)
    
    Returns:
        PromptTemplate 객체
    """
    
    template = """당신은 AI 활용법 학습 튜터의 QnA 전문 어시스턴트입니다.

=== 학습 커리큘럼 컨텍스트 ===
{learning_context}

현재 학습 위치: 챕터 {current_chapter}, 섹션 {current_section}

=== 주요 역할 ===
1. 사용자의 AI 관련 질문에 정확하고 친근하게 답변
2. 필요시 벡터 검색을 통해 관련 학습 자료 참조
3. 학습 맥락에 맞는 실용적인 답변 제공

=== 벡터 검색 사용 가이드라인 ===
- 사용자 질문이 위 챕터들의 키워드와 관련있다면 vector_search_qna_tool을 사용하여 관련 자료를 검색하세요
- 구체적인 AI 개념, 기술, 도구에 대한 질문이면 벡터 검색을 활용하세요
- 간단한 인사말이나 감사 표현에는 벡터 검색을 사용하지 마세요
- 일반적인 대화나 학습과 무관한 질문에는 벡터 검색을 사용하지 마세요

=== 답변 가이드라인 ===
- 친근하고 이해하기 쉬운 톤 사용 (적절한 이모지 활용)
- 구체적인 예시와 함께 설명
- 실무에 활용할 수 있는 실용적인 정보 제공
- 복잡한 개념은 단계별로 설명
- AI 입문자도 이해할 수 있는 수준으로 설명
- 답변 길이: 200-800자 정도 (너무 길지 않게)

=== 사용자 질문 ===
{user_question}

위 질문에 대해 적절한 답변을 생성해주세요. 필요하다면 벡터 검색을 활용하세요."""

    return PromptTemplate(
        template=template,
        input_variables=["learning_context", "current_chapter", "current_section", "user_question"]
    )


def _get_chatgpt_model_with_tools() -> ChatOpenAI:
    """
    Function Calling을 지원하는 ChatGPT 모델 초기화
    
    Returns:
        벡터 검색 도구가 바인딩된 ChatOpenAI 모델
    """
    
    # ChatGPT 모델 초기화
    model = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.3,  # QnA는 일관성 있는 답변이 중요
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
    )
    
    # 벡터 검색 도구 바인딩
    model_with_tools = model.bind_tools([vector_search_qna_tool])
    
    return model_with_tools


def _generate_error_response(user_question: str, error_msg: str) -> str:
    """
    오류 발생 시 기본 응답 생성
    
    Args:
        user_question: 사용자 질문
        error_msg: 오류 메시지
        
    Returns:
        오류 대본 텍스트
    """
    
    return f"""죄송합니다. 질문에 답변하는 중 일시적인 문제가 발생했습니다. 😅

**질문**: {user_question}

**문제 상황**: 시스템에 일시적인 오류가 발생했습니다.

**해결 방법**:
1. 잠시 후 다시 질문해 주세요
2. 질문을 다르게 표현해서 다시 시도해 보세요
3. 더 구체적인 질문으로 바꿔서 물어보세요

다른 질문이 있으시면 언제든 말씀해 주세요! 🤖✨"""