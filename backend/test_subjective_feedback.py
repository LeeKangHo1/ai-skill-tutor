# backend/test_subjective_feedback.py

import json
import os
import sys
from typing import Dict, Any

# 백엔드 경로를 sys.path에 추가
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.tools.analysis.evaluation_tools import determine_next_step
from app.tools.analysis.feedback_tools_chatgpt import evaluate_subjective_with_feedback


def load_subjective_quiz_from_chapter() -> Dict[str, Any]:
    """
    챕터 파일에서 주관식 퀴즈 데이터 찾기
    
    Returns:
        주관식 퀴즈 데이터 또는 None
    """
    try:
        # 여러 챕터에서 섹션 2의 주관식 퀴즈 찾기 (또는 직접 챕터 5 섹션 2 탐색)
        target_chapters = [5]  # 챕터 5 우선 탐색
        for chapter_num in target_chapters:
            chapter_file = os.path.join(
                backend_dir, "data", "chapters", f"chapter_{chapter_num:02d}.json"
            )
            
            if not os.path.exists(chapter_file):
                continue
                
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            sections = chapter_data.get('sections', [])
            for section in sections:
                # 섹션 2의 주관식 퀴즈를 우선 찾기
                if section.get('section_number') == 2:
                    quiz_data = section.get('quiz', {})
                    if quiz_data.get('type') == 'subjective':
                        print(f"✅ 챕터 {chapter_num} 섹션 2 주관식 퀴즈 발견")
                        return quiz_data
        
        print("❌ 챕터 5 섹션 2 주관식 퀴즈를 찾을 수 없습니다")
        return None
        
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {str(e)}")
        return None


def get_sample_subjective_quiz() -> Dict[str, Any]:
    """
    챕터 5 섹션 2 주관식 퀴즈 데이터 반환
    """
    return {
        "type": "subjective",
        "question": "아래의 밋밋한 프롬프트를 '분량', '대상', '분위기'에 대한 구체적인 조건을 2가지 이상 추가하여, 훨씬 좋은 결과물을 얻을 수 있는 프롬프트로 개선해보세요.\n\n[기존 프롬프트]\n\"회사 워크샵에 대한 공지 이메일을 써줘.\"",
        "sample_answer": "전 직원을 대상으로 한 회사 워크샵 공지 이메일을 작성해줘. 정중하면서도 친근한 톤으로 5-7문장 분량으로 써주고, 참석 독려 문구와 문의처를 반드시 포함해줘.",
        "evaluation_criteria": [
            "구체적 조건 2가지 이상 추가",
            "분량, 대상, 분위기 중 최소 2가지 명시",
            "기존 프롬프트 대비 명확한 개선"
        ]
    }


