# backend/app/tools/content/qna_tools_chatgpt_stream.py

import logging
import os
import json
import asyncio
from typing import Dict, Any, List, AsyncGenerator
from app.tools.external.vector_search_tools import search_qna_materials_parallel

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.tools.external.vector_search_tools import search_qna_materials

logger = logging.getLogger(__name__)


async def qna_streaming_generation_tool(user_question: str, current_context: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
    """
    Agent + ChatGPT 스트리밍 분리 방식 QnA 답변 생성
    
    Phase 1: Agent가 컨텍스트 준비 (빠른 분석 + 병렬 벡터 검색)
    Phase 2: ChatGPT 직접 스트리밍 (실제 토큰 단위)
    
    Args:
        user_question: 사용자 질문
        current_context: 현재 학습 컨텍스트
        
    Yields:
        str: 실시간 스트리밍 토큰
    """
    logger.info("QnA 스트리밍 답변 생성 시작 - Agent + ChatGPT 분리 방식")
    print(f"[QnA 스트리밍] Phase 1: Agent 컨텍스트 분석 시작")
    
    try:
        # 1. QnA 컨텍스트 메타데이터 로드
        context_metadata = _load_qna_context_metadata()
        
        # Phase 1: Agent가 빠르게 컨텍스트 준비 (병렬 벡터 검색)
        agent_context = await _run_agent_for_context(user_question, current_context, context_metadata)
        
        logger.info(f"Agent 분석 완료 - 결정: {agent_context['reasoning']}")
        print(f"[QnA 스트리밍] Agent 결정: {agent_context['reasoning']}")
        
        if agent_context["should_use_vector_search"]:
            print(f"[QnA 스트리밍] 벡터 검색 완료: {len(agent_context['vector_results'])}개 결과")
        else:
            print(f"[QnA 스트리밍] 벡터 검색 불필요로 판단됨")
        
        # Phase 2: ChatGPT 직접 스트리밍 (실시간 토큰 생성)
        print(f"[QnA 스트리밍] Phase 2: ChatGPT 스트리밍 시작")
        
        async for token in _stream_final_answer(user_question, agent_context, current_context):
            yield token
            
        print(f"[QnA 스트리밍] 스트리밍 완료")
        logger.info("QnA 스트리밍 답변 생성 완료")
        
    except Exception as e:
        logger.error(f"QnA 스트리밍 답변 생성 실패: {str(e)}")
        print(f"[QnA 스트리밍] 오류: {str(e)}")
        error_message = f"죄송합니다. 답변 생성 중 오류가 발생했습니다: {str(e)}"
        async for chunk in _split_into_words(error_message):
            yield chunk


async def _run_agent_for_context(user_question: str, current_context: Dict[str, Any], context_metadata: Dict[str, Any]) -> Dict:
    """
    Agent가 컨텍스트 준비만 담당 (스트리밍 X, 빠른 결정 + 병렬 벡터 검색)
    
    Args:
        user_question: 사용자 질문
        current_context: 현재 학습 컨텍스트  
        context_metadata: QnA 컨텍스트 메타데이터
        
    Returns:
        Agent 분석 결과 및 준비된 컨텍스트
    """
    try:
        # 현재 학습 상황 정보
        current_chapter = current_context.get("chapter", "알 수 없음") if current_context else "알 수 없음"
        current_section = current_context.get("section", "알 수 없음") if current_context else "알 수 없음"

        # 메타데이터를 JSON 문자열로 변환하고 중괄호 이스케이프 처리
        learning_context_str = json.dumps(context_metadata, ensure_ascii=False, indent=2)
        learning_context_str = learning_context_str.replace("{", "{{").replace("}", "}}")
        
        # 빠른 분석용 프롬프트 (답변 생성 X, 판단만)
        analysis_prompt = f"""당신은 AI 활용법 학습 튜터의 분석 전문가입니다.

=== 학습 커리큘럼 컨텍스트 ===
{learning_context_str}

현재 학습 위치: 챕터 {current_chapter}, 섹션 {current_section}

=== 사용자 질문 ===
"{user_question}"

=== 임무 ===
다음 중 하나를 선택하고 JSON으로 응답하세요:

1. VECTOR_SEARCH_NEEDED: 벡터 검색이 필요한 경우
   - 구체적인 AI 개념, 도구, 기술에 대한 질문
   - 학습 컨텐츠와 직접 관련된 질문
   - 예: "ChatGPT란?", "프롬프트 작성법", "트랜스포머 구조"

2. NO_SEARCH_NEEDED: 벡터 검색이 불필요한 경우
   - 일반적인 대화나 인사
   - 매우 간단한 질문
   - 개인적 의견을 묻는 질문

=== 검색 쿼리 생성 규칙 ===
- 단일 개념: 1개 쿼리
- 복합 질문: 최대 3개로 분리하여 각각 검색
- 각 쿼리는 핵심 키워드 중심으로 5단어 이내
- 예시:
  * "ChatGPT란?" → ["ChatGPT"]
  * "제프리 힌튼과 트랜스포머" → ["제프리 힌튼", "트랜스포머 아키텍처"]
  * "프롬프트 작성법과 CoT 기법" → ["프롬프트 작성법", "Chain of Thought", "CoT 기법"]

=== 응답 형식 ===
{{
    "decision": "VECTOR_SEARCH_NEEDED" 또는 "NO_SEARCH_NEEDED",
    "search_queries": ["쿼리1", "쿼리2", "쿼리3"],
    "reasoning": "판단 근거 (한 줄로)"
}}

JSON만 응답하세요."""

        # 빠른 분석 실행 (스트리밍 X)
        model = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=0,  # 일관된 분석을 위해 낮은 온도
            streaming=False  # 스트리밍 비활성화
        )
        
        result = await model.ainvoke([HumanMessage(content=analysis_prompt)])
        decision_data = json.loads(result.content.strip())
        
        # 벡터 검색 필요시 병렬 실행
        vector_results = []
        if decision_data["decision"] == "VECTOR_SEARCH_NEEDED":
            search_queries = decision_data.get("search_queries", [])
            
            if search_queries:
                print(f"[QnA 분석] 병렬 벡터 검색 실행 - 쿼리 {len(search_queries)}개: {search_queries}")
                
                # 병렬 벡터 검색 실행
                vector_results = search_qna_materials_parallel(search_queries)
                print(f"[QnA 분석] 병렬 벡터 검색 결과: 총 {len(vector_results)}개")
            else:
                # 쿼리가 없으면 원본 질문으로 단일 검색
                print(f"[QnA 분석] 단일 벡터 검색 실행 - 쿼리: '{user_question}'")
                vector_results = search_qna_materials(user_question)
        
        return {
            "should_use_vector_search": decision_data["decision"] == "VECTOR_SEARCH_NEEDED",
            "search_queries": decision_data.get("search_queries", []),
            "vector_results": vector_results,
            "reasoning": decision_data["reasoning"]
        }
        
    except json.JSONDecodeError as e:
        logger.warning(f"Agent JSON 파싱 실패: {str(e)} - 기본값 사용")
        # JSON 파싱 실패 시 안전한 기본값
        return {
            "should_use_vector_search": True,  # 안전하게 검색 실행
            "search_queries": [user_question],     # 원본 질문을 검색 쿼리로 사용
            "vector_results": search_qna_materials(user_question),
            "reasoning": "JSON 파싱 실패로 안전한 기본값 적용"
        }
    
    except Exception as e:
        logger.error(f"Agent 컨텍스트 분석 실패: {str(e)}")
        # 오류 시 기본값
        return {
            "should_use_vector_search": False,
            "search_queries": [],
            "vector_results": [],
            "reasoning": f"분석 오류 발생: {str(e)}"
        }


