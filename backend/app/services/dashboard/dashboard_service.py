# backend/app/services/dashboard/dashboard_service.py
# 대시보드 비즈니스 로직 서비스 - user_statistics 테이블 전용

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date

from app.utils.database.connection import fetch_one
from app.config.db_config import DatabaseQueryError

# 로깅 설정
logger = logging.getLogger(__name__)

class DashboardService:
    """
    대시보드 관련 비즈니스 로직을 처리하는 서비스 클래스
    
    user_statistics 테이블의 학습 통계 정보만 제공합니다.
    """
    
    def get_dashboard_overview(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        대시보드 개요 데이터 조회 (user_statistics 테이블만)
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Optional[Dict[str, Any]]: 사용자 학습 통계 데이터 또는 None
            
        Raises:
            DatabaseQueryError: 데이터베이스 조회 오류 시
        """
        try:
            logger.info(f"사용자 통계 데이터 조회 시작 - 사용자 ID: {user_id}")
            
            # user_statistics 테이블에서 모든 통계 정보 조회
            query = """
                SELECT 
                    total_study_time_minutes,
                    total_study_sessions,
                    total_completed_sessions,
                    total_multiple_choice_count,
                    total_multiple_choice_correct,
                    multiple_choice_accuracy,
                    total_subjective_count,
                    total_subjective_score,
                    subjective_average_score,
                    last_study_date
                FROM user_statistics
                WHERE user_id = %s
            """
            
            result = fetch_one(query, (user_id,))
            
            if result:
                # 조회된 데이터를 API 응답 형식으로 변환
                overview_data = {
                    "total_study_time_minutes": result.get("total_study_time_minutes", 0),
                    "total_study_sessions": result.get("total_study_sessions", 0),
                    "total_completed_sessions": result.get("total_completed_sessions", 0),
                    "total_multiple_choice_count": result.get("total_multiple_choice_count", 0),
                    "total_multiple_choice_correct": result.get("total_multiple_choice_correct", 0),
                    "multiple_choice_accuracy": float(result.get("multiple_choice_accuracy", 0.0)),
                    "total_subjective_count": result.get("total_subjective_count", 0),
                    "total_subjective_score": result.get("total_subjective_score", 0),
                    "subjective_average_score": float(result.get("subjective_average_score", 0.0)),
                    "last_study_date": result.get("last_study_date").isoformat() if result.get("last_study_date") else None
                }
                
                logger.info(f"사용자 통계 데이터 조회 성공 - 사용자 ID: {user_id}")
                return overview_data
            else:
                # user_statistics 레코드가 없는 경우
                logger.warning(f"사용자 통계 데이터가 없음 - 사용자 ID: {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"사용자 통계 데이터 조회 오류 - 사용자 ID: {user_id}: {e}")
            raise DatabaseQueryError(f"사용자 통계 데이터 조회 중 오류가 발생했습니다: {e}")