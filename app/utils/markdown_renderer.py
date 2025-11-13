"""
Markdown → HTML 렌더러

리포트의 Markdown을 HTML로 변환하고 Pygments를 사용하여
C# 코드 블록에 구문 강조를 적용합니다.
"""

import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from pygments.formatters import HtmlFormatter
from typing import Optional


class MarkdownRenderer:
    """
    Markdown → HTML 변환기

    python-markdown과 Pygments를 사용하여 Markdown을
    구문 강조가 적용된 HTML로 변환합니다.
    """

    def __init__(self, theme: str = "monokai"):
        """
        MarkdownRenderer 초기화

        Args:
            theme: Pygments 색상 테마 (기본값: monokai)
                   옵션: monokai, github-dark, vs, vim, etc.
        """
        self.theme = theme

        # Markdown 확장 설정
        self.extensions = [
            FencedCodeExtension(),  # ```로 코드 블록 감싸기
            TableExtension(),        # 표 지원
            CodeHiliteExtension(    # 코드 구문 강조
                linenums=False,      # 라인 번호 비활성화 (이미 에디터에 있음)
                css_class="highlight",
                guess_lang=False,    # 언어 자동 감지 비활성화
                pygments_style=theme
            ),
            'nl2br',                 # 줄바꿈을 <br>로 변환
            'sane_lists',            # 리스트 파싱 개선
        ]

        # Markdown 파서 생성
        self.md = markdown.Markdown(extensions=self.extensions)

        # Pygments CSS 생성기
        self.formatter = HtmlFormatter(style=theme, cssclass="highlight")

    def render(self, markdown_text: str) -> str:
        """
        Markdown 텍스트를 HTML로 변환

        Args:
            markdown_text: 변환할 Markdown 문자열

        Returns:
            HTML 문자열 (CSS 포함)
        """
        if not markdown_text:
            return ""

        # Markdown → HTML 변환
        html_body = self.md.convert(markdown_text)

        # Markdown 파서 상태 초기화 (재사용 시 필요)
        self.md.reset()

        # 완전한 HTML 문서로 래핑
        full_html = self._wrap_with_html(html_body)

        return full_html

    def _wrap_with_html(self, body: str) -> str:
        """
        HTML body를 완전한 HTML 문서로 래핑

        Args:
            body: HTML body 내용

        Returns:
            완전한 HTML 문서 (<!DOCTYPE>, <html>, <head>, <body> 포함)
        """
        # Pygments CSS 생성
        pygments_css = self.formatter.get_style_defs('.highlight')

        # GitHub 스타일 CSS (별도 파일에서 로드 가능하도록 @import 사용)
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* GitHub-style 기본 스타일 */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #c9d1d9;
            background-color: #0d1117;
            padding: 20px;
            margin: 0;
        }}

        /* 헤더 스타일 */
        h1 {{
            font-size: 2em;
            font-weight: 600;
            border-bottom: 1px solid #21262d;
            padding-bottom: 0.3em;
            margin-top: 24px;
            margin-bottom: 16px;
            color: #58a6ff;
        }}

        h2 {{
            font-size: 1.5em;
            font-weight: 600;
            border-bottom: 1px solid #21262d;
            padding-bottom: 0.3em;
            margin-top: 24px;
            margin-bottom: 16px;
            color: #58a6ff;
        }}

        h3 {{
            font-size: 1.25em;
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 16px;
            color: #58a6ff;
        }}

        /* 단락 및 텍스트 */
        p {{
            margin-top: 0;
            margin-bottom: 16px;
        }}

        strong {{
            font-weight: 600;
            color: #c9d1d9;
        }}

        em {{
            font-style: italic;
            color: #8b949e;
        }}

        /* 코드 블록 */
        pre {{
            background-color: #161b22;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
            margin-bottom: 16px;
            border: 1px solid #30363d;
        }}

        code {{
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
            font-size: 85%;
            background-color: rgba(110, 118, 129, 0.4);
            padding: 0.2em 0.4em;
            border-radius: 6px;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
            border-radius: 0;
            font-size: 100%;
        }}

        /* 리스트 */
        ul, ol {{
            margin-top: 0;
            margin-bottom: 16px;
            padding-left: 2em;
        }}

        li {{
            margin-top: 0.25em;
        }}

        li + li {{
            margin-top: 0.25em;
        }}

        /* 표 */
        table {{
            border-collapse: collapse;
            border-spacing: 0;
            width: 100%;
            margin-bottom: 16px;
            overflow: auto;
        }}

        table tr {{
            background-color: #0d1117;
            border-top: 1px solid #21262d;
        }}

        table tr:nth-child(2n) {{
            background-color: #161b22;
        }}

        table th, table td {{
            padding: 6px 13px;
            border: 1px solid #30363d;
        }}

        table th {{
            font-weight: 600;
            background-color: #161b22;
        }}

        /* 구분선 */
        hr {{
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #21262d;
            border: 0;
        }}

        /* 링크 */
        a {{
            color: #58a6ff;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        /* 인용문 */
        blockquote {{
            padding: 0 1em;
            color: #8b949e;
            border-left: 0.25em solid #30363d;
            margin: 0 0 16px 0;
        }}

        /* Pygments 구문 강조 CSS */
        {pygments_css}

        /* Pygments 추가 스타일 조정 */
        .highlight {{
            background-color: #161b22 !important;
            border-radius: 6px;
        }}

        .highlight pre {{
            background-color: transparent;
            border: none;
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
{body}
</body>
</html>"""

        return html

    def get_css(self) -> str:
        """
        Pygments CSS만 반환 (별도 파일로 저장할 때 사용)

        Returns:
            Pygments CSS 문자열
        """
        return self.formatter.get_style_defs('.highlight')


# 사용 예제
if __name__ == "__main__":
    # 테스트 Markdown
    test_markdown = """# C# 코드 리뷰 리포트

**생성 일시**: 2025-01-14 14:30:00
**분석 모델**: phi3:mini
**생성 도구**: C# Code Reviewer v1.0.0

---

## 📊 요약

- **원본 코드**: 4 줄
- **개선 코드**: 7 줄
- **추가된 줄**: +3 줄
- **적용 카테고리**: 2개

---

## 🎯 적용된 리뷰 카테고리

- ✅ **Null 참조 체크**
- ✅ **Exception 처리**

---

## 📝 코드 비교

### Before (원본 코드)

```csharp
public void ProcessData(string data)
{
    var result = data.ToUpper();
    Console.WriteLine(result);
}
```

### After (개선된 코드)

```csharp
public void ProcessData(string data)
{
    if (string.IsNullOrEmpty(data))
        throw new ArgumentNullException(nameof(data));

    var result = data.ToUpper();
    Console.WriteLine(result);
}
```

---

## 🔍 주요 개선 사항

- 🔍 **Null 체크 추가**: 입력 검증으로 NullReferenceException 방지
- 🚫 **명시적 예외 발생**: 잘못된 입력에 대한 명확한 피드백

---

## 📌 참고사항

이 리포트는 AI(Phi-3-mini)가 자동으로 생성한 코드 리뷰 결과입니다.
최종 적용 전에 반드시 개발자가 검토해야 합니다.

**생성 도구**: [C# Code Reviewer](https://github.com/daehyub71/csharp-code-reviewer)
**LLM**: Microsoft Phi-3-mini (3.8B parameters)
"""

    # 렌더러 생성
    renderer = MarkdownRenderer(theme="monokai")

    # HTML 변환
    html = renderer.render(test_markdown)

    # 결과 출력
    print("=" * 80)
    print("Markdown → HTML 변환 테스트")
    print("=" * 80)
    print(html)
    print("=" * 80)
    print(f"HTML 길이: {len(html)} 글자")
    print("=" * 80)

    # 파일로 저장 (브라우저에서 확인 가능)
    with open("test_output.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\n✅ 테스트 완료!")
    print("📄 test_output.html 파일을 브라우저로 열어서 확인하세요.")
