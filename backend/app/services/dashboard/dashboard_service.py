# backend/app/services/dashboard_service.py
"""
대시보드 서비스
사용자의 학습 현황, 통계, 챕터별 진행 상태를 조회하는 서비스입니다.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.utils.database.connection import fetch_one, fetch_all
from app.utils.database.query_builder import QueryBuilder
from app.utils.response.formatter import success_response, error_response
from app.utils.response.error_formatter import ErrorFormatter
from app.config.db_config import DatabaseQueryError

# 로깅 설정
logger = logging.getLogger(__name__)


class DashboardService:
    """대시보드 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    @staticmethod
    def get_dashboard_overview(user_id: int) -> tuple:
        """
        대시보드 개요 데이터 조회
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            tuple: (응답 데이터, HTTP 상태 코드)
        """
        try:
            # 사용자 진행 상태 조회
            user_progress = DashboardService._get_user_progress(user_id)
            if not user_progress:
                return ErrorFormatter.format_database_error(
                    Exception("사용자 진행 상태를 찾을 수 없습니다.")
                )
            
            # 학습 통계 조회
            learning_statistics = DashboardService._get_learning_statistics(user_id)
            if not learning_statistics:
                return ErrorFormatter.format_database_error(
                    Exception("학습 통계를 찾을 수 없습니다.")
                )
            
            # 완료된 세션 정보 조회 (완료 날짜 계산용)
            completed_sessions = DashboardService._get_completed_sessions(user_id)
            
            # 챕터 상태 조회 (섹션 정보 포함)
            chapter_status = DashboardService._get_chapter_status(
                user_progress["current_chapter"], 
                user_progress["current_section"],
                completed_sessions
            )
            
            # 응답 데이터 구성
            dashboard_data = {
                "user_progress": {
                    "current_chapter": user_progress["current_chapter"],
                    "current_section": user_progress["current_section"],
                    "completion_percentage": DashboardService._calculate_completion_percentage(
                        user_progress["current_chapter"], 
                        user_progress["current_section"]
                    )
                },
                "learning_statistics": {
                    "total_study_time_seconds": learning_statistics["total_study_time_seconds"],
                    "total_study_sessions": learning_statistics["total_study_sessions"],
                    "multiple_choice_accuracy": float(learning_statistics["multiple_choice_accuracy"]),
                    "subjective_average_score": float(learning_statistics["subjective_average_score"]),
                    "total_multiple_choice_count": learning_statistics["total_multiple_choice_count"],
                    "total_subjective_count": learning_statistics["total_subjective_count"],
                    "last_study_date": learning_statistics["last_study_date"].strftime("%Y-%m-%d") if learning_statistics["last_study_date"] else None
                },
                "chapter_status": chapter_status
            }
            
            logger.info(f"대시보드 개요 조회 성공: user_id={user_id}")
            return success_response(
                data=dashboard_data,
                message="대시보드 데이터를 성공적으로 조회했습니다."
            )
            
        except DatabaseQueryError as e:
            logger.error(f"대시보드 조회 데이터베이스 오류: {e}")
            return ErrorFormatter.format_database_error(e)
        except Exception as e:
            logger.error(f"대시보드 조회 예상치 못한 오류: {e}")
            return ErrorFormatter.format_external_api_error("대시보드 서비스", e)
    
    @staticmethod
    def _get_user_progress(user_id: int) -> Optional[Dict[str, Any]]:
        """
        사용자 진행 상태 조회
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Optional[Dict[str, Any]]: 사용자 진행 상태 데이터
        """
        query_builder = QueryBuilder()
        query, params = (query_builder
                        .select([
                            'current_chapter',
                            'current_section', 
                            'last_study_date'
                        ])
                        .from_table('user_progress')
                        .where('user_id = %s', [user_id])
                        .build())
        
        result = fetch_one(query, params)
        return result
    
    @staticmethod
    def _get_learning_statistics(user_id: int) -> Optional[Dict[str, Any]]:
        """
        학습 통계 조회
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Optional[Dict[str, Any]]: 학습 통계 데이터
        """
        query_builder = QueryBuilder()
        query, params = (query_builder
                        .select([
                            'total_study_time_seconds',
                            'total_study_sessions',
                            'multiple_choice_accuracy',
                            'subjective_average_score',
                            'total_multiple_choice_count',
                            'total_subjective_count',
                            'last_study_date'
                        ])
                        .from_table('user_statistics')
                        .where('user_id = %s', [user_id])
                        .build())
        
        result = fetch_one(query, params)
        return result
    
    @staticmethod
    def _get_completed_sessions(user_id: int) -> List[Dict[str, Any]]:
        """
        완료된 세션 정보 조회
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            List[Dict[str, Any]]: 완료된 세션 리스트
        """
        query_builder = QueryBuilder()
        query, params = (query_builder
                        .select([
                            'chapter_number',
                            'section_number', 
                            'DATE(session_end_time) as completion_date',
                            'retry_decision_result'
                        ])
                        .from_table('learning_sessions')
                        .where('user_id = %s', [user_id])
                        .where('retry_decision_result = %s', ['proceed'])
                        .order_by('session_end_time', 'ASC')
                        .build())
        
        results = fetch_all(query, params)
        return results or []
    
    @staticmethod
    def _get_chapter_status(current_chapter: int, current_section: int, completed_sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        챕터별 상태 조회 (섹션 정보 포함)
        
        Args:
            current_chapter (int): 현재 진행 중인 챕터
            current_section (int): 현재 진행 중인 섹션
            completed_sessions (List[Dict[str, Any]]): 완료된 세션 리스트
            
        Returns:
            List[Dict[str, Any]]: 챕터별 상태 데이터
        """
        try:
            # JSON 파일에서 챕터 구조 로드
            chapters_structure = DashboardService._load_chapters_metadata()
            
            # 챕터별 상태 생성
            chapter_status_list = []
            
            for chapter_data in chapters_structure["chapters"]:
                chapter_num = chapter_data["chapter_number"]
                chapter_title = chapter_data["chapter_title"]
                
                # 챕터 상태 결정
                chapter_status = DashboardService._determine_chapter_status(
                    chapter_num, current_chapter, current_section
                )
                
                # 챕터 완료 날짜 (DB 세션 데이터 기반)
                chapter_completion_date = DashboardService._get_chapter_completion_date(
                    chapter_num, completed_sessions
                )
                
                # 섹션별 상태 생성
                sections = []
                for section_data in chapter_data["sections"]:
                    section_num = section_data["section_number"]
                    section_title = section_data["section_title"]
                    
                    section_status = DashboardService._determine_section_status(
                        chapter_num, section_num, current_chapter, current_section
                    )
                    
                    section_completion_date = DashboardService._get_section_completion_date(
                        chapter_num, section_num, completed_sessions
                    )
                    
                    sections.append({
                        "section_number": section_num,
                        "section_title": section_title,
                        "status": section_status,
                        "completion_date": section_completion_date
                    })
                
                chapter_status_list.append({
                    "chapter_number": chapter_num,
                    "chapter_title": chapter_title,
                    "status": chapter_status,
                    "completion_date": chapter_completion_date,
                    "sections": sections
                })
            
            return chapter_status_list
            
        except Exception as e:
            logger.error(f"챕터 상태 조회 오류: {e}")
            return []
    
    @staticmethod
    def _load_chapters_metadata() -> Dict[str, Any]:
        """
        JSON 파일에서 챕터 메타데이터 로드
        
        Returns:
            Dict[str, Any]: 챕터 구조 데이터
        """
        try:
            # 프로젝트 루트에서 JSON 파일 경로 구성
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # backend 폴더
            json_path = os.path.join(backend_root, 'data', 'chapters', 'chapters_metadata.json')
            
            with open(json_path, 'r', encoding='utf-8') as f:
                chapters_data = json.load(f)
            
            logger.debug(f"챕터 메타데이터 로드 성공: {chapters_data['metadata']['total_chapters']}개 챕터")
            return chapters_data
            
        except FileNotFoundError:
            logger.error(f"챕터 메타데이터 파일을 찾을 수 없습니다: {json_path}")
            return {"chapters": [], "metadata": {"total_chapters": 0}}
        except json.JSONDecodeError as e:
            logger.error(f"챕터 메타데이터 JSON 파싱 오류: {e}")
            return {"chapters": [], "metadata": {"total_chapters": 0}}
        except Exception as e:
            logger.error(f"챕터 메타데이터 로드 오류: {e}")
            return {"chapters": [], "metadata": {"total_chapters": 0}}
    
    @staticmethod
    def _determine_chapter_status(chapter_num: int, current_chapter: int, current_section: int) -> str:
        """
        챕터 상태 결정 (논리적 계산)
        
        Args:
            chapter_num (int): 판단할 챕터 번호
            current_chapter (int): 현재 진행 중인 챕터
            current_section (int): 현재 진행 중인 섹션
            
        Returns:
            str: 챕터 상태 ('completed', 'in_progress', 'locked')
        """
        if chapter_num < current_chapter:
            return "completed"
        elif chapter_num == current_chapter:
            return "in_progress"
        else:
            return "locked"
    
    @staticmethod
    def _determine_section_status(chapter_num: int, section_num: int, current_chapter: int, current_section: int) -> str:
        """
        섹션 상태 결정 (논리적 계산)
        
        Args:
            chapter_num (int): 섹션이 속한 챕터 번호
            section_num (int): 판단할 섹션 번호
            current_chapter (int): 현재 진행 중인 챕터
            current_section (int): 현재 진행 중인 섹션
            
        Returns:
            str: 섹션 상태 ('completed', 'in_progress', 'locked')
        """
        if chapter_num < current_chapter:
            return "completed"
        elif chapter_num == current_chapter:
            if section_num < current_section:
                return "completed"
            elif section_num == current_section:
                return "in_progress"
            else:
                return "locked"
        else:
            return "locked"
    
    @staticmethod
    def _get_chapter_completion_date(chapter_num: int, completed_sessions: List[Dict[str, Any]]) -> Optional[str]:
        """
        챕터 완료 날짜 조회 (해당 챕터의 마지막 섹션 완료 날짜)
        
        Args:
            chapter_num (int): 챕터 번호
            completed_sessions (List[Dict[str, Any]]): 완료된 세션 리스트
            
        Returns:
            Optional[str]: 완료 날짜 (YYYY-MM-DD 형식) 또는 None
        """
        chapter_sessions = [s for s in completed_sessions if s["chapter_number"] == chapter_num]
        if not chapter_sessions:
            return None
        
        # 해당 챕터의 가장 늦은 완료 날짜 반환
        latest_session = max(chapter_sessions, key=lambda x: x["completion_date"])
        completion_date = latest_session["completion_date"]
        
        if isinstance(completion_date, str):
            return completion_date
        elif hasattr(completion_date, 'strftime'):
            return completion_date.strftime("%Y-%m-%d")
        else:
            return None
    
    @staticmethod
    def _get_section_completion_date(chapter_num: int, section_num: int, completed_sessions: List[Dict[str, Any]]) -> Optional[str]:
        """
        섹션 완료 날짜 조회
        
        Args:
            chapter_num (int): 챕터 번호
            section_num (int): 섹션 번호
            completed_sessions (List[Dict[str, Any]]): 완료된 세션 리스트
            
        Returns:
            Optional[str]: 완료 날짜 (YYYY-MM-DD 형식) 또는 None
        """
        for session in completed_sessions:
            if (session["chapter_number"] == chapter_num and 
                session["section_number"] == section_num):
                completion_date = session["completion_date"]
                
                if isinstance(completion_date, str):
                    return completion_date
                elif hasattr(completion_date, 'strftime'):
                    return completion_date.strftime("%Y-%m-%d")
                else:
                    return None
        
        return None
    
    @staticmethod
    def _calculate_completion_percentage(current_chapter: int, current_section: int) -> float:
        """
        전체 학습 진행률 계산 (JSON 메타데이터 기반)
        
        Args:
            current_chapter (int): 현재 챕터
            current_section (int): 현재 섹션
            
        Returns:
            float: 진행률 (0.0 ~ 100.0)
        """
        try:
            # JSON에서 총 섹션 수 조회
            chapters_data = DashboardService._load_chapters_metadata()
            total_sections = chapters_data["metadata"]["total_sections"]
            
            # 완료된 섹션 수 계산
            completed_sections = 0
            
            for chapter_data in chapters_data["chapters"]:
                chapter_num = chapter_data["chapter_number"]
                
                if chapter_num < current_chapter:
                    # 이전 챕터는 모든 섹션 완료
                    completed_sections += chapter_data["total_sections"]
                elif chapter_num == current_chapter:
                    # 현재 챕터는 현재 섹션 이전까지만 완료
                    completed_sections += (current_section - 1)
                # 이후 챕터는 완료되지 않음
            
            # 진행률 계산 (소수점 첫째 자리까지)
            percentage = (completed_sections / total_sections) * 100
            return round(percentage, 1)
            
        except Exception as e:
            logger.error(f"진행률 계산 오류: {e}")
            # fallback: 기존 방식으로 계산
            total_chapters = 8
            sections_per_chapter = 4
            total_sections = total_chapters * sections_per_chapter
            completed_sections = (current_chapter - 1) * sections_per_chapter + (current_section - 1)
            percentage = (completed_sections / total_sections) * 100
            return round(percentage, 1)


# 서비스 인스턴스 생성
dashboard_service = DashboardService()