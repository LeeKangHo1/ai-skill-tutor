# backend/app/services/dashboard_service.py
"""
대시보드 서비스
사용자의 학습 현황, 통계, 챕터별 진행 상태를 조회하는 서비스입니다.
"""

import logging
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
            
            # 챕터 상태 조회 (섹션 정보 포함)
            chapter_status = DashboardService._get_chapter_status(user_id)
            
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
                    "total_study_time_minutes": learning_statistics["total_study_time_minutes"],
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
        query, params = query_builder.select([
            'current_chapter',
            'current_section', 
            'last_study_date'
        ]).from_table('user_progress').where('user_id = %s', [user_id]).build()
        
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
        query = """
        SELECT 
            total_study_time_minutes,
            total_study_sessions,
            multiple_choice_accuracy,
            subjective_average_score,
            total_multiple_choice_count,
            total_subjective_count,
            last_study_date
        FROM user_statistics 
        WHERE user_id = %s
        """
        
        result = fetch_one(query, (user_id,))
        return result
    
    @staticmethod
    def _get_chapter_status(user_id: int) -> List[Dict[str, Any]]:
        """
        챕터별 상태 조회 (섹션 정보 포함)
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            List[Dict[str, Any]]: 챕터별 상태 데이터
        """
        try:
            # 사용자의 현재 진행 상태 조회
            current_progress = DashboardService._get_user_progress(user_id)
            current_chapter = current_progress["current_chapter"] if current_progress else 1
            current_section = current_progress["current_section"] if current_progress else 1
            
            # 완료된 세션 정보 조회 (챕터/섹션별 완료 날짜)
            completed_sessions = DashboardService._get_completed_sessions(user_id)
            
            # 하드코딩된 챕터/섹션 구조 (향후 DB나 JSON 파일로 분리 가능)
            chapters_structure = DashboardService._get_chapters_structure()
            
            # 챕터별 상태 생성
            chapter_status_list = []
            
            for chapter_num, chapter_info in chapters_structure.items():
                # 챕터 상태 결정
                chapter_status = DashboardService._determine_chapter_status(
                    chapter_num, current_chapter, current_section
                )
                
                # 챕터 완료 날짜 조회
                chapter_completion_date = DashboardService._get_chapter_completion_date(
                    chapter_num, completed_sessions
                )
                
                # 섹션별 상태 생성
                sections = []
                for section_num, section_title in chapter_info["sections"].items():
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
                    "chapter_title": chapter_info["title"],
                    "status": chapter_status,
                    "completion_date": chapter_completion_date,
                    "sections": sections
                })
            
            return chapter_status_list
            
        except Exception as e:
            logger.error(f"챕터 상태 조회 오류: {e}")
            return []
    
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
        query, params = query_builder.select([
            'chapter_number',
            'section_number', 
            'DATE(session_end_time) as completion_date',
            'retry_decision_result'
        ]).from_table('learning_sessions').where('user_id = %s', [user_id]).where('retry_decision_result = %s', ['proceed']).order_by('session_end_time', 'ASC').build()
        
        results = fetch_all(query, params)
        return results or []
    
    @staticmethod
    def _get_chapters_structure() -> Dict[int, Dict[str, Any]]:
        """
        하드코딩된 챕터/섹션 구조 반환
        향후 DB의 chapters 테이블이나 JSON 파일로 분리 예정
        
        Returns:
            Dict[int, Dict[str, Any]]: 챕터 구조 데이터
        """
        return {
            1: {
                "title": "AI는 무엇인가?",
                "sections": {
                    1: "AI의 정의와 특징",
                    2: "AI의 역사와 발전", 
                    3: "AI의 종류와 분류",
                    4: "AI의 활용 사례"
                }
            },
            2: {
                "title": "LLM이란 무엇인가",
                "sections": {
                    1: "LLM의 기본 개념",
                    2: "LLM의 동작 원리",
                    3: "대표적인 LLM 모델들",
                    4: "LLM의 한계와 특징"
                }
            },
            3: {
                "title": "프롬프트란 무엇인가",
                "sections": {
                    1: "프롬프트의 기본 개념",
                    2: "효과적인 프롬프트 작성법",
                    3: "프롬프트 엔지니어링 기초",
                    4: "프롬프트 실습과 예제"
                }
            },
            4: {
                "title": "좋은 프롬프트 작성법",
                "sections": {
                    1: "역할 부여의 마법",
                    2: "구체적 조건 제시하기",
                    3: "형식 지정 방법",
                    4: "이미지 생성 프롬프트"
                }
            },
            5: {
                "title": "ChatGPT로 할 수 있는 것들",
                "sections": {
                    1: "문서 요약하기",
                    2: "똑똑한 AI 번역기",
                    3: "아이디어 발전시키기",
                    4: "여행 계획 짜기"
                }
            },
            6: {
                "title": "AI와 함께하는 일상업무",
                "sections": {
                    1: "이메일 작성하기",
                    2: "엑셀 함수 활용",
                    3: "회의록 정리",
                    4: "업무 비서 만들기"
                }
            },
            7: {
                "title": "다양한 AI 챗봇들 소개",
                "sections": {
                    1: "ChatGPT 소개",
                    2: "Claude 소개",
                    3: "Gemini 소개",
                    4: "한국형 챗봇들"
                }
            },
            8: {
                "title": "AI 활용 고급 팁과 주의사항",
                "sections": {
                    1: "환각 현상과 해결 방법",
                    2: "Chain-of-Thought 활용",
                    3: "AI와 함께 학습하기",
                    4: "AI 윤리 문제"
                }
            }
        }
    
    @staticmethod
    def _determine_chapter_status(chapter_num: int, current_chapter: int, current_section: int) -> str:
        """
        챕터 상태 결정
        
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
        섹션 상태 결정
        
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
        latest_date = max(chapter_sessions, key=lambda x: x["completion_date"])
        return latest_date["completion_date"].strftime("%Y-%m-%d") if latest_date["completion_date"] else None
    
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
                return session["completion_date"].strftime("%Y-%m-%d") if session["completion_date"] else None
        
        return None
    
    @staticmethod
    def _calculate_completion_percentage(current_chapter: int, current_section: int) -> float:
        """
        전체 학습 진행률 계산
        
        Args:
            current_chapter (int): 현재 챕터
            current_section (int): 현재 섹션
            
        Returns:
            float: 진행률 (0.0 ~ 100.0)
        """
        # 총 챕터 수와 섹션 수 (하드코딩, 향후 동적으로 변경 가능)
        total_chapters = 8
        sections_per_chapter = 4
        total_sections = total_chapters * sections_per_chapter
        
        # 완료된 섹션 수 계산
        completed_sections = (current_chapter - 1) * sections_per_chapter + (current_section - 1)
        
        # 진행률 계산 (소수점 첫째 자리까지)
        percentage = (completed_sections / total_sections) * 100
        return round(percentage, 1)


# 서비스 인스턴스 생성
dashboard_service = DashboardService()