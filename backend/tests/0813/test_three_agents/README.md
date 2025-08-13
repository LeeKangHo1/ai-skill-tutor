# 세 에이전트 통합 테스트

이 폴더는 이론 에이전트 → 퀴즈 생성 에이전트 → 피드백 에이전트의 순차 실행을 테스트하는 통합 테스트를 포함합니다.

## 테스트 파일 구성

### 1. `test_agents_integration.py`
- **목적**: 세 에이전트의 순차 실행 및 State 데이터 흐름 테스트
- **테스트 케이스**:
  - 객관식 퀴즈 플로우 (챕터 2 섹션 2)
  - 주관식 퀴즈 플로우 (챕터 5 섹션 3)
  - State 데이터 지속성 검증

### 2. `test_state_validation.py`
- **목적**: State 객체의 데이터 구조 및 업데이트 로직 검증
- **테스트 케이스**:
  - State 초기화
  - 이론 내용 추가 후 업데이트
  - 퀴즈 데이터 추가 후 업데이트
  - 사용자 답변 및 피드백 추가 후 업데이트
  - 주관식 퀴즈 State 흐름

### 3. `conftest.py`
- **목적**: pytest 설정 및 공통 fixture 정의
- **기능**:
  - 테스트 환경 설정
  - API 응답 모킹 fixture

### 4. `run_test.py`
- **목적**: 테스트 실행 스크립트
- **기능**:
  - 환경 설정
  - 순차적 테스트 실행
  - 결과 출력

## 실행 방법

### 1. 직접 실행
```bash
# 프로젝트 루트에서
cd backend/tests/0813/test_three_agents
python run_test.py
```

### 2. pytest 실행
```bash
# 프로젝트 루트에서
cd backend
pytest tests/0813/test_three_agents/ -v
```

### 3. 개별 테스트 실행
```bash
# State 검증 테스트만 실행
python tests/0813/test_three_agents/test_state_validation.py

# 통합 테스트만 실행
python tests/0813/test_three_agents/test_agents_integration.py
```

## 테스트 시나리오

### 객관식 퀴즈 플로우 (챕터 2 섹션 2)
1. **초기 State 설정**: user_id=1, beginner, chapter=2, section=2, objective
2. **이론 에이전트 실행**: theory_content 생성
3. **퀴즈 생성 에이전트 실행**: 객관식 문제 생성 (question, options, correct_answer)
4. **사용자 답변 시뮬레이션**: 정답 선택
5. **피드백 에이전트 실행**: 채점 및 피드백 생성
6. **결과 검증**: is_correct, score, can_proceed, feedback_content

### 주관식 퀴즈 플로우 (챕터 5 섹션 3)
1. **초기 State 설정**: user_id=2, beginner, chapter=5, section=3, subjective
2. **이론 에이전트 실행**: theory_content 생성
3. **퀴즈 생성 에이전트 실행**: 주관식 문제 생성 (question, type, example_answer)
4. **사용자 답변 시뮬레이션**: 프롬프트 엔지니어링 관련 답변
5. **피드백 에이전트 실행**: ChatGPT 기반 채점 및 피드백
6. **결과 검증**: score (0-100), can_proceed, feedback_content

## 검증 항목

### State 데이터 지속성
- 초기 설정값 (user_id, user_type, chapter_number 등)이 모든 단계에서 유지
- 각 에이전트 실행 후 새로운 데이터가 올바르게 추가
- 기존 데이터가 손실되지 않음

### 에이전트 출력 검증
- **이론 에이전트**: theory_content 생성 확인
- **퀴즈 생성 에이전트**: quiz_data 구조 및 내용 확인
- **피드백 에이전트**: 채점 결과 및 피드백 내용 확인

### 데이터 타입 검증
- 점수는 숫자형 (int/float)
- 점수 범위는 0-100
- Boolean 값들 (is_correct, can_proceed) 확인
- 문자열 필드들의 존재 및 길이 확인

## 주의사항

1. **환경변수**: 실제 API 키가 필요합니다 (.env 파일 설정)
2. **네트워크**: OpenAI/Google API 호출이 포함되어 실제 비용이 발생할 수 있습니다
3. **실행 시간**: AI 모델 호출로 인해 테스트 실행에 시간이 소요됩니다
4. **데이터 의존성**: 실제 학습 데이터 파일들이 존재해야 합니다

## 예상 출력

테스트 실행 시 다음과 같은 정보가 출력됩니다:

```
=== 객관식 퀴즈 플로우 테스트 시작 (챕터 2 섹션 2) ===
초기 State: State(user_id=1, user_type='beginner', ...)

--- 1단계: 이론 에이전트 실행 ---
이론 설명 결과:
- theory_content 길이: 1250
- theory_content 미리보기: AI의 기본 개념에 대해 알아보겠습니다...

--- 2단계: 퀴즈 생성 에이전트 실행 ---
퀴즈 생성 결과:
- quiz_data 존재: True
- 문제: AI의 정의는 무엇인가요?
- 선택지 개수: 4
- 정답: A

--- 3단계: 사용자 답변 시뮬레이션 (정답) ---
사용자 답변: A (정답: A)

--- 4단계: 평가 피드백 에이전트 실행 ---
평가 피드백 결과:
- is_correct: True
- score: 100
- can_proceed: True
- feedback_content 길이: 180
- feedback_content 미리보기: 정답입니다! 훌륭한 선택이었습니다...

=== 최종 State 확인 ===
- user_id: 1
- chapter_number: 2
- section_number: 2
- quiz_type: objective
- is_correct: True
- score: 100
- can_proceed: True
```