# backend/app/services/diagnosis_service.py

def calculate_score(answers):
    """답변 리스트에서 총 점수 계산"""
    total_score = 0
    for i, answer in enumerate(answers):
        value = answer.get('answer')
        if value not in ['option_1', 'option_2', 'option_3', 'option_4']:
            raise ValueError(f"{i+1}번째 문항의 답변 형식이 잘못되었습니다.")
        score = int(value[-1])  # 'option_3' -> 3
        total_score += score
    return total_score

def recommend_type_by_score(score):
    """점수 기반 추천 사용자 유형 반환"""
    if score <= 13:
        return {
            "recommended_type": "beginner",
            "recommended_description": "AI 입문자",
            "recommended_chapters": 8,
            "recommended_duration": "15시간"
        }
    else:
        return {
            "recommended_type": "advanced",
            "recommended_description": "실무 응용형",
            "recommended_chapters": 10,
            "recommended_duration": "20시간"
        }

def update_user_type_in_db(user_id, selected_type, connection):
    """유저 유형을 DB에 저장"""
    cursor = connection.cursor()
    try:
        query = """
        UPDATE users
        SET user_type = %s, diagnosis_completed = TRUE, updated_at = NOW()
        WHERE user_id = %s
        """
        cursor.execute(query, (selected_type, user_id))
        connection.commit()
    finally:
        cursor.close()
