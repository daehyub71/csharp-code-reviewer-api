"""
C# 코드 리뷰 리포트 생성기

LLM 응답을 파싱하고 Markdown 형식의 리포트를 생성합니다.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import re


class ReportGenerator:
    """
    Markdown 리포트 생성 클래스

    LLM의 코드 분석 결과를 파싱하여 구조화된 Markdown 리포트를 생성합니다.
    """

    def __init__(self):
        """ReportGenerator 초기화"""
        pass

    def generate_report(
        self,
        original_code: str,
        improved_code: str,
        categories: List[str],
        model_name: str = "phi3:mini",
        analysis_time: Optional[datetime] = None
    ) -> str:
        """
        코드 리뷰 리포트 생성

        Args:
            original_code: 원본 C# 코드
            improved_code: 개선된 C# 코드 (LLM 응답)
            categories: 적용된 리뷰 카테고리 목록
            model_name: 사용된 LLM 모델 이름
            analysis_time: 분석 수행 시각 (None이면 현재 시각)

        Returns:
            Markdown 형식의 리포트 문자열
        """
        if analysis_time is None:
            analysis_time = datetime.now()

        # 개선 코드에서 순수 코드만 추출 (마크다운 코드 블록 제거)
        clean_improved_code = self._extract_code_from_response(improved_code)

        # 리포트 섹션 생성
        sections = []

        # 1. 헤더
        sections.append(self._generate_header(analysis_time, model_name))

        # 2. 요약
        sections.append(self._generate_summary(original_code, clean_improved_code, categories))

        # 3. 적용된 리뷰 카테고리
        sections.append(self._generate_categories_section(categories))

        # 4. Before/After 코드 비교
        sections.append(self._generate_code_comparison(original_code, clean_improved_code))

        # 5. 개선 사항 분석
        sections.append(self._generate_improvements_section(original_code, clean_improved_code))

        # 6. 푸터
        sections.append(self._generate_footer(model_name))

        return "\n\n".join(sections)

    def _extract_code_from_response(self, llm_response: str) -> str:
        """
        LLM 응답에서 순수 코드만 추출

        Args:
            llm_response: LLM의 전체 응답

        Returns:
            순수 C# 코드
        """
        # 마크다운 코드 블록 제거
        code_block_pattern = r'```(?:csharp|c#)?\s*\n(.*?)\n```'
        matches = re.findall(code_block_pattern, llm_response, re.DOTALL | re.IGNORECASE)

        if matches:
            # 첫 번째 코드 블록 반환
            return matches[0].strip()

        # 코드 블록이 없으면 전체 응답에서 설명 부분 제거
        # "분석:", "개선:", "설명:" 등의 섹션 제거
        lines = llm_response.split('\n')
        code_lines = []
        in_code = True

        for line in lines:
            # 한글 설명이나 분석 섹션은 건너뛰기
            if any(keyword in line for keyword in ['분석:', '개선:', '설명:', 'Analysis:', 'Improvement:']):
                in_code = False
                continue

            # 코드처럼 보이는 줄만 수집
            if in_code or line.strip().startswith(('public', 'private', 'protected', 'internal',
                                                     'class', 'interface', 'namespace', 'using',
                                                     '{', '}', '//')):
                code_lines.append(line)

        result = '\n'.join(code_lines).strip()

        # 결과가 비어있으면 원본 응답 반환
        return result if result else llm_response.strip()

    def _generate_header(self, analysis_time: datetime, model_name: str) -> str:
        """리포트 헤더 생성"""
        return f"""# C# 코드 리뷰 리포트

