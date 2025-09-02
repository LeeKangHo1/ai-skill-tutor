# backend/app/core/langraph/state/state_definition.py
# v2.0 TutorState 정의 - 퀴즈 필드 완전 재설계, 객관식/주관식 분리

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class TutorState(TypedDict):
    """
    LangGraph 워크플로우에서 사용하는 State 정의
    AI 활용법 학습 튜터 v2.0 기준
    
    State 필드 분류:
    - 기본 사용자 정보: user_id, user_type
    - 학습 진행 상태: current_chapter, current_section, current_agent
    - 세션 진행 단계: session_progress_stage
    - UI 제어: ui_mode
    - 퀴즈 시스템: quiz_* 필드들 (v2.0 완전 재설계)
    - 에이전트 대본: *_draft 필드들
    - 라우팅 제어: user_intent, previous_agent
    - 세션 관리: retry_decision_result, current_session_count, session_start_time
    - 대화 관리: current_session_conversations, recent_sessions_summary
    - 워크플로우 응답: workflow_response
    """
    
    # === 기본 사용자 정보 ===
    user_id: int
    """사용자 고유 ID (MySQL users 테이블 기본키)"""
    
    user_type: str
    """
    사용자 유형 분류
    - "unassigned": 진단 미완료 상태
    - "beginner": AI 입문자 (8챕터)
    - "advanced": 실무 응용형 (10챕터)
    """
    
    # === 학습 진행 상태 ===
    current_chapter: int
    """현재 진행 중인 챕터 번호 (1부터 시작)"""
    
    current_section: int
    """현재 진행 중인 섹션 번호 (1부터 시작, 1학습 세션 = 1섹션)"""
    
    current_agent: str
    """
    현재 활성화된 에이전트 이름 (스네이크 케이스)
    - "session_manager": 세션 초기화 및 완료
    - "learning_supervisor": 워크플로우 시작점/끝점, 라우팅
    - "theory_educator": 이론 설명 대본 생성
    - "quiz_generator": 퀴즈 및 힌트 생성
    - "evaluation_feedback_agent": 평가 및 피드백 생성
    - "qna_resolver": 실시간 질문 답변
    """
    
    # === 학습 세션 진행 단계 ===
    session_progress_stage: str
    """
    현재 세션의 진행 단계
    - "session_start": 세션 시작 (이론 설명 예정)
    - "theory_completed": 이론 완료 (퀴즈 진행 또는 질문 답변 가능)
    - "quiz_and_feedback_completed": 퀴즈와 피드백 완료 (세션 완료 또는 추가 질문 가능)
    """
    
    # === UI 모드 제어 ===
    ui_mode: str
    """
    프론트엔드 UI 모드 제어
    - "chat": 자유 대화 모드 (채팅 입력창 활성화)
    - "quiz": 퀴즈 풀이 모드 (객관식/주관식 답변 영역 활성화)
    """
    
    # === 퀴즈 시스템 (v2.0 완전 재설계) ===
    quiz_type: str
    """
    퀴즈 유형 분류
    - "multiple_choice": 객관식 (4지 선다, 로컬 채점)
    - "subjective": 주관식 (서술형, ChatGPT 채점)
    """
    
    quiz_content: str
    """퀴즈 문제 내용 (ChatGPT에서 생성)"""
    
    quiz_options: List[str]
    """
    객관식 선택지 배열
    - 객관식: ["선택지1", "선택지2", "선택지3", "선택지4"]
    - 주관식: [] (빈 배열)
    """
    
    quiz_correct_answer: Any
    """
    정답 정보
    - 객관식: 정답 번호 (int, 1-4)
    - 주관식: None
    """
    
    quiz_explanation: str
    """
    정답 해설
    - 객관식: 정답 해설 문구
    - 주관식: "" (빈 문자열)
    """
    
    quiz_sample_answer: str
    """
    모범 답안 예시
    - 객관식: "" (빈 문자열)
    - 주관식: 모범 답안 예시 문구
    """
    
    quiz_evaluation_criteria: List[str]
    """
    평가 기준 배열
    - 객관식: [] (빈 배열)
    - 주관식: ["평가기준1", "평가기준2", "평가기준3"]
    """
    
    quiz_hint: str
    """퀴즈 힌트 내용 (객관식/주관식 공통)"""
    
    user_answer: str
    """
    사용자 답변
    - 객관식: 선택한 번호를 문자열로 ("1", "2", "3", "4")
    - 주관식: 입력한 서술형 답변
    """
    
    multiple_answer_correct: bool
    """
    객관식 정답 여부
    - 객관식: True/False
    - 주관식: False (기본값)
    """
    
    subjective_answer_score: int
    """
    주관식 점수
    - 객관식: 0 (기본값)
    - 주관식: 0-100점
    """
    
    evaluation_feedback: str
    """평가 피드백 내용 (EvaluationFeedbackAgent에서 생성)"""
    
    hint_usage_count: int
    """힌트 사용 횟수 (세션별 집계)"""
    
    # === 에이전트 대본 저장 ===
    theory_draft: str
    """TheoryEducator가 생성한 순수 이론 설명 대본"""
    
    quiz_draft: str
    """QuizGenerator가 생성한 퀴즈 JSON 문자열"""
    
    feedback_draft: str
    """EvaluationFeedbackAgent가 생성한 순수 피드백 대본"""
    
    qna_draft: str
    """QnAResolver가 생성한 질문 답변 대본"""
    
    # === 라우팅 & 디버깅 ===
    user_intent: str
    """
    사용자 의도 분석 결과
    - "next_step": 다음 단계 진행 (기본값)
    - "question": 질문 답변 요청
    - "quiz_answer": 퀴즈 답변 제출
    - "question_streaming": 질문 답변 스트리밍 요청
    - "theory_streaming": 이론 설명 스트리밍 요청
    """
    
    previous_agent: str
    """이전 에이전트 이름 (디버깅 및 복귀 추적용)"""
    
    # === 학습 세션 제어 ===
    retry_decision_result: str
    """
    사용자의 재학습 여부 결정
    - "proceed": 다음 단계 진행
    - "retry": 현재 구간 재학습
    - "": 미결정 상태 (기본값)
    """
    
    current_session_count: int
    """현재 구간에서 학습 세션 횟수 (최대 1회 제한)"""
    
    session_start_time: datetime
    """현재 학습 세션 시작 시간"""
    
    # === 대화 관리 ===
    current_session_conversations: List[Dict[str, Any]]
    """
    현재 학습 세션의 대화 내용
    형식: [
        {
            "agent_name": "user",
            "message": "사용자 메시지",
            "timestamp": datetime,
            "message_type": "user",
            "session_stage": "session_start"
        },
        {
            "agent_name": "theory_educator", 
            "message": "AI 응답",
            "timestamp": datetime,
            "message_type": "system",
            "session_stage": "theory_completed"
        }
    ]
    """
    
    recent_sessions_summary: List[Dict[str, str]]
    """
    최근 5개 학습 세션 요약 (QnAResolver 맥락 제공용)
    형식: [
        {
            "chapter": "1",
            "section": "1", 
            "topic": "AI의 정의",
            "summary": "AI의 기본 개념과 특징을 학습"
        }
    ]
    """
    
    # === v2.0 워크플로우 응답 ===
    workflow_response: Dict[str, Any]
    """
    표준화된 워크플로우 응답 구조
    LearningSupervisor Output에서 프론트엔드로 전달되는 최종 응답
    형식: {
        "current_agent": "theory_educator",
        "session_progress_stage": "theory_completed", 
        "ui_mode": "chat",
        "content": {
            "type": "theory",
            "title": "AI란 무엇인가?",
            "content": "AI는 인공지능으로...",
            "key_points": ["포인트1", "포인트2"],
            "examples": ["예시1", "예시2"]
        }
    }
    """


