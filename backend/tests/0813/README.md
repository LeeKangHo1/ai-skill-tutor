# AI 학습 도구 테스트 (2025-08-13)

## 📋 개요

8월 13일자 퀴즈 생성 시스템 LangChain LCEL 파이프라인 전환에 따른 이론툴과 퀴즈툴 테스트 파일들입니다.

## 🛠️ 주요 기능

- **이론 생성**: ChatGPT를 사용한 AI 이론 설명 생성
- **객관식 퀴즈**: ChatGPT를 사용한 객관식 문제 생성
- **주관식 퀴즈**: ChatGPT를 사용한 주관식 문제 생성

## 📁 파일 구조

```
backend/tests/0813/
├── README.md                    # 이 파일
├── run_tests.py                 # 테스트 런처 (메인 실행 파일)
├── quick_test.py                # 빠른 테스트 (3개 기능 순차 실행)
├── test_integrated_tools.py     # 대화형 통합 테스트
├── test_theory_tools_chatgpt.py # 이론 도구 단위 테스트
└── test_quiz_tools_chatgpt.py   # 퀴즈 도구 단위 테스트
```

## 🚀 실행 방법

### 1. 메인 런처 실행 (권장)

```bash
cd backend/tests/0813
python run_tests.py
```

메뉴에서 선택할 수 있는 옵션:
- `1`: 환경 설정 확인 (Python, 모듈, 환경변수, 데이터 파일)
- `2`: 빠른 테스트 실행 (이론+객관식+주관식 순차 실행)
- `3`: 대화형 테스트 실행 (개별 기능 선택 가능)

### 2. 빠른 테스트 직접 실행

```bash
cd backend/tests/0813
python quick_test.py
```

이론 생성 → 객관식 퀴즈 → 주관식 퀴즈 순서로 자동 실행됩니다.

### 3. 대화형 테스트 직접 실행

```bash
cd backend/tests/0813
python test_integrated_tools.py
```

메뉴에서 개별 기능을 선택해서 테스트할 수 있습니다.

## ⚙️ 환경 설정 요구사항

### 필수 Python 패키지
```
langchain==0.3.27
langchain-core==0.3.72
langchain-openai
openai
python-dotenv
pydantic
```

### 환경변수 설정
```bash
# .env 파일에 다음 변수들을 설정하세요
OPENAI_API_KEY=your_openai_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here  # 선택사항
```

### 데이터 파일
다음 파일들이 존재해야 합니다:
- `data/chapters/chapter_01.json` (이론 생성, 객관식 퀴즈용)
- `data/chapters/chapter_05.json` (주관식 퀴즈용)

## 🧪 테스트 내용

### 1. 이론 생성 테스트
- **대상**: 챕터 1 섹션 1 (AI 기초 개념)
- **사용자 유형**: beginner
- **출력**: 자연스러운 텍스트 형태의 이론 설명

### 2. 객관식 퀴즈 테스트
- **대상**: 챕터 1 섹션 2 (객관식 퀴즈 섹션)
- **사용자 유형**: beginner
- **출력**: JSON 형태의 객관식 문제 (문제, 선택지, 정답, 해설)

### 3. 주관식 퀴즈 테스트
- **대상**: 챕터 5 섹션 1 (주관식 퀴즈 섹션)
- **사용자 유형**: beginner
- **출력**: JSON 형태의 주관식 문제 (문제, 예시 답안, 평가 기준)

## 🔧 기술적 특징

### LangChain LCEL 파이프라인
- **이론 도구**: `PromptTemplate | ChatOpenAI | StrOutputParser`
- **퀴즈 도구**: `PromptTemplate | ChatOpenAI | JsonOutputParser`
- **직접 OpenAI API 호출**: 별도 클라이언트 클래스 없이 LangChain 사용

### JSON 스키마 검증
- Pydantic 스키마를 사용한 퀴즈 응답 구조 보장
- 기존 프론트엔드 호환성 유지

### 사용자 유형별 맞춤화
- **beginner**: 친근한 톤, 쉬운 설명
- **advanced**: 실무 중심, 효율적 설명

### 간소화된 아키텍처
- ChatGPT 클라이언트, AI 클라이언트 매니저, Gemini 클라이언트 제거
- LangChain을 통한 직접 OpenAI API 호출로 단순화

## 🐛 문제 해결

### 환경변수 오류
```bash
# .env 파일이 프로젝트 루트에 있는지 확인
ls -la ../../.env

# 환경변수가 제대로 로드되는지 확인
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:10] if os.getenv('OPENAI_API_KEY') else 'None')"
```

### 모듈 임포트 오류
```bash
# 가상환경 활성화 확인
# Windows
venv\Scripts\activate

# 필요한 패키지 설치
pip install langchain langchain-openai openai python-dotenv pydantic
```

### OpenAI API 연결 오류
```bash
# API 키 확인
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows

# 간단한 연결 테스트
python -c "
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini', openai_api_key=os.getenv('OPENAI_API_KEY'))
print(model.invoke('Hello').content)
"
```

### 데이터 파일 오류
```bash
# 데이터 파일 존재 확인
ls -la ../../data/chapters/chapter_01.json
ls -la ../../data/chapters/chapter_05.json
```

## 📊 예상 출력 예시

### 이론 생성 결과
```
✅ 생성된 이론 설명:
----------------------------------------
안녕하세요! 오늘은 인공지능(AI)의 기본 개념에 대해 알아보겠습니다.

인공지능이란 컴퓨터가 사람처럼 생각하고 학습할 수 있도록 만든 기술입니다...
----------------------------------------
```

### 객관식 퀴즈 결과
```json
{
  "type": "multiple_choice",
  "question": "인공지능의 정의로 가장 적절한 것은?",
  "options": {
    "option_1": "컴퓨터가 사람처럼 생각하는 기술",
    "option_2": "단순한 계산을 빠르게 하는 기술",
    "option_3": "인터넷을 통해 정보를 검색하는 기술",
    "option_4": "게임을 만드는 기술"
  },
  "correct_answer": "option_1",
  "explanation": "인공지능은 컴퓨터가 인간의 지능을 모방하여..."
}
```

## 📝 참고사항

- 모든 테스트는 실제 ChatGPT API를 호출합니다
- API 사용량에 따른 비용이 발생할 수 있습니다
- 네트워크 연결이 필요합니다
- 테스트 실행 시간은 API 응답 속도에 따라 달라집니다