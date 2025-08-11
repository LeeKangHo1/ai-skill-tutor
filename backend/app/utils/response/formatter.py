# backend/app/utils/response/formatter.py

from flask import jsonify

class ResponseFormatter:
    @staticmethod
    def success_response(data=None, message="요청이 성공적으로 처리되었습니다.", status_code=200):
        return jsonify({
            "success": True,
            "data": data,
            "message": message
        }), status_code

    @staticmethod
    def error_response(code, message, details=None, status_code=400):
        return jsonify({
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {}
            }
        }), status_code

    @staticmethod
    def paginated_response(data, page, per_page, total, message="데이터가 성공적으로 조회되었습니다."):
        return jsonify({
            "success": True,
            "data": {
                "items": data,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            },
            "message": message
        }), 200

    @staticmethod
    def validation_error_response(validation_errors):
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "입력값이 올바르지 않습니다.",
                "details": validation_errors
            }
        }), 400

# 함수 형태 alias
success_response = ResponseFormatter.success_response
error_response = ResponseFormatter.error_response
paginated_response = ResponseFormatter.paginated_response
validation_error_response = ResponseFormatter.validation_error_response