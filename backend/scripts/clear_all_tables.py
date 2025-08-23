# backend/scripts/clear_all_tables.py
# 모든 테이블의 데이터를 삭제하는 스크립트

import os
import sys
import logging
from typing import List, Dict, Any

# 프로젝트 루트 경로를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

from app.config.db_config import get_db_connection, DatabaseConnectionError

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', 'clear_tables.log'))
    ]
)
logger = logging.getLogger(__name__)

class TableCleaner:
    """테이블 데이터 삭제 클래스"""
    
    def __init__(self):
        """초기화"""
        # DB 설계 문서에 따른 테이블 목록 (의존성 순서 고려)
        self.tables_to_clear = [
            # 1. 종속 테이블들 먼저 삭제 (외래키 제약조건 고려)
            'session_conversations',  # learning_sessions 참조
            'session_quizzes',        # learning_sessions 참조
            'learning_sessions',      # users 참조
            'user_auth_tokens',       # users 참조
            'user_statistics',        # users 참조
            'user_progress',          # users 참조
            
            # 2. 기본 테이블들
            'users',                  # 기본 사용자 테이블
            'chapters'                # 독립적 테이블 (추후 구현)
        ]
    
    def get_existing_tables(self) -> List[str]:
        """현재 데이터베이스에 존재하는 테이블 목록 조회"""
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    results = cursor.fetchall()
                    
                    # 결과에서 테이블 이름 추출
                    existing_tables = []
                    for row in results:
                        # SHOW TABLES 결과는 딕셔너리 형태로 반환됨
                        table_name = list(row.values())[0]
                        existing_tables.append(table_name)
                    
                    logger.info(f"데이터베이스에서 발견된 테이블: {existing_tables}")
                    return existing_tables
                    
        except Exception as e:
            logger.error(f"테이블 목록 조회 실패: {e}")
            raise
    
    def get_table_row_count(self, table_name: str) -> int:
        """특정 테이블의 행 수 조회"""
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
                    result = cursor.fetchone()
                    return result['count'] if result else 0
                    
        except Exception as e:
            logger.warning(f"테이블 {table_name}의 행 수 조회 실패: {e}")
            return 0
    
    def clear_table(self, table_name: str) -> bool:
        """특정 테이블의 모든 데이터 삭제"""
        try:
            # 삭제 전 행 수 확인
            row_count_before = self.get_table_row_count(table_name)
            
            if row_count_before == 0:
                logger.info(f"테이블 '{table_name}'은 이미 비어있습니다.")
                return True
            
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    # 외래키 제약조건 임시 비활성화
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                    
                    # 테이블 데이터 삭제 (TRUNCATE 사용 - 빠르고 AUTO_INCREMENT 리셋)
                    cursor.execute(f"TRUNCATE TABLE `{table_name}`")
                    
                    # 외래키 제약조건 다시 활성화
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                    
                    logger.info(f"테이블 '{table_name}' 삭제 완료 (삭제된 행 수: {row_count_before})")
                    return True
                    
        except Exception as e:
            logger.error(f"테이블 '{table_name}' 삭제 실패: {e}")
            return False
    
    def clear_all_tables(self, confirm: bool = False) -> Dict[str, Any]:
        """모든 테이블의 데이터 삭제"""
        if not confirm:
            logger.error("확인 플래그가 설정되지 않았습니다. confirm=True로 설정해주세요.")
            return {
                'success': False,
                'message': '확인 플래그가 필요합니다.',
                'cleared_tables': [],
                'failed_tables': [],
                'total_rows_deleted': 0
            }
        
        logger.info("=== 모든 테이블 데이터 삭제 시작 ===")
        
        # 현재 존재하는 테이블 확인
        existing_tables = self.get_existing_tables()
        
        # 삭제할 테이블 목록 (존재하는 테이블만)
        tables_to_process = [table for table in self.tables_to_clear if table in existing_tables]
        
        if not tables_to_process:
            logger.info("삭제할 테이블이 없습니다.")
            return {
                'success': True,
                'message': '삭제할 테이블이 없습니다.',
                'cleared_tables': [],
                'failed_tables': [],
                'total_rows_deleted': 0
            }
        
        logger.info(f"삭제 대상 테이블: {tables_to_process}")
        
        # 삭제 전 전체 행 수 계산
        total_rows_before = 0
        for table in tables_to_process:
            total_rows_before += self.get_table_row_count(table)
        
        logger.info(f"삭제 예정 총 행 수: {total_rows_before}")
        
        # 테이블별 삭제 실행
        cleared_tables = []
        failed_tables = []
        
        for table_name in tables_to_process:
            logger.info(f"테이블 '{table_name}' 삭제 중...")
            
            if self.clear_table(table_name):
                cleared_tables.append(table_name)
            else:
                failed_tables.append(table_name)
        
        # 결과 요약
        success = len(failed_tables) == 0
        
        result = {
            'success': success,
            'message': f"성공: {len(cleared_tables)}개, 실패: {len(failed_tables)}개",
            'cleared_tables': cleared_tables,
            'failed_tables': failed_tables,
            'total_rows_deleted': total_rows_before
        }
        
        if success:
            logger.info("=== 모든 테이블 데이터 삭제 완료 ===")
        else:
            logger.error(f"=== 테이블 삭제 중 오류 발생: {failed_tables} ===")
        
        return result
    
    def show_table_status(self) -> Dict[str, int]:
        """모든 테이블의 현재 상태 조회"""
        logger.info("=== 테이블 상태 조회 ===")
        
        existing_tables = self.get_existing_tables()
        table_status = {}
        
        for table_name in self.tables_to_clear:
            if table_name in existing_tables:
                row_count = self.get_table_row_count(table_name)
                table_status[table_name] = row_count
                logger.info(f"테이블 '{table_name}': {row_count}행")
            else:
                table_status[table_name] = -1  # 테이블이 존재하지 않음
                logger.info(f"테이블 '{table_name}': 존재하지 않음")
        
        total_rows = sum(count for count in table_status.values() if count > 0)
        logger.info(f"총 데이터 행 수: {total_rows}")
        
        return table_status

