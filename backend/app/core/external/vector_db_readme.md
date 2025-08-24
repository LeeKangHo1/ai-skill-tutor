# ChromaDB 벡터 데이터베이스 사용 가이드

## 📋 개요

AI 활용법 학습 튜터의 이론 생성 품질 향상을 위해 ChromaDB 벡터 데이터베이스를 사용합니다.
학습 콘텐츠를 벡터화하여 저장하고, 이론 생성 시 관련 자료를 검색하여 활용합니다.

## 🏗️ 구조

```
backend/app/core/external/
├── chroma_client.py      # ChromaDB 연결 관리
├── vector_db_setup.py    # 데이터 삽입 및 초기화
├── README.md            # 이 파일
backend/data/
├── chroma_db/           # ChromaDB 데이터 저장소 (자동 생성)
├── chapters_vec/        # 삽입할 JSON 데이터 폴더
└── vector_insertion_log.json  # 삽입 기록 파일 (자동 생성)
```

## 🚀 벡터 DB 구축 방법

### 1단계: 환경 설정

**.env 파일에 OpenAI API 키 설정:**
```bash
OPENAI_API_KEY=your_openai_api_key_here
# CHROMA_DB_PATH=backend/data/chroma_db  # 선택사항 (기본값 사용시 생략)
```

### 2단계: 학습 데이터 준비

**`backend/data/chapters_vec/` 폴더에 JSON 파일들 배치:**
```
backend/data/chapters_vec/
├── chapter_01_content.json
├── chapter_02_content.json
├── any_filename.json      # 파일명은 자유롭게
└── ...
```

**JSON 파일 형식 예시:**
```json
[
  {
    "id": "chapter_1-section_1-chunk_1-gemini",
    "chunk_type": "core_concept",
    "chapter": 1,
    "section": 1,
    "user_type": ["beginner"],
    "primary_keywords": ["인공지능", "AI 정의", "머신러닝"],
    "content_category": "definition",
    "content_quality_score": 98,
    "source_url": "https://example.com",
    "generated_by_llm_name": "Gemini-2.5Pro",
    "content": "실제 학습 콘텐츠 텍스트..."
  }
]
```

### 3단계: 벡터 DB 구축 실행

**명령어:**
```bash
# backend 폴더에서 실행
cd backend
python app/core/external/vector_db_setup.py
```

**실행 결과:**
```
=== AI 튜터 벡터 데이터베이스 구축 시작 ===
✅ 벡터 데이터베이스 구축 성공!
📊 총 문서 수: 15
📈 청크 타입별 통계: {'core_concept': 8, 'analogy': 4, 'practical_example': 3}
=== 벡터 데이터베이스 구축 완료 ===
```

## 📊 데이터 검증

### 삽입 기록 확인

**`backend/data/vector_insertion_log.json`** 파일이 자동 생성됩니다:
```json
{
  "insertion_date": "2025-08-24T10:30:45",
  "total_chunks": 15,
  "successful_insertions": 14,
  "failed_insertions": 1,
  "results": [
    {
      "id": "chapter_1-section_1-chunk_1-gemini",
      "chunk_type": "core_concept",
      "user_type": ["beginner"],
      "section_title": "AI는 어떻게 우리 삶에 들어와 있을까?",
      "chapter": 1,
      "section": 1,
      "inserted_at": "2025-08-24T10:30:46",
      "status": "success"
    }
  ]
}
```

### 데이터베이스 상태 확인

**Python으로 상태 확인:**
```python
from app.core.external.vector_db_setup import VectorDBSetup

db_setup = VectorDBSetup()
status = db_setup.verify_database()
print(status)
```

## 🔍 벡터 검색 동작 방식

### 검색 우선순위

1. **core_concept 청크**
   - `content_quality_score >= 90점`
   - 점수 높은 순으로 최대 3개 선택

2. **기타 청크 타입** (analogy, practical_example, technical_detail)
   - `content_quality_score >= 90점`
   - 점수 높은 순으로 2개 선택

### 폴백 전략

```python
# 벡터 검색 결과가 부족한 경우
core_chunks = search_core_concept(chapter=1, section=1)

if len(core_chunks) == 0:
    # 기존 JSON 파일 (backend/data/chapters/chapter_01.json) 사용
    return use_fallback_json_data()
else:
    # 벡터 검색 결과 사용
    return use_vector_search_results()
```

## 🛠️ 문제 해결

### 일반적인 오류

**1. OpenAI API 키 오류**
```
ERROR: OpenAI API key not found
해결: .env 파일에 OPENAI_API_KEY 설정 확인
```

**2. JSON 파일 없음**
```
ERROR: chapters_vec 폴더에 JSON 파일이 없음
해결: backend/data/chapters_vec/ 폴더에 JSON 파일 배치
```

**3. 권한 오류**
```
ERROR: Permission denied creating chroma_db directory
해결: backend/data/ 폴더 쓰기 권한 확인
```

### 데이터베이스 초기화

**전체 데이터 삭제 후 재구축:**
```python
from app.core.external.chroma_client import get_chroma_client

client = get_chroma_client()
client.reset_database()  # 주의: 모든 데이터 삭제

# 이후 다시 구축
python app/core/external/vector_db_setup.py
```

## 📈 성능 정보

- **임베딩 모델**: OpenAI `text-embedding-3-large`
- **벡터 차원**: 3,072차원
- **저장 방식**: 로컬 파일 기반 (Persistent)
- **예상 용량**: 청크 100개당 약 20-30MB

## ⚡ 다음 단계

벡터 DB 구축 완료 후:
1. `vector_search_tools.py`로 검색 기능 테스트
2. `theory_educator_agent.py`에 벡터 검색 통합
3. 이론 생성 품질 개선 확인