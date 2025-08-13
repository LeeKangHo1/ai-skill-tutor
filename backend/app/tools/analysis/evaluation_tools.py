# backend/app/tools/analysis/evaluation_tools.py

import json
import logging
from typing import Dict, Any, Tuple

def evaluate_multiple_choice(quiz_data: Dict[str, Any], user_answer: str) -> Tuple[int, bool, str]:
    """
    객관식 문제 로컬 채점 (간소화)
    
    Args:
        quiz_data: 퀴즈 JSON 데이터
        user_answer: 사용자 답변 (문자열)
        
    Returns:
        Tuple[점수(0/1), 정답여부, 설명]
    """
    logger = logging.getLogger(__name__)
    
    try:
        # 퀴즈 데이터에서 정답 추출
        correct_answer = quiz_data.get('correct_answer')
        explanation = quiz_data.get('explanation', '')
        
        logger.info(f"객관식 채점 시작 - 정답: {correct_answer}, 사용자답변: {user_answer}")
        
        # 사용자 답변을 정수로 변환
        try:
            user_answer_int = int(user_answer.strip())
        except (ValueError, AttributeError):
            logger.warning(f"잘못된 답변 형식: {user_answer}")
            return 0, False, "답변 형식이 올바르지 않습니다."
        
        # 답변 범위 체크 (1-4)
        options = quiz_data.get('options', [])
        if not (1 <= user_answer_int <= len(options)):
            logger.warning(f"답변 범위 초과: {user_answer_int}")
            return 0, False, f"1-{len(options)} 범위의 번호를 선택해주세요."
        
        # 정답 비교
        is_correct = (user_answer_int == correct_answer)
        score = 1 if is_correct else 0
        
        logger.info(f"객관식 채점 완료 - 결과: {'정답' if is_correct else '오답'}")
        return score, is_correct, explanation
        
    except Exception as e:
        logger.error(f"객관식 채점 중 오류 발생: {str(e)}")
        return 0, False, f"채점 중 오류가 발생했습니다: {str(e)}"


def determine_next_step(score: int, quiz_type: str, current_session_count: int) -> str:
    """
    점수와 세션 횟수를 바탕으로 다음 단계 결정
    
    Args:
        score: 획득 점수 (객관식: 0/1, 주관식: 0-100)
        quiz_type: 퀴즈 타입 ("multiple_choice" or "subjective")
        current_session_count: 현재 세션 반복 횟수
        
    Returns:
        다음 단계 ("proceed" or "retry")
    """
    logger = logging.getLogger(__name__)
    
    # 최대 1회 재학습 제한
    if current_session_count >= 1:
        logger.info(f"최대 재학습 횟수 도달 - 강제 진행 (세션 횟수: {current_session_count})")
        return "proceed"
    
    if quiz_type == "multiple_choice":
        # 객관식: 정답이면 진행, 오답이면 재학습
        decision = "proceed" if score == 1 else "retry"
        logger.info(f"객관식 판단 - 점수: {score}, 결정: {decision}")
        return decision
    
    elif quiz_type == "subjective":
        # 주관식: 60점 이상이면 진행, 미만이면 재학습
        decision = "proceed" if score >= 60 else "retry"
        logger.info(f"주관식 판단 - 점수: {score}, 결정: {decision}")
        return decision
    
    else:
        logger.warning(f"알 수 없는 퀴즈 타입: {quiz_type} - 기본값 proceed 반환")
        return "proceed"


