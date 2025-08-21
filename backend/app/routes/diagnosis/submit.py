# backend/app/routes/diagnosis/submit.py

from flask import Blueprint, request, jsonify
from app.utils.database.connection import get_db_connection, fetch_one
from app.utils.auth.jwt_handler import get_current_user_from_request, generate_access_token
from app.utils.logging.logger import log_error
from app.services.diagnosis_service import calculate_score, recommend_type_by_score, update_user_type_in_db

# Blueprint 생성
diagnosis_submit_bp = Blueprint('diagnosis_submit', __name__)

@diagnosis_submit_bp.route('/submit', methods=['POST'])
def submit_diagnosis():
    """
    진단 결과 제출 API
    사용자의 진단 답변을 받아 점수 계산 후 추천 유형을 제시합니다.
    """
    try:
        current_user = get_current_user_from_request()
        if not current_user:
            return jsonify({
                "success": False,
                "error": {
                    "code": "AUTH_REQUIRED",
                    "message": "로그인이 필요합니다."
                }
            }), 401

        data = request.get_json()
        answers = data.get('answers')
        if not answers or len(answers) != 5:
            return jsonify({
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "5개 문항에 대한 답변이 필요합니다."
                }
            }), 400

        try:
            total_score = calculate_score(answers)
            recommended = recommend_type_by_score(total_score)
        except ValueError as ve:
            return jsonify({
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(ve)
                }
            }), 400

        return jsonify({
            "success": True,
            "data": {
                "total_score": total_score,
                **recommended,
                "user_types": [
                    {
                        "type": "beginner",
                        "description": "AI 입문자",
                        "chapters": 8,
                        "duration": "15시간",
                        "features": [
                            "기초적인 AI 개념 학습",
                            "단계별 상세 설명",
                            "일상생활 비유를 통한 이해"
                        ]
                    },
                    {
                        "type": "advanced",
                        "description": "실무 응용형",
                        "chapters": 10,
                        "duration": "20시간",
                        "features": [
                            "기술적 원리 중심 학습",
                            "실무 케이스 및 코드 예제",
                            "고급 프롬프트 엔지니어링"
                        ]
                    }
                ]
            },
            "message": "진단 결과가 생성되었습니다. 원하는 유형을 선택해주세요."
        }), 200

    except Exception as e:
        log_error(e, {"route": "/submit"})
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다."
            }
        }), 500

@diagnosis_submit_bp.route('/select-type', methods=['POST'])
def select_user_type():
    """
    사용자 유형 선택 API
    사용자가 최종 선택한 유형을 데이터베이스에 저장하고 새로운 JWT 토큰을 발급합니다.
    """
    try:
        current_user = get_current_user_from_request()
        if not current_user:
            return jsonify({
                "success": False,
                "error": {
                    "code": "AUTH_REQUIRED",
                    "message": "로그인이 필요합니다."
                }
            }), 401

        data = request.get_json()
        selected_type = data.get('selected_type')

        if selected_type not in ['beginner', 'advanced']:
            return jsonify({
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "유효하지 않은 사용자 유형입니다."
                }
            }), 400

        try:
            with get_db_connection() as connection:
                update_user_type_in_db(current_user['user_id'], selected_type, connection)
        except Exception as db_error:
            log_error(db_error, {"route": "/select-type"})
            return jsonify({
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "데이터베이스 업데이트 중 오류가 발생했습니다."
                }
            }), 500

        # DB 업데이트 후 최신 사용자 정보로 새로운 JWT 토큰 생성
        try:
            # 데이터베이스에서 최신 사용자 정보 조회
            updated_user = fetch_one(
                """
                SELECT user_id, login_id, user_type, diagnosis_completed 
                FROM users 
                WHERE user_id = %s
                """,
                (current_user['user_id'],)
            )
            
            if not updated_user:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "message": "사용자 정보를 찾을 수 없습니다."
                    }
                }), 404
            
            # 새로운 access_token 생성
            token_data = {
                'user_id': updated_user['user_id'],
                'login_id': updated_user['login_id'],
                'user_type': updated_user['user_type'],
                'diagnosis_completed': bool(updated_user['diagnosis_completed'])
            }
            
            new_access_token = generate_access_token(token_data)
            
        except Exception as token_error:
            log_error(token_error, {"route": "/select-type", "action": "token_generation"})
            return jsonify({
                "success": False,
                "error": {
                    "code": "TOKEN_GENERATION_ERROR",
                    "message": "토큰 생성 중 오류가 발생했습니다."
                }
            }), 500

        # 선택된 유형에 따른 정보 직접 반환
        type_info_map = {
            "beginner": {
                "recommended_type": "beginner",
                "recommended_description": "AI 입문자",
                "recommended_chapters": 8,
                "recommended_duration": "15시간"
            },
            "advanced": {
                "recommended_type": "advanced",
                "recommended_description": "실무 응용형",
                "recommended_chapters": 10,
                "recommended_duration": "20시간"
            }
        }

        # 응답에 새로운 access_token 포함
        response_data = type_info_map[selected_type]
        response_data['access_token'] = new_access_token

        return jsonify({
            "success": True,
            "data": response_data,
            "message": "사용자 유형이 성공적으로 설정되었습니다."
        }), 200

    except Exception as e:
        log_error(e, {"route": "/select-type"})
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다."
            }
        }), 500

