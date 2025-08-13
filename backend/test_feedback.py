# backend/test_feedback.py

import json
import os
import sys
from typing import Dict, Any

# 백엔드 경로를 sys.path에 추가
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# 직접 함수를 import
from app.tools.analysis.evaluation_tools import evaluate_multiple_choice
from app.tools.analysis.feedback_tools_chatgpt import generate_multiple_choice_feedback


def load_chapter_data(chapter_number: int, section_number: int) -> Dict[str, Any]:
    """
    챕터 파일에서 특정 섹션 데이터 로드
    
    Args:
        chapter_number: 챕터 번호
        section_number: 섹션 번호
        
    Returns:
        섹션 데이터 또는 None
    """
    try:
        chapter_file = os.path.join(
            backend_dir, "data", "chapters", f"chapter_{chapter_number:02d}.json"
        )
        
        if not os.path.exists(chapter_file):
            print(f"❌ 챕터 파일이 존재하지 않습니다: {chapter_file}")
            return None
        
        with open(chapter_file, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        # 특정 섹션 찾기
        sections = chapter_data.get('sections', [])
        for section in sections:
            if section.get('section_number') == section_number:
                print(f"✅ 챕터 {chapter_number} 섹션 {section_number} 데이터 로드 완료")
                return section
        
        print(f"❌ 섹션 {section_number}를 찾을 수 없습니다")
        return None
        
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {str(e)}")
        return None


def test_multiple_choice_feedback():
    """
    객관식 피드백 테스트 함수
    """
    print("="*80)
    print("📋 객관식 피드백 테스트 시작")
    print("="*80)
    
    # 챕터 1 섹션 2 데이터 로드
    section_data = load_chapter_data(1, 2)
    if not section_data:
        return
    
    quiz_data = section_data.get('quiz', {})
    if not quiz_data:
        print("❌ 퀴즈 데이터를 찾을 수 없습니다")
        return
    
    # 퀴즈 정보 출력
    print("\n📝 퀴즈 정보:")
    print(f"문제: {quiz_data.get('question', '')}")
    print(f"선택지:")
    for i, option in enumerate(quiz_data.get('options', []), 1):
        print(f"  {i}. {option}")
    print(f"정답: {quiz_data.get('correct_answer', '')}")
    print(f"설명: {quiz_data.get('explanation', '')}")
    
    # 정답 케이스 테스트
    print("\n" + "="*50)
    print("🟢 정답 케이스 테스트")
    print("="*50)
    
    correct_answer = str(quiz_data.get('correct_answer', 1))
    print(f"사용자 답변: {correct_answer}")
    
    # 1. 평가
    score, evaluation_detail = evaluate_multiple_choice(quiz_data, correct_answer)
    print(f"평가 결과: 점수 {score}, 정답 여부: {evaluation_detail.get('is_correct', False)}")
    
    # 2. beginner 피드백
    print("\n--- Beginner 사용자 피드백 ---")
    beginner_feedback = generate_multiple_choice_feedback(
        quiz_data, evaluation_detail, "beginner", "proceed"
    )
    print(beginner_feedback)
    
    # 3. advanced 피드백  
    print("\n--- Advanced 사용자 피드백 ---")
    advanced_feedback = generate_multiple_choice_feedback(
        quiz_data, evaluation_detail, "advanced", "proceed"
    )
    print(advanced_feedback)
    
    # 오답 케이스 테스트
    print("\n" + "="*50)
    print("🔴 오답 케이스 테스트")
    print("="*50)
    
    # 정답이 아닌 다른 번호 선택
    correct_num = quiz_data.get('correct_answer', 1)
    wrong_answer = str(2 if correct_num != 2 else 3)
    print(f"사용자 답변: {wrong_answer}")
    
    # 1. 평가
    score, evaluation_detail = evaluate_multiple_choice(quiz_data, wrong_answer)
    print(f"평가 결과: 점수 {score}, 정답 여부: {evaluation_detail.get('is_correct', False)}")
    
    # 2. beginner 피드백
    print("\n--- Beginner 사용자 피드백 ---")
    beginner_feedback = generate_multiple_choice_feedback(
        quiz_data, evaluation_detail, "beginner", "retry"
    )
    print(beginner_feedback)
    
    # 3. advanced 피드백
    print("\n--- Advanced 사용자 피드백 ---")
    advanced_feedback = generate_multiple_choice_feedback(
        quiz_data, evaluation_detail, "advanced", "retry"
    )
    print(advanced_feedback)
    
    print("\n" + "="*80)
    print("✅ 객관식 피드백 테스트 완료")
    print("="*80)


def test_with_custom_quiz():
    """
    커스텀 퀴즈로 테스트 (JSON 파일이 없는 경우 대비)
    """
    print("\n📋 커스텀 퀴즈 테스트")
    print("="*50)
    
    custom_quiz = {
        "type": "multiple_choice",
        "question": "다음 중 AI 기술이 활용된 사례로 가장 적절한 것은 무엇일까요?",
        "options": [
            "친구와 카카오톡으로 메시지를 주고받는 것",
            "온라인 쇼핑몰에서 내가 좋아할 만한 상품을 추천해주는 것",
            "계산기를 사용해 덧셈을 하는 것",
            "TV 리모컨으로 채널을 바꾸는 것"
        ],
        "correct_answer": 2,
        "explanation": "온라인 쇼핑몰의 상품 추천 시스템은 사용자의 구매 패턴, 검색 기록 등을 분석하여 개인화된 추천을 제공하는 AI 기술입니다."
    }
    
    print(f"문제: {custom_quiz['question']}")
    print("선택지:")
    for i, option in enumerate(custom_quiz['options'], 1):
        print(f"  {i}. {option}")
    
    # 정답 테스트
    print("\n🟢 정답 테스트 (답변: 2)")
    score, evaluation_detail = evaluate_multiple_choice(custom_quiz, "2")
    
    print("\n--- Beginner 피드백 ---")
    feedback = generate_multiple_choice_feedback(
        custom_quiz, evaluation_detail, "beginner", "proceed"
    )
    print(feedback)
    
    # 오답 테스트
    print("\n🔴 오답 테스트 (답변: 1)")
    score, evaluation_detail = evaluate_multiple_choice(custom_quiz, "1")
    
    print("\n--- Beginner 피드백 ---")
    feedback = generate_multiple_choice_feedback(
        custom_quiz, evaluation_detail, "beginner", "retry"
    )
    print(feedback)


def main():
    """
    메인 테스트 함수
    """
    print("🧪 피드백 생성 테스트 시작")
    
    # 환경 변수 체크
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("⚠️ .env 파일을 확인하거나 환경변수를 설정해주세요.")
        return
    
    try:
        # 실제 JSON 파일로 테스트
        test_multiple_choice_feedback()
        
    except Exception as e:
        print(f"❌ 실제 파일 테스트 실패: {str(e)}")
        print("🔄 커스텀 퀴즈로 테스트를 진행합니다...")
        
        try:
            test_with_custom_quiz()
        except Exception as e2:
            print(f"❌ 커스텀 퀴즈 테스트도 실패: {str(e2)}")
            print("🔧 OpenAI API 키와 네트워크 연결을 확인해주세요.")


if __name__ == "__main__":
    main()