"""
Markdown 렌더링 테스트

MarkdownRenderer와 ResultPanel의 Markdown → HTML 변환 기능을 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.markdown_renderer import MarkdownRenderer
from app.core.report_generator import ReportGenerator


def test_markdown_renderer():
    """MarkdownRenderer 기본 기능 테스트"""

    print("=" * 80)
    print("MarkdownRenderer 테스트")
    print("=" * 80)

    # 테스트 Markdown
    test_markdown = """# 테스트 헤더

일반 텍스트 **굵은 글씨** *기울임*

## 코드 블록 테스트

```csharp
public void TestMethod()
{
    Console.WriteLine("Hello World");
}
```

## 리스트 테스트

- 항목 1
- 항목 2
- 항목 3

## 표 테스트

| 헤더1 | 헤더2 |
|------|------|
| 값1  | 값2  |
"""

    # 렌더러 생성
    renderer = MarkdownRenderer(theme="monokai")

    # HTML 변환
    html = renderer.render(test_markdown)

    # 검증
    checks = {
        "HTML 문서 생성": "<!DOCTYPE html>" in html,
        "헤더 포함": "<h1>테스트 헤더</h1>" in html,
        "코드 블록 구문 강조": "highlight" in html,
        "C# 키워드 강조": "public" in html or "Console" in html,
        "리스트 렌더링": "<ul>" in html and "<li>" in html,
        "표 렌더링": "<table>" in html and "<th>" in html,
        "CSS 포함": "background-color" in html,
        "Pygments CSS 포함": ".highlight" in html,
    }

    print("\n📊 검증 결과:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    print(f"\n📏 HTML 길이: {len(html):,} 글자")

    all_passed = all(checks.values())

    if all_passed:
        print("\n✅ 모든 검증 통과!")
    else:
        print("\n❌ 일부 검증 실패")

    return all_passed


def test_report_generation_with_markdown():
    """ReportGenerator + MarkdownRenderer 통합 테스트"""

    print("\n\n" + "=" * 80)
    print("ReportGenerator → MarkdownRenderer 통합 테스트")
    print("=" * 80)

    # 테스트 데이터
    original_code = """public void ProcessData(string data)
{
    var result = data.ToUpper();
    Console.WriteLine(result);
}"""

    improved_code = """public void ProcessData(string data)
{
    if (string.IsNullOrEmpty(data))
        throw new ArgumentNullException(nameof(data));

    var result = data.ToUpper();
    Console.WriteLine(result);
}"""

    categories = ['null_reference', 'exception_handling']

    # ReportGenerator로 Markdown 생성
    print("\n📋 ReportGenerator로 Markdown 생성 중...")
    report_gen = ReportGenerator()
    markdown_report = report_gen.generate_report(
        original_code=original_code,
        improved_code=improved_code,
        categories=categories,
        model_name="phi3:mini"
    )

    print(f"✅ Markdown 생성 완료 ({len(markdown_report)} 글자)")

    # MarkdownRenderer로 HTML 변환
    print("\n🎨 MarkdownRenderer로 HTML 변환 중...")
    renderer = MarkdownRenderer(theme="monokai")
    html = renderer.render(markdown_report)

    print(f"✅ HTML 변환 완료 ({len(html)} 글자)")

    # 검증
    checks = {
        "리포트 헤더 포함": "C# 코드 리뷰 리포트" in html,
        "요약 섹션 포함": "📊 요약" in html,
        "카테고리 섹션 포함": "🎯 적용된 리뷰 카테고리" in html,
        "Before 코드 구문 강조": "public void ProcessData" in html,
        "After 코드 구문 강조": "ArgumentNullException" in html,
        "개선 사항 섹션 포함": "🔍 주요 개선 사항" in html,
        "Null 체크 감지": "Null 체크 추가" in html or "null" in html.lower(),
        "모델 정보 포함": "phi3:mini" in html,
    }

    print("\n📊 검증 결과:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    all_passed = all(checks.values())

    if all_passed:
        print("\n✅ 모든 검증 통과!")
    else:
        print("\n❌ 일부 검증 실패")

    # HTML 파일로 저장 (브라우저에서 확인 가능)
    output_file = "test_integrated_report.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n💾 테스트 리포트 저장: {output_file}")
    print("   (브라우저로 열어서 시각적으로 확인하세요)")

    return all_passed


def test_multiple_code_blocks():
    """여러 코드 블록이 있는 Markdown 테스트"""

    print("\n\n" + "=" * 80)
    print("다중 코드 블록 테스트")
    print("=" * 80)

    markdown = """# 여러 코드 블록 테스트

## C# 예제 1

```csharp
public class Calculator
{
    public int Add(int a, int b)
    {
        return a + b;
    }
}
```

## C# 예제 2

```csharp
public interface IService
{
    Task<string> GetDataAsync();
}
```

## Python 예제

```python
def hello():
    print("Hello, World!")
```
"""

    renderer = MarkdownRenderer(theme="monokai")
    html = renderer.render(markdown)

    # 검증
    checks = {
        "첫 번째 코드 블록": "Calculator" in html,
        "두 번째 코드 블록": "IService" in html,
        "세 번째 코드 블록": "def hello" in html,
        "구문 강조 적용": html.count("highlight") >= 3,
    }

    print("\n📊 검증 결과:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    all_passed = all(checks.values())

    if all_passed:
        print("\n✅ 모든 검증 통과!")
    else:
        print("\n❌ 일부 검증 실패")

    return all_passed


def test_css_generation():
    """Pygments CSS 생성 테스트"""

    print("\n\n" + "=" * 80)
    print("CSS 생성 테스트")
    print("=" * 80)

    renderer = MarkdownRenderer(theme="monokai")

    # Pygments CSS 추출
    css = renderer.get_css()

    # 검증
    checks = {
        "CSS 생성됨": len(css) > 0,
        "Monokai 테마 색상 포함": "#272822" in css or "#F8F8F2" in css,
        "하이라이트 클래스 정의": ".highlight" in css,
    }

    print("\n📊 검증 결과:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    print(f"\n📏 CSS 길이: {len(css):,} 글자")

    # CSS 파일로 저장
    css_file = "test_pygments.css"
    with open(css_file, "w", encoding="utf-8") as f:
        f.write(css)

    print(f"💾 CSS 저장: {css_file}")

    all_passed = all(checks.values())

    if all_passed:
        print("\n✅ 모든 검증 통과!")
    else:
        print("\n❌ 일부 검증 실패")

    return all_passed


if __name__ == "__main__":
    print("\n🚀 Markdown 렌더링 종합 테스트 시작\n")

    # 테스트 실행
    result1 = test_markdown_renderer()
    result2 = test_report_generation_with_markdown()
    result3 = test_multiple_code_blocks()
    result4 = test_css_generation()

    # 최종 결과
    print("\n\n" + "=" * 80)
    print("🎬 최종 결과")
    print("=" * 80)
    print(f"기본 렌더링 테스트: {'✅ 통과' if result1 else '❌ 실패'}")
    print(f"통합 테스트: {'✅ 통과' if result2 else '❌ 실패'}")
    print(f"다중 코드 블록 테스트: {'✅ 통과' if result3 else '❌ 실패'}")
    print(f"CSS 생성 테스트: {'✅ 통과' if result4 else '❌ 실패'}")

    if all([result1, result2, result3, result4]):
        print("\n🎉 모든 테스트 통과!")
        print("Markdown → HTML 렌더링이 정상적으로 작동합니다.")
    else:
        print("\n⚠️ 일부 테스트 실패")

    print("=" * 80)
