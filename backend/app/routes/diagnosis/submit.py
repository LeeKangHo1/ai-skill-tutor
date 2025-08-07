# backend/app/routes/diagnosis/submit.py

from flask import Blueprint, request, jsonify
from app.utils.database.connection import get_db_connection
from app.utils.auth.jwt_handler import get_current_user
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
        current_user = get_current_user()
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
    사용자가 최종 선택한 유형을 데이터베이스에 저장합니다.
    """
    try:
        current_user = get_current_user()
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

        connection = get_db_connection()
        try:
            update_user_type_in_db(current_user['user_id'], selected_type, connection)
        except Exception as db_error:
            connection.rollback()
            log_error(db_error, {"route": "/select-type"})
            return jsonify({
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "데이터베이스 업데이트 중 오류가 발생했습니다."
                }
            }), 500
        finally:
            connection.close()

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

        return jsonify({
            "success": True,
            "data": type_info_map[selected_type],
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

