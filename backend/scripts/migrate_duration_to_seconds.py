# backend/scripts/migrate_duration_to_seconds.py
# 시간 관련 컬럼을 분(minutes)에서 초(seconds)로 변경하는 마이그레이션 스크립트

import os
import sys
import logging
from typing import Dict, Any, List

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
        logging.FileHandler(os.path.join(project_root, 'logs', 'migration.log'))
    ]
)
logger = logging.getLogger(__name__)

class DurationMigrator:
    """시간 단위 마이그레이션 클래스"""
    
    def __init__(self):
        """초기화"""
        self.migrations = [
            {
                'table': 'learning_sessions',
                'old_column': 'study_duration_minutes',
                'new_column': 'study_duration_seconds',
                'comment': '해당 세션 학습 소요 시간 (초)',
                'conversion_factor': 60  # 분을 초로 변환 (1분 = 60초)
            },
            {
                'table': 'user_statistics',
                'old_column': 'total_study_time_minutes',
                'new_column': 'total_study_time_seconds',
                'comment': '총 학습 시간 (초)',
                'conversion_factor': 60  # 분을 초로 변환 (1분 = 60초)
            }
        ]
    
    def check_table_exists(self, table_name: str) -> bool:
        """테이블 존재 여부 확인"""
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) as count 
                        FROM information_schema.tables 
                        WHERE table_schema = DATABASE() 
                        AND table_name = %s
                    """, (table_name,))
                    result = cursor.fetchone()
                    return result['count'] > 0
        except Exception as e:
            logger.error(f"테이블 존재 확인 실패 ({table_name}): {e}")
            return False
    
    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """컬럼 존재 여부 확인"""
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) as count 
                        FROM information_schema.columns 
                        WHERE table_schema = DATABASE() 
                        AND table_name = %s 
                        AND column_name = %s
                    """, (table_name, column_name))
                    result = cursor.fetchone()
                    return result['count'] > 0
        except Exception as e:
            logger.error(f"컬럼 존재 확인 실패 ({table_name}.{column_name}): {e}")
            return False
    
    def get_column_data_count(self, table_name: str, column_name: str) -> int:
        """컬럼에 NULL이 아닌 데이터 개수 확인"""
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT COUNT(*) as count 
                        FROM `{table_name}` 
                        WHERE `{column_name}` IS NOT NULL
                    """)
                    result = cursor.fetchone()
                    return result['count']
        except Exception as e:
            logger.warning(f"데이터 개수 확인 실패 ({table_name}.{column_name}): {e}")
            return 0
    
    def migrate_column(self, migration: Dict[str, Any]) -> bool:
        """단일 컬럼 마이그레이션 실행"""
        table_name = migration['table']
        old_column = migration['old_column']
        new_column = migration['new_column']
        comment = migration['comment']
        conversion_factor = migration['conversion_factor']
        
        logger.info(f"=== {table_name}.{old_column} → {new_column} 마이그레이션 시작 ===")
        
        try:
            # 1. 테이블 존재 확인
            if not self.check_table_exists(table_name):
                logger.warning(f"테이블 '{table_name}'이 존재하지 않습니다. 건너뜁니다.")
                return True
            
            # 2. 기존 컬럼 존재 확인
            if not self.check_column_exists(table_name, old_column):
                logger.warning(f"기존 컬럼 '{table_name}.{old_column}'이 존재하지 않습니다. 건너뜁니다.")
                return True
            
            # 3. 새 컬럼이 이미 존재하는지 확인
            if self.check_column_exists(table_name, new_column):
                logger.warning(f"새 컬럼 '{table_name}.{new_column}'이 이미 존재합니다. 건너뜁니다.")
                return True
            
            # 4. 기존 데이터 개수 확인
            data_count = self.get_column_data_count(table_name, old_column)
            logger.info(f"변환할 데이터 개수: {data_count}개")
            
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    # 5. 새 컬럼 추가
                    logger.info(f"새 컬럼 '{new_column}' 추가 중...")
                    cursor.execute(f"""
                        ALTER TABLE `{table_name}` 
                        ADD COLUMN `{new_column}` INT COMMENT '{comment}'
                    """)
                    
                    # 6. 데이터 변환 및 복사 (분 → 초)
                    if data_count > 0:
                        logger.info(f"데이터 변환 중... (x{conversion_factor})")
                        cursor.execute(f"""
                            UPDATE `{table_name}` 
                            SET `{new_column}` = CASE 
                                WHEN `{old_column}` IS NOT NULL 
                                THEN `{old_column}` * {conversion_factor}
                                ELSE NULL 
                            END
                        """)
                        
                        # 변환 결과 확인
                        cursor.execute(f"""
                            SELECT COUNT(*) as converted_count 
                            FROM `{table_name}` 
                            WHERE `{new_column}` IS NOT NULL
                        """)
                        converted_count = cursor.fetchone()['converted_count']
                        logger.info(f"변환 완료: {converted_count}개 데이터")
                    
                    # 7. 기존 컬럼 삭제
                    logger.info(f"기존 컬럼 '{old_column}' 삭제 중...")
                    cursor.execute(f"""
                        ALTER TABLE `{table_name}` 
                        DROP COLUMN `{old_column}`
                    """)
                    
                    logger.info(f"✅ {table_name}.{old_column} → {new_column} 마이그레이션 완료")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ {table_name}.{old_column} 마이그레이션 실패: {e}")
            return False
    
    def run_migration(self, confirm: bool = False) -> Dict[str, Any]:
        """전체 마이그레이션 실행"""
        if not confirm:
            logger.error("확인 플래그가 설정되지 않았습니다. confirm=True로 설정해주세요.")
            return {
                'success': False,
                'message': '확인 플래그가 필요합니다.',
                'completed_migrations': [],
                'failed_migrations': []
            }
        
        logger.info("=== 시간 단위 마이그레이션 시작 ===")
        
        completed_migrations = []
        failed_migrations = []
        
        for migration in self.migrations:
            table_name = migration['table']
            old_column = migration['old_column']
            new_column = migration['new_column']
            
            if self.migrate_column(migration):
                completed_migrations.append(f"{table_name}.{old_column} → {new_column}")
            else:
                failed_migrations.append(f"{table_name}.{old_column} → {new_column}")
        
        # 결과 요약
        success = len(failed_migrations) == 0
        
        result = {
            'success': success,
            'message': f"성공: {len(completed_migrations)}개, 실패: {len(failed_migrations)}개",
            'completed_migrations': completed_migrations,
            'failed_migrations': failed_migrations
        }
        
        if success:
            logger.info("=== 모든 마이그레이션 완료 ===")
        else:
            logger.error(f"=== 마이그레이션 중 오류 발생: {failed_migrations} ===")
        
        return result
    
    def check_migration_status(self) -> Dict[str, Any]:
        """마이그레이션 상태 확인"""
        logger.info("=== 마이그레이션 상태 확인 ===")
        
        status = {}
        
        for migration in self.migrations:
            table_name = migration['table']
            old_column = migration['old_column']
            new_column = migration['new_column']
            
            table_exists = self.check_table_exists(table_name)
            old_column_exists = self.check_column_exists(table_name, old_column) if table_exists else False
            new_column_exists = self.check_column_exists(table_name, new_column) if table_exists else False
            
            if not table_exists:
                migration_status = "테이블 없음"
            elif old_column_exists and not new_column_exists:
                migration_status = "마이그레이션 필요"
            elif not old_column_exists and new_column_exists:
                migration_status = "마이그레이션 완료"
            elif old_column_exists and new_column_exists:
                migration_status = "중간 상태 (수동 확인 필요)"
            else:
                migration_status = "알 수 없음"
            
            status[f"{table_name}.{old_column}→{new_column}"] = migration_status
            logger.info(f"{table_name}.{old_column} → {new_column}: {migration_status}")
        
        return status

def main():
    """메인 실행 함수"""
    try:
        # 로그 디렉토리 생성
        log_dir = os.path.join(project_root, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logger.info("시간 단위 마이그레이션 스크립트 시작")
        
        # DurationMigrator 인스턴스 생성
        migrator = DurationMigrator()
        
        # 현재 마이그레이션 상태 확인
        logger.info("현재 마이그레이션 상태:")
        migration_status = migrator.check_migration_status()
        
        # 마이그레이션이 필요한지 확인
        needs_migration = any("마이그레이션 필요" in status for status in migration_status.values())
        
        if not needs_migration:
            logger.info("마이그레이션이 필요하지 않습니다.")
            return
        
        # 사용자 확인 (대화형 모드)
        if len(sys.argv) > 1 and sys.argv[1] == '--force':
            # --force 옵션이 있으면 확인 없이 실행
            confirm = True
            logger.info("--force 옵션으로 확인 없이 실행합니다.")
        else:
            # 사용자 확인 요청
            print("\n⚠️  경고: 데이터베이스 구조가 변경됩니다!")
            print("이 작업은 되돌릴 수 없습니다.")
            print("변경 내용:")
            print("- learning_sessions.study_duration_minutes → study_duration_seconds (데이터 x60)")
            print("- user_statistics.total_study_time_minutes → total_study_time_seconds (데이터 x60)")
            
            user_input = input("\n계속하시겠습니까? (yes/no): ").strip().lower()
            confirm = user_input in ['yes', 'y']
            
            if not confirm:
                logger.info("사용자가 마이그레이션을 취소했습니다.")
                return
        
        # 마이그레이션 실행
        result = migrator.run_migration(confirm=confirm)
        
        # 결과 출력
        print(f"\n=== 마이그레이션 결과 ===")
        print(f"성공 여부: {result['success']}")
        print(f"메시지: {result['message']}")
        print(f"완료된 마이그레이션: {result['completed_migrations']}")
        print(f"실패한 마이그레이션: {result['failed_migrations']}")
        
        # 마이그레이션 후 상태 확인
        logger.info("\n마이그레이션 후 상태:")
        migrator.check_migration_status()
        
        logger.info("시간 단위 마이그레이션 스크립트 완료")
        
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