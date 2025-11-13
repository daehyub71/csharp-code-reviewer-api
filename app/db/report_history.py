"""
리포트 히스토리 관리 데이터베이스

SQLite를 사용하여 분석 리포트 히스토리를 관리합니다.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ReportRecord:
    """리포트 레코드 데이터클래스"""
    id: Optional[int] = None
    filename: str = ""
    report_name: str = ""
    timestamp: str = ""
    markdown_path: str = ""
    html_path: str = ""
    success: bool = True
    error_message: str = ""
    analysis_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'filename': self.filename,
            'report_name': self.report_name,
            'timestamp': self.timestamp,
            'markdown_path': self.markdown_path,
            'html_path': self.html_path,
            'success': self.success,
            'error_message': self.error_message,
            'analysis_time': self.analysis_time
        }


class ReportHistoryDB:
    """
    리포트 히스토리 데이터베이스 관리 클래스

    SQLite를 사용하여 분석 리포트의 메타데이터를 저장하고 조회합니다.
    """

    def __init__(self, db_path: str = "reports/reports.db"):
        """
        데이터베이스 초기화

        Args:
            db_path: 데이터베이스 파일 경로 (기본: reports/reports.db)
        """
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """데이터베이스 파일 및 테이블 생성"""
        # 데이터베이스 디렉토리 생성
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # 테이블 생성
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS report_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    report_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    markdown_path TEXT NOT NULL,
                    html_path TEXT NOT NULL,
                    success INTEGER NOT NULL DEFAULT 1,
                    error_message TEXT DEFAULT '',
                    analysis_time REAL DEFAULT 0.0
                )
            ''')

            # 인덱스 생성 (빠른 조회를 위해)
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_filename
                ON report_history(filename)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON report_history(timestamp DESC)
            ''')

            conn.commit()
        finally:
            conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """SQLite 연결 반환"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Row 객체로 반환
        return conn

    def add_report(self, record: ReportRecord) -> int:
        """
        리포트 레코드 추가

        Args:
            record: 추가할 리포트 레코드

        Returns:
            int: 생성된 레코드의 ID
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO report_history
                (filename, report_name, timestamp, markdown_path, html_path,
                 success, error_message, analysis_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.filename,
                record.report_name,
                record.timestamp,
                record.markdown_path,
                record.html_path,
                1 if record.success else 0,
                record.error_message,
                record.analysis_time
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_all_reports(self, limit: Optional[int] = None) -> List[ReportRecord]:
        """
        모든 리포트 조회 (최신순)

        Args:
            limit: 조회할 최대 개수 (None이면 전체)

        Returns:
            List[ReportRecord]: 리포트 레코드 목록
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            if limit:
                cursor.execute('''
                    SELECT * FROM report_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            else:
                cursor.execute('''
                    SELECT * FROM report_history
                    ORDER BY timestamp DESC
                ''')

            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]
        finally:
            conn.close()

    def get_reports_by_filename(self, filename: str) -> List[ReportRecord]:
        """
        특정 파일의 리포트 조회

        Args:
            filename: 파일명 (예: UserService.cs)

        Returns:
            List[ReportRecord]: 해당 파일의 리포트 레코드 목록
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM report_history
                WHERE filename = ?
                ORDER BY timestamp DESC
            ''', (filename,))

            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]
        finally:
            conn.close()

    def get_report_by_id(self, report_id: int) -> Optional[ReportRecord]:
        """
        ID로 리포트 조회

        Args:
            report_id: 리포트 ID

        Returns:
            Optional[ReportRecord]: 리포트 레코드 (없으면 None)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM report_history
                WHERE id = ?
            ''', (report_id,))

            row = cursor.fetchone()
            return self._row_to_record(row) if row else None
        finally:
            conn.close()

    def delete_report(self, report_id: int) -> bool:
        """
        리포트 삭제 (DB 레코드만 삭제, 파일은 유지)

        Args:
            report_id: 삭제할 리포트 ID

        Returns:
            bool: 삭제 성공 여부
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM report_history
                WHERE id = ?
            ''', (report_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_report_with_files(self, report_id: int) -> bool:
        """
        리포트 삭제 (DB 레코드 + 파일)

        Args:
            report_id: 삭제할 리포트 ID

        Returns:
            bool: 삭제 성공 여부
        """
        # 먼저 레코드 조회
        record = self.get_report_by_id(report_id)
        if not record:
            return False

        # 파일 삭제
        try:
            if record.markdown_path and Path(record.markdown_path).exists():
                Path(record.markdown_path).unlink()

            if record.html_path and Path(record.html_path).exists():
                Path(record.html_path).unlink()
        except Exception as e:
            print(f"파일 삭제 중 오류: {e}")
            # 파일 삭제 실패해도 DB 레코드는 삭제

        # DB 레코드 삭제
        return self.delete_report(report_id)

    def get_statistics(self) -> Dict[str, Any]:
        """
        리포트 통계 조회

        Returns:
            Dict[str, Any]: 통계 정보
                - total: 전체 리포트 개수
                - success: 성공한 리포트 개수
                - failed: 실패한 리포트 개수
                - total_analysis_time: 총 분석 시간
                - avg_analysis_time: 평균 분석 시간
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed,
                    SUM(analysis_time) as total_time,
                    AVG(analysis_time) as avg_time
                FROM report_history
            ''')

            row = cursor.fetchone()

            return {
                'total': row['total'] or 0,
                'success': row['success'] or 0,
                'failed': row['failed'] or 0,
                'total_analysis_time': row['total_time'] or 0.0,
                'avg_analysis_time': row['avg_time'] or 0.0
            }
        finally:
            conn.close()

    def _row_to_record(self, row: sqlite3.Row) -> ReportRecord:
        """SQLite Row를 ReportRecord로 변환"""
        return ReportRecord(
            id=row['id'],
            filename=row['filename'],
            report_name=row['report_name'],
            timestamp=row['timestamp'],
            markdown_path=row['markdown_path'],
            html_path=row['html_path'],
            success=bool(row['success']),
            error_message=row['error_message'],
            analysis_time=row['analysis_time']
        )


# 편의 함수
def get_db() -> ReportHistoryDB:
    """전역 DB 인스턴스 반환"""
    return ReportHistoryDB()
