# backend/app/tools/content/qna_tools_chatgpt.py

import logging
import os
import json
from typing import Dict, Any, List

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from app.tools.external.vector_search_tools import search_qna_materials


def qna_generation_tool(user_question: str, current_context: Dict[str, Any] = None) -> str:
    """
    LangChain Agent 기반 QnA 답변 생성
    - create_tool_calling_agent + AgentExecutor 사용
    - Function calling을 통한 완전한 벡터 검색 실행
    
    Args:
        user_question: 사용자 질문
        current_context: 현재 학습 컨텍스트
        
    Returns:
        생성된 답변 텍스트
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("QnA 답변 생성 시작 (LangChain Agent)")
        print(f"[QnA Agent] LangChain Agent 기반 답변 생성 시작")
        
        # 1. QnA 컨텍스트 메타데이터 로드
        context_metadata = _load_qna_context_metadata()
        
        # 2. ChatGPT 모델 초기화
        model = _get_chatgpt_model()
        
        # 3. 프롬프트 템플릿 생성
        prompt_template = _create_agent_prompt_template(context_metadata, current_context)
        
        # 4. 벡터 검색 도구 리스트
        tools = [vector_search_qna_tool]
        
        # 5. LangChain Agent 생성
        agent = create_tool_calling_agent(model, tools, prompt_template)
        
        # 6. AgentExecutor 생성
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,  # 디버깅용
            handle_parsing_errors=True,
            max_iterations=1,  # 최대 1번의 도구 호출 허용
            early_stopping_method="generate"  # 답변 생성 후 중단
        )
        
        print(f"[QnA Agent] Agent 실행 중...")
        
        # 7. Agent 실행
        response = agent_executor.invoke({
            "input": user_question
        })
        
        # 8. 결과 추출
        final_answer = response.get("output", "")
        
        logger.info("QnA 답변 생성 완료 (LangChain Agent)")
        print(f"[QnA Agent] Agent 답변 생성 완료 - 길이: {len(final_answer)}자")
        
        return final_answer
        
    except Exception as e:
        logger.error(f"QnA Agent 답변 생성 실패: {str(e)}")
        print(f"[QnA Agent] Agent 실행 오류: {str(e)}")
        return _generate_error_response(user_question, str(e))


@tool
def vector_search_qna_tool(search_query: str) -> List[Dict[str, Any]]:
    """
    QnA용 벡터 검색 도구 (LangChain Tool for Agent)
    
    Args:
        search_query: 검색할 쿼리 텍스트
        
    Returns:
        검색된 벡터 자료 리스트
    """
    logger = logging.getLogger(__name__)
    logger.info(f"벡터 검색 도구 호출 - 쿼리: {search_query[:50]}...")
    print(f"[벡터 검색] Agent가 벡터 검색 시작 - 쿼리: '{search_query}'")
    
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
                content_preview = result.get('content', '')[:100]
                
                print(f"[벡터 검색] 결과 {i}: {chunk_type} (유사도: {similarity_score:.3f})")
                print(f"[벡터 검색]   내용: {content_preview}...")
        else:
            print(f"[벡터 검색] 결과 없음")
        
        # Agent가 이해하기 쉬운 형태로 반환
        agent_friendly_results = []
        for result in search_results:
            agent_result = {
                "content": result["content"],
                "type": result["chunk_type"],
                "keywords": result["primary_keywords"],
                "quality": result["content_quality_score"],
                "similarity": round(result["similarity_score"], 3),
                "source": f"챕터 {result['chapter']}-{result['section']}"
            }
            agent_friendly_results.append(agent_result)
        
        return agent_friendly_results
        
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
        
        print(f"[QnA Agent] 컨텍스트 메타데이터 로드 완료 - {len(metadata.get('chapters', []))}개 챕터")
        return metadata
        
    except Exception as e:
        logging.getLogger(__name__).error(f"QnA 컨텍스트 메타데이터 로드 실패: {str(e)}")
        print(f"[QnA Agent] 메타데이터 로드 실패: {str(e)}")
        
        # 폴백: 기본 컨텍스트 반환
        return {
            "learning_context": {
                "curriculum_overview": "AI 활용법 학습 과정"
            },
            "chapters": []
        }


def _create_agent_prompt_template(context_metadata: Dict[str, Any], current_context: Dict[str, Any] = None) -> ChatPromptTemplate:
    """
    Agent용 프롬프트 템플릿 생성
    
    Args:
        context_metadata: QnA 컨텍스트 메타데이터
        current_context: 현재 학습 컨텍스트
        
    Returns:
        ChatPromptTemplate 객체
    """
    
    # 메타데이터를 JSON 문자열로 변환하고 중괄호 이스케이프 처리
    learning_context_str = json.dumps(context_metadata, ensure_ascii=False, indent=2)
    # ChatPromptTemplate에서 중괄호를 변수로 인식하지 않도록 이스케이프 처리
    learning_context_str = learning_context_str.replace("{", "{{").replace("}", "}}")
    
    # 현재 학습 위치 정보
    current_chapter = current_context.get("chapter", "알 수 없음") if current_context else "알 수 없음"
    current_section = current_context.get("section", "알 수 없음") if current_context else "알 수 없음"
    
    system_message = f"""당신은 AI 활용법 학습 튜터의 QnA 전문 어시스턴트입니다.

=== 학습 커리큘럼 컨텍스트 ===
{learning_context_str}

현재 학습 위치: 챕터 {current_chapter}, 섹션 {current_section}

=== 주요 역할 ===
1. 사용자의 AI 관련 질문에 정확하고 친근하게 답변
2. 필요시 vector_search_qna_tool을 사용하여 관련 학습 자료 검색
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

=== 도구 사용법 ===
벡터 검색이 필요하다고 판단되면 vector_search_qna_tool을 호출하세요.
검색 결과를 바탕으로 정확하고 상세한 답변을 생성해주세요."""

    # ChatPromptTemplate 생성 (Agent 전용 형식)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")  # Agent가 도구 사용 기록을 저장하는 곳
    ])
    
    return prompt


def _get_chatgpt_model() -> ChatOpenAI:
    """
    ChatGPT 모델 초기화 (Agent용)
    
    Returns:
        ChatOpenAI 모델 객체
    """
    
    model = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.3,  # QnA는 일관성 있는 답변이 중요
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
    )
    
    return model


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