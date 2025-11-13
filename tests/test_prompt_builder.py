"""
PromptBuilder 테스트

샘플 C# 코드 5개로 프롬프트 생성을 테스트합니다.
토큰 수가 목표인 1500개 이하인지 확인합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.prompt_builder import PromptBuilder, ReviewCategory, OutputFormat


# 샘플 코드 5개
SAMPLE_CODES = [
    {
        "name": "Sample 1: 간단한 데이터 처리",
        "code": """public class DataProcessor
{
    public void ProcessData(string data)
    {
        var result = data.ToUpper();
        Console.WriteLine(result);
    }
}""",
        "categories": [ReviewCategory.NULL_REFERENCE]
    },
    {
        "name": "Sample 2: 파일 읽기",
        "code": """public class FileReader
{
    public string ReadFile(string path)
    {
        StreamReader reader = new StreamReader(path);
        string content = reader.ReadToEnd();
        return content;
    }
}""",
        "categories": [
            ReviewCategory.RESOURCE_MANAGEMENT,
            ReviewCategory.EXCEPTION_HANDLING
        ]
    },
    {
        "name": "Sample 3: 데이터베이스 연결",
        "code": """public class DatabaseManager
{
    private string connectionString;

    public void ExecuteQuery(string query)
    {
        SqlConnection conn = new SqlConnection(connectionString);
        conn.Open();
        SqlCommand cmd = new SqlCommand(query, conn);
        cmd.ExecuteNonQuery();
    }
}""",
        "categories": [
            ReviewCategory.RESOURCE_MANAGEMENT,
            ReviewCategory.SECURITY,
            ReviewCategory.EXCEPTION_HANDLING
        ]
    },
    {
        "name": "Sample 4: 데이터 변환",
        "code": """public class DataConverter
{
    public string ConvertToJson(List<User> users)
    {
        string json = "";
        foreach (var user in users)
        {
            json += "{\"name\":\"" + user.Name + "\",\"age\":" + user.Age + "},";
        }
        return json;
    }
}""",
        "categories": [
            ReviewCategory.PERFORMANCE,
            ReviewCategory.NAMING_CONVENTION
        ]
    },
    {
        "name": "Sample 5: 사용자 검증",
        "code": """public class UserValidator
{
    public bool validate(string username, string pwd)
    {
        if (username.Length > 0 && pwd.Length > 0)
        {
            return true;
        }
        return false;
    }
}""",
        "categories": [
            ReviewCategory.NAMING_CONVENTION,
            ReviewCategory.SECURITY,
            ReviewCategory.NULL_REFERENCE
        ]
    }
]


def test_all_samples():
    """모든 샘플 코드 테스트"""
    builder = PromptBuilder()

    print("=" * 80)
    print("PromptBuilder 종합 테스트")
    print("=" * 80)

    total_tokens = 0
    max_tokens = 0
    results = []

    for i, sample in enumerate(SAMPLE_CODES, 1):
        print(f"\n{'=' * 80}")
        print(f"테스트 {i}: {sample['name']}")
        print('=' * 80)

        # 1. 코드 리뷰 프롬프트 생성
        review_prompt = builder.build_review_prompt(
            code=sample['code'],
            categories=sample['categories'],
            output_format=OutputFormat.IMPROVED_CODE,
            include_examples=True
        )

        # 2. 토큰 수 계산
        token_count = builder.estimate_tokens(review_prompt)
        total_tokens += token_count
        max_tokens = max(max_tokens, token_count)

        # 3. 최적화 확인
        is_optimized = token_count <= 1500

        print(f"\n카테고리: {[cat.value for cat in sample['categories']]}")
        print(f"토큰 수: {token_count}")
        print(f"최적화 상태: {'✅ 통과 (<= 1500)' if is_optimized else '❌ 실패 (> 1500)'}")

        # 4. 프롬프트 미리보기
        print(f"\n프롬프트 미리보기:")
        print("-" * 80)
        print(review_prompt[:500] + "..." if len(review_prompt) > 500 else review_prompt)
        print("-" * 80)

        results.append({
            'sample': sample['name'],
            'tokens': token_count,
            'optimized': is_optimized
        })

    # 전체 결과 요약
    print(f"\n{'=' * 80}")
    print("전체 테스트 결과 요약")
    print('=' * 80)

    print(f"\n총 샘플 수: {len(SAMPLE_CODES)}")
    print(f"평균 토큰 수: {total_tokens / len(SAMPLE_CODES):.0f}")
    print(f"최대 토큰 수: {max_tokens}")
    print(f"최적화 통과: {sum(1 for r in results if r['optimized'])}/{len(results)}")

    print("\n개별 결과:")
    for result in results:
        status = "✅" if result['optimized'] else "❌"
        print(f"{status} {result['sample']}: {result['tokens']} 토큰")

    # 최종 판정
    all_passed = all(r['optimized'] for r in results)
    print(f"\n{'=' * 80}")
    if all_passed:
        print("✅ 모든 테스트 통과! 토큰 최적화 목표 달성 (<= 1500)")
    else:
        print("❌ 일부 테스트 실패. 프롬프트 최적화 필요")
    print('=' * 80)

    return results


def test_output_formats():
    """출력 형식별 테스트"""
    builder = PromptBuilder()
    test_code = SAMPLE_CODES[0]['code']

    print(f"\n{'=' * 80}")
    print("출력 형식별 테스트")
    print('=' * 80)

    formats = [
        OutputFormat.IMPROVED_CODE,
        OutputFormat.CODE_COMMENTS,
        OutputFormat.FLOW_DIAGRAM
    ]

    for output_format in formats:
        print(f"\n형식: {output_format.value}")
        print("-" * 80)

        if output_format == OutputFormat.IMPROVED_CODE:
            prompt = builder.build_review_prompt(
                code=test_code,
                categories=[ReviewCategory.NULL_REFERENCE],
                output_format=output_format
            )
        elif output_format == OutputFormat.CODE_COMMENTS:
            prompt = builder.build_comment_prompt(test_code)
        else:  # FLOW_DIAGRAM
            prompt = builder.build_flow_diagram_prompt(test_code)

        tokens = builder.estimate_tokens(prompt)
        print(f"토큰 수: {tokens}")
        print(f"프롬프트 길이: {len(prompt)} 글자")
        print()


def test_optimization():
    """프롬프트 최적화 테스트"""
    builder = PromptBuilder()

    print(f"\n{'=' * 80}")
    print("프롬프트 최적화 테스트")
    print('=' * 80)

    # 긴 코드로 테스트
    long_code = """public class LongExample
{
    private string field1;
    private string field2;
    private string field3;

    public void Method1(string param1) { }
    public void Method2(string param2) { }
    public void Method3(string param3) { }
    public void Method4(string param4) { }
    public void Method5(string param5) { }
}""" * 3  # 3배로 늘림

    # 모든 카테고리로 프롬프트 생성
    all_categories = list(ReviewCategory)

    original_prompt = builder.build_review_prompt(
        code=long_code,
        categories=all_categories,
        include_examples=True
    )

    original_tokens = builder.estimate_tokens(original_prompt)
    print(f"\n원본 프롬프트 토큰 수: {original_tokens}")

    # 최적화 적용
    optimized_prompt = builder.optimize_prompt(original_prompt, max_tokens=1500)
    optimized_tokens = builder.estimate_tokens(optimized_prompt)

    print(f"최적화된 프롬프트 토큰 수: {optimized_tokens}")
    print(f"감소율: {((original_tokens - optimized_tokens) / original_tokens * 100):.1f}%")
    print(f"최적화 성공: {'✅' if optimized_tokens <= 1500 else '❌'}")


if __name__ == "__main__":
    # 1. 모든 샘플 코드 테스트
    results = test_all_samples()

    # 2. 출력 형식별 테스트
    test_output_formats()

    # 3. 프롬프트 최적화 테스트
    test_optimization()

    print(f"\n{'=' * 80}")
    print("모든 테스트 완료!")
    print('=' * 80)
