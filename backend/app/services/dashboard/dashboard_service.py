# backend/app/services/dashboard_service.py
# 대시보드 서비스 - 학습 현황 및 통계 조회

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date

from app.utils.auth.jwt_handler import decode_jwt_token
from app.utils.database.connection import fetch_one, fetch_all
from app.utils.database.query_builder import QueryBuilder
from app.utils.response.formatter import ResponseFormatter
from app.utils.response.error_formatter import ErrorFormatter

# 로깅 설정
logger = logging.getLogger(__name__)


class DashboardService:
    """
    대시보드 서비스 클래스
    사용자 학습 현황, 통계, 챕터 진행 상태 등을 제공합니다.
    """
    
    def __init__(self):
        self.service_name = "DashboardService"
    
    def get_dashboard_overview(self, token: str) -> Dict[str, Any]:
        """
        대시보드 개요 데이터 조회
        
        Args:
            token: JWT 액세스 토큰
            
        Returns:
            Dict: 대시보드 개요 응답
            {
                "success": true,
                "data": {
                    "user_progress": {...},
                    "learning_statistics": {...},
                    "chapter_status": [...]
                },
                "message": "대시보드 정보를 조회했습니다."
            }
        """
        try:
            # JWT 토큰 검증 및 사용자 정보 추출
            user_info = self._validate_token_and_get_user(token)
            if not user_info.get('success'):
                return user_info
            
            user_id = user_info['data']['user_id']
            user_type = user_info['data']['user_type']
            
            # 진단 완료 여부 확인
            if not user_info['data'].get('diagnosis_completed', False):
                return ErrorFormatter.format_authorization_error("진단 미완료", "대시보드 조회")[0]
            
            # 대시보드 데이터 수집
            dashboard_data = {}
            
            # 1. 사용자 진행 상태 조회
            user_progress = self._get_user_progress(user_id)
            dashboard_data['user_progress'] = user_progress
            
            # 2. 학습 통계 조회
            learning_statistics = self._get_learning_statistics(user_id)
            dashboard_data['learning_statistics'] = learning_statistics
            
            # 3. 챕터별 상태 조회
            chapter_status = self._get_chapter_status(user_id, user_type)
            dashboard_data['chapter_status'] = chapter_status
            
            return ResponseFormatter.success_response(
                data=dashboard_data,
                message="대시보드 정보를 조회했습니다."
            )[0]
            
        except Exception as e:
            logger.error(f"대시보드 개요 조회 오류: {e}")
            return ResponseFormatter.error_response(
                "DASHBOARD_OVERVIEW_ERROR",
                f"대시보드 정보 조회 중 오류가 발생했습니다: {str(e)}",
                status_code=500
            )[0]
    
    def _validate_token_and_get_user(self, token: str) -> Dict[str, Any]:
        """
        JWT 토큰 검증 및 사용자 정보 조회
        
        Args:
            token: JWT 액세스 토큰
            
        Returns:
            Dict: 사용자 정보 또는 에러 응답
        """
        try:
            # JWT 토큰 디코딩
            decoded_token = decode_jwt_token(token)
            if not decoded_token:
                return ErrorFormatter.format_authentication_error("token_invalid")[0]
            
            user_id = decoded_token.get('user_id')
            if not user_id:
                return ErrorFormatter.format_authentication_error("token_invalid")[0]
            
            # 사용자 정보 조회
            user_query = """
                SELECT user_id, login_id, username, user_type, diagnosis_completed
                FROM users 
                WHERE user_id = %s
            """
            user_record = fetch_one(user_query, (user_id,))
            
            if not user_record:
                return ErrorFormatter.format_authentication_error("token_invalid")[0]
            
            return {
                'success': True,
                'data': {
                    'user_id': user_record['user_id'],
                    'login_id': user_record['login_id'],
                    'username': user_record['username'],
                    'user_type': user_record['user_type'],
                    'diagnosis_completed': user_record['diagnosis_completed']
                }
            }
            
        except Exception as e:
            logger.error(f"토큰 검증 오류: {e}")
            return ErrorFormatter.format_authentication_error("token_invalid")[0]
    
    def _get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """
        사용자 진행 상태 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict: 사용자 진행 상태 정보
        """
        try:
            progress_query = """
                SELECT 
                    current_chapter,
                    current_section,
                    last_study_date
                FROM user_progress 
                WHERE user_id = %s
            """
            progress_record = fetch_one(progress_query, (user_id,))
            
            if not progress_record:
                # user_progress 레코드가 없는 경우 기본값 반환
                return {
                    "current_chapter": 1,
                    "current_section": 1,
                    "total_chapters": 8,  # 기본값 (추후 동적으로 계산)
                    "completion_percentage": 0.0
                }
            
            current_chapter = progress_record['current_chapter']
            current_section = progress_record['current_section']
            
            # TODO: 사용자 타입에 따른 총 챕터 수 동적 계산
            # 현재는 기본값 8개 챕터로 설정
            total_chapters = 8
            
            # 완료율 계산 (간단한 공식: (완료된 챕터 수) / 총 챕터 수 * 100)
            completed_chapters = max(0, current_chapter - 1)
            completion_percentage = (completed_chapters / total_chapters) * 100.0
            
            return {
                "current_chapter": current_chapter,
                "current_section": current_section,
                "total_chapters": total_chapters,
                "completion_percentage": round(completion_percentage, 1)
            }
            
        except Exception as e:
            logger.error(f"사용자 진행 상태 조회 오류: {e}")
            return {
                "current_chapter": 1,
                "current_section": 1,
                "total_chapters": 8,
                "completion_percentage": 0.0
            }
    
    def _get_learning_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        학습 통계 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict: 학습 통계 정보
        """
        try:
            stats_query = """
                SELECT 
                    total_study_time_minutes,
                    total_study_sessions,
                    total_completed_sessions,
                    multiple_choice_accuracy,
                    subjective_average_score,
                    last_study_date
                FROM user_statistics 
                WHERE user_id = %s
            """
            stats_record = fetch_one(stats_query, (user_id,))
            
            if not stats_record:
                # user_statistics 레코드가 없는 경우 기본값 반환
                return {
                    "total_study_time_minutes": 0,
                    "total_study_sessions": 0,
                    "total_completed_sessions": 0,
                    "multiple_choice_accuracy": 0.0,
                    "subjective_average_score": 0.0,
                    "last_study_date": None
                }
            
            # 마지막 학습일 포맷팅
            last_study_date = None
            if stats_record['last_study_date']:
                if isinstance(stats_record['last_study_date'], date):
                    last_study_date = stats_record['last_study_date'].strftime('%Y-%m-%d')
                else:
                    last_study_date = str(stats_record['last_study_date'])
            
            return {
                "total_study_time_minutes": stats_record['total_study_time_minutes'] or 0,
                "total_study_sessions": stats_record['total_study_sessions'] or 0,
                "total_completed_sessions": stats_record['total_completed_sessions'] or 0,
                "multiple_choice_accuracy": float(stats_record['multiple_choice_accuracy'] or 0.0),
                "subjective_average_score": float(stats_record['subjective_average_score'] or 0.0),
                "last_study_date": last_study_date
            }
            
        except Exception as e:
            logger.error(f"학습 통계 조회 오류: {e}")
            return {
                "total_study_time_minutes": 0,
                "total_study_sessions": 0,
                "total_completed_sessions": 0,
                "multiple_choice_accuracy": 0.0,
                "subjective_average_score": 0.0,
                "last_study_date": None
            }
    
    def _get_chapter_status(self, user_id: int, user_type: str) -> List[Dict[str, Any]]:
        """
        챕터별 진행 상태 조회
        
        Args:
            user_id: 사용자 ID
            user_type: 사용자 타입 ("beginner" 또는 "advanced")
            
        Returns:
            List[Dict]: 챕터별 상태 정보 리스트
        """
        try:
            # 사용자 현재 진행 상태 조회
            current_progress = self._get_user_progress(user_id)
            current_chapter = current_progress['current_chapter']
            
            # 완료된 챕터들의 학습 통계 조회
            completed_chapters_query = """
                SELECT 
                    chapter_number,
                    COUNT(*) as session_count,
                    AVG(study_duration_minutes) as avg_study_time,
                    MIN(session_start_time) as first_session,
                    MAX(session_start_time) as last_session
                FROM learning_sessions 
                WHERE user_id = %s 
                GROUP BY chapter_number
                ORDER BY chapter_number
            """
            completed_chapters = fetch_all(completed_chapters_query, (user_id,))
            
            # 챕터별 퀴즈 성과 조회
            quiz_stats_query = """
                SELECT 
                    ls.chapter_number,
                    AVG(CASE WHEN sq.quiz_type = 'multiple_choice' AND sq.multiple_answer_correct = 1 THEN 100 ELSE 0 END) as mc_accuracy,
                    AVG(CASE WHEN sq.quiz_type = 'subjective' THEN sq.subjective_answer_score ELSE NULL END) as subj_avg_score
                FROM learning_sessions ls
                JOIN session_quizzes sq ON ls.session_id = sq.session_id
                WHERE ls.user_id = %s
                GROUP BY ls.chapter_number
                ORDER BY ls.chapter_number
            """
            quiz_stats = fetch_all(quiz_stats_query, (user_id,))
            
            # 챕터별 상태 생성
            chapter_status_list = []
            total_chapters = 8 if user_type == "beginner" else 10
            
            # 완료된 챕터 통계를 딕셔너리로 변환
            completed_stats = {ch['chapter_number']: ch for ch in completed_chapters}
            quiz_stats_dict = {qs['chapter_number']: qs for qs in quiz_stats}
            
            for chapter_num in range(1, total_chapters + 1):
                chapter_info = {
                    "chapter_number": chapter_num,
                    "chapter_title": self._get_chapter_title(chapter_num),
                    "status": self._determine_chapter_status(chapter_num, current_chapter),
                    "completion_date": None,
                    "session_count": 0,
                    "avg_study_time_minutes": 0,
                    "average_score": 0
                }
                
                # 완료된 챕터인 경우 통계 추가
                if chapter_num in completed_stats:
                    stats = completed_stats[chapter_num]
                    chapter_info.update({
                        "session_count": stats['session_count'],
                        "avg_study_time_minutes": int(stats['avg_study_time'] or 0),
                        "completion_date": stats['last_session'].strftime('%Y-%m-%d') if stats['last_session'] else None
                    })
                
                # 퀴즈 성과 추가
                if chapter_num in quiz_stats_dict:
                    quiz_stat = quiz_stats_dict[chapter_num]
                    mc_accuracy = quiz_stat['mc_accuracy'] or 0
                    subj_score = quiz_stat['subj_avg_score'] or 0
                    
                    # 객관식과 주관식 점수를 평균내어 종합 점수 계산
                    if subj_score > 0:
                        chapter_info["average_score"] = int((mc_accuracy + subj_score) / 2)
                    else:
                        chapter_info["average_score"] = int(mc_accuracy)
                
                chapter_status_list.append(chapter_info)
            
            return chapter_status_list
            
        except Exception as e:
            logger.error(f"챕터 상태 조회 오류: {e}")
            # 에러 시 기본 챕터 리스트 반환
            return self._get_default_chapter_status(user_type)
    
    def _get_chapter_title(self, chapter_number: int) -> str:
        """
        챕터 번호에 따른 제목 반환
        
        Args:
            chapter_number: 챕터 번호
            
        Returns:
            str: 챕터 제목
        """
        chapter_titles = {
            1: "AI는 무엇인가?",
            2: "LLM이란 무엇인가",
            3: "다양한 AI 챗봇들 소개",
            4: "프롬프트란 무엇인가",
            5: "좋은 프롬프트 작성법",
            6: "ChatGPT로 할 수 있는 것들",
            7: "AI와 함께하는 일상업무",
            8: "AI 활용 고급 팁과 주의사항",
            9: "고급 프롬프트 엔지니어링",  # 실무 응용형 전용
            10: "API 연동 및 자동화"        # 실무 응용형 전용
        }
        return chapter_titles.get(chapter_number, f"{chapter_number}챕터")
    
    def _determine_chapter_status(self, chapter_number: int, current_chapter: int) -> str:
        """
        챕터 상태 결정
        
        Args:
            chapter_number: 챕터 번호
            current_chapter: 현재 진행 중인 챕터
            
        Returns:
            str: 챕터 상태 ("completed", "in_progress", "locked")
        """
        if chapter_number < current_chapter:
            return "completed"
        elif chapter_number == current_chapter:
            return "in_progress"
        else:
            return "locked"
    
    def _get_default_chapter_status(self, user_type: str) -> List[Dict[str, Any]]:
        """
        기본 챕터 상태 리스트 반환 (에러 시 사용)
        
        Args:
            user_type: 사용자 타입
            
        Returns:
            List[Dict]: 기본 챕터 상태 리스트
        """
        total_chapters = 8 if user_type == "beginner" else 10
        default_chapters = []
        
        for chapter_num in range(1, total_chapters + 1):
            default_chapters.append({
                "chapter_number": chapter_num,
                "chapter_title": self._get_chapter_title(chapter_num),
                "status": "locked" if chapter_num > 1 else "in_progress",
                "completion_date": None,
                "session_count": 0,
                "avg_study_time_minutes": 0,
                "average_score": 0
            })
        
        return default_chapters


# 전역 인스턴스 생성
dashboard_service = DashboardService()