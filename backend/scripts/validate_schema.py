# backend/scripts/validate_schema.py
"""
데이터베이스 스키마 검증 스크립트
테이블 구조, 인덱스, 제약조건을 검증하고 보고서를 생성합니다.
"""

import sys
import os
import json
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from app.core.database.mysql_client import MySQLClient
from app.core.database.schema_validator import SchemaValidator, ValidationStatus


def main():
    """메인 함수"""
    # 명령행 인수 파싱
    parser = argparse.ArgumentParser(description='데이터베이스 스키마 검증 도구')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='출력 형식 (기본값: text)')
    parser.add_argument('--summary', action='store_true',
                       help='스키마 요약 정보만 출력')
    parser.add_argument('--health', action='store_true',
                       help='스키마 상태 확인만 수행')
    parser.add_argument('--output', type=str,
                       help='결과를 파일로 저장할 경로')
    parser.add_argument('--quiet', action='store_true',
                       help='최소한의 출력만 표시')
    
    args = parser.parse_args()
    
    # 환경변수 로드
    load_dotenv()
    
    if not args.quiet:
        print("데이터베이스 스키마 검증을 시작합니다...")
        print("=" * 60)
    
    try:
        # MySQL 클라이언트 초기화
        mysql_client = MySQLClient()
        
        # 스키마 검증기 초기화
        validator = SchemaValidator(mysql_client)
        
        # 요청된 작업 수행
        if args.summary:
            # 스키마 요약 정보
            if not args.quiet:
                print("스키마 요약 정보를 조회 중...")
            
            summary = validator.get_schema_summary()
            
            if args.format == 'json':
                output = json.dumps(summary, ensure_ascii=False, indent=2)
            else:
                output = format_summary_text(summary)
            
        elif args.health:
            # 스키마 상태 확인
            if not args.quiet:
                print("스키마 상태를 확인 중...")
            
            health = validator.check_schema_health()
            
            if args.format == 'json':
                output = json.dumps(health, ensure_ascii=False, indent=2)
            else:
                output = format_health_text(health)
        
        else:
            # 전체 검증 실행
            if not args.quiet:
                print("스키마 검증 중...")
            
            validation_results = validator.validate_all()
            
            if args.format == 'json':
                json_report = validator.generate_json_report(validation_results)
                output = json.dumps(json_report, ensure_ascii=False, indent=2)
            else:
                output = validator.generate_validation_report(validation_results)
        
        # 결과 출력
        print(output)
        
        # 파일로 저장
        if args.output:
            output_file = Path(args.output)
        else:
            # 기본 저장 경로
            logs_dir = project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            if args.summary:
                filename = "schema_summary"
            elif args.health:
                filename = "schema_health"
            else:
                filename = "schema_validation_report"
            
            extension = ".json" if args.format == 'json' else ".txt"
            output_file = logs_dir / f"{filename}{extension}"
        
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        if not args.quiet:
            print(f"\n결과가 저장되었습니다: {output_file}")
        
        # 전체 검증인 경우 실패 여부 확인
        if not args.summary and not args.health:
            if args.format == 'json':
                # JSON 형태에서 실패 확인
                json_data = json.loads(output)
                has_issues = json_data['summary']['total_fail'] > 0 or json_data['summary']['total_missing'] > 0
            else:
                # 텍스트 형태에서 실패 확인
                has_issues = False
                for category_results in validation_results.values():
                    for result in category_results:
                        if result.status in [ValidationStatus.FAIL, ValidationStatus.MISSING]:
                            has_issues = True
                            break
                    if has_issues:
                        break
            
            if has_issues:
                if not args.quiet:
                    print("\n⚠️ 스키마에 문제가 발견되었습니다.")
                sys.exit(1)
            else:
                if not args.quiet:
                    print("\n✅ 모든 스키마 검증이 통과되었습니다!")
                sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ 스키마 검증 중 오류가 발생했습니다: {str(e)}")
        sys.exit(1)
    
    finally:
        # 연결 정리
        try:
            mysql_client.disconnect()
        except:
            pass


def format_summary_text(summary: dict) -> str:
    """스키마 요약을 텍스트 형태로 포맷팅합니다."""
    if "error" in summary:
        return f"❌ {summary['error']}"
    
    lines = []
    lines.append("=" * 60)
    lines.append("데이터베이스 스키마 요약")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"데이터베이스: {summary['database_name']}")
    lines.append(f"테이블 수: {summary['total_tables']}")
    lines.append(f"뷰 수: {summary['total_views']}")
    lines.append(f"총 인덱스 수: {summary['total_indexes']}")
    lines.append(f"총 제약조건 수: {summary['total_constraints']}")
    lines.append("")
    
    if summary['tables']:
        lines.append("테이블 상세 정보:")
        lines.append("-" * 40)
        for table in summary['tables']:
            lines.append(f"📋 {table['name']}")
            lines.append(f"   엔진: {table['engine']}")
            lines.append(f"   문자셋: {table['charset']}")
            lines.append(f"   행 수: {table['row_count']:,}")
            lines.append(f"   컬럼 수: {table['column_count']}")
            lines.append(f"   인덱스 수: {table['index_count']}")
            lines.append(f"   제약조건 수: {table['constraint_count']}")
            lines.append(f"   데이터 크기: {table['data_size_mb']} MB")
            lines.append(f"   인덱스 크기: {table['index_size_mb']} MB")
            lines.append("")
    
    if summary['views']:
        lines.append("뷰 목록:")
        lines.append("-" * 40)
        for view in summary['views']:
            lines.append(f"👁️ {view['name']}")
        lines.append("")
    
    return "\n".join(lines)


def format_health_text(health: dict) -> str:
    """스키마 상태를 텍스트 형태로 포맷팅합니다."""
    lines = []
    lines.append("=" * 60)
    lines.append("데이터베이스 스키마 상태 확인")
    lines.append("=" * 60)
    lines.append("")
    
    # 상태 표시
    status_icons = {
        "healthy": "✅",
        "degraded": "⚠️",
        "unhealthy": "❌",
        "error": "💥"
    }
    
    status = health.get("status", "unknown")
    icon = status_icons.get(status, "❓")
    lines.append(f"전체 상태: {icon} {status.upper()}")
    lines.append("")
    
    # 문제점
    if health.get("issues"):
        lines.append("발견된 문제:")
        lines.append("-" * 40)
        for issue in health["issues"]:
            lines.append(f"❌ {issue}")
        lines.append("")
    
    # 권장사항
    if health.get("recommendations"):
        lines.append("권장사항:")
        lines.append("-" * 40)
        for recommendation in health["recommendations"]:
            lines.append(f"💡 {recommendation}")
        lines.append("")
    
    if not health.get("issues") and not health.get("recommendations"):
        lines.append("✅ 특별한 문제나 권장사항이 없습니다.")
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()