**생성 일시**: {analysis_time.strftime('%Y-%m-%d %H:%M:%S')}
**분석 모델**: {model_name}
**생성 도구**: C# Code Reviewer v1.0.0"""

    def _generate_summary(self, original: str, improved: str, categories: List[str]) -> str:
        """요약 섹션 생성"""
        original_lines = len([l for l in original.split('\n') if l.strip()])
        improved_lines = len([l for l in improved.split('\n') if l.strip()])
        added_lines = improved_lines - original_lines

        return f"""## 📊 요약

- **원본 코드**: {original_lines} 줄
- **개선 코드**: {improved_lines} 줄
- **추가된 줄**: {added_lines:+d} 줄
- **적용 카테고리**: {len(categories)}개"""

    def _generate_categories_section(self, categories: List[str]) -> str:
        """적용된 카테고리 섹션 생성"""
        category_names = {
            'null_reference': 'Null 참조 체크',
            'exception_handling': 'Exception 처리',
            'resource_management': '리소스 관리',
            'performance': '성능 최적화',
            'security': '보안',
            'naming_convention': '네이밍 컨벤션',
            'code_documentation': 'XML 문서 주석',
            'hardcoding_to_config': '하드코딩 → Config 파일'
        }

        items = [f"- ✅ **{category_names.get(cat, cat)}**" for cat in categories]

        return f"""## 🎯 적용된 리뷰 카테고리

{chr(10).join(items)}"""

    def _generate_code_comparison(self, original: str, improved: str) -> str:
        """Before/After 코드 비교 섹션"""
        return f"""## 📝 코드 비교

### Before (원본 코드)

```csharp
{original}
```

### After (개선된 코드)

```csharp
{improved}
```"""

    def _generate_improvements_section(self, original: str, improved: str) -> str:
        """개선 사항 분석 섹션"""
        improvements = []

        # 간단한 휴리스틱으로 개선 사항 감지
        if 'null' in improved.lower() and 'null' not in original.lower():
            improvements.append("- 🔍 **Null 체크 추가**: 입력 검증으로 NullReferenceException 방지")

        if 'using' in improved and 'using' not in original:
            improvements.append("- 🧹 **리소스 관리 개선**: using 문으로 자동 리소스 해제")

        if 'try' in improved or 'catch' in improved:
            improvements.append("- ⚠️ **예외 처리 추가**: try-catch 블록으로 에러 핸들링 강화")

        if 'throw' in improved and 'throw' not in original:
            improvements.append("- 🚫 **명시적 예외 발생**: 잘못된 입력에 대한 명확한 피드백")

        if not improvements:
            improvements.append("- ✨ 코드 품질 개선")

        improvements_text = '\n'.join(improvements)

        return f"""## 🔍 주요 개선 사항

{improvements_text}"""

    def _generate_footer(self, model_name: str = "Unknown") -> str:
        """리포트 푸터 생성"""
        return f"""---

## 📌 참고사항

이 리포트는 AI({model_name})가 자동으로 생성한 코드 리뷰 결과입니다.
최종 적용 전에 반드시 개발자가 검토해야 합니다.

**생성 도구**: [C# Code Reviewer (API)](https://github.com/daehyub71/csharp-code-reviewer-api)
**사용 모델**: {model_name}"""

    def save_report(self, report: str, output_path: str) -> None:
        """
        리포트를 파일로 저장

        Args:
            report: Markdown 리포트 문자열
            output_path: 저장할 파일 경로

        Raises:
            IOError: 파일 저장 실패 시
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)

        except Exception as e:
            raise IOError(f"리포트 저장 실패: {e}")

    @staticmethod
    def generate_filename(timestamp: Optional[datetime] = None) -> str:
        """
        자동 파일명 생성

        Args:
            timestamp: 타임스탬프 (None이면 현재 시각)

        Returns:
            파일명 (예: code_review_20250112_143052.md)
        """
        if timestamp is None:
            timestamp = datetime.now()

        return f"code_review_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"


# 사용 예제
if __name__ == "__main__":
    # 테스트 데이터
    original_code = """public void ProcessData(string data)
{
    var result = data.ToUpper();
    Console.WriteLine(result);
}"""

    improved_code = """```csharp
public void ProcessData(string data)
{
    if (string.IsNullOrEmpty(data))
        throw new ArgumentNullException(nameof(data));

    var result = data.ToUpper();
    Console.WriteLine(result);
}
```

분석: null 체크를 추가하여 안전성을 향상시켰습니다."""

    categories = ['null_reference', 'exception_handling']

    # 리포트 생성
    generator = ReportGenerator()
    report = generator.generate_report(
        original_code=original_code,
        improved_code=improved_code,
        categories=categories,
        model_name="phi3:mini"
    )

    print(report)
    print("\n" + "=" * 80)
    print(f"생성된 파일명: {generator.generate_filename()}")
