"""
다중 파일 배치 분석기

여러 C# 파일을 순차적으로 분석하고 결과를 집계합니다.
"""

from dataclasses import dataclass
from typing import List, Optional, Callable, Dict
from pathlib import Path
from datetime import datetime
import time
import traceback

from app.core.api_client import APIClient, APIClientError
from app.core.prompt_builder import PromptBuilder, ReviewCategory, OutputFormat
from app.core.report_generator import ReportGenerator


@dataclass
class FileAnalysisResult:
    """파일 분석 결과"""
    file_path: str
    file_name: str
    success: bool
    original_code: str = ""
    improved_code: str = ""
    report_markdown: str = ""
    error_message: str = ""
    analysis_time: float = 0.0  # 초 단위
    retry_count: int = 0


@dataclass
class BatchAnalysisResult:
    """배치 분석 결과"""
    total_files: int
    success_count: int
    failure_count: int
    skipped_count: int
    total_time: float  # 초 단위
    results: List[FileAnalysisResult]
    start_time: datetime
    end_time: datetime


class BatchAnalyzer:
    """
    다중 파일 배치 분석기

    여러 C# 파일을 순차적으로 분석하고 결과를 집계합니다.
    - 에러 발생 시 재시도 (최대 3회)
    - 파일 읽기 실패 시 스킵
    - 프로그레스 콜백 지원
    - 중단 가능 (is_cancelled 콜백)
    """

    MAX_RETRIES = 3  # 최대 재시도 횟수

    def __init__(
        self,
        api_client: APIClient,
        prompt_builder: Optional[PromptBuilder] = None,
        report_generator: Optional[ReportGenerator] = None
    ):
        """
        배치 분석기 초기화

        Args:
            api_client: API 클라이언트
            prompt_builder: 프롬프트 빌더 (None이면 새로 생성)
            report_generator: 리포트 생성기 (None이면 새로 생성)
        """
        self.api_client = api_client
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.report_generator = report_generator or ReportGenerator()

        # 기본 리뷰 카테고리
        self.categories = [
            ReviewCategory.NULL_REFERENCE,
            ReviewCategory.EXCEPTION_HANDLING,
            ReviewCategory.RESOURCE_MANAGEMENT,
            ReviewCategory.PERFORMANCE,
            ReviewCategory.SECURITY,
            ReviewCategory.NAMING_CONVENTION,
            ReviewCategory.CODE_DOCUMENTATION
        ]

    def analyze_files(
        self,
        file_paths: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        is_cancelled_callback: Optional[Callable[[], bool]] = None
    ) -> BatchAnalysisResult:
        """
        파일 목록을 순차적으로 분석

        Args:
            file_paths: 분석할 파일 경로 리스트
            progress_callback: 진행 상황 콜백 (현재 인덱스, 전체 개수, 파일명)
            is_cancelled_callback: 취소 여부 확인 콜백 (True 반환 시 중단)

        Returns:
            BatchAnalysisResult: 배치 분석 결과
        """
        start_time = datetime.now()
        results = []

        success_count = 0
        failure_count = 0
        skipped_count = 0

        for i, file_path in enumerate(file_paths):
            # 취소 확인
            if is_cancelled_callback and is_cancelled_callback():
                print(f"⚠️ 분석이 취소되었습니다. (처리된 파일: {i}/{len(file_paths)})")
                break

            # 프로그레스 업데이트
            file_name = Path(file_path).name
            if progress_callback:
                progress_callback(i, len(file_paths), file_name)

            # 파일 분석
            result = self._analyze_single_file(file_path)
            results.append(result)

            # 결과 집계
            if result.success:
                success_count += 1
            elif result.error_message and "스킵" in result.error_message:
                skipped_count += 1
            else:
                failure_count += 1

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        return BatchAnalysisResult(
            total_files=len(file_paths),
            success_count=success_count,
            failure_count=failure_count,
            skipped_count=skipped_count,
            total_time=total_time,
            results=results,
            start_time=start_time,
            end_time=end_time
        )

    def _analyze_single_file(self, file_path: str) -> FileAnalysisResult:
        """
        단일 파일 분석 (재시도 로직 포함)

        Args:
            file_path: 파일 경로

        Returns:
            FileAnalysisResult: 파일 분석 결과
        """
        file_name = Path(file_path).name
        start_time = time.time()

        # 1. 파일 읽기
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read().strip()

            if not original_code:
                return FileAnalysisResult(
                    file_path=file_path,
                    file_name=file_name,
                    success=False,
                    error_message=f"빈 파일 (스킵)",
                    analysis_time=time.time() - start_time
                )

        except UnicodeDecodeError:
            return FileAnalysisResult(
                file_path=file_path,
                file_name=file_name,
                success=False,
                error_message=f"UTF-8 인코딩 오류 (스킵)",
                analysis_time=time.time() - start_time
            )

        except Exception as e:
            return FileAnalysisResult(
                file_path=file_path,
                file_name=file_name,
                success=False,
                error_message=f"파일 읽기 실패: {str(e)} (스킵)",
                analysis_time=time.time() - start_time
            )

        # 2. LLM 분석 (재시도 로직)
        retry_count = 0
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                # 프롬프트 생성
                prompt = self.prompt_builder.build_review_prompt(
                    code=original_code,
                    categories=self.categories,
                    output_format=OutputFormat.IMPROVED_CODE,
                    include_examples=True
                )

                full_prompt = f"{self.prompt_builder.SYSTEM_PROMPT}\n\n{prompt}"

                # LLM 호출 (스트리밍 활성화)
                improved_code = ""
                for token in self.api_client.analyze_code(
                    prompt=full_prompt,
                    stream=True  # 스트리밍 활성화 (토큰 제한 완화)
                ):
                    improved_code += token

                # 리포트 생성
                report_markdown = self.report_generator.generate_report(
                    original_code=original_code,
                    improved_code=improved_code,
                    categories=[cat.value for cat in self.categories],
                    model_name="phi3:mini"
                )

                # 성공
                analysis_time = time.time() - start_time

                return FileAnalysisResult(
                    file_path=file_path,
                    file_name=file_name,
                    success=True,
                    original_code=original_code,
                    improved_code=improved_code,
                    report_markdown=report_markdown,
                    analysis_time=analysis_time,
                    retry_count=retry_count
                )

            except APIClientError as e:
                retry_count += 1
                last_error = e
                print(f"⚠️ {file_name} 분석 실패 (시도 {attempt + 1}/{self.MAX_RETRIES}): {str(e)}")

                # 마지막 재시도가 아니면 대기
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(1)  # 1초 대기 후 재시도

            except Exception as e:
                retry_count += 1
                last_error = e
                print(f"❌ {file_name} 분석 중 예상치 못한 오류 (시도 {attempt + 1}/{self.MAX_RETRIES}): {str(e)}")
                print(traceback.format_exc())

                # 마지막 재시도가 아니면 대기
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(1)

        # 모든 재시도 실패
        analysis_time = time.time() - start_time

        return FileAnalysisResult(
            file_path=file_path,
            file_name=file_name,
            success=False,
            original_code=original_code,
            error_message=f"LLM 분석 실패 ({self.MAX_RETRIES}회 재시도): {str(last_error)}",
            analysis_time=analysis_time,
            retry_count=retry_count
        )


