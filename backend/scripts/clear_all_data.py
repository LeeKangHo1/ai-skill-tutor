# backend/scripts/clear_all_data.py
# 데이터베이스의 모든 테이블 데이터를 안전하게 삭제하는 스크립트

import sys
import os
import logging
from typing import List, Dict

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from app.config.db_config import get_db_connection, init_db_config

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseCleaner:
    """
    데이터베이스 모든 테이블의 데이터를 안전하게 삭제하는 클래스
    """
    
    def __init__(self):
        """초기화"""
        # 테이블 삭제 순서 (외래키 제약조건 고려)
        self.table_order = [
            'session_conversations',  # learning_sessions 참조
            'session_quizzes',       # learning_sessions 참조
            'learning_sessions',     # users 참조
            'user_auth_tokens',      # users 참조
            'user_statistics',       # users 참조
            'user_progress',         # users 참조
            'users',                 # 기본 테이블
            'chapters'               # 독립 테이블
        ]
    
    def connect_database(self) -> bool:
        """데이터베이스 연결"""
        try:
            # 데이터베이스 설정 초기화
            init_db_config()
            
            # 연결 테스트
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 as test")
                    result = cursor.fetchone()
                    
                    if result and result.get('test') == 1:
                        logger.info("✅ 데이터베이스 연결 성공")
                        return True
                    else:
                        logger.error("❌ 데이터베이스 연결 실패")
                        return False
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 오류: {e}")
            return False
    
    def get_existing_tables(self) -> List[str]:
        """현재 존재하는 테이블 목록 조회"""
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    results = cursor.fetchall()
                    
                    if results:
                        # MySQL의 SHOW TABLES 결과는 딕셔너리 형태
                        table_names = [list(row.values())[0] for row in results]
                        logger.info(f"📋 현재 존재하는 테이블: {table_names}")
                        return table_names
                    else:
                        logger.info("📋 존재하는 테이블이 없습니다")
                        return []
                
        except Exception as e:
            logger.error(f"❌ 테이블 목록 조회 오류: {e}")
            return []    

    def get_table_row_count(self, table_name: str) -> int:
        """특정 테이블의 행 수 조회"""
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                    result = cursor.fetchone()
                    
                    if result:
                        return result['count']
                    else:
                        return 0
                
        except Exception as e:
            logger.warning(f"⚠️ 테이블 {table_name} 행 수 조회 오류: {e}")
            return 0
    
    def show_current_data_status(self) -> Dict[str, int]:
        """현재 데이터 상태 표시"""
        logger.info("\n=== 현재 데이터베이스 상태 ===")
        
        existing_tables = self.get_existing_tables()
        table_counts = {}
        
        for table in self.table_order:
            if table in existing_tables:
                count = self.get_table_row_count(table)
                table_counts[table] = count
                logger.info(f"📊 {table}: {count}개 행")
            else:
                logger.info(f"📊 {table}: 테이블 없음")
                table_counts[table] = 0
        
        total_rows = sum(table_counts.values())
        logger.info(f"\n📈 전체 데이터 행 수: {total_rows}개")
        
        return table_counts
    
    def clear_table_data(self, table_name: str) -> bool:
        """특정 테이블의 모든 데이터 삭제"""
        try:
            # 먼저 테이블이 존재하는지 확인
            existing_tables = self.get_existing_tables()
            if table_name not in existing_tables:
                logger.info(f"⏭️ 테이블 {table_name}이 존재하지 않아 건너뜁니다")
                return True
            
            # 현재 행 수 확인
            current_count = self.get_table_row_count(table_name)
            if current_count == 0:
                logger.info(f"⏭️ 테이블 {table_name}에 데이터가 없어 건너뜁니다")
                return True
            
            # 데이터 삭제 실행
            logger.info(f"🗑️ 테이블 {table_name}의 {current_count}개 행 삭제 중...")
            
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    # TRUNCATE 대신 DELETE 사용 (외래키 제약조건 고려)
                    cursor.execute(f"DELETE FROM {table_name}")
            
            # 삭제 후 확인
            after_count = self.get_table_row_count(table_name)
            if after_count == 0:
                logger.info(f"✅ 테이블 {table_name} 데이터 삭제 완료")
                return True
            else:
                logger.error(f"❌ 테이블 {table_name} 데이터 삭제 실패 (남은 행: {after_count}개)")
                return False
                
        except Exception as e:
            logger.error(f"❌ 테이블 {table_name} 데이터 삭제 오류: {e}")
            return False
    
    def clear_all_data(self) -> bool:
        """모든 테이블의 데이터 삭제"""
        logger.info("\n🚀 모든 테이블 데이터 삭제 시작...")
        
        # 현재 상태 표시
        initial_counts = self.show_current_data_status()
        total_initial_rows = sum(initial_counts.values())
        
        if total_initial_rows == 0:
            logger.info("✅ 삭제할 데이터가 없습니다")
            return True
        
        # 외래키 제약조건 임시 비활성화
        logger.info("\n🔧 외래키 제약조건 임시 비활성화...")
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            logger.info("✅ 외래키 제약조건 비활성화 완료")
        except Exception as e:
            logger.warning(f"⚠️ 외래키 제약조건 비활성화 실패: {e}")
        
        # 테이블별 데이터 삭제
        success_count = 0
        failed_tables = []
        
        for table in self.table_order:
            if self.clear_table_data(table):
                success_count += 1
            else:
                failed_tables.append(table)
        
        # 외래키 제약조건 재활성화
        logger.info("\n🔧 외래키 제약조건 재활성화...")
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            logger.info("✅ 외래키 제약조건 재활성화 완료")
        except Exception as e:
            logger.warning(f"⚠️ 외래키 제약조건 재활성화 실패: {e}")
        
        # 결과 확인
        logger.info("\n=== 데이터 삭제 후 상태 ===")
        final_counts = self.show_current_data_status()
        total_final_rows = sum(final_counts.values())
        
        # 결과 요약
        logger.info(f"\n📊 삭제 결과 요약:")
        logger.info(f"   - 삭제 전 총 행 수: {total_initial_rows}개")
        logger.info(f"   - 삭제 후 총 행 수: {total_final_rows}개")
        logger.info(f"   - 성공한 테이블: {success_count}개")
        
        if failed_tables:
            logger.error(f"   - 실패한 테이블: {failed_tables}")
            return False
        else:
            logger.info("✅ 모든 테이블 데이터 삭제 완료!")
            return True
    
    def disconnect_database(self):
        """데이터베이스 연결 해제"""
        # get_db_connection 컨텍스트 매니저를 사용하므로 별도 해제 불필요
        logger.info("✅ 데이터베이스 연결 해제 완료")

