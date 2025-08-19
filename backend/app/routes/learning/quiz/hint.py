# backend/app/routes/learning/quiz/hint.py
"""
퀴즈 힌트 요청 라우트
사용자에게 퀴즈 힌트를 제공합니다.

**현재 사용하지 않는 기능입니다.**
"""

# from flask import Blueprint, request, jsonify
# from app.utils.auth.jwt_handler import require_auth, get_current_user_from_request
# from app.utils.response.formatter import format_validation_error

# # 퀴즈 힌트 Blueprint 생성
# hint_bp = Blueprint('quiz_hint', __name__)


# @hint_bp.route('/hint', methods=['POST'])
# @require_auth
# def request_quiz_hint():
#     """
#     퀴즈 힌트 요청 (선택적 기능)
    
#     Request Body:
#     {
#         "hint_request": true
#     }
    
#     Response:
#     {
#         "success": true,
#         "data": {
#             "hint": "LLM의 'L'이 무엇을 의미하는지 생각해보세요.",
#             "hint_usage_count": 1
#         },
#         "message": "힌트를 제공했습니다."
#     }
#     """
#     try:
#         # 요청 데이터 검증
#         request_data = request.get_json()
#         if not request_data:
#             return jsonify(format_validation_error(
#                 "VALIDATION_ERROR", 
#                 "요청 데이터가 필요합니다."
#             )), 400
        
#         hint_request = request_data.get('hint_request', False)
        
#         if not isinstance(hint_request, bool) or not hint_request:
#             return jsonify(format_validation_error(
#                 "VALIDATION_ERROR", 
#                 "hint_request는 true여야 합니다."
#             )), 400
        
#         # 현재 사용자 정보 가져오기
#         current_user = get_current_user_from_request()
#         if not current_user:
#             return jsonify(format_validation_error(
#                 "AUTH_TOKEN_INVALID", 
#                 "유효하지 않은 토큰입니다."
#             )), 401
        
#         # Authorization 헤더에서 토큰 추출
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return jsonify(format_validation_error(
#                 "AUTH_TOKEN_REQUIRED", 
#                 "인증 토큰이 필요합니다."
#             )), 401
        
#         token = auth_header.split(' ')[1]
        
#         # 힌트 요청 처리 (향후 구현 예정)
#         # TODO: SessionService에 get_quiz_hint 메서드 추가 필요
#         return jsonify(format_validation_error(
#             "FEATURE_NOT_IMPLEMENTED", 
#             "힌트 기능은 현재 구현 중입니다."
#         )), 501
        
#     except Exception as e:
#         return jsonify(format_validation_error(
#             "HINT_REQUEST_ERROR", 
#             f"힌트 요청 중 예상치 못한 오류가 발생했습니다: {str(e)}"
#         )), 500