# State 필드 그룹 정의 (유틸리티 함수에서 사용)
STATE_FIELD_GROUPS = {
    "user_info": [
        "user_id", "user_type"
    ],
    "progress": [
        "current_chapter", "current_section", "current_agent"
    ],
    "session_control": [
        "session_progress_stage", "ui_mode"
    ],
    "quiz_basic": [
        "quiz_type", "quiz_content", "quiz_hint", "user_answer"
    ],
    "quiz_multiple_choice": [
        "quiz_options", "quiz_correct_answer", "quiz_explanation", "multiple_answer_correct"
    ],
    "quiz_subjective": [
        "quiz_sample_answer", "quiz_evaluation_criteria", "subjective_answer_score"
    ],
    "quiz_evaluation": [
        "evaluation_feedback", "hint_usage_count"
    ],
    "agent_drafts": [
        "theory_draft", "quiz_draft", "feedback_draft", "qna_draft"
    ],
    "routing": [
        "user_intent", "previous_agent"
    ],
    "session_management": [
        "retry_decision_result", "current_session_count", "session_start_time"
    ],
    "conversations": [
        "current_session_conversations", "recent_sessions_summary"
    ],
    "workflow": [
        "workflow_response"
    ]
}

# 필수 필드 정의 (검증에서 사용)
REQUIRED_FIELDS = [
    "user_id", "user_type", "current_chapter", "current_section", 
    "current_agent", "session_progress_stage", "ui_mode", "quiz_type"
]

# 유효한 값 범위 정의
VALID_VALUES = {
    "user_type": ["beginner", "advanced", "unassigned"],
    "session_progress_stage": ["session_start", "theory_completed", "quiz_and_feedback_completed"],
    "ui_mode": ["chat", "quiz"],
    "quiz_type": ["multiple_choice", "subjective"],
    "user_intent": ["next_step", "question", "quiz_answer", "question_streaming", "theory_streaming"],
    "retry_decision_result": ["proceed", "retry", ""],
    "agent_names": [
        "session_manager", "learning_supervisor", "theory_educator", 
        "quiz_generator", "evaluation_feedback_agent", "qna_resolver"
    ]
}

# 기본값 정의
DEFAULT_VALUES = {
    "user_id": 0,
    "user_type": "unassigned",
    "current_chapter": 1,
    "current_section": 1,
    "current_agent": "session_manager",
    "session_progress_stage": "session_start",
    "ui_mode": "chat",
    "quiz_type": "multiple_choice",
    "quiz_content": "",
    "quiz_options": [],
    "quiz_correct_answer": None,
    "quiz_explanation": "",
    "quiz_sample_answer": "",
    "quiz_evaluation_criteria": [],
    "quiz_hint": "",
    "user_answer": "",
    "multiple_answer_correct": False,
    "subjective_answer_score": 0,
    "evaluation_feedback": "",
    "hint_usage_count": 0,
    "theory_draft": "",
    "quiz_draft": "",
    "feedback_draft": "",
    "qna_draft": "",
    "user_intent": "next_step",
    "previous_agent": "",
    "retry_decision_result": "",
    "current_session_count": 0,
    "current_session_conversations": [],
    "recent_sessions_summary": [],
    "workflow_response": {}
}