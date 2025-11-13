"""
ReportGenerator 테스트

Markdown 리포트 생성 및 저장 기능을 테스트합니다.
"""

import sys
from pathlib import Path
import tempfile
import os

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.report_generator import ReportGenerator


def test_report_generation():
    """리포트 생성 테스트"""

    print("=" * 80)
    print("ReportGenerator 테스트")
    print("=" * 80)

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

    # ReportGenerator 생성
    generator = ReportGenerator()

    # 리포트 생성
    print("\n📋 리포트 생성 중...")
    report = generator.generate_report(
        original_code=original_code,
        improved_code=improved_code,
        categories=categories,
        model_name="phi3:mini"
    )

    print("✅ 리포트 생성 완료")

    # 리포트 내용 표시
    print("\n" + "=" * 80)
    print("생성된 리포트:")
    print("=" * 80)
    print(report)
    print("=" * 80)

    # 검증
    checks = {
        "헤더 포함": "# C# 코드 리뷰 리포트" in report,
        "요약 섹션": "## 📊 요약" in report,
        "카테고리 섹션": "## 🎯 적용된 리뷰 카테고리" in report,
        "코드 비교 섹션": "## 📝 코드 비교" in report,
        "개선 사항 섹션": "## 🔍 주요 개선 사항" in report,
        "Before 코드 포함": original_code in report,
        "After 코드 추출 성공": "ArgumentNullException" in report,
        "모델 정보 포함": "phi3:mini" in report
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


def test_file_save():
    """파일 저장 테스트"""

    print("\n\n" + "=" * 80)
    print("파일 저장 테스트")
    print("=" * 80)

    # 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as tmpdir:
        # 테스트 데이터
        original_code = "public class Test { }"
        improved_code = "public class Test { /* improved */ }"
        categories = ['naming_convention']

        # ReportGenerator 생성
        generator = ReportGenerator()

        # 리포트 생성
        report = generator.generate_report(
            original_code=original_code,
            improved_code=improved_code,
            categories=categories
        )

        # 파일 저장
        output_path = Path(tmpdir) / "test_report.md"
        print(f"\n💾 파일 저장 중: {output_path}")

        generator.save_report(report, str(output_path))

        # 검증
        if output_path.exists():
            print("✅ 파일 생성 확인")

            # 파일 내용 확인
            with open(output_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()

            if saved_content == report:
                print("✅ 파일 내용 일치")
                return True
            else:
                print("❌ 파일 내용 불일치")
                return False
        else:
            print("❌ 파일 생성 실패")
            return False


def test_filename_generation():
    """파일명 자동 생성 테스트"""

    print("\n\n" + "=" * 80)
    print("파일명 생성 테스트")
    print("=" * 80)

    generator = ReportGenerator()

    # 파일명 생성
    filename = generator.generate_filename()

    print(f"\n생성된 파일명: {filename}")

    # 검증
    checks = {
        "접두사 확인": filename.startswith("code_review_"),
        "확장자 확인": filename.endswith(".md"),
        "날짜 포함": len(filename.split('_')) >= 3,
        "타임스탬프 포함": any(char.isdigit() for char in filename)
    }

    print("\n📊 검증 결과:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    return all(checks.values())


def test_code_extraction():
    """LLM 응답에서 코드 추출 테스트"""

    print("\n\n" + "=" * 80)
    print("코드 추출 테스트")
    print("=" * 80)

    generator = ReportGenerator()

    # 테스트 케이스 1: 마크다운 코드 블록
    response1 = """```csharp
public class Test
{
    // Test
}
```

분석: 테스트 클래스입니다."""

    extracted1 = generator._extract_code_from_response(response1)
    print(f"\n케이스 1 (마크다운 블록):")
    print(f"입력 길이: {len(response1)} 글자")
    print(f"추출 결과: {len(extracted1)} 글자")
    print(f"추출된 코드:\n{extracted1}")

    test1_pass = "public class Test" in extracted1 and "분석:" not in extracted1

    # 테스트 케이스 2: 코드 블록 없음
    response2 = """public class Test
{
    // Test
}"""

    extracted2 = generator._extract_code_from_response(response2)
    print(f"\n케이스 2 (순수 코드):")
    print(f"입력 길이: {len(response2)} 글자")
    print(f"추출 결과: {len(extracted2)} 글자")

    test2_pass = len(extracted2) > 0

    # 결과
    print("\n📊 검증 결과:")
    print(f"{'✅' if test1_pass else '❌'} 마크다운 블록 추출")
    print(f"{'✅' if test2_pass else '❌'} 순수 코드 처리")

    return test1_pass and test2_pass


if __name__ == "__main__":
    print("\n🚀 ReportGenerator 종합 테스트 시작\n")

    # 테스트 실행
    result1 = test_report_generation()
    result2 = test_file_save()
    result3 = test_filename_generation()
    result4 = test_code_extraction()

    # 최종 결과
    print("\n\n" + "=" * 80)
    print("🎬 최종 결과")
    print("=" * 80)
    print(f"리포트 생성: {'✅ 통과' if result1 else '❌ 실패'}")
    print(f"파일 저장: {'✅ 통과' if result2 else '❌ 실패'}")
    print(f"파일명 생성: {'✅ 통과' if result3 else '❌ 실패'}")
    print(f"코드 추출: {'✅ 통과' if result4 else '❌ 실패'}")

    if all([result1, result2, result3, result4]):
        print("\n🎉 모든 테스트 통과!")
        print("ReportGenerator가 정상적으로 작동합니다.")
    else:
        print("\n⚠️ 일부 테스트 실패")

    print("=" * 80)