async def _parallel_vector_search(search_queries: List[str]) -> List[Dict]:
    """
    병렬 벡터 검색 실행 및 결과 통합
    
    Args:
        search_queries: 검색 쿼리 리스트 (최대 3개)
        
    Returns:
        통합된 벡터 검색 결과 리스트
    """
    try:
        # 병렬 검색 작업 생성
        search_tasks = [
            _async_vector_search(query) 
            for query in search_queries[:3]  # 최대 3개로 제한
        ]
        
        # 병렬 실행
        all_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # 결과 통합 및 중복 제거
        combined_results = []
        seen_contents = set()
        
        for i, results in enumerate(all_results):
            if isinstance(results, Exception):
                logger.warning(f"검색 쿼리 '{search_queries[i]}' 실패: {str(results)}")
                continue
                
            if isinstance(results, list):
                for result in results:
                    content = result.get('content', '')
                    # 중복 제거 (내용 기준)
                    if content and content not in seen_contents:
                        seen_contents.add(content)
                        combined_results.append(result)
        
        # 유사도 점수 기준 정렬 (상위 5개만)
        combined_results.sort(
            key=lambda x: x.get('similarity_score', 0), 
            reverse=True
        )
        
        return combined_results[:5]
        
    except Exception as e:
        logger.error(f"병렬 벡터 검색 실패: {str(e)}")
        # 오류 시 첫 번째 쿼리로 단일 검색
        if search_queries:
            return search_qna_materials(search_queries[0])
        return []


