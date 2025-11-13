"""
Mermaid 다이어그램 → PNG 변환기

Markdown 내 Mermaid 코드 블록을 PNG 이미지로 변환하고
Base64로 인코딩하여 Markdown에 임베딩합니다.
"""

import re
import subprocess
import tempfile
import base64
from pathlib import Path
from typing import Optional, Tuple
import shutil
import logging

# 로깅 설정
logger = logging.getLogger(__name__)


class DiagramConverter:
    """
    Mermaid 다이어그램 변환기

    Mermaid CLI (mmdc)를 사용하여 다이어그램을 PNG로 변환합니다.
    """

    def __init__(self, timeout: int = 10):
        """
        DiagramConverter 초기화

        Args:
            timeout: mmdc 명령어 실행 타임아웃 (초 단위, 기본값: 10)
        """
        self.timeout = timeout

        # mmdc 명령어 존재 확인
        self.mmdc_path = shutil.which("mmdc")
        if not self.mmdc_path:
            logger.warning("mmdc 명령어를 찾을 수 없습니다. Mermaid 다이어그램 변환이 비활성화됩니다.")
            logger.warning("설치: npm install -g @mermaid-js/mermaid-cli")

    def is_available(self) -> bool:
        """
        Mermaid CLI 사용 가능 여부 확인

        Returns:
            True if mmdc is available, False otherwise
        """
        return self.mmdc_path is not None

    def convert_markdown(self, markdown_text: str) -> str:
        """
        Markdown 내 모든 Mermaid 코드 블록을 PNG 이미지로 변환

        Args:
            markdown_text: Mermaid 코드 블록이 포함된 Markdown 텍스트

        Returns:
            Mermaid 블록이 이미지로 변환된 Markdown 텍스트
        """
        if not self.is_available():
            # mmdc가 없으면 원본 반환
            logger.warning("mmdc를 사용할 수 없어 Mermaid 변환을 건너뜁니다.")
            return markdown_text

        # Mermaid 코드 블록 패턴
        # ```mermaid
        # graph TD
        #   A --> B
        # ```
        pattern = r'```mermaid\s*\n(.*?)\n```'

        def replace_mermaid_block(match):
            """각 Mermaid 블록을 이미지로 변환"""
            mermaid_code = match.group(1)

            try:
                # PNG 이미지 생성
                png_data = self._generate_png(mermaid_code)

                if png_data:
                    # Base64로 인코딩
                    base64_img = base64.b64encode(png_data).decode('utf-8')

                    # HTML 이미지 태그로 변환
                    img_tag = f'<img src="data:image/png;base64,{base64_img}" alt="Mermaid Diagram" style="max-width: 100%; height: auto; background-color: white; padding: 10px; border-radius: 6px;" />'

                    return img_tag
                else:
                    # 변환 실패 시 원본 코드 블록 유지 (폴백)
                    logger.warning("Mermaid 블록 변환 실패, 원본 유지")
                    return match.group(0)

            except Exception as e:
                logger.error(f"Mermaid 변환 중 오류 발생: {e}")
                # 에러 발생 시 원본 유지
                return match.group(0)

        # 모든 Mermaid 블록 변환
        converted_markdown = re.sub(
            pattern,
            replace_mermaid_block,
            markdown_text,
            flags=re.DOTALL
        )

        return converted_markdown

    def _generate_png(self, mermaid_code: str) -> Optional[bytes]:
        """
        Mermaid 코드를 PNG 이미지로 변환

        Args:
            mermaid_code: Mermaid 다이어그램 코드

        Returns:
            PNG 이미지 바이트 데이터 (실패 시 None)
        """
        # 임시 디렉토리 생성
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # 임시 .mmd 파일 생성
            mmd_file = tmp_path / "diagram.mmd"
            png_file = tmp_path / "diagram.png"

            try:
                # Mermaid 코드를 파일로 저장
                with open(mmd_file, 'w', encoding='utf-8') as f:
                    f.write(mermaid_code)

                # mmdc 명령어 실행
                # -i: 입력 파일
                # -o: 출력 파일
                # -b: 배경색 (투명 또는 흰색)
                # -t: 테마 (default, dark, forest, neutral)
                cmd = [
                    self.mmdc_path,
                    '-i', str(mmd_file),
                    '-o', str(png_file),
                    '-b', 'white',        # 흰색 배경
                    '-t', 'default',      # 기본 테마
                    '--quiet'             # 조용한 모드
                ]

                # subprocess로 실행 (타임아웃 설정)
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False  # 에러 발생 시 예외 발생하지 않음
                )

                # 실행 결과 확인
                if result.returncode != 0:
                    logger.error(f"mmdc 실행 실패 (exit code {result.returncode})")
                    logger.error(f"stderr: {result.stderr}")
                    return None

                # PNG 파일 존재 확인
                if not png_file.exists():
                    logger.error("PNG 파일이 생성되지 않았습니다.")
                    return None

                # PNG 파일 읽기
                with open(png_file, 'rb') as f:
                    png_data = f.read()

                logger.info(f"Mermaid 다이어그램 변환 성공 ({len(png_data)} bytes)")
                return png_data

            except subprocess.TimeoutExpired:
                logger.error(f"mmdc 실행 타임아웃 ({self.timeout}초 초과)")
                return None

            except Exception as e:
                logger.error(f"PNG 생성 중 오류: {e}")
                return None

    def extract_mermaid_blocks(self, markdown_text: str) -> list[str]:
        """
        Markdown에서 모든 Mermaid 코드 블록 추출

        Args:
            markdown_text: Markdown 텍스트

        Returns:
            Mermaid 코드 블록 리스트
        """
        pattern = r'```mermaid\s*\n(.*?)\n```'
        matches = re.findall(pattern, markdown_text, flags=re.DOTALL)
        return matches