def main():
    """메인 실행 함수"""
    try:
        # 로그 디렉토리 생성
        log_dir = os.path.join(project_root, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logger.info("테이블 삭제 스크립트 시작")
        
        # TableCleaner 인스턴스 생성
        cleaner = TableCleaner()
        
        # 현재 테이블 상태 확인
        logger.info("현재 테이블 상태:")
        table_status = cleaner.show_table_status()
        
        # 데이터가 있는 테이블이 있는지 확인
        has_data = any(count > 0 for count in table_status.values())
        
        if not has_data:
            logger.info("모든 테이블이 이미 비어있습니다.")
            return
        
        # 사용자 확인 (대화형 모드)
        if len(sys.argv) > 1 and sys.argv[1] == '--force':
            # --force 옵션이 있으면 확인 없이 실행
            confirm = True
            logger.info("--force 옵션으로 확인 없이 실행합니다.")
        else:
            # 사용자 확인 요청
            print("\n⚠️  경고: 모든 테이블의 데이터가 삭제됩니다!")
            print("이 작업은 되돌릴 수 없습니다.")
            print(f"삭제될 총 행 수: {sum(count for count in table_status.values() if count > 0)}")
            
            user_input = input("\n계속하시겠습니까? (yes/no): ").strip().lower()
            confirm = user_input in ['yes', 'y']
            
            if not confirm:
                logger.info("사용자가 작업을 취소했습니다.")
                return
        
        # 테이블 삭제 실행
        result = cleaner.clear_all_tables(confirm=confirm)
        
        # 결과 출력
        print(f"\n=== 삭제 결과 ===")
        print(f"성공 여부: {result['success']}")
        print(f"메시지: {result['message']}")
        print(f"삭제된 테이블: {result['cleared_tables']}")
        print(f"실패한 테이블: {result['failed_tables']}")
        print(f"삭제된 총 행 수: {result['total_rows_deleted']}")
        
        # 삭제 후 상태 확인
        logger.info("\n삭제 후 테이블 상태:")
        cleaner.show_table_status()
        
        logger.info("테이블 삭제 스크립트 완료")
        
    except DatabaseConnectionError as e:
        logger.error(f"데이터베이스 연결 오류: {e}")
        print(f"❌ 데이터베이스 연결 실패: {e}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()