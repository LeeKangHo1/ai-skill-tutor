# backend/test_chapter5_section1.py

import json
import os
import sys
from typing import Dict, Any

# 백엔드 경로를 sys.path에 추가
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.tools.analysis.evaluation_tools import determine_next_step
from app.tools.analysis.feedback_tools_chatgpt import evaluate_subjective_with_feedback


def get_chapter5_section1_quiz() -> Dict[str, Any]:
    """
    챕터 5 섹션 1 주관식 퀴즈 데이터 반환
    """
    return {
        "type": "subjective",
        "question": "효과적인 다이어트 식단을 짜고 싶습니다. AI에게 '숙련된 영양사' 역할을 부여하여, 일주일치 아침 식단 추천을 요청하는 프롬프트를 직접 작성해보세요.",
        "sample_answer": "당신은 10년 경력의 숙련된 영양사입니다. 건강한 다이어트를 원하는 30대 직장인을 위해 일주일치 아침 식단을 추천해주세요. 각 식단마다 칼로리와 주요 영양소, 간단한 조리법을 포함해서 전문가 관점에서 설명해주세요.",
        "evaluation_criteria": [
            "명확한 역할 부여 ('당신은 ~영양사입니다')",
            "구체적인 요청 사항 (일주일치 아침 식단)",
            "세부 조건 제시 (칼로리, 영양소, 조리법 등)"
        ]
    }


def test_chapter5_section1_subjective():
    """
    챕터 5 섹션 1 주관식 피드백 테스트
    """
    print("="*80)
    print("📋 챕터 5 섹션 1 주관식 피드백 테스트")
    print("(전문가 역할 부여 프롬프트 작성)")
    print("="*80)
    
    quiz_data = get_chapter5_section1_quiz()
    
    # 퀴즈 정보 출력
    print("\n📝 퀴즈 정보:")
    print(f"문제: {quiz_data['question']}")
    print(f"\n샘플 답안: {quiz_data['sample_answer']}")
    print(f"\n평가 기준:")
    for i, criteria in enumerate(quiz_data['evaluation_criteria'], 1):
        print(f"  {i}. {criteria}")
    
    # 테스트 케이스 정의
    test_cases = [
        {
            "user_type": "beginner",
            "answer": "당신은 경험이 풍부한 영양사입니다. 다이어트를 하고 싶은 직장인을 위해 일주일치 아침 식단을 추천해주세요. 각 메뉴의 칼로리, 영양소, 조리법을 자세히 알려주세요.",
            "expected_range": "70-85점"
        },
        {
            "user_type": "advanced", 
            "answer": "당신은 10년 경력의 전문 영양사입니다. 30대 직장인의 건강한 다이어트를 위한 일주일치 아침 식단을 추천해주세요. 각 식단별로 칼로리, 주요 영양소 함량, 간단한 조리법을 포함하여 전문가 관점에서 상세히 설명해주세요.",
            "expected_range": "85-95점"
        }
    ]
    
    # 각 테스트 케이스 실행
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n" + "="*60)
        print(f"🧪 테스트 케이스 {i}: {test_case['user_type'].upper()} 사용자")
        print(f"예상 점수: {test_case['expected_range']}")
        print("="*60)
        
        user_answer = test_case['answer']
        user_type = test_case['user_type']
        
        print(f"\n📝 사용자 답변:")
        print(f"'{user_answer}'")
        
        try:
            # 평가 및 피드백 생성
            print(f"\n🤖 ChatGPT 평가 중...")
            score, feedback_text = evaluate_subjective_with_feedback(
                quiz_data, user_answer, user_type
            )
            
            print(f"\n📊 결과:")
            print(f"점수: {score}점")
            
            # 다음 단계 결정
            next_step = determine_next_step(score, "subjective", 0)  # 첫 번째 시도
            print(f"다음 단계: {next_step}")
            
            # 피드백 출력
            print(f"\n💬 생성된 피드백:")
            print("-" * 50)
            print(feedback_text)
            print("-" * 50)
            
            # 점수 범위 확인
            expected_min = int(test_case['expected_range'].split('-')[0])
            expected_max = int(test_case['expected_range'].split('-')[1].replace('점', ''))
            
            if expected_min <= score <= expected_max:
                print(f"\n✅ 점수가 예상 범위({test_case['expected_range']}) 내에 있습니다.")
            else:
                print(f"\n⚠️ 점수가 예상 범위({test_case['expected_range']})를 벗어났습니다.")
            
        except Exception as e:
            print(f"\n❌ 테스트 실패: {str(e)}")
        
        print(f"\n{'='*60}")
    
    print(f"\n" + "="*80)
    print("✅ 챕터 5 섹션 1 테스트 완료")
    print("="*80)


def test_edge_cases():
    """
    경계 케이스 테스트
    """
    print("\n" + "="*80)
    print("🔍 경계 케이스 테스트")
    print("="*80)
    
    quiz_data = get_chapter5_section1_quiz()
    
    edge_cases = [
        {
            "name": "매우 부족한 답변",
            "answer": "영양사한테 다이어트 식단 추천해달라고 해주세요.",
            "expected": "40점 미만"
        },
        {
            "name": "빈 답변",
            "answer": "",
            "expected": "오류 처리"
        },
        {
            "name": "한 글자 답변",
            "answer": "네",
            "expected": "낮은 점수"
        }
    ]
    
    for case in edge_cases:
        print(f"\n--- {case['name']} ---")
        print(f"답변: '{case['answer']}'")
        print(f"예상: {case['expected']}")
        
        try:
            if case['answer'].strip():  # 빈 답변이 아닌 경우만 테스트
                score, feedback = evaluate_subjective_with_feedback(
                    quiz_data, case['answer'], "beginner"
                )
                print(f"결과: {score}점")
                print(f"피드백: {feedback[:100]}...")
            else:
                print("빈 답변으로 인한 테스트 스킵")
                
        except Exception as e:
            print(f"오류: {str(e)}")


def main():
    """
    메인 테스트 함수
    """
    print("🧪 챕터 5 섹션 1 - 전문가 역할 부여 프롬프트 테스트 시작")
    
    # 환경 변수 체크
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("⚠️ .env 파일을 확인하거나 환경변수를 설정해주세요.")
        return
    
    try:
        # 메인 테스트
        test_chapter5_section1_subjective()
        
        # 경계 케이스 테스트
        test_edge_cases()
        
        print("\n🎉 모든 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {str(e)}")
        print("🔧 OpenAI API 키와 네트워크 연결을 확인해주세요.")


if __name__ == "__main__":
    main()