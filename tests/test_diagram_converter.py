"""
Mermaid 다이어그램 변환 테스트

DiagramConverter의 Mermaid → PNG 변환 기능을 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.diagram_converter import DiagramConverter
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def test_converter_availability():
    """DiagramConverter 사용 가능 여부 테스트"""

    print("=" * 80)
    print("DiagramConverter 사용 가능 여부 테스트")
    print("=" * 80)

    converter = DiagramConverter()

    if converter.is_available():
        print(f"✅ mmdc 명령어 발견: {converter.mmdc_path}")
        return True
    else:
        print("❌ mmdc를 찾을 수 없습니다.")
        print("설치: npm install -g @mermaid-js/mermaid-cli")
        return False


def test_mermaid_extraction():
    """Mermaid 코드 블록 추출 테스트"""

    print("\n\n" + "=" * 80)
    print("Mermaid 블록 추출 테스트")
    print("=" * 80)

    markdown = """# 테스트

```mermaid
graph TD
    A --> B
```

일반 텍스트

```python
print("hello")
```

```mermaid
sequenceDiagram
    Alice->>Bob: Hello
```
"""

    converter = DiagramConverter()
    blocks = converter.extract_mermaid_blocks(markdown)

    print(f"\n📋 추출된 블록 수: {len(blocks)}")

    # 검증
    checks = {
        "2개의 블록 추출": len(blocks) == 2,
        "첫 번째 블록에 'graph TD' 포함": "graph TD" in blocks[0],
        "두 번째 블록에 'sequenceDiagram' 포함": "sequenceDiagram" in blocks[1],
    }

    print("\n📊 검증 결과:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    return all(checks.values())


def test_simple_flowchart():
    """간단한 플로우차트 변환 테스트"""

    print("\n\n" + "=" * 80)
    print("간단한 플로우차트 변환 테스트")
    print("=" * 80)

    markdown = """# 간단한 플로우차트

