"""
통합 테스트: PromptBuilder + OllamaClient

실제로 Phi-3-mini LLM을 사용하여 C# 코드 분석을 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.prompt_builder import PromptBuilder, ReviewCategory, OutputFormat
from app.core.ollama_client import OllamaClient, OllamaClientError


def test_end_to_end_code_analysis():
    """종단간 코드 분석 테스트"""

    print("=" * 80)
    print("통합 테스트: PromptBuilder + OllamaClient + Phi-3-mini")
    print("=" * 80)

    # 1. 테스트 코드 (문제가 있는 C# 코드)
    test_code = """public void ProcessData(string data)
{
    var result = data.ToUpper();
    Console.WriteLine(result);
}"""

    print(f"\n📝 테스트 코드:")
    print("-" * 80)
    print(test_code)
    print("-" * 80)

    # 2. PromptBuilder 생성
    print("\n🔧 PromptBuilder 초기화...")
    builder = PromptBuilder()

    # 3. 프롬프트 생성
    print("📋 프롬프트 생성 중...")
    categories = [
        ReviewCategory.NULL_REFERENCE,
        ReviewCategory.EXCEPTION_HANDLING
    ]

    prompt = builder.build_review_prompt(
        code=test_code,
        categories=categories,
        output_format=OutputFormat.IMPROVED_CODE,
        include_examples=True
    )

    # 시스템 프롬프트 결합
    full_prompt = f"{builder.SYSTEM_PROMPT}\n\n{prompt}"

    # 토큰 수 추정
    token_count = builder.estimate_tokens(full_prompt)
    print(f"✅ 프롬프트 생성 완료 (예상 토큰: {token_count})")

    # 4. OllamaClient 초기화
    print("\n🔌 Ollama 클라이언트 초기화...")
    try:
        client = OllamaClient(model_name="phi3:mini")
        client.test_connection()
        print("✅ Ollama 연결 성공")

        # 모델 정보 가져오기
        model_info = client.get_model_info()
        print(f"📦 모델: {model_info['name']}")
        print(f"📊 파라미터: {model_info['details']['parameter_size']}")
        print(f"⚙️ 양자화: {model_info['details']['quantization_level']}")

    except OllamaClientError as e:
        print(f"❌ Ollama 연결 실패: {e}")
        print("Ollama 서버가 실행 중인지 확인하세요: ollama serve")
        return

    # 5. 코드 분석 실행
    print("\n🤖 LLM 코드 분석 시작...")
    print("⏳ 분석 중... (최대 30초 소요)")

    try:
        import time
        start_time = time.time()

        # 스트리밍 모드로 분석 (진행 상황 표시)
        improved_code = ""
        for chunk in client.analyze_code(full_prompt, stream=True):
            improved_code += chunk
            # 첫 100자만 미리보기
            if len(improved_code) <= 100:
                print(chunk, end='', flush=True)

        elapsed_time = time.time() - start_time

        print(f"\n\n✅ 분석 완료! (소요 시간: {elapsed_time:.1f}초)")

        # 6. 결과 출력
        print("\n" + "=" * 80)
        print("🎯 개선된 코드:")
        print("=" * 80)
        print(improved_code)
        print("=" * 80)

        # 7. 결과 검증
        print("\n📊 결과 검증:")

        # 기본 검증
        checks = {
            "코드가 생성되었는가?": len(improved_code.strip()) > 0,
            "원본보다 길어졌는가? (개선 사항 추가)": len(improved_code) > len(test_code),
            "C# 키워드 포함?": any(keyword in improved_code for keyword in ['public', 'void', 'string']),
            "null 체크 추가?": 'null' in improved_code.lower() or 'IsNullOrEmpty' in improved_code,
        }

        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check}")

        # 전체 성공 여부
        all_passed = all(checks.values())
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ 통합 테스트 성공! 모든 검증 통과")
        else:
            print("⚠️ 일부 검증 실패 (LLM 출력 품질 확인 필요)")
        print("=" * 80)

        return all_passed

    except Exception as e:
        print(f"\n❌ 분석 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_categories():
    """여러 카테고리 동시 적용 테스트"""

    print("\n\n" + "=" * 80)
    print("다중 카테고리 테스트")
    print("=" * 80)

    # 더 복잡한 코드
    complex_code = """public void ExecuteQuery(string query)
{
    SqlConnection conn = new SqlConnection(connectionString);
    conn.Open();
    SqlCommand cmd = new SqlCommand(query, conn);
    cmd.ExecuteNonQuery();
}"""

    print(f"\n📝 테스트 코드:")
    print(complex_code)

    builder = PromptBuilder()
    client = OllamaClient(model_name="phi3:mini")

    # 모든 카테고리 적용
    all_categories = [
        ReviewCategory.NULL_REFERENCE,
        ReviewCategory.EXCEPTION_HANDLING,
        ReviewCategory.RESOURCE_MANAGEMENT,
        ReviewCategory.SECURITY
    ]

    prompt = builder.build_review_prompt(
        code=complex_code,
        categories=all_categories,
        output_format=OutputFormat.IMPROVED_CODE,
        include_examples=True
    )

    full_prompt = f"{builder.SYSTEM_PROMPT}\n\n{prompt}"

    print(f"\n🤖 분석 중... (카테고리: {len(all_categories)}개)")

    try:
        improved = client.analyze_code(full_prompt, stream=False)

        print("\n" + "=" * 80)
        print("🎯 개선된 코드:")
        print("=" * 80)
        print(improved)
        print("=" * 80)

        # 검증
        improvements = {
            "using 문 사용 (리소스 관리)": 'using' in improved,
            "try-catch 추가 (예외 처리)": 'try' in improved or 'catch' in improved,
            "파라미터화 쿼리 (보안)": 'Parameter' in improved or 'parameter' in improved,
        }

        print("\n📊 개선 사항 검증:")
        for improvement, found in improvements.items():
            status = "✅" if found else "⚠️"
            print(f"{status} {improvement}")

        return any(improvements.values())

    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 C# Code Reviewer 통합 테스트 시작\n")

    # 테스트 1: 기본 종단간 테스트
    result1 = test_end_to_end_code_analysis()

    # 테스트 2: 다중 카테고리 테스트
    result2 = test_multiple_categories()

    # 최종 결과
    print("\n\n" + "=" * 80)
    print("🎬 최종 결과")
    print("=" * 80)
    print(f"기본 테스트: {'✅ 통과' if result1 else '❌ 실패'}")
    print(f"다중 카테고리 테스트: {'✅ 통과' if result2 else '❌ 실패'}")

    if result1 and result2:
        print("\n🎉 모든 통합 테스트 통과!")
        print("이제 GUI에서 실제 코드 분석을 사용할 수 있습니다.")
    else:
        print("\n⚠️ 일부 테스트 실패")

    print("=" * 80)
