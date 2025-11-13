"""
통합 리포트 생성기

배치 분석 결과를 집계하여 프로젝트 전체 요약 리포트를 생성합니다.
카테고리별 이슈 통계, 차트 생성 기능을 제공합니다.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import re

try:
    import matplotlib
    matplotlib.use('Agg')  # GUI 없이 사용
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


@dataclass
class CategoryStatistics:
    """카테고리별 통계"""
    category_name: str
    issue_count: int
    percentage: float
    files_with_issues: List[str]  # 이슈가 있는 파일 경로


@dataclass
class IntegratedReportData:
    """통합 리포트 데이터"""
    project_name: str
    analysis_time: datetime
    total_files: int
    success_files: int
    failure_files: int
    total_time: float
    category_stats: List[CategoryStatistics]
    priority_recommendations: List[str]


class IntegratedReportGenerator:
    """
    통합 리포트 생성기

    배치 분석 결과를 집계하여 프로젝트 전체 요약 리포트를 생성합니다.
    """

    # 카테고리 한글 이름 매핑
    CATEGORY_NAMES = {
        'null_reference': 'Null 참조 체크',
        'exception_handling': 'Exception 처리',
        'resource_management': '리소스 관리',
        'performance': '성능 최적화',
        'security': '보안',
        'naming_convention': '네이밍 컨벤션',
        'code_documentation': 'XML 문서 주석',
        'hardcoding_to_config': '하드코딩 → Config 파일'
    }

    # 우선순위 가중치 (높을수록 중요)
    CATEGORY_PRIORITY = {
        'security': 10,              # 보안 최우선
        'resource_management': 9,    # 메모리 누수 등
        'exception_handling': 8,     # 안정성
        'null_reference': 7,         # NullReferenceException
        'hardcoding_to_config': 6,   # 유지보수성
        'performance': 5,            # 성능
        'naming_convention': 3,      # 코드 품질
        'code_documentation': 2      # 문서화
    }

    def __init__(self):
        """통합 리포트 생성기 초기화"""
        pass

    def generate_integrated_report(
        self,
        batch_result,  # BatchAnalysisResult
        project_name: str = "C# Project"
    ) -> str:
        """
        통합 리포트 생성

        Args:
            batch_result: 배치 분석 결과
            project_name: 프로젝트 이름

        Returns:
            Markdown 형식의 통합 리포트
        """
        # 통합 데이터 수집
        report_data = self._collect_report_data(batch_result, project_name)

        # Markdown 리포트 생성
        markdown = self._generate_markdown(report_data)

        return markdown

    def _collect_report_data(
        self,
        batch_result,
        project_name: str
    ) -> IntegratedReportData:
        """통합 리포트 데이터 수집"""
        # 카테고리별 이슈 통계 수집
        category_stats = self._analyze_category_statistics(batch_result.results)

        # 우선순위 권장 생성
        priority_recommendations = self._generate_priority_recommendations(category_stats)

        return IntegratedReportData(
            project_name=project_name,
            analysis_time=batch_result.start_time,
            total_files=batch_result.total_files,
            success_files=batch_result.success_count,
            failure_files=batch_result.failure_count,
            total_time=batch_result.total_time,
            category_stats=category_stats,
            priority_recommendations=priority_recommendations
        )

    def _analyze_category_statistics(
        self,
        results: List  # List[FileAnalysisResult]
    ) -> List[CategoryStatistics]:
        """카테고리별 이슈 통계 분석"""
        category_issues: Dict[str, List[str]] = {
            category_id: [] for category_id in self.CATEGORY_NAMES.keys()
        }

        # 각 파일의 리포트에서 이슈 추출
        for result in results:
            if not result.success or not result.report_markdown:
                continue

            # 리포트 마크다운에서 카테고리 감지
            for category_id, category_name in self.CATEGORY_NAMES.items():
                # "✅ **Null 참조 체크**" 같은 패턴 찾기
                if f"**{category_name}**" in result.report_markdown:
                    # 실제로 개선 사항이 있는지 확인 (간단한 휴리스틱)
                    if self._has_improvements(result.report_markdown, category_name):
                        category_issues[category_id].append(result.file_name)

        # 통계 생성
        stats = []
        total_issues = sum(len(files) for files in category_issues.values())

        for category_id, files in category_issues.items():
            issue_count = len(files)
            percentage = (issue_count / total_issues * 100) if total_issues > 0 else 0

            stats.append(CategoryStatistics(
                category_name=self.CATEGORY_NAMES[category_id],
                issue_count=issue_count,
                percentage=percentage,
                files_with_issues=files[:10]  # 최대 10개만
            ))

        # 이슈 개수 내림차순 정렬
        stats.sort(key=lambda x: x.issue_count, reverse=True)

        return stats

    def _has_improvements(self, report_markdown: str, category_name: str) -> bool:
        """리포트에 실제 개선 사항이 있는지 확인 (휴리스틱)"""
        # Before/After 코드 차이가 있으면 개선 사항이 있는 것으로 판단
        before_section = "### Before (원본 코드)" in report_markdown
        after_section = "### After (개선된 코드)" in report_markdown

        if not (before_section and after_section):
            return False

        # Before와 After 코드 추출
        try:
            before_code = re.search(
                r'### Before \(원본 코드\)\s*```csharp\s*(.*?)\s*```',
                report_markdown,
                re.DOTALL
            )
            after_code = re.search(
                r'### After \(개선된 코드\)\s*```csharp\s*(.*?)\s*```',
                report_markdown,
                re.DOTALL
            )

            if before_code and after_code:
                # 코드가 다르면 개선 사항 있음
                return before_code.group(1) != after_code.group(1)
        except:
            pass

        return True  # 안전하게 True 반환

    def _generate_priority_recommendations(
        self,
        category_stats: List[CategoryStatistics]
    ) -> List[str]:
        """개선 우선순위 권장 생성"""
        recommendations = []

        # 우선순위 점수 계산 (이슈 개수 × 가중치)
        scored_categories = []
        for stat in category_stats:
            if stat.issue_count > 0:
                # 카테고리 ID 찾기
                category_id = None
                for cid, cname in self.CATEGORY_NAMES.items():
                    if cname == stat.category_name:
                        category_id = cid
                        break

                if category_id:
                    priority = self.CATEGORY_PRIORITY.get(category_id, 1)
                    score = stat.issue_count * priority
                    scored_categories.append((stat.category_name, score, stat.issue_count))

        # 점수 내림차순 정렬
        scored_categories.sort(key=lambda x: x[1], reverse=True)

        # 상위 3개 권장
        for i, (category_name, score, count) in enumerate(scored_categories[:3], 1):
            recommendations.append(
                f"{i}. **{category_name}** - {count}개 파일에서 발견 (우선순위: 높음)"
            )

        # 나머지 권장
        for i, (category_name, score, count) in enumerate(scored_categories[3:], 4):
            recommendations.append(
                f"{i}. **{category_name}** - {count}개 파일에서 발견"
            )

        if not recommendations:
            recommendations.append("✅ 모든 카테고리에서 이슈가 발견되지 않았습니다.")

        return recommendations

    def _generate_markdown(self, data: IntegratedReportData) -> str:
        """Markdown 형식의 통합 리포트 생성"""
        lines = []

        # 헤더
        lines.append("# 📊 C# 프로젝트 코드 리뷰 통합 리포트")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 프로젝트 정보
        lines.append("## 📁 프로젝트 정보")
        lines.append("")
        lines.append(f"- **프로젝트명**: {data.project_name}")
        lines.append(f"- **분석 일시**: {data.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **전체 파일**: {data.total_files}개")
        lines.append(f"- **분석 성공**: {data.success_files}개 ✅")
        if data.failure_files > 0:
            lines.append(f"- **분석 실패**: {data.failure_files}개 ❌")
        lines.append(f"- **소요 시간**: {self._format_time(data.total_time)}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 카테고리별 이슈 통계
        lines.append("## 📈 카테고리별 이슈 통계")
        lines.append("")

        if any(stat.issue_count > 0 for stat in data.category_stats):
            # 테이블 형식
            lines.append("| 카테고리 | 이슈 파일 수 | 비율 |")
            lines.append("|---------|-------------|------|")

            for stat in data.category_stats:
                if stat.issue_count > 0:
                    bar = self._generate_bar(stat.percentage)
                    lines.append(
                        f"| {stat.category_name} | {stat.issue_count}개 | "
                        f"{stat.percentage:.1f}% {bar} |"
                    )

            lines.append("")

            # 상세 파일 목록
            lines.append("### 🔍 카테고리별 상세")
            lines.append("")

            for stat in data.category_stats:
                if stat.issue_count > 0:
                    lines.append(f"#### {stat.category_name}")
                    lines.append("")
                    lines.append(f"총 {stat.issue_count}개 파일에서 발견:")
                    lines.append("")

                    for file_name in stat.files_with_issues:
                        lines.append(f"- `{file_name}`")

                    if stat.issue_count > len(stat.files_with_issues):
                        remaining = stat.issue_count - len(stat.files_with_issues)
                        lines.append(f"- ... (외 {remaining}개 파일)")

                    lines.append("")
        else:
            lines.append("✅ **모든 카테고리에서 이슈가 발견되지 않았습니다!**")
            lines.append("")

        lines.append("---")
        lines.append("")

        # 개선 우선순위 권장
        lines.append("## 🎯 개선 우선순위 권장")
        lines.append("")
        lines.append("다음 순서로 개선하는 것을 권장합니다:")
        lines.append("")

        for recommendation in data.priority_recommendations:
            lines.append(recommendation)

        lines.append("")
        lines.append("---")
        lines.append("")

        # 푸터
        lines.append("## 📝 참고사항")
        lines.append("")
        lines.append("- 이 리포트는 AI 기반 정적 분석 결과입니다")
        lines.append("- 실제 코드 동작과 다를 수 있으니 개발자의 검토가 필요합니다")
        lines.append("- 각 파일의 상세 리포트는 개별적으로 저장되어 있습니다")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"*생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(lines)

    def _generate_bar(self, percentage: float) -> str:
        """퍼센티지 바 생성"""
        bar_length = 20
        filled = int(percentage / 100 * bar_length)
        return "█" * filled + "░" * (bar_length - filled)

    def _format_time(self, seconds: float) -> str:
        """시간을 읽기 쉬운 형식으로 변환"""
        if seconds < 60:
            return f"{seconds:.1f}초"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}분"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}시간"

    def generate_chart(
        self,
        data: IntegratedReportData,
        output_path: str
    ) -> bool:
        """
        카테고리별 이슈 분포 차트 생성 (원형 차트)

        Args:
            data: 통합 리포트 데이터
            output_path: 출력 파일 경로 (PNG)

        Returns:
            성공 여부
        """
        if not MATPLOTLIB_AVAILABLE:
            return False

        try:
            # 이슈가 있는 카테고리만 필터링
            categories = [stat for stat in data.category_stats if stat.issue_count > 0]

            if not categories:
                return False

            # 데이터 준비
            labels = [stat.category_name for stat in categories]
            sizes = [stat.issue_count for stat in categories]

            # 색상 팔레트
            colors = [
                '#ff6b6b',  # 빨강
                '#feca57',  # 노랑
                '#48dbfb',  # 파랑
                '#1dd1a1',  # 초록
                '#ee5a6f',  # 분홍
                '#c56cf0',  # 보라
                '#f368e0',  # 핑크
                '#ff9f43'   # 주황
            ]

            # 차트 생성
            plt.figure(figsize=(10, 7))
            plt.pie(
                sizes,
                labels=labels,
                colors=colors[:len(labels)],
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 11, 'weight': 'bold'}
            )
            plt.axis('equal')
            plt.title(
                f'{data.project_name}\n카테고리별 이슈 분포',
                fontsize=14,
                weight='bold',
                pad=20
            )

            # 저장
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            return True

        except Exception as e:
            print(f"차트 생성 실패: {e}")
            return False
