# Design Document

## Overview

이 설계는 퀴즈 생성 에이전트의 데이터 소스 개선과 QnA 에이전트의 완전한 재구현을 다룹니다. 퀴즈 생성 에이전트는 기존 JSON 파일 대신 theory_draft를 우선 참고하도록 수정하고, QnA 에이전트는 이론 생성 에이전트의 워크플로우를 참고하여 벡터 DB 기반 RAG 시스템으로 구현합니다.

## Architecture

### 전체 시스템 구조

```
QuizGenerator (수정)
├── theory_draft 우선 참조
├── chapters_metadata.json 메타데이터 활용
└── 기존 JSON 파일 (폴백 전략)

QnAResolver (완전 재구현)
├── 사용자 질문 분석
├── LangChain Function Calling
│   └── 벡터 검색 Tool 자동 호출
├── 벡터 검색 결과 기반 답변 생성
└── 폴백: LLM 일반 지식 활용
```

### 데이터 플로우

#### 퀴즈 생성 에이전트 플로우
```
1. State에서 theory_draft 확인
2. chapters_metadata.json에서 챕터/섹션 제목 로드
3. IF theory_draft 존재:
   → theory_draft + 메타데이터로 퀴즈 생성
4. ELSE:
   → 기존 JSON 파일 폴백 전략 사용
5. 퀴즈 파싱 및 State 업데이트
```

#### QnA 에이전트 플로우
```
1. 사용자 질문 추출 (최근 대화에서)
2. LangChain Function Calling 체인 실행
3. ChatGPT가 자동으로 벡터 검색 필요성 판단
4. IF 검색 필요:
   → search_qna_materials() tool 자동 호출
   → 검색 결과 기반 답변 생성
5. ELSE:
   → 일반 지식 기반 답변 생성
6. State 업데이트 (이론 생성 에이전트 패턴)
```

## Components and Interfaces

### 1. QuizGenerator 수정 사항

#### 기존 메서드 수정
- `process()`: 데이터 소스 우선순위 변경
- `_load_section_data()` → `_load_section_metadata()` + `_load_section_data_fallback()`

#### 새로운 메서드 추가
```python
def _load_section_metadata(self, chapter_number: int, section_number: int) -> Dict[str, Any]:
    """chapters_metadata.json에서 챕터/섹션 제목만 로드"""
    
def _get_theory_draft_from_state(self, state: TutorState) -> str:
    """State에서 theory_draft 추출"""
    
def _create_quiz_with_theory_draft(self, theory_draft: str, metadata: Dict[str, Any], 
                                  user_type: str, is_retry: bool) -> str:
    """theory_draft 기반 퀴즈 생성"""
```

### 2. QnAResolver 완전 재구현

#### 새로운 클래스 구조
```python
class QnAResolverAgent:
    def __init__(self):
        self.agent_name = "qna_resolver"
        self.chapter_data_path = "backend/data/chapters"
        
    def process(self, state: TutorState) -> TutorState:
        """이론 생성 에이전트 패턴 적용"""
        
    def _extract_user_question(self, state: TutorState) -> str:
        """최근 대화에서 사용자 질문 추출"""
        
    def _generate_qna_response(self, user_question: str) -> str:
        """LangChain Function Calling 기반 답변 생성"""
        
    def _create_error_response(self, error_message: str) -> str:
        """오류 시 기본 응답 생성"""
```

### 3. QnA 도구 (새로 구현)

#### 벡터 검색 활용 방식
기존 `vector_search_tools.py`의 `search_qna_materials()` 함수를 활용하여 두 가지 방식 중 선택:

**방식 1: 직접 호출**
```python
# QnAResolver 에이전트에서 직접 호출
from app.tools.external.vector_search_tools import search_qna_materials

vector_results = search_qna_materials(user_question)
```

**방식 2: LangChain Tool 래핑**
```python
# backend/app/tools/content/qna_tools_chatgpt.py

from langchain_core.tools import tool
from app.tools.external.vector_search_tools import search_qna_materials

@tool
def vector_search_qna_tool(query: str) -> List[Dict[str, Any]]:
    """기존 search_qna_materials() 함수를 LangChain tool로 래핑"""
    return search_qna_materials(query)

def qna_generation_tool(user_question: str) -> str:
    """Function Calling 기반 QnA 답변 생성"""
    # ChatGPT + 벡터 검색 tool 체인 구성
```

## Data Models

### 퀴즈 생성 데이터 모델

#### 입력 데이터 구조
```python
QuizGenerationInput = {
    "theory_draft": str,           # 우선 데이터 소스
    "section_metadata": {          # chapters_metadata.json에서
        "chapter_title": str,
        "section_title": str,
        "chapter_number": int,
        "section_number": int
    },
    "fallback_section_data": Dict, # 기존 JSON 파일 (폴백)
    "user_type": str,
    "is_retry_session": bool
}
```

