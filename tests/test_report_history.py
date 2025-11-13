"""
Report History 및 Report Saver 테스트

리포트 저장 및 히스토리 관리 기능을 테스트합니다.
"""

import pytest
import sys
from pathlib import Path
import tempfile
import shutil

# 프로젝트 루트를 PYTHONPATH에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.report_history import ReportHistoryDB, ReportRecord
from app.services.report_saver import ReportSaver


@pytest.fixture
def temp_dir(tmp_path):
    """임시 디렉토리"""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    return reports_dir


@pytest.fixture
def temp_db(temp_dir):
    """임시 DB"""
    db_path = temp_dir / "test_reports.db"
    db = ReportHistoryDB(str(db_path))
    return db


class TestReportHistoryDB:
    """ReportHistoryDB 테스트 클래스"""

    def test_db_initialization(self, temp_db):
        """DB 초기화 테스트"""
        assert temp_db is not None
        assert Path(temp_db.db_path).exists()

    def test_add_report(self, temp_db):
        """리포트 추가 테스트"""
        record = ReportRecord(
            filename="Test.cs",
            report_name="Test_review_20250118_120000",
            timestamp="2025-01-18T12:00:00",
            markdown_path="/path/to/Test_review_20250118_120000.md",
            html_path="/path/to/Test_review_20250118_120000.html",
            success=True,
            analysis_time=5.5
        )

        record_id = temp_db.add_report(record)

        assert record_id > 0

    def test_get_all_reports(self, temp_db):
        """전체 리포트 조회 테스트"""
        # 3개 리포트 추가
        for i in range(3):
            record = ReportRecord(
                filename=f"Test{i}.cs",
                report_name=f"Test{i}_review_20250118",
                timestamp=f"2025-01-18T12:00:{i:02d}",
                markdown_path=f"/path/Test{i}.md",
                html_path=f"/path/Test{i}.html",
                success=True,
                analysis_time=1.0 + i
            )
            temp_db.add_report(record)

        reports = temp_db.get_all_reports()

        assert len(reports) == 3
        # 최신순 정렬 확인
        assert reports[0].filename == "Test2.cs"
        assert reports[2].filename == "Test0.cs"

    def test_get_reports_by_filename(self, temp_db):
        """파일명으로 리포트 조회 테스트"""
        # 동일 파일의 여러 리포트 추가
        for i in range(2):
            record = ReportRecord(
                filename="UserService.cs",
                report_name=f"UserService_review_{i}",
                timestamp=f"2025-01-18T12:00:{i:02d}",
                markdown_path=f"/path/UserService_{i}.md",
                html_path=f"/path/UserService_{i}.html",
                success=True,
                analysis_time=1.0
            )
            temp_db.add_report(record)

        # 다른 파일 추가
        record = ReportRecord(
            filename="FileReader.cs",
            report_name="FileReader_review_0",
            timestamp="2025-01-18T12:00:03",
            markdown_path="/path/FileReader.md",
            html_path="/path/FileReader.html",
            success=True,
            analysis_time=1.0
        )
        temp_db.add_report(record)

        # UserService.cs 리포트만 조회
        reports = temp_db.get_reports_by_filename("UserService.cs")

        assert len(reports) == 2
        assert all(r.filename == "UserService.cs" for r in reports)

    def test_delete_report(self, temp_db):
        """리포트 삭제 테스트"""
        record = ReportRecord(
            filename="Test.cs",
            report_name="Test_review",
            timestamp="2025-01-18T12:00:00",
            markdown_path="/path/Test.md",
            html_path="/path/Test.html",
            success=True,
            analysis_time=1.0
        )

        record_id = temp_db.add_report(record)

        # 삭제
        success = temp_db.delete_report(record_id)

        assert success is True

        # 조회 확인
        deleted_record = temp_db.get_report_by_id(record_id)
        assert deleted_record is None

    def test_get_statistics(self, temp_db):
        """통계 조회 테스트"""
        # 성공 2개, 실패 1개 추가
        for i, success in enumerate([True, True, False]):
            record = ReportRecord(
                filename=f"Test{i}.cs",
                report_name=f"Test{i}_review",
                timestamp=f"2025-01-18T12:00:{i:02d}",
                markdown_path=f"/path/Test{i}.md",
                html_path=f"/path/Test{i}.html",
                success=success,
                analysis_time=1.0 + i
            )
            temp_db.add_report(record)

        stats = temp_db.get_statistics()

        assert stats['total'] == 3
        assert stats['success'] == 2
        assert stats['failed'] == 1
        assert stats['total_analysis_time'] == 6.0  # 1.0 + 2.0 + 3.0
        assert stats['avg_analysis_time'] == 2.0


class TestReportSaver:
    """ReportSaver 테스트 클래스"""

    def test_saver_initialization(self, temp_dir):
        """ReportSaver 초기화 테스트"""
        saver = ReportSaver(
            reports_dir=str(temp_dir),
            db_path=str(temp_dir / "reports.db")
        )

        assert saver is not None
        assert (temp_dir / "markdown").exists()
        assert (temp_dir / "html").exists()

    def test_save_report(self, temp_dir):
        """리포트 저장 테스트"""
        saver = ReportSaver(
            reports_dir=str(temp_dir),
            db_path=str(temp_dir / "reports.db")
        )

        md_path, html_path, record_id = saver.save_report(
            filename="UserService.cs",
            original_code="public class UserService { }",
            improved_code="public class UserService\n{\n    // Improved\n}",
            report_markdown="# Code Review\n\nThis is a test report.",
            analysis_time=2.5,
            success=True
        )

        # 파일 생성 확인
        assert Path(md_path).exists()
        assert Path(html_path).exists()

        # DB 레코드 확인
        record = saver.db.get_report_by_id(record_id)
        assert record is not None
        assert record.filename == "UserService.cs"
        assert record.success is True
        assert record.analysis_time == 2.5

        # Markdown 파일 내용 확인
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Code Review" in content
            assert "test report" in content

        # HTML 파일 내용 확인
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "<html" in content
            assert "Code Review" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
