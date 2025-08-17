# UI 설계 v2.0 수정 내용 정리

## 📋 수정 개요

기존 UI 설계 v1.3에서 v2.0으로 업데이트하면서 변경된 PRD, API, DB, State 설계에 맞춰 UI 시스템을 전면 개편했습니다.

---

## 🔄 주요 변경사항

### 1. **통합 워크플로우 기반 UI 시스템**

**기존 (v1.3):**
- 여러 API 엔드포인트로 에이전트별 개별 호출
- 복잡한 상태 관리 및 UI 전환 로직
- 에이전트 간 불일치한 응답 형식

**변경 (v2.0):**
- **단일 API**: `POST /learning/session/message`로 모든 상호작용 통합
- **SupervisorRouter 기반**: 사용자 의도에 따른 자동 에이전트 라우팅
- **통합 응답 구조**: `workflow_response` 필드로 에이전트 정보, UI 모드, 컨텐츠 통합 제공

### 2. **하이브리드 UX 시스템 도입**

**신규 추가:**
- **chat 모드**: 자유 대화 (이론 설명, 피드백, QnA 시)
- **quiz 모드**: 퀴즈 풀이 (객관식/주관식 통합)
- **자동 모드 전환**: 에이전트 응답에 따른 실시간 UI 모드 변경

**UI 모드 전환 흐름:**
```
session_start → chat (이론 설명)
theory_completed → quiz (퀴즈) OR chat (질문)
quiz_answer → chat (피드백)
quiz_and_feedback_completed → chat (세션 완료) OR chat (추가 질문)
```

### 3. **에이전트별 UI 패턴 정의**

**새로 추가된 에이전트별 UI 디자인:**

- **TheoryEducator**: 이론 설명 + 핵심 포인트 + 대표 예시 + 사용자 액션 가이드
- **QuizGenerator**: 문제 표시 + 선택지/입력창 + 힌트 버튼 + 제출 버튼
- **EvaluationFeedbackAgent**: 점수 표시 + 상세 피드백 + 다음 단계 결정 + 사용자 선택
- **QnAResolver**: 질문 표시 + 답변 + 관계도/시각화 + 관련 학습 연결
- **SessionManager**: 세션 결과 요약 + 다음 학습 안내 + 학습 기록 저장 확인

### 4. **세션 진행 단계 시각화**

**신규 컴포넌트**: `SessionProgressIndicator.vue`
- 4단계 진행 표시: 📖 이론 설명 → 📝 퀴즈 진행 → ✅ 완료 → ❓ 질문하기
- 활성/완료/비활성 상태 시각적 구분
- 연결선과 아이콘으로 직관적인 진행 상황 제공

### 5. **상태 관리 시스템 v2.0**

**Vue Pinia Store 확장:**
```javascript
// 신규 추가된 주요 상태
currentAgent: 현재 활성 에이전트
sessionProgressStage: 세션 진행 단계
userIntent: 사용자 의도
lastWorkflowResponse: 최근 워크플로우 응답
sessionInfo: 세션 관리 정보

// 신규 추가된 주요 액션
sendMessage(): 통합 메시지 전송
updateFromWorkflowResponse(): 워크플로우 응답 처리
submitQuizAnswer(): 퀴즈 답변 제출
startSession(): 세션 시작
completeSession(): 세션 완료

// 신규 추가된 게터
sessionSteps: 진행 단계 표시용 데이터
canAskQuestion: 질문 가능 여부
canProceedNext: 다음 단계 진행 가능 여부
```

### 6. **컴포넌트 구조 재편**

**새로 추가된 핵심 컴포넌트:**
- `SessionProgressIndicator.vue`: 진행 단계 시각화
- `InteractionArea.vue`: chat/quiz 모드 통합 상호작용 영역
- `MainContentArea.vue`: 에이전트별 동적 컨텐츠 표시
- `TheoryContent.vue`, `QuizContent.vue`, `FeedbackContent.vue` 등: 에이전트별 전용 컴포넌트

