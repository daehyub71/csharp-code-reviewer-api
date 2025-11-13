"""
결과 패널 UI 컴포넌트

Markdown 리포트를 HTML로 렌더링하여 표시하는 패널입니다.
QTextBrowser를 사용하여 구문 강조된 코드를 포함한
풍부한 포맷의 리포트를 보여줍니다.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QToolBar, QMessageBox
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QFont, QIcon, QTextCursor
from pathlib import Path
from typing import Optional

from app.utils.markdown_renderer import MarkdownRenderer


class ResultPanel(QWidget):
    """
    리포트 결과 패널

    Markdown → HTML로 렌더링된 코드 리뷰 리포트를 표시합니다.
    Pygments를 사용하여 C# 코드 블록에 구문 강조가 적용됩니다.
    """

    def __init__(self, parent=None):
        """
        ResultPanel 초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)

        # Markdown 렌더러 초기화 (Monokai 테마)
        self.renderer = MarkdownRenderer(theme="monokai")

        # 현재 표시 중인 Markdown 텍스트
        self.current_markdown: Optional[str] = None

        # 스크롤 위치 저장
        self.scroll_position = 0

        # UI 초기화
        self._init_ui()

    def _init_ui(self):
        """UI 구성요소 초기화"""

        # 레이아웃 생성
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 툴바 생성
        self.toolbar = self._create_toolbar()
        layout.addWidget(self.toolbar)

        # QTextBrowser 생성 (HTML 렌더링용)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)  # 외부 링크 클릭 허용
        self.browser.setOpenLinks(True)

        # 폰트 설정
        font = QFont("Consolas", 10)
        self.browser.setFont(font)

        # 배경색 설정 (GitHub Dark)
        self.browser.setStyleSheet("""
            QTextBrowser {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
            }
        """)

        layout.addWidget(self.browser)

        # 초기 메시지 표시
        self._show_placeholder()

    def _create_toolbar(self) -> QToolBar:
        """
        툴바 생성

        Returns:
            QToolBar: 생성된 툴바
        """
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # 새로고침 액션
        refresh_action = QAction("🔄 새로고침", self)
        refresh_action.setToolTip("리포트 새로고침")
        refresh_action.triggered.connect(self._on_refresh)
        toolbar.addAction(refresh_action)

        toolbar.addSeparator()

        # 확대 액션
        zoom_in_action = QAction("🔍+ 확대", self)
        zoom_in_action.setToolTip("글자 크기 확대")
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self._on_zoom_in)
        toolbar.addAction(zoom_in_action)

        # 축소 액션
        zoom_out_action = QAction("🔍- 축소", self)
        zoom_out_action.setToolTip("글자 크기 축소")
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self._on_zoom_out)
        toolbar.addAction(zoom_out_action)

        # 원래 크기 액션
        zoom_reset_action = QAction("↺ 원래 크기", self)
        zoom_reset_action.setToolTip("글자 크기 원래대로")
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self._on_zoom_reset)
        toolbar.addAction(zoom_reset_action)

        toolbar.addSeparator()

        # 맨 위로 액션
        top_action = QAction("⬆ 맨 위로", self)
        top_action.setToolTip("문서 맨 위로 이동")
        top_action.setShortcut("Home")
        top_action.triggered.connect(self._on_scroll_to_top)
        toolbar.addAction(top_action)

        # 맨 아래로 액션
        bottom_action = QAction("⬇ 맨 아래로", self)
        bottom_action.setToolTip("문서 맨 아래로 이동")
        bottom_action.setShortcut("End")
        bottom_action.triggered.connect(self._on_scroll_to_bottom)
        toolbar.addAction(bottom_action)

        return toolbar

    def set_markdown(self, markdown_text: str):
        """
        Markdown 텍스트를 설정하고 HTML로 렌더링

        Args:
            markdown_text: Markdown 형식의 텍스트
        """
        self.current_markdown = markdown_text

        # 현재 스크롤 위치 저장
        scrollbar = self.browser.verticalScrollBar()
        self.scroll_position = scrollbar.value()

        # Markdown → HTML 변환
        html = self.renderer.render(markdown_text)

        # HTML 설정
        self.browser.setHtml(html)

        # 스크롤 위치 복원 (내용이 변경되지 않은 경우)
        scrollbar.setValue(self.scroll_position)

    def clear(self):
        """리포트 내용 지우기"""
        self.current_markdown = None
        self._show_placeholder()

    def _show_placeholder(self):
        """플레이스홀더 메시지 표시"""
        placeholder_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #8b949e;
            padding: 40px;
            text-align: center;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        h1 {
            font-size: 24px;
            color: #58a6ff;
            margin-bottom: 16px;
        }
        p {
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 12px;
        }
        .icon {
            font-size: 64px;
            margin-bottom: 24px;
        }
        .steps {
            text-align: left;
            margin-top: 32px;
            padding: 16px;
            background-color: #161b22;
            border-radius: 6px;
            border: 1px solid #30363d;
        }
        .steps li {
            margin: 8px 0;
            color: #c9d1d9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">📄</div>
        <h1>코드 리뷰 리포트</h1>
        <p>AI 코드 분석 결과가 여기에 표시됩니다.</p>

        <div class="steps">
            <strong>사용 방법:</strong>
            <ol>
                <li>왼쪽에 원본 C# 코드를 입력하세요</li>
                <li>검토할 카테고리를 선택하세요</li>
                <li>"🤖 AI 분석" 버튼을 클릭하세요</li>
                <li>개선된 코드와 상세 리포트를 확인하세요</li>
                <li>"💾 저장" 버튼으로 리포트를 저장하세요</li>
            </ol>
        </div>
    </div>
</body>
</html>"""
        self.browser.setHtml(placeholder_html)

    # 액션 핸들러

    def _on_refresh(self):
        """새로고침 핸들러"""
        if self.current_markdown:
            self.set_markdown(self.current_markdown)

    def _on_zoom_in(self):
        """확대 핸들러"""
        self.browser.zoomIn(1)

    def _on_zoom_out(self):
        """축소 핸들러"""
        self.browser.zoomOut(1)

    def _on_zoom_reset(self):
        """원래 크기 핸들러"""
        self.browser.setZoomFactor(1.0)

    def _on_scroll_to_top(self):
        """맨 위로 스크롤"""
        self.browser.moveCursor(QTextCursor.MoveOperation.Start)

    def _on_scroll_to_bottom(self):
        """맨 아래로 스크롤"""
        self.browser.moveCursor(QTextCursor.MoveOperation.End)


# 사용 예제
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 테스트용 Markdown
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

    # ResultPanel 생성
    panel = ResultPanel()
    panel.set_markdown(test_markdown)
    panel.setWindowTitle("ResultPanel 테스트")
    panel.resize(800, 600)
    panel.show()

    sys.exit(app.exec())