def test_subjective_feedback():
    """
    주관식 피드백 테스트 함수
    """
    print("="*80)
    print("📋 주관식 피드백 테스트 시작 - 챕터 5 섹션 2")
    print("(구체적 조건 제시 프롬프트 개선)")
    print("="*80)
    
    # 퀴즈 데이터 로드 (실제 파일에서 또는 샘플 사용)
    quiz_data = load_subjective_quiz_from_chapter()
    if not quiz_data:
        print("🔄 챕터 5 섹션 2 샘플 퀴즈 사용")
        quiz_data = get_sample_subjective_quiz()
    
    # 퀴즈 정보 출력
    print("\n📝 퀴즈 정보:")
    print(f"문제: {quiz_data.get('question', '')}")
    print(f"샘플 답안: {quiz_data.get('sample_answer', '')}")
    print(f"평가 기준:")
    for i, criteria in enumerate(quiz_data.get('evaluation_criteria', []), 1):
        print(f"  {i}. {criteria}")
    
    # 테스트 케이스들 (챕터 5 섹션 2 기준)
    test_cases = [
        {
            "name": "우수한 답변 (80점 이상 예상)",
            "answer": "전 직원을 대상으로 한 회사 워크샵 공지 이메일을 작성해줘. 정중하면서도 친근한 톤으로 5-7문장 분량으로 써주고, 참석 독려 문구와 문의처를 반드시 포함해줘. 제목에는 [필독]을 붙이고 워크샵 일정과 장소도 명시해줘.",
            "expected_score_range": "80-100점"
        },
        {
            "name": "보통 답변 (60-79점 예상)",
            "answer": "전 직원 대상 회사 워크샵 공지 이메일을 친근한 톤으로 5문장 정도로 작성해줘. 참석 독려 문구도 포함해줘.",
            "expected_score_range": "60-79점"
        },
        {
            "name": "부족한 답변 (40-59점 예상)",
            "answer": "회사 워크샵 공지 이메일을 정중한 톤으로 써줘.",
            "expected_score_range": "40-59점"
        },
        {
            "name": "매우 부족한 답변 (40점 미만 예상)",
            "answer": "회사 워크샵 이메일 좀 더 자세히 써줘.",
            "expected_score_range": "40점 미만"
        }
    ]
    
    # 각 테스트 케이스 실행
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n" + "="*60)
        print(f"🧪 테스트 케이스 {i}: {test_case['name']}")
        print(f"예상 점수: {test_case['expected_score_range']}")
        print("="*60)
        
        user_answer = test_case['answer']
        print(f"\n📝 사용자 답변:")
        print(f"'{user_answer}'")
        
        # Beginner 사용자 테스트
        print(f"\n--- Beginner 사용자 평가 및 피드백 ---")
        try:
            score, evaluation_detail = evaluate_subjective_with_feedback(
                quiz_data, user_answer, "beginner"
            )
            
            print(f"📊 점수: {score}점")
            
            # 다음 단계 결정
            next_step = determine_next_step(score, "subjective", 0)  # 첫 번째 시도
            print(f"🚦 다음 단계: {next_step}")
            
            # 상세 피드백
            detailed_feedback = evaluation_detail.get("detailed_feedback", "")
            if detailed_feedback:
                print(f"\n💬 피드백:")
                print(detailed_feedback)
            
            # 기준별 분석
            criteria_analysis = evaluation_detail.get("criteria_analysis", {})
            if criteria_analysis:
                print(f"\n📋 기준별 분석:")
                for criteria, analysis in criteria_analysis.items():
                    print(f"  • {criteria}: {analysis}")
                    
        except Exception as e:
            print(f"❌ Beginner 테스트 실패: {str(e)}")
        
        # Advanced 사용자 테스트
        print(f"\n--- Advanced 사용자 평가 및 피드백 ---")
        try:
            score, evaluation_detail = evaluate_subjective_with_feedback(
                quiz_data, user_answer, "advanced"
            )
            
            print(f"📊 점수: {score}점")
            
            # 다음 단계 결정
            next_step = determine_next_step(score, "subjective", 0)
            print(f"🚦 다음 단계: {next_step}")
            
            # 상세 피드백
            detailed_feedback = evaluation_detail.get("detailed_feedback", "")
            if detailed_feedback:
                print(f"\n💬 피드백:")
                print(detailed_feedback)
                
        except Exception as e:
            print(f"❌ Advanced 테스트 실패: {str(e)}")
        
        print(f"\n{'='*60}")
    
    print(f"\n" + "="*80)
    print("✅ 주관식 피드백 테스트 완료")
    print("="*80)


def test_scoring_consistency():
    """
    점수 일관성 테스트 - 같은 답변을 여러 번 평가하여 일관성 확인
    """
    print("\n" + "="*80)
    print("🔄 점수 일관성 테스트 (같은 답변 3회 평가)")
    print("="*80)
    
    quiz_data = get_sample_subjective_quiz()
    test_answer = "전 직원 대상 회사 워크샵 공지 이메일을 친근한 톤으로 5문장 정도로 작성해줘. 참석 독려 문구도 포함해줘."
    
    print(f"테스트 답변: '{test_answer}'")
    
    scores = []
    for i in range(3):
        print(f"\n--- 평가 {i+1}회차 ---")
        try:
            score, evaluation_detail = evaluate_subjective_with_feedback(
                quiz_data, test_answer, "beginner"
            )
            scores.append(score)
            print(f"점수: {score}점")
            
        except Exception as e:
            print(f"❌ 평가 {i+1}회차 실패: {str(e)}")
    
    if scores:
        avg_score = sum(scores) / len(scores)
        score_range = max(scores) - min(scores)
        print(f"\n📊 점수 통계:")
        print(f"  평균 점수: {avg_score:.1f}점")
        print(f"  점수 범위: {min(scores)}~{max(scores)}점 (차이: {score_range}점)")
        print(f"  일관성: {'좋음' if score_range <= 10 else '보통' if score_range <= 20 else '낮음'}")


def main():
    """
    메인 테스트 함수
    """
    print("🧪 주관식 피드백 생성 테스트 시작")
    
    # 환경 변수 체크
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("⚠️ .env 파일을 확인하거나 환경변수를 설정해주세요.")
        return
    
    try:
        # 주관식 피드백 테스트
        # test_subjective_feedback()
        
        # 점수 일관성 테스트
        test_scoring_consistency()
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {str(e)}")
        print("🔧 OpenAI API 키와 네트워크 연결을 확인해주세요.")


if __name__ == "__main__":
    main()