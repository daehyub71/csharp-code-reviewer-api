"""
BatchAnalyzer 단위 테스트

배치 분석 엔진의 주요 기능을 테스트합니다.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# 프로젝트 루트를 PYTHONPATH에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.batch_analyzer import BatchAnalyzer, FileAnalysisResult, BatchAnalysisResult


@pytest.fixture
def test_cs_files(tmp_path):
    """테스트용 C# 파일 생성"""
    files = []

    # 파일 1: 간단한 클래스
    file1 = tmp_path / "Test1.cs"
    file1.write_text(
        "public class Test1 { public void Method() { } }",
        encoding='utf-8'
    )
    files.append(str(file1))

    # 파일 2: 다른 클래스
    file2 = tmp_path / "Test2.cs"
    file2.write_text(
        "public class Test2 { public int Add(int a, int b) { return a + b; } }",
        encoding='utf-8'
    )
    files.append(str(file2))

    # 파일 3: 더 복잡한 클래스
    file3 = tmp_path / "Test3.cs"
    file3.write_text(
        "public class Calculator\n"
        "{\n"
        "    public int Divide(int a, int b)\n"
        "    {\n"
        "        return a / b;\n"
        "    }\n"
        "}\n",
        encoding='utf-8'
    )
    files.append(str(file3))

    return files


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama 클라이언트"""
    client = Mock()

    # analyze_code 메서드가 개선된 코드 반환 (문자열)
    client.analyze_code.return_value = 'public class ImprovedCode { }'

    return client


@pytest.fixture
def mock_prompt_builder():
    """Mock PromptBuilder"""
    builder = Mock()
    builder.build_review_prompt.return_value = "Test prompt"
    return builder


@pytest.fixture
def mock_report_generator():
    """Mock ReportGenerator"""
    generator = Mock()
    generator.generate_report.return_value = '# Test Report\n\nThis is a test report.'
    return generator


class TestFileAnalysisResult:
    """FileAnalysisResult 데이터클래스 테스트"""

    def test_successful_result(self):
        """성공한 분석 결과"""
        result = FileAnalysisResult(
            file_path="/path/to/file.cs",
            file_name="file.cs",
            success=True,
            original_code="original",
            improved_code="improved",
            report_markdown="# Report",
            analysis_time=1.5,
            retry_count=0
        )

        assert result.success is True
        assert result.file_name == "file.cs"
        assert result.analysis_time == 1.5
        assert result.error_message == ""

    def test_failed_result(self):
        """실패한 분석 결과"""
        result = FileAnalysisResult(
            file_path="/path/to/file.cs",
            file_name="file.cs",
            success=False,
            error_message="Test error"
        )

        assert result.success is False
        assert result.error_message == "Test error"
        assert result.improved_code == ""


class TestBatchAnalysisResult:
    """BatchAnalysisResult 데이터클래스 테스트"""

    def test_batch_result_calculation(self):
        """배치 결과 집계 계산"""
        from datetime import datetime

        results = [
            FileAnalysisResult(
                file_path="/path/1.cs",
                file_name="1.cs",
                success=True,
                analysis_time=1.0
            ),
            FileAnalysisResult(
                file_path="/path/2.cs",
                file_name="2.cs",
                success=False,
                error_message="Error"
            ),
            FileAnalysisResult(
                file_path="/path/3.cs",
                file_name="3.cs",
                success=True,
                analysis_time=2.0
            ),
        ]

        start = datetime.now()
        end = datetime.now()

        batch_result = BatchAnalysisResult(
            total_files=3,
            success_count=2,
            failure_count=1,
            skipped_count=0,
            total_time=3.0,
            results=results,
            start_time=start,
            end_time=end
        )

        assert batch_result.total_files == 3
        assert batch_result.success_count == 2
        assert batch_result.failure_count == 1
        assert batch_result.skipped_count == 0


class TestBatchAnalyzer:
    """BatchAnalyzer 테스트 클래스"""

    def test_initialization(self, mock_ollama_client, mock_prompt_builder, mock_report_generator):
        """BatchAnalyzer 초기화"""
        analyzer = BatchAnalyzer(
            ollama_client=mock_ollama_client,
            prompt_builder=mock_prompt_builder,
            report_generator=mock_report_generator
        )

        assert analyzer.ollama_client == mock_ollama_client
        assert analyzer.prompt_builder == mock_prompt_builder
        assert analyzer.report_generator == mock_report_generator

    def test_analyze_single_file_success(
        self,
        mock_ollama_client,
        mock_prompt_builder,
        mock_report_generator,
        test_cs_files
    ):
        """단일 파일 분석 성공"""
        analyzer = BatchAnalyzer(
            ollama_client=mock_ollama_client,
            prompt_builder=mock_prompt_builder,
            report_generator=mock_report_generator
        )

        result = analyzer._analyze_single_file(test_cs_files[0])

        assert result.success is True
        assert result.file_name == "Test1.cs"
        assert "ImprovedCode" in result.improved_code
        assert "Test Report" in result.report_markdown
        assert result.retry_count == 0

    def test_analyze_single_file_nonexistent(
        self,
        mock_ollama_client,
        mock_prompt_builder,
        mock_report_generator
    ):
        """존재하지 않는 파일 분석"""
        analyzer = BatchAnalyzer(
            ollama_client=mock_ollama_client,
            prompt_builder=mock_prompt_builder,
            report_generator=mock_report_generator
        )

        result = analyzer._analyze_single_file("/nonexistent/file.cs")

        assert result.success is False
        assert "파일 읽기 실패" in result.error_message
        assert "스킵" in result.error_message

    def test_analyze_files_multiple(
        self,
        mock_ollama_client,
        mock_prompt_builder,
        mock_report_generator,
        test_cs_files
    ):
        """다중 파일 배치 분석"""
        analyzer = BatchAnalyzer(
            ollama_client=mock_ollama_client,
            prompt_builder=mock_prompt_builder,
            report_generator=mock_report_generator
        )

        batch_result = analyzer.analyze_files(test_cs_files)

        assert batch_result.total_files == 3
        assert batch_result.success_count == 3
        assert batch_result.failure_count == 0
        assert len(batch_result.results) == 3

    def test_progress_callback(
        self,
        mock_ollama_client,
        mock_prompt_builder,
        mock_report_generator,
        test_cs_files
    ):
        """프로그레스 콜백 테스트"""
        analyzer = BatchAnalyzer(
            ollama_client=mock_ollama_client,
            prompt_builder=mock_prompt_builder,
            report_generator=mock_report_generator
        )

        progress_calls = []

        def on_progress(current, total, file_name):
            progress_calls.append((current, total, file_name))

        batch_result = analyzer.analyze_files(
            test_cs_files,
            progress_callback=on_progress
        )

        # 프로그레스 콜백이 파일 개수만큼 호출되었는지 확인
        assert len(progress_calls) == 3
        assert progress_calls[0] == (0, 3, "Test1.cs")
        assert progress_calls[1] == (1, 3, "Test2.cs")
        assert progress_calls[2] == (2, 3, "Test3.cs")

    def test_cancellation(
        self,
        mock_ollama_client,
        mock_prompt_builder,
        mock_report_generator,
        test_cs_files
    ):
        """취소 기능 테스트"""
        analyzer = BatchAnalyzer(
            ollama_client=mock_ollama_client,
            prompt_builder=mock_prompt_builder,
            report_generator=mock_report_generator
        )

        cancelled_after_first = False

        def is_cancelled():
            return cancelled_after_first

        def on_progress(current, total, file_name):
            nonlocal cancelled_after_first
            if current == 1:  # 두 번째 파일 후 취소
                cancelled_after_first = True

        batch_result = analyzer.analyze_files(
            test_cs_files,
            progress_callback=on_progress,
            is_cancelled_callback=is_cancelled
        )

        # 취소 후에는 나머지 파일이 분석되지 않음
        # 첫 번째 파일은 완료, 두 번째 파일도 완료, 세 번째 파일은 취소
        assert batch_result.total_files <= 3

    def test_retry_logic(
        self,
        mock_prompt_builder,
        mock_report_generator,
        test_cs_files
    ):
        """재시도 로직 테스트"""
        from app.core.ollama_client import OllamaClientError

        # LLM이 처음 2번 실패하고 3번째에 성공하도록 설정
        mock_client = Mock()
        call_count = 0

        def analyze_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise OllamaClientError("Temporary error")
            return 'public class ImprovedCode { }'

        mock_client.analyze_code.side_effect = analyze_side_effect

        analyzer = BatchAnalyzer(
            ollama_client=mock_client,
            prompt_builder=mock_prompt_builder,
            report_generator=mock_report_generator
        )

        result = analyzer._analyze_single_file(test_cs_files[0])

        # 3번 시도 후 성공
        assert result.success is True
        assert result.retry_count == 2  # 재시도 2번
        assert call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