def main():
    """메인 실행 함수"""
    logger.info("=== 데이터베이스 전체 데이터 삭제 스크립트 ===")
    
    # 사용자 확인
    print("\n⚠️  경고: 이 스크립트는 데이터베이스의 모든 테이블 데이터를 삭제합니다!")
    print("   - users (사용자 정보)")
    print("   - user_progress (학습 진행 상태)")
    print("   - user_statistics (학습 통계)")
    print("   - learning_sessions (학습 세션)")
    print("   - session_conversations (세션 대화)")
    print("   - session_quizzes (세션 퀴즈)")
    print("   - user_auth_tokens (인증 토큰)")
    print("   - chapters (챕터 정보)")
    
    confirm = input("\n정말로 모든 데이터를 삭제하시겠습니까? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        logger.info("❌ 사용자가 취소했습니다")
        return False
    
    # 데이터베이스 클리너 실행
    cleaner = DatabaseCleaner()
    
    try:
        # 데이터베이스 연결
        if not cleaner.connect_database():
            return False
        
        # 모든 데이터 삭제
        success = cleaner.clear_all_data()
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 스크립트 실행 중 오류: {e}")
        return False
        
    finally:
        # 연결 해제
        cleaner.disconnect_database()

if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            logger.info("\n🎉 데이터베이스 전체 데이터 삭제 완료!")
            sys.exit(0)
        else:
            logger.error("\n💥 데이터베이스 전체 데이터 삭제 실패!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ 사용자가 중단했습니다")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)