def validate_quiz_data(quiz_data: Dict[str, Any], quiz_type: str) -> bool:
    """
    퀴즈 데이터 유효성 검증
    
    Args:
        quiz_data: 퀴즈 JSON 데이터
        quiz_type: 퀴즈 타입
        
    Returns:
        유효성 여부
    """
    logger = logging.getLogger(__name__)
    
    if not isinstance(quiz_data, dict):
        logger.error("퀴즈 데이터가 딕셔너리가 아닙니다.")
        return False
    
    # 공통 필수 필드
    required_common = ['question', 'type']
    for field in required_common:
        if field not in quiz_data:
            logger.error(f"필수 필드 누락: {field}")
            return False
    
    if quiz_type == "multiple_choice":
        # 객관식 필수 필드
        required_mc = ['options', 'correct_answer']
        for field in required_mc:
            if field not in quiz_data:
                logger.error(f"객관식 필수 필드 누락: {field}")
                return False
        
        # 선택지와 정답 번호 검증
        options = quiz_data.get('options', [])
        correct_answer = quiz_data.get('correct_answer')
        
        if not isinstance(options, list) or len(options) < 2:
            logger.error("선택지가 2개 미만입니다.")
            return False
        
        if not isinstance(correct_answer, int) or not (1 <= correct_answer <= len(options)):
            logger.error(f"정답 번호가 유효하지 않습니다: {correct_answer}")
            return False
    
    elif quiz_type == "subjective":
        # 주관식 필수 필드
        required_subj = ['sample_answer', 'evaluation_criteria']
        for field in required_subj:
            if field not in quiz_data:
                logger.error(f"주관식 필수 필드 누락: {field}")
                return False
        
        # 평가 기준 검증
        criteria = quiz_data.get('evaluation_criteria', [])
        if not isinstance(criteria, list) or len(criteria) < 1:
            logger.error("평가 기준이 1개 미만입니다.")
            return False
    
    logger.info(f"{quiz_type} 퀴즈 데이터 검증 완료")
    return True


def get_user_answer_info(quiz_data: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
    """
    사용자 답변 관련 정보 추출 (객관식용)
    
    Args:
        quiz_data: 퀴즈 JSON 데이터
        user_answer: 사용자 답변
        
    Returns:
        답변 관련 정보 딕셔너리
    """
    try:
        user_answer_int = int(user_answer.strip())
        options = quiz_data.get('options', [])
        correct_answer = quiz_data.get('correct_answer', 1)
        
        return {
            "user_answer": user_answer_int,
            "selected_option": options[user_answer_int - 1] if 1 <= user_answer_int <= len(options) else "",
            "correct_answer": correct_answer,
            "correct_option": options[correct_answer - 1] if 1 <= correct_answer <= len(options) else "",
            "all_options": options
        }
    except (ValueError, IndexError, TypeError):
        return {
            "user_answer": user_answer,
            "selected_option": "",
            "correct_answer": quiz_data.get('correct_answer', 1),
            "correct_option": "",
            "all_options": quiz_data.get('options', [])
        }


def extract_subjective_feedback(chatgpt_result: Dict[str, Any]) -> str:
    """
    ChatGPT 주관식 결과에서 피드백 텍스트 추출
    
    Args:
        chatgpt_result: ChatGPT 응답 딕셔너리
        
    Returns:
        피드백 텍스트
    """
    try:
        # feedback.content 우선 사용
        feedback_content = chatgpt_result.get('feedback', {}).get('content', '')
        if feedback_content:
            return feedback_content
        
        # 점수 정보만이라도 추출
        score = chatgpt_result.get('evaluation', {}).get('score', 0)
        return f"점수: {score}점"
        
    except Exception:
        return "피드백 생성 중 오류가 발생했습니다."


def create_simple_evaluation_summary(
    quiz_type: str,
    score: int, 
    is_correct: bool = None,
    explanation: str = "",
    next_step: str = "proceed"
) -> Dict[str, Any]:
    """
    간단한 평가 요약 생성 (State 업데이트용)
    
    Args:
        quiz_type: 퀴즈 타입
        score: 점수
        is_correct: 정답 여부 (객관식만)
        explanation: 설명
        next_step: 다음 단계
        
    Returns:
        간단한 평가 요약
    """
    summary = {
        "quiz_type": quiz_type,
        "score": score,
        "next_step": next_step,
        "explanation": explanation
    }
    
    if quiz_type == "multiple_choice" and is_correct is not None:
        summary["is_correct"] = is_correct
    
    return summary