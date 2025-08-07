# backend/app/routes/diagnosis/questions.py

from flask import Blueprint, jsonify
import json
import os
from app.utils.logging.logger import log_error  # ✅ 추가

# Blueprint 생성
diagnosis_questions_bp = Blueprint('diagnosis_questions', __name__)

@diagnosis_questions_bp.route('/questions', methods=['GET'])
def get_diagnosis_questions():
    """
    진단 문항 조회 API
    사용자 진단을 위한 문항 목록을 반환합니다.
    """
    try:
        # JSON 파일 경로 설정
        current_dir = os.path.dirname(__file__)
        json_file_path = os.path.join(current_dir, '..', '..', '..', 'data', 'diagnosis_questions.json')

        # JSON 파일 읽기
        with open(json_file_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)

        return jsonify({
            "success": True,
            "data": {
                "questions": questions_data["questions"],
                "total_questions": len(questions_data["questions"])
            },
            "message": "진단 문항을 성공적으로 조회했습니다."
        }), 200

    except FileNotFoundError as e:
        log_error(e, {"route": "/questions", "error": "file_not_found"})  # ✅ 로그 추가
        return jsonify({
            "success": False,
            "error": {
                "code": "FILE_NOT_FOUND",
                "message": "진단 문항 파일을 찾을 수 없습니다."
            }
        }), 500

    except json.JSONDecodeError as e:
        log_error(e, {"route": "/questions", "error": "json_parse_error"})  # ✅ 로그 추가
        return jsonify({
            "success": False,
            "error": {
                "code": "JSON_PARSE_ERROR",
                "message": "진단 문항 파일을 읽는 중 오류가 발생했습니다."
            }
        }), 500

    except Exception as e:
        log_error(e, {"route": "/questions"})  # ✅ 로그 추가
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다."
            }
        }), 500