### QnA 생성 데이터 모델

#### 입력 데이터 구조
```python
QnAGenerationInput = {
    "user_question": str,          # 사용자 질문
    "current_context": {           # 현재 학습 컨텍스트
        "chapter": int,
        "section": int,
        "theory_draft": str        # 참고용
    }
}
```

#### 벡터 검색 결과 구조
```python
VectorSearchResult = {
    "content": str,
    "chunk_type": str,
    "content_quality_score": int,
    "primary_keywords": List[str],
    "source_url": str,
    "chapter": int,
    "section": int,
    "distance": float,
    "similarity_score": float
}
```

## Error Handling

### 퀴즈 생성 에이전트 오류 처리

1. **theory_draft 없음**: 자동으로 폴백 전략 활성화
2. **메타데이터 로드 실패**: 기존 JSON 파일로 전환
3. **퀴즈 파싱 실패**: 오류 메시지와 함께 기본 퀴즈 제공
4. **JSON 파일 폴백 실패**: 명확한 오류 메시지 반환

### QnA 에이전트 오류 처리

1. **사용자 질문 추출 실패**: 기본 안내 메시지 제공
2. **벡터 검색 실패**: LLM 일반 지식으로 자동 전환
3. **Function Calling 오류**: 단순 텍스트 기반 답변 생성
4. **전체 시스템 오류**: 사과 메시지와 재시도 안내

## Testing Strategy

### 단위 테스트

#### 퀴즈 생성 에이전트
- `_load_section_metadata()` 메서드 테스트
- `_get_theory_draft_from_state()` 메서드 테스트
- theory_draft 우선순위 로직 테스트
- 폴백 전략 동작 테스트

#### QnA 에이전트
- `_extract_user_question()` 메서드 테스트
- 벡터 검색 tool 등록 테스트
- Function calling 체인 테스트
- State 업데이트 패턴 테스트

### 통합 테스트

#### 워크플로우 테스트
- 퀴즈 생성 → 사용자 질문 → QnA 응답 전체 플로우
- 벡터 검색 성공/실패 시나리오
- 다양한 질문 유형별 응답 품질 테스트

#### 성능 테스트
- Function calling 응답 시간 측정
- 벡터 검색 vs LLM 답변 품질 비교
- 메모리 사용량 및 State 크기 모니터링

## Implementation Details

### 퀴즈 생성 에이전트 구현 순서

1. **메타데이터 로더 구현**
   - `_load_section_metadata()` 메서드
   - chapters_metadata.json 파싱 로직

2. **theory_draft 활용 로직**
   - State에서 theory_draft 추출
   - 메타데이터와 결합한 퀴즈 생성

3. **폴백 전략 통합**
   - 기존 `_load_section_data()` 메서드를 폴백으로 활용
   - 우선순위 기반 데이터 소스 선택

4. **퀴즈 도구 수정**
   - `quiz_tools_chatgpt.py`에서 theory_draft 지원
   - 프롬프트 템플릿 분기 처리

### QnA 에이전트 구현 순서

1. **기본 구조 구현**
   - 이론 생성 에이전트 패턴 적용
   - `process()` 메서드 기본 틀 구성

2. **질문 추출 로직**
   - 대화 기록에서 최근 사용자 메시지 찾기
   - 질문 유효성 검증

3. **벡터 검색 도구 구현**
   - LangChain tool 데코레이터 적용
   - `search_qna_materials()` 함수 래핑

4. **Function Calling 체인**
   - ChatGPT + 벡터 검색 tool 통합
   - 자동 검색 판단 및 실행 로직

5. **State 업데이트 로직**
   - 이론 생성 에이전트와 동일한 패턴 적용
   - 오류 처리 및 로깅 시스템

### 파일 구조

```
backend/app/
├── agents/
│   ├── quiz_generator/
│   │   └── quiz_generator_agent.py (수정)
│   └── qna_resolver/
│       └── qna_resolver_agent.py (완전 재구현)
├── tools/
│   └── content/
│       ├── quiz_tools_chatgpt.py (수정)
│       └── qna_tools_chatgpt.py (신규)
└── tests/0812/
    ├── test_quiz_generator_v3.py
    └── test_qna_resolver_v2.py
```

## Performance Considerations

### 최적화 전략

1. **퀴즈 생성 최적화**
   - theory_draft 캐싱으로 중복 로드 방지
   - 메타데이터 파일 메모리 캐싱

2. **QnA 응답 최적화**
   - Function calling 결과 캐싱
   - 벡터 검색 결과 임시 저장

3. **메모리 관리**
   - 불필요한 벡터 검색 결과 정리
   - State 크기 최적화

### 모니터링 지표

- 퀴즈 생성 시간 (theory_draft vs 폴백)
- QnA 응답 시간 (벡터 검색 vs LLM)
- 벡터 검색 적중률
- 사용자 만족도 (답변 품질)