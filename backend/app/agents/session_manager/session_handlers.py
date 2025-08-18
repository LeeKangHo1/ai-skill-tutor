# backend/app/agents/session_manager/session_handlers.py

"""
SessionHandlers v2.0 - 세션 데이터 DB 저장 핸들러

주요 v2.0 변경사항:
- AUTO_INCREMENT 세션 ID 반환 (save_session_info 메서드)
- 객관식/주관식 분리된 통계 계산 (_recalculate_average_accuracy)
- retry_decision_result 필드명 변경
- section_number 필드 추가로 섹션별 진행 관리
- 분리된 퀴즈 통계 (multiple_choice_accuracy, subjective_average_score)
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from app.utils.database.query_builder import insert_record, update_record, count_records
from app.utils.database.connection import fetch_one, fetch_all
from app.utils.database.transaction import execute_transaction
from app.config.db_config import DatabaseQueryError, DatabaseIntegrityError


class SessionHandlers:
    """
    세션 데이터 DB 저장을 담당하는 핸들러 클래스
    
    주요 기능:
    1. learning_sessions 테이블에 세션 정보 저장
    2. session_conversations 테이블에 대화 기록 저장
    3. session_quizzes 테이블에 퀴즈 정보 저장
    4. user_progress, user_statistics 테이블 업데이트
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def save_session_info(self, session_data: Dict[str, Any]) -> int:
        """
        learning_sessions 테이블에 세션 기본 정보 저장 (v2.0: AUTO_INCREMENT 세션 ID 반환)
        
        Args:
            session_data: 세션 정보 딕셔너리 (session_id 필드 제외)
            
        Returns:
            생성된 세션 ID (AUTO_INCREMENT), 실패 시 None
        """
        try:
            # v2.0: AUTO_INCREMENT 세션 ID 사용
            session_id = insert_record('learning_sessions', session_data, return_id=True)
            
            if session_id:
                self.logger.info(f"세션 정보 저장 완료: session_id={session_id}")
                
                # user_progress 및 user_statistics 업데이트
                session_data_with_id = session_data.copy()
                session_data_with_id['session_id'] = session_id
                self._update_user_progress(session_data_with_id)
                self._update_user_statistics(session_data_with_id)
                
                return session_id
            else:
                self.logger.error("세션 ID 생성 실패")
                return None
                
        except DatabaseIntegrityError as e:
            self.logger.error(f"세션 정보 저장 무결성 오류: {str(e)}")
            return None
        except DatabaseQueryError as e:
            self.logger.error(f"세션 정보 저장 쿼리 오류: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"세션 정보 저장 중 예상치 못한 오류: {str(e)}")
            return None
    
    def save_session_conversations(self, session_id: int, conversations: List[Dict[str, Any]]) -> bool:
        """
        session_conversations 테이블에 대화 기록 저장
        
        Args:
            session_id: 세션 ID
            conversations: 대화 기록 리스트
            
        Returns:
            저장 성공 여부
        """
        try:
            if not conversations:
                self.logger.info("저장할 대화 기록이 없습니다.")
                return True
            
            # 배치 INSERT를 위한 트랜잭션 작업 준비
            operations = []
            
            for idx, conv in enumerate(conversations, 1):
                record_data = {
                    'session_id': session_id,
                    'message_sequence': idx,
                    'agent_name': conv.get('agent_name', 'unknown'),
                    'message_type': conv.get('message_type', 'system'),
                    'message_content': str(conv.get('message', '')),
                    'message_timestamp': self._format_timestamp(conv.get('timestamp')),
                    'session_progress_stage': conv.get('session_stage', 'session_start')
                }
                
                operation = {
                    'type': 'insert',
                    'table': 'session_conversations',
                    'data': record_data,
                    'return_id': False
                }
                operations.append(operation)
            
            # 트랜잭션으로 배치 INSERT
            result = execute_transaction(operations)
            
            if result:
                self.logger.info(f"대화 기록 저장 완료: {session_id} ({len(conversations)}개)")
                return True
            else:
                self.logger.error("대화 기록 저장 실패")
                return False
                
        except DatabaseIntegrityError as e:
            self.logger.error(f"대화 기록 저장 무결성 오류: {str(e)}")
            return False
        except DatabaseQueryError as e:
            self.logger.error(f"대화 기록 저장 쿼리 오류: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"대화 기록 저장 중 예상치 못한 오류: {str(e)}")
            return False
    
    def save_session_quiz(self, quiz_data: Dict[str, Any]) -> bool:
        """
        session_quizzes 테이블에 퀴즈 정보 저장
        
        Args:
            quiz_data: 퀴즈 정보 딕셔너리
            
        Returns:
            저장 성공 여부
        """
        try:
            if not quiz_data:
                self.logger.info("저장할 퀴즈 정보가 없습니다.")
                return True
            
            result = insert_record('session_quizzes', quiz_data, return_id=False)
            
            # insert_record는 return_id=False일 때 None을 반환하므로 예외가 없으면 성공
            self.logger.info(f"퀴즈 정보 저장 완료: {quiz_data['session_id']}")
            return True
                
        except DatabaseIntegrityError as e:
            self.logger.error(f"퀴즈 정보 저장 무결성 오류: {str(e)}")
            return False
        except DatabaseQueryError as e:
            self.logger.error(f"퀴즈 정보 저장 쿼리 오류: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"퀴즈 정보 저장 중 예상치 못한 오류: {str(e)}")
            return False
    
    def _update_user_progress(self, session_data: Dict[str, Any]) -> bool:
        """
        user_progress 테이블 업데이트
        
        Args:
            session_data: 세션 정보
            
        Returns:
            업데이트 성공 여부
        """
        try:
            # proceed인 경우에만 진행 상태 업데이트 (v2.0: 필드명 변경)
            if session_data.get('retry_decision_result') == 'proceed':
                update_data = {
                    'current_chapter': session_data['chapter_number'],
                    'current_section': session_data['section_number'],  # v2.0: 섹션 정보 추가
                    'last_study_date': datetime.now().date(),
                    'updated_at': datetime.now()
                }
                
                where_clause = "user_id = %s"
                where_params = [session_data['user_id']]
                
                result = update_record(
                    'user_progress', 
                    update_data, 
                    where_clause, 
                    where_params
                )
                
                if result > 0:
                    self.logger.info(f"사용자 진행 상태 업데이트 완료: user_id={session_data['user_id']}")
                    return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"사용자 진행 상태 업데이트 중 오류: {str(e)}")
            return False
    
    def _update_user_statistics(self, session_data: Dict[str, Any]) -> bool:
        """
        user_statistics 테이블 업데이트
        
        Args:
            session_data: 세션 정보
            
        Returns:
            업데이트 성공 여부
        """
        try:
            # 통계 업데이트 데이터 준비
            query = """
            UPDATE user_statistics 
            SET total_study_sessions = total_study_sessions + 1,
                total_completed_sessions = total_completed_sessions + 1,
                total_study_time_minutes = total_study_time_minutes + %s,
                last_study_date = CURDATE(),
                updated_at = NOW()
            WHERE user_id = %s
            """
            
            params = [
                session_data.get('study_duration_minutes', 0),
                session_data['user_id']
            ]
            
            # 직접 쿼리 실행 (복잡한 계산이 포함된 업데이트)
            from app.utils.database.connection import execute_query
            result = execute_query(query, params)
            
            if result > 0:
                # 평균 정확도 재계산
                self._recalculate_average_accuracy(session_data['user_id'])
                self.logger.info(f"사용자 통계 업데이트 완료: user_id={session_data['user_id']}")
                return True
            else:
                self.logger.error("사용자 통계 업데이트 실패")
                return False
                
        except Exception as e:
            self.logger.error(f"사용자 통계 업데이트 중 오류: {str(e)}")
            return False
    
    def _recalculate_average_accuracy(self, user_id: int) -> bool:
        """
        사용자의 평균 정확도 재계산 (v2.0: 객관식/주관식 분리 통계)
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            재계산 성공 여부
        """
        try:
            # v2.0: 객관식/주관식 분리된 퀴즈 점수 조회
            query = """
            SELECT sq.quiz_type, sq.multiple_answer_correct, sq.subjective_answer_score
            FROM session_quizzes sq
            JOIN learning_sessions ls ON sq.session_id = ls.session_id
            WHERE ls.user_id = %s
            """
            
            quiz_results = fetch_all(query, [user_id])
            
            if not quiz_results:
                return True  # 퀴즈 결과가 없으면 그대로 유지
            
            # v2.0: 객관식/주관식 분리 통계 계산
            multiple_choice_count = 0
            multiple_choice_correct = 0
            subjective_count = 0
            subjective_total_score = 0
            
            for result in quiz_results:
                quiz_type = result.get('quiz_type', 'multiple_choice')
                
                if quiz_type == 'multiple_choice':
                    multiple_choice_count += 1
                    if result.get('multiple_answer_correct', False):
                        multiple_choice_correct += 1
                else:  # subjective
                    subjective_count += 1
                    subjective_total_score += result.get('subjective_answer_score', 0)
            
            # 객관식 정답률 계산
            multiple_choice_accuracy = (multiple_choice_correct / multiple_choice_count * 100) if multiple_choice_count > 0 else 0
            
            # 주관식 평균 점수 계산
            subjective_average_score = (subjective_total_score / subjective_count) if subjective_count > 0 else 0
            
            # v2.0: 분리된 통계 업데이트
            update_data = {
                'total_multiple_choice_count': multiple_choice_count,
                'total_multiple_choice_correct': multiple_choice_correct,
                'multiple_choice_accuracy': round(multiple_choice_accuracy, 2),
                'total_subjective_count': subjective_count,
                'total_subjective_score': subjective_total_score,
                'subjective_average_score': round(subjective_average_score, 2),
                'updated_at': datetime.now()
            }
            
            where_clause = "user_id = %s"
            where_params = [user_id]
            
            result = update_record(
                'user_statistics', 
                update_data, 
                where_clause, 
                where_params
            )
            
            if result > 0:
                self.logger.info(f"분리 통계 재계산 완료: user_id={user_id}, 객관식={multiple_choice_accuracy:.2f}%, 주관식={subjective_average_score:.2f}점")
                return True
            else:
                self.logger.error("분리 통계 업데이트 실패")
                return False
                
        except Exception as e:
            self.logger.error(f"분리 통계 재계산 중 오류: {str(e)}")
            return False
    
    def _format_timestamp(self, timestamp) -> datetime:
        """
        타임스탬프 포맷 통일
        
        Args:
            timestamp: 다양한 형태의 타임스탬프
            
        Returns:
            datetime 객체
        """
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return datetime.now()
        else:
            return datetime.now()
    
    def get_session_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        사용자의 세션 기록 조회 (선택적 기능) - v2.0 필드명 업데이트
        
        Args:
            user_id: 사용자 ID
            limit: 조회할 세션 개수
            
        Returns:
            세션 기록 리스트
        """
        try:
            query = """
            SELECT 
                session_id, chapter_number, section_number,
                session_start_time, session_end_time, study_duration_minutes,
                retry_decision_result, created_at
            FROM learning_sessions
            WHERE user_id = %s
            ORDER BY session_start_time DESC
            LIMIT %s
            """
            
            params = [user_id, limit]
            results = fetch_all(query, params)
            
            if results:
                self.logger.info(f"세션 기록 조회 완료: user_id={user_id}, count={len(results)}")
                return results
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"세션 기록 조회 중 오류: {str(e)}")
            return []
    
    def get_session_conversations(self, session_id: int) -> List[Dict[str, Any]]:
        """
        특정 세션의 대화 기록 조회 (선택적 기능)
        
        Args:
            session_id: 세션 ID
            
        Returns:
            대화 기록 리스트
        """
        try:
            query = """
            SELECT 
                message_sequence, agent_name, message_type, message_content,
                message_timestamp, session_progress_stage, created_at
            FROM session_conversations
            WHERE session_id = %s
            ORDER BY message_sequence
            """
            
            params = [session_id]
            results = fetch_all(query, params)
            
            if results:
                self.logger.info(f"대화 기록 조회 완료: session_id={session_id}, count={len(results)}")
                return results
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"대화 기록 조회 중 오류: {str(e)}")
            return []
    
    def get_user_session_count(self, user_id: int, chapter_number: int, section_number: int) -> int:
        """
        특정 사용자의 특정 챕터/섹션에서의 세션 횟수 조회
        
        Args:
            user_id: 사용자 ID
            chapter_number: 챕터 번호
            section_number: 섹션 번호
            
        Returns:
            해당 섹션에서의 세션 횟수
        """
        try:
            # v2.0: section_number 필드 추가로 섹션별 조회 가능
            where_clause = "user_id = %s AND chapter_number = %s AND section_number = %s"
            where_params = [user_id, chapter_number, section_number]
            
            count = count_records('learning_sessions', where_clause, where_params)
            
            self.logger.info(f"세션 횟수 조회: user_id={user_id}, chapter={chapter_number}, section={section_number}, count={count}")
            return count
            
        except Exception as e:
            self.logger.error(f"세션 횟수 조회 중 오류: {str(e)}")
            return 0
    
    def cleanup_old_sessions(self, days_to_keep: int = 90) -> bool:
        """
        오래된 세션 데이터 정리 (선택적 기능)
        
        Args:
            days_to_keep: 보관할 일 수
            
        Returns:
            정리 성공 여부
        """
        try:
            # 트랜잭션으로 순서대로 삭제
            operations = [
                {
                    'type': 'query',
                    'query': """
                    DELETE FROM session_conversations 
                    WHERE session_id IN (
                        SELECT session_id FROM learning_sessions 
                        WHERE session_start_time < DATE_SUB(NOW(), INTERVAL %s DAY)
                    )
                    """,
                    'params': [days_to_keep]
                },
                {
                    'type': 'query',
                    'query': """
                    DELETE FROM session_quizzes 
                    WHERE session_id IN (
                        SELECT session_id FROM learning_sessions 
                        WHERE session_start_time < DATE_SUB(NOW(), INTERVAL %s DAY)
                    )
                    """,
                    'params': [days_to_keep]
                },
                {
                    'type': 'query',
                    'query': """
                    DELETE FROM learning_sessions 
                    WHERE session_start_time < DATE_SUB(NOW(), INTERVAL %s DAY)
                    """,
                    'params': [days_to_keep]
                }
            ]
            
            result = execute_transaction(operations)
            
            if result:
                self.logger.info(f"오래된 세션 데이터 정리 완료: {days_to_keep}일 이전 데이터 삭제")
                return True
            else:
                self.logger.error("세션 데이터 정리 실패")
                return False
                
        except Exception as e:
            self.logger.error(f"세션 데이터 정리 중 오류: {str(e)}")
            return False