# 사용 예제
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 프로젝트 루트 추가
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from app.core.api_client import APIClient

    # API 클라이언트 생성
    client = APIClient()

    # BatchAnalyzer 생성
    analyzer = BatchAnalyzer(api_client=client)

    # 테스트 파일 목록
    test_files = [
        str(project_root / "test_files" / "Sample1.cs"),
        str(project_root / "test_files" / "Sample2.cs"),
        str(project_root / "test_files" / "Sample3.cs"),
    ]

    # 프로그레스 콜백
    def on_progress(current, total, file_name):
        print(f"[{current + 1}/{total}] 분석 중: {file_name}")

    # 배치 분석 실행
    print("=" * 80)
    print("배치 분석 시작")
    print("=" * 80)

    result = analyzer.analyze_files(
        file_paths=test_files,
        progress_callback=on_progress
    )

    # 결과 출력
    print("\n" + "=" * 80)
    print("배치 분석 완료")
    print("=" * 80)
    print(f"전체 파일: {result.total_files}개")
    print(f"성공: {result.success_count}개")
    print(f"실패: {result.failure_count}개")
    print(f"스킵: {result.skipped_count}개")
    print(f"총 소요 시간: {result.total_time:.1f}초")
    print()

    # 개별 결과
    for i, file_result in enumerate(result.results, 1):
        status = "✅" if file_result.success else "❌"
        print(f"{status} {i}. {file_result.file_name}")
        print(f"   소요 시간: {file_result.analysis_time:.1f}초")
        if file_result.retry_count > 0:
            print(f"   재시도: {file_result.retry_count}회")
        if not file_result.success:
            print(f"   오류: {file_result.error_message}")
        print()