**기존 컴포넌트 유지:**
- `LoginPage.vue`, `DiagnosisPage.vue`, `HeaderComponent.vue` 등은 그대로 유지

### 7. **대시보드 페이지 개선**

**기존:**
- 기본적인 학습 현황 표시
- 챕터별 간단한 진행 상태

**변경:**
- **섹션별 진행 상태**: 챕터 내 섹션 단위 진행 표시
- **분리된 통계**: 객관식 정답률 / 주관식 평균 점수 분리 표시
- **연속 학습일**: 사용자 학습 습관 추적
- **상세 성과 정보**: 챕터별 평균 점수, 학습 시간 등

### 8. **스타일링 시스템 강화**

**에이전트별 테마 시스템:**
- 각 에이전트별 고유 색상 및 배경 테마
- 왼쪽 테두리 색상으로 에이전트 구분
- 그라데이션 배경으로 시각적 차별화

**애니메이션 시스템:**
- 에이전트 전환 시 애니메이션 효과
- slideInLeft, slideInRight, fadeIn, bounceIn, zoomIn 등
- 부드러운 UI 전환으로 사용자 경험 향상

---

## 🗑️ 제거된 내용

### 1. **모바일 관련 내용 전체 제거**
- 반응형 디자인 섹션
- 모바일 우선 설계
- 태블릿/데스크톱 브레이크포인트
- 터치 친화적 UI 언급

### 2. **기술적 구현 세부사항 제거**
- 성능 최적화 전략 (API 캐싱, 가상 스크롤링 등)
- 개발자 도구 및 디버깅
- 테스트 전략
- 문서화 및 가이드

### 3. **복잡한 코드 예시 제거**
- 상세한 JavaScript/Vue 코드
- CSS 스타일링 코드
- API 서비스 구현 코드

---

## 🎯 핵심 개선 효과

### 1. **사용자 경험 향상**
- 일관된 워크플로우로 혼란 최소화
- 자동 UI 모드 전환으로 자연스러운 상호작용
- 진행 단계 시각화로 현재 위치 명확화

### 2. **개발 효율성 증대**
- 단일 API로 복잡도 감소
- 통합된 상태 관리로 버그 최소화
- 컴포넌트 재사용성 향상

### 3. **확장성 확보**
- 에이전트별 독립적인 UI 컴포넌트
- 새로운 에이전트 추가 시 기존 구조 재사용 가능
- 일관된 디자인 패턴으로 유지보수성 향상

---

## 📅 구현 단계

### Phase 1 (즉시 구현)
- `LearningPage.vue`: v2.0 통합 워크플로우 기반
- `InteractionArea.vue`: chat/quiz 모드 통합
- `MainContentArea.vue`: 에이전트별 동적 컨텐츠
- `SessionProgressIndicator.vue`: 진행 단계 시각화

### Phase 2 (단계별 구현)
- 에이전트별 컨텐츠 컴포넌트 개발
- `DashboardPage.vue` API 연동
- 스타일링 시스템 및 애니메이션 적용

### Phase 3 (고도화)
- 애니메이션 시스템 완성
- 상태 관리 최적화
- UI/UX 개선

---

## 🔄 호환성 유지

### 기존 시스템과의 연계
- 완성된 인증/진단 시스템은 그대로 유지
- 기존 API (`/auth/*`, `/diagnosis/*`) 호환성 보장
- authStore, diagnosisStore 등 기존 상태 관리 유지
- 라우터 가드 시스템 연동

### 점진적 마이그레이션
- 새로운 tutorStore 추가로 기존 시스템과 병행 운영
- 학습 관련 기능만 v2.0 시스템으로 전환
- 단계별 이주로 안정성 확보

---

*수정 완료일: 2025.08.17*  
*주요 변경 배경: PRD v2.0, API v2.0, DB v2.0, State v2.0 업데이트 반영*