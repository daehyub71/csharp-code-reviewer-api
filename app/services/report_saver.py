"""
리포트 저장 서비스

분석 리포트를 Markdown 및 HTML 형식으로 저장하고 DB에 기록합니다.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Tuple
import markdown

from app.db.report_history import ReportHistoryDB, ReportRecord


class ReportSaver:
    """
    리포트 저장 서비스

    분석 결과를 파일로 저장하고 DB에 메타데이터를 기록합니다.
    """

    def __init__(
        self,
        reports_dir: str = "reports",
        db_path: str = "reports/reports.db"
    ):
        """
        ReportSaver 초기화

        Args:
            reports_dir: 리포트 저장 디렉토리 (기본: reports)
            db_path: DB 파일 경로 (기본: reports/reports.db)
        """
        self.reports_dir = Path(reports_dir)
        self.markdown_dir = self.reports_dir / "markdown"
        self.html_dir = self.reports_dir / "html"

        # 디렉토리 생성
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        self.html_dir.mkdir(parents=True, exist_ok=True)

        # DB 초기화
        self.db = ReportHistoryDB(db_path)

    def save_report(
        self,
        filename: str,
        original_code: str,
        improved_code: str,
        report_markdown: str,
        analysis_time: float = 0.0,
        success: bool = True,
        error_message: str = ""
    ) -> Tuple[str, str, int]:
        """
        리포트 저장 (Markdown + HTML)

        Args:
            filename: 원본 파일명 (예: UserService.cs)
            original_code: 원본 코드
            improved_code: 개선된 코드
            report_markdown: Markdown 리포트
            analysis_time: 분석 소요 시간 (초)
            success: 성공 여부
            error_message: 에러 메시지 (실패 시)

        Returns:
            Tuple[str, str, int]: (markdown_path, html_path, record_id)
        """
        # 타임스탬프 생성 (YYYYMMDD_HHMMSS 형식)
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        timestamp_iso = timestamp.isoformat()

        # 파일명 생성
        base_name = Path(filename).stem
        report_name = f"{base_name}_review_{timestamp_str}"

        markdown_filename = f"{report_name}.md"
        html_filename = f"{report_name}.html"

        markdown_path = self.markdown_dir / markdown_filename
        html_path = self.html_dir / html_filename

        # Markdown 리포트 저장
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(report_markdown)

        # HTML 변환 및 저장
        html_content = self._convert_markdown_to_html(
            report_markdown=report_markdown,
            filename=filename,
            timestamp_str=timestamp.strftime("%Y-%m-%d %H:%M:%S")
        )

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # DB에 기록
        record = ReportRecord(
            filename=filename,
            report_name=report_name,
            timestamp=timestamp_iso,
            markdown_path=str(markdown_path),
            html_path=str(html_path),
            success=success,
            error_message=error_message,
            analysis_time=analysis_time
        )

        record_id = self.db.add_report(record)

        return str(markdown_path), str(html_path), record_id

    def _convert_markdown_to_html(
        self,
        report_markdown: str,
        filename: str,
        timestamp_str: str
    ) -> str:
        """
        Markdown을 HTML로 변환

        Args:
            report_markdown: Markdown 리포트
            filename: 파일명
            timestamp_str: 타임스탬프 문자열

        Returns:
            str: HTML 문서
        """
        # Markdown → HTML 변환 (코드 하이라이팅, 테이블 지원)
        md = markdown.Markdown(
            extensions=[
                'fenced_code',  # 코드 블록 지원
                'tables',       # 테이블 지원
                'nl2br',        # 줄바꿈 지원
                'sane_lists'    # 리스트 개선
            ]
        )

        html_body = md.convert(report_markdown)

        # 완전한 HTML 문서 생성
        html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>코드 리뷰 리포트 - {filename}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #d4d4d4;
            background-color: #1e1e1e;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            background: #252526;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #007acc;
        }}

        .header h1 {{
            color: #ffffff;
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .header .meta {{
            color: #858585;
            font-size: 14px;
        }}

        .content {{
            background: #252526;
            padding: 30px;
            border-radius: 8px;
        }}

        h1 {{
            color: #4ec9b0;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
            margin: 30px 0 20px 0;
            font-size: 24px;
        }}

        h2 {{
            color: #569cd6;
            margin: 25px 0 15px 0;
            font-size: 20px;
        }}

        h3 {{
            color: #dcdcaa;
            margin: 20px 0 10px 0;
            font-size: 18px;
        }}

        p {{
            margin: 10px 0;
        }}

        ul, ol {{
            margin: 10px 0 10px 30px;
        }}

        li {{
            margin: 5px 0;
        }}

        code {{
            background: #1e1e1e;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            color: #ce9178;
            font-size: 14px;
        }}

        pre {{
            background: #1e1e1e;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
            border: 1px solid #3e3e42;
        }}

        pre code {{
            background: none;
            padding: 0;
            color: #d4d4d4;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #3e3e42;
        }}

        th {{
            background: #094771;
            color: #ffffff;
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background: #2d2d30;
        }}

        blockquote {{
            border-left: 4px solid #007acc;
            padding-left: 15px;
            margin: 15px 0;
            color: #858585;
            font-style: italic;
        }}

        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #3e3e42;
            color: #858585;
            font-size: 14px;
        }}

        a {{
            color: #4fc3f7;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 5px;
        }}

        .badge-success {{
            background: #388e3c;
            color: #ffffff;
        }}

        .badge-warning {{
            background: #f57c00;
            color: #ffffff;
        }}

        .badge-error {{
            background: #d32f2f;
            color: #ffffff;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 코드 리뷰 리포트</h1>
        <div class="meta">
            <strong>파일:</strong> {filename} |
            <strong>생성 시각:</strong> {timestamp_str}
        </div>
    </div>

    <div class="content">
        {html_body}
    </div>

    <div class="footer">
        <p>Generated by <strong>C# Code Reviewer</strong> | Powered by Phi-3-mini</p>
    </div>
</body>
</html>
"""

        return html_template


# 편의 함수
def get_report_saver() -> ReportSaver:
    """전역 ReportSaver 인스턴스 반환"""
    return ReportSaver()