```mermaid
graph TD
    Start[시작] --> Process[처리]
    Process --> End[종료]
```
"""

    converter = DiagramConverter(timeout=30)

    if not converter.is_available():
        print("⚠️ mmdc를 사용할 수 없어 테스트를 건너뜁니다.")
        return False

    print("\n🎨 변환 중...")
    converted = converter.convert_markdown(markdown)

    # 검증
    checks = {
        "원본보다 긴 텍스트": len(converted) > len(markdown),
        "이미지 태그 포함": "<img " in converted,
        "Base64 데이터 포함": "data:image/png;base64," in converted,
        "원본 코드 블록 제거됨": "```mermaid" not in converted,
    }

    print("\n📊 검증 결과:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    print(f"\n📏 원본 길이: {len(markdown)} 글자")
    print(f"📏 변환 후 길이: {len(converted)} 글자")

    all_passed = all(checks.values())

    if all_passed:
        # HTML로 저장
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
{converted}
</body>
</html>"""

        with open("test_simple_flowchart.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("\n💾 결과 저장: test_simple_flowchart.html")

    return all_passed


def test_complex_diagram():
    """복잡한 다이어그램 변환 테스트"""

    print("\n\n" + "=" * 80)
    print("복잡한 다이어그램 변환 테스트")
    print("=" * 80)

    markdown = """# 복잡한 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant User
    participant MainWindow
    participant PromptBuilder
    participant OllamaClient
    participant LLM
    participant ReportGenerator

    User->>MainWindow: 코드 입력
    User->>MainWindow: 카테고리 선택
    User->>MainWindow: AI 분석 클릭

    MainWindow->>PromptBuilder: build_review_prompt()
    PromptBuilder-->>MainWindow: 프롬프트 반환

    MainWindow->>OllamaClient: analyze_code(prompt)
    OllamaClient->>LLM: HTTP POST
    LLM-->>OllamaClient: 개선된 코드
    OllamaClient-->>MainWindow: 분석 결과

    MainWindow->>ReportGenerator: generate_report()
    ReportGenerator-->>MainWindow: Markdown 리포트

    MainWindow->>User: 결과 표시
```

## 클래스 다이어그램

```mermaid
classDiagram
    class MainWindow {
        +QPlainTextEdit before_editor
        +QPlainTextEdit after_editor
        +ResultPanel result_panel
        +_on_analyze()
        +_on_save()
    }

    class PromptBuilder {
        +build_review_prompt()
        +estimate_tokens()
    }

    class OllamaClient {
        +analyze_code()
        +test_connection()
    }

    class ReportGenerator {
        +generate_report()
        +save_report()
    }

    MainWindow --> PromptBuilder
    MainWindow --> OllamaClient
    MainWindow --> ReportGenerator
```
"""

    converter = DiagramConverter(timeout=30)

    if not converter.is_available():
        print("⚠️ mmdc를 사용할 수 없어 테스트를 건너뜁니다.")
        return False

    print("\n🎨 변환 중... (복잡한 다이어그램은 시간이 걸릴 수 있습니다)")
    converted = converter.convert_markdown(markdown)

    # 검증
    checks = {
        "2개의 이미지 생성": converted.count("<img ") == 2,
        "원본 코드 블록 모두 제거": "```mermaid" not in converted,
        "Base64 데이터 2개 포함": converted.count("data:image/png;base64,") == 2,
    }

    print("\n📊 검증 결과:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    print(f"\n📏 원본 길이: {len(markdown)} 글자")
    print(f"📏 변환 후 길이: {len(converted)} 글자")

    all_passed = all(checks.values())

    if all_passed:
        # HTML로 저장
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background-color: #f5f5f5; }}
        h1, h2 {{ color: #333; }}
        img {{ display: block; margin: 20px auto; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
{converted}
</body>
</html>"""

        with open("test_complex_diagram.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("\n💾 결과 저장: test_complex_diagram.html")

    return all_passed


def test_error_handling():
    """에러 처리 테스트"""

    print("\n\n" + "=" * 80)
    print("에러 처리 테스트")
    print("=" * 80)

    # 잘못된 Mermaid 코드
    markdown = """# 에러 테스트

```mermaid
graph TD
    INVALID SYNTAX HERE
```
"""

    converter = DiagramConverter(timeout=10)

    if not converter.is_available():
        print("⚠️ mmdc를 사용할 수 없어 테스트를 건너뜁니다.")
        return False

    print("\n🎨 변환 중... (에러가 예상됨)")
    converted = converter.convert_markdown(markdown)

    # 검증: 에러 발생 시 원본 유지
    checks = {
        "원본 코드 블록 유지됨": "```mermaid" in converted,
        "프로그램이 중단되지 않음": True,  # 여기까지 도달했다면 성공
    }

    print("\n📊 검증 결과:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    print("\n원본 유지 (폴백):")
    print(converted[:200])

    return all(checks.values())


def test_no_mermaid_blocks():
    """Mermaid 블록이 없는 경우 테스트"""

    print("\n\n" + "=" * 80)
    print("Mermaid 블록 없음 테스트")
    print("=" * 80)

    markdown = """# 일반 Markdown

일반 텍스트입니다.

```python
print("Hello")
```

코드 블록은 있지만 Mermaid는 없습니다.
"""

    converter = DiagramConverter()
    converted = converter.convert_markdown(markdown)

    # 검증
    checks = {
        "원본과 동일": converted == markdown,
        "변경 없음": len(converted) == len(markdown),
    }

    print("\n📊 검증 결과:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    return all(checks.values())


if __name__ == "__main__":
    print("\n🚀 Mermaid 다이어그램 변환 종합 테스트 시작\n")

    # 테스트 실행
    result1 = test_converter_availability()

    if not result1:
        print("\n❌ mmdc가 설치되지 않아 테스트를 중단합니다.")
        print("설치: npm install -g @mermaid-js/mermaid-cli")
        exit(1)

    result2 = test_mermaid_extraction()
    result3 = test_simple_flowchart()
    result4 = test_complex_diagram()
    result5 = test_error_handling()
    result6 = test_no_mermaid_blocks()

    # 최종 결과
    print("\n\n" + "=" * 80)
    print("🎬 최종 결과")
    print("=" * 80)
    print(f"사용 가능 여부: {'✅ 통과' if result1 else '❌ 실패'}")
    print(f"블록 추출 테스트: {'✅ 통과' if result2 else '❌ 실패'}")
    print(f"간단한 플로우차트: {'✅ 통과' if result3 else '❌ 실패'}")
    print(f"복잡한 다이어그램: {'✅ 통과' if result4 else '❌ 실패'}")
    print(f"에러 처리: {'✅ 통과' if result5 else '❌ 실패'}")
    print(f"Mermaid 없음: {'✅ 통과' if result6 else '❌ 실패'}")

    if all([result1, result2, result3, result4, result5, result6]):
        print("\n🎉 모든 테스트 통과!")
        print("Mermaid → PNG 변환이 정상적으로 작동합니다.")
    else:
        print("\n⚠️ 일부 테스트 실패")

    print("=" * 80)