async def _async_vector_search(query: str) -> List[Dict]:
    """
    비동기 벡터 검색 래퍼
    
    Args:
        query: 검색 쿼리
        
    Returns:
        벡터 검색 결과
    """
    try:
        # search_qna_materials가 동기 함수이므로 asyncio.to_thread 사용
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, search_qna_materials, query)
        return result
    except Exception as e:
        logger.error(f"비동기 벡터 검색 실패 (쿼리: '{query}'): {str(e)}")
        return []


async def _stream_final_answer(user_question: str, agent_context: Dict, current_context: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """
    Agent가 준비한 컨텍스트로 ChatGPT 직접 스트리밍
    
    Args:
        user_question: 사용자 질문
        agent_context: Agent가 준비한 컨텍스트
        current_context: 현재 학습 컨텍스트
        
    Yields:
        str: 실시간 ChatGPT 토큰
    """
    try:
        # 현재 학습 정보
        current_chapter = current_context.get("chapter", 1) if current_context else 1
        current_section = current_context.get("section", 1) if current_context else 1
        
        # Agent 결과에 따른 프롬프트 구성
        if agent_context["should_use_vector_search"] and agent_context["vector_results"]:
            # 벡터 검색 결과를 컨텍스트로 활용
            vector_context = ""
            for i, result in enumerate(agent_context["vector_results"][:5], 1):  # 상위 5개 사용
                vector_context += f"참고자료 {i}:\n{result['content']}\n\n"
            
            search_queries = agent_context.get("search_queries", [])
            queries_text = ", ".join(search_queries) if search_queries else user_question
            
            prompt = f"""당신은 AI 활용법 학습 튜터입니다.

=== 검색 쿼리 ===
{queries_text}

=== 검색된 관련 자료 ===
{vector_context.strip()}

=== 사용자 질문 ===
{user_question}

=== 답변 가이드라인 ===
- 위 참고자료를 바탕으로 정확하고 친근하게 답변해주세요
- AI 입문자도 이해할 수 있는 수준으로 설명해주세요
- 구체적인 예시를 들어 설명해주세요
- 참고자료에 없는 내용은 일반적인 지식으로 보완해주세요
- 답변 길이: 200-500자 정도로 적절하게 작성해주세요
- 마크다운 사용 금지: ##, ** 등의 마크다운 문법을 사용하지 마세요

친근하고 이해하기 쉽게 답변해주세요."""

        else:
            # 벡터 검색 없이 일반 답변
            prompt = f"""당신은 AI 활용법 학습 튜터입니다.

=== 현재 학습 위치 ===
챕터 {current_chapter}, 섹션 {current_section}

=== 사용자 질문 ===
{user_question}

=== 답변 가이드라인 ===
- AI 활용법과 관련된 친근하고 이해하기 쉬운 답변을 해주세요
- AI 입문자도 이해할 수 있는 수준으로 설명해주세요
- 구체적인 예시를 들어 설명해주세요
- 답변 길이: 200-500자 정도로 적절하게 작성해주세요
- 마크다운 사용 금지: ##, ** 등의 마크다운 문법을 사용하지 마세요

친근하고 이해하기 쉽게 답변해주세요."""

        # ChatGPT 직접 스트리밍
        model = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=0.3,
            streaming=True,  # 스트리밍 활성화
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
        )
        
        # 실제 토큰 단위 스트리밍
        async for chunk in model.astream([HumanMessage(content=prompt)]):
            if chunk.content:
                # 마크다운 제거 (실시간)
                clean_content = chunk.content.replace('##', '').replace('**', '')
                if clean_content:
                    yield clean_content
                    
    except Exception as e:
        logger.error(f"ChatGPT 스트리밍 실패: {str(e)}")
        error_message = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
        async for chunk in _split_into_words(error_message):
            yield chunk


async def _split_into_words(text: str) -> AsyncGenerator[str, None]:
    """
    오류 메시지용 단어 단위 스트리밍 (기존 함수 유지)
    """
    if not text:
        return
    
    # 마크다운 제거
    clean_text = text.replace('##', '').replace('**', '')
    
    # 단어 단위로 분할
    words = clean_text.split(' ')
    
    for i, word in enumerate(words):
        chunk = word
        if i < len(words) - 1:
            chunk += ' '
        
        yield chunk
        await asyncio.sleep(0.05)  # 50ms 딜레이


def _load_qna_context_metadata() -> Dict[str, Any]:
    """
    QnA용 컨텍스트 메타데이터 로드 (기존 함수 유지)
    """
    try:
        current_dir = os.path.dirname(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        metadata_path = os.path.join(backend_dir, "data", "qna_context_metadata.json")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"[QnA 분석] 컨텍스트 메타데이터 로드 완료")
        return metadata
        
    except Exception as e:
        logger.error(f"QnA 메타데이터 로드 실패: {str(e)}")
        return {"learning_context": {"curriculum_overview": "AI 활용법 학습 과정"}, "chapters": []}