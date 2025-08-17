# State 설계 v2.0 업데이트 내용

## 📝 랭그래프 State 설계 v2.0 변경사항

### 🔄 TutorState 구조 개편

#### 퀴즈 관련 필드 완전 재설계
**기존 (v1.3):**
```python
current_question_type: str        # "multiple_choice": 객관식, "subjective": 주관식
current_question_number: int      # 문제 번호 (기본키)
current_question_content: str     # 현재 문제 내용
current_question_answer: str      # 사용자 답변
is_answer_correct: int            # 객관식: 1(정답)/0(오답), 주관식: 0~100(점수)
```

**신규 (v2.0):**
```python
# === 퀴즈 관련 정보 ===
quiz_type: str                        # "multiple_choice" 또는 "subjective"
quiz_content: str                     # 퀴즈 문제 내용
quiz_options: List[str]               # 객관식: ["선택지1", "선택지2", "선택지3", "선택지4"], 주관식: []
quiz_correct_answer: Any              # 객관식: 정답 번호(int), 주관식: None
quiz_explanation: str                 # 객관식: 정답 해설, 주관식: ""
quiz_sample_answer: str               # 객관식: "", 주관식: 모범 답안 예시
quiz_evaluation_criteria: List[str]   # 객관식: [], 주관식: ["평가기준1", "평가기준2", "평가기준3"]
quiz_hint: str                        # 힌트 내용 (공통)
user_answer: str                      # 사용자 답변
multiple_answer_correct: bool         # 객관식 정답 여부 (True/False)
subjective_answer_score: int          # 주관식 점수 (0~100점)
```

#### 세션 관리 필드 수정
**기존:**
```python
session_decision_result: str  # "proceed": 다음 단계 진행, "retry": 현재 구간 재학습
current_session_count: int    # 현재 구간에서 학습 세션 횟수 (3회 제한)
```

**신규:**
```python
retry_decision_result: str  # "proceed": 다음 단계 진행, "retry": 현재 구간 재학습
current_session_count: int    # 현재 구간에서 학습 세션 횟수 (1회 제한)
```

#### 세션 ID 생성 방식 변경
**기존:** 복잡한 문자열 생성 (`user{id}_ch{chapter}_s{section}_{timestamp}`)
**신규:** MySQL AUTO_INCREMENT 자동 생성

### 🎯 변경 사유 및 효과

#### 1. quiz_tools_chatgpt.py JSON 형식 연동
- ChatGPT에서 생성되는 퀴즈 JSON 구조와 State 필드 일대일 매핑
- 객관식/주관식 모든 정보를 개별 필드로 분리하여 명확한 데이터 관리

#### 2. 평가 시스템 명확화
- `is_answer_correct` 통합 필드 → `multiple_answer_correct`(bool) + `subjective_answer_score`(int) 분리
- 객관식/주관식 평가 결과를 타입 안전하게 관리

#### 3. DB 연동 최적화
- `current_question_number` 삭제: DB AUTO_INCREMENT로 관리
- 세션 ID 자동 생성: 복잡한 로직 제거, DB 무결성 향상

#### 4. 네이밍 일관성
- `current_` 접두사 제거로 간결한 필드명
- `session_decision_result` → `retry_decision_result` 명확한 의미 전달

### 📊 호환성 영향

#### State Manager 업데이트 필요
- `update_quiz_info()` 메서드 전면 수정
- 퀴즈 정보 파싱 로직 개편
- 평가 결과 저장 로직 분리

#### 에이전트 업데이트 필요
- QuizGenerator: JSON 파싱 후 개별 필드 저장
- EvaluationFeedbackAgent: 객관식/주관식 분리 처리
- SessionManager: retry_decision_result 필드명 변경 대응

#### DB 스키마 호환성
- session_quizzes 테이블과의 매핑 관계 유지
- AUTO_INCREMENT 세션 ID 활용