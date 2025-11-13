"""
Markdown 파일 파서

리뷰 카테고리 Markdown 파일을 파싱하여 구조화된 데이터로 변환합니다.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ReviewCategoryParser:
    """
    리뷰 카테고리 Markdown 파일 파서

    Markdown 파일에서 카테고리 정보, 규칙, 예제를 추출합니다.
    """

    def __init__(self, markdown_path: Path):
        """
        파서 초기화

        Args:
            markdown_path: Markdown 파일 경로
        """
        self.markdown_path = markdown_path
        self.content = self._read_file()

    def _read_file(self) -> str:
        """파일 읽기"""
        with open(self.markdown_path, 'r', encoding='utf-8') as f:
            return f.read()

    def parse(self) -> Dict:
        """
        Markdown 파일을 파싱하여 딕셔너리로 반환

        Returns:
            {
                'name': str,  # 카테고리 이름
                'description': str,  # 설명
                'rules': List[str],  # 규칙 리스트
                'examples': List[Dict]  # Before/After 예제 리스트
            }
        """
        result = {
            'name': self._extract_title(),
            'description': self._extract_description(),
            'rules': self._extract_rules(),
            'examples': self._extract_examples()
        }

        return result

    def _extract_title(self) -> str:
        """# 제목 추출"""
        match = re.search(r'^# (.+)$', self.content, re.MULTILINE)
        return match.group(1).strip() if match else ""

    def _extract_description(self) -> str:
        """## 설명 섹션 추출"""
        # "## 설명" 다음부터 다음 "##"까지
        pattern = r'## 설명\s*\n(.*?)\n##'
        match = re.search(pattern, self.content, re.DOTALL)

        if match:
            description = match.group(1).strip()
            # 여러 줄을 하나의 문장으로 합치기
            description = ' '.join(line.strip() for line in description.split('\n') if line.strip())
            return description

        return ""

    def _extract_rules(self) -> List[str]:
        """## 규칙 섹션에서 규칙 리스트 추출"""
        # "## 규칙" 다음부터 다음 "##"까지
        pattern = r'## 규칙\s*\n(.*?)\n##'
        match = re.search(pattern, self.content, re.DOTALL)

        if not match:
            return []

        rules_section = match.group(1).strip()

        # "- "로 시작하는 줄들 추출
        rules = []
        for line in rules_section.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                rule = line[2:].strip()  # "- " 제거
                # Markdown 강조 제거 (**, `, 등)
                rule = re.sub(r'`([^`]+)`', r'\1', rule)  # `text` → text
                rule = re.sub(r'\*\*([^*]+)\*\*', r'\1', rule)  # **text** → text
                rules.append(rule)

        return rules

    def _extract_examples(self) -> List[Dict]:
        """Before/After 예제 추출"""
        examples = []

        # "## Before 예제"와 "## After 예제" 패턴 찾기
        # 여러 개의 케이스가 있을 수 있음 (code_documentation.md의 경우)

        # 모든 "### Before" ~ "### After" 또는 "## Before 예제" ~ "## After 예제" 쌍 찾기
        pattern = r'(?:###|##)\s*Before(?:\s+예제)?\s*\n```csharp\s*\n(.*?)\n```\s*\n(?:###|##)\s*After(?:\s+예제)?\s*\n```csharp\s*\n(.*?)\n```'

        matches = re.findall(pattern, self.content, re.DOTALL)

        for before_code, after_code in matches:
            examples.append({
                'before': before_code.strip(),
                'after': after_code.strip()
            })

        return examples

    def _extract_code_block(self, text: str) -> str:
        """코드 블록에서 순수 코드만 추출"""
        # ```csharp ... ``` 패턴
        pattern = r'```csharp\s*\n(.*?)\n```'
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()


class CategoryLoader:
    """
    리뷰 카테고리 Markdown 파일 로더

    지정된 디렉토리에서 모든 카테고리 파일을 로드합니다.
    """

    def __init__(self, categories_dir: Path):
        """
        로더 초기화

        Args:
            categories_dir: 카테고리 Markdown 파일들이 있는 디렉토리
        """
        self.categories_dir = Path(categories_dir)

    def load_all(self) -> Dict[str, Dict]:
        """
        모든 카테고리 파일 로드

        Returns:
            {
                'null_reference': {
                    'name': 'Null 참조 체크',
                    'description': '...',
                    'rules': [...],
                    'examples': [...]
                },
                ...
            }
        """
        categories = {}

        # 디렉토리의 모든 .md 파일 로드
        if not self.categories_dir.exists():
            raise FileNotFoundError(f"카테고리 디렉토리를 찾을 수 없습니다: {self.categories_dir}")

        for md_file in self.categories_dir.glob('*.md'):
            # 파일명에서 카테고리 키 추출 (null_reference.md → null_reference)
            category_key = md_file.stem

            # 파싱
            parser = ReviewCategoryParser(md_file)
            category_data = parser.parse()

            categories[category_key] = category_data

        return categories

    def load_category(self, category_key: str) -> Dict:
        """
        특정 카테고리 파일 로드

        Args:
            category_key: 카테고리 키 (예: 'null_reference')

        Returns:
            카테고리 데이터 딕셔너리
        """
        md_file = self.categories_dir / f"{category_key}.md"

        if not md_file.exists():
            raise FileNotFoundError(f"카테고리 파일을 찾을 수 없습니다: {md_file}")

        parser = ReviewCategoryParser(md_file)
        return parser.parse()


# 사용 예제
if __name__ == "__main__":
    from pathlib import Path

    # 프로젝트 루트 찾기
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    categories_dir = project_root / "resources" / "templates" / "review_categories"

    print("=" * 80)
    print("Markdown 파서 테스트")
    print("=" * 80)

    # 모든 카테고리 로드
    loader = CategoryLoader(categories_dir)
    categories = loader.load_all()

    print(f"\n로드된 카테고리 수: {len(categories)}\n")

    # 각 카테고리 정보 출력
    for key, data in categories.items():
        print(f"📋 {key}")
        print(f"   이름: {data['name']}")
        print(f"   설명: {data['description'][:100]}...")
        print(f"   규칙 수: {len(data['rules'])}")
        print(f"   예제 수: {len(data['examples'])}")

        if data['rules']:
            print(f"   첫 번째 규칙: {data['rules'][0]}")

        if data['examples']:
            example = data['examples'][0]
            print(f"   첫 번째 예제 Before: {len(example['before'])} 글자")
            print(f"   첫 번째 예제 After: {len(example['after'])} 글자")

        print()

    print("=" * 80)
    print("✅ 파싱 완료!")
    print("=" * 80)