# 사용 예제
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # 테스트 Markdown (Mermaid 다이어그램 포함)
    test_markdown = """# 코드 리뷰 프로세스

## 프로세스 플로우

```mermaid
graph TD
    A[코드 입력] --> B{카테고리 선택}
    B --> C[PromptBuilder]
    C --> D[LLM 분석]
    D --> E[코드 개선]
    E --> F[ReportGenerator]
    F --> G[Markdown 리포트]
    G --> H[HTML 렌더링]
    H --> I[결과 표시]
```

## 에이전트 구조

```mermaid
graph LR
    User[사용자] --> UI[MainWindow]
    UI --> PB[PromptBuilder]
    UI --> OC[OllamaClient]
    OC --> LLM[Phi-3-mini]
    LLM --> RG[ReportGenerator]
    RG --> RP[ResultPanel]
    RP --> User
```

## 테스트 완료
"""

    print("=" * 80)
    print("Mermaid → PNG 변환 테스트")
    print("=" * 80)

    # DiagramConverter 생성
    converter = DiagramConverter(timeout=30)

    # 사용 가능 여부 확인
    if converter.is_available():
        print(f"✅ mmdc 명령어 발견: {converter.mmdc_path}")
    else:
        print("❌ mmdc를 찾을 수 없습니다.")
        print("설치: npm install -g @mermaid-js/mermaid-cli")
        exit(1)

    # Mermaid 블록 추출
    print(f"\n📋 Mermaid 블록 추출 중...")
    blocks = converter.extract_mermaid_blocks(test_markdown)
    print(f"✅ {len(blocks)}개의 Mermaid 블록 발견")

    for i, block in enumerate(blocks, 1):
        print(f"\n블록 {i}:")
        print("-" * 80)
        print(block[:100] + "..." if len(block) > 100 else block)
        print("-" * 80)

    # Markdown 변환
    print(f"\n🎨 Markdown 변환 중...")
    converted = converter.convert_markdown(test_markdown)

    # 결과 확인
    print("\n📊 변환 결과:")
    print(f"원본 길이: {len(test_markdown)} 글자")
    print(f"변환 후 길이: {len(converted)} 글자")
    print(f"이미지 태그 개수: {converted.count('<img ')}")

    # HTML 파일로 저장 (시각적 확인용)
    output_file = "test_mermaid_output.html"

    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1, h2 {{
            color: #333;
        }}
        img {{
            display: block;
            margin: 20px auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
{converted}
</body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"\n💾 결과 저장: {output_file}")
    print("   (브라우저로 열어서 다이어그램 확인)")

    print("\n" + "=" * 80)
    print("✅ 테스트 완료!")
    print("=" * 80)
