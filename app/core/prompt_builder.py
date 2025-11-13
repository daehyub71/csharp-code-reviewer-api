"""
C# 코드 리뷰를 위한 프롬프트 빌더

이 모듈은 LLM에 전달할 프롬프트를 생성하고 최적화합니다.
토큰 수를 최소화하면서 효과적인 코드 리뷰를 수행합니다.

리뷰 규칙과 예제는 Markdown 파일에서 동적으로 로드됩니다.
"""

from typing import List, Dict, Any
from enum import Enum
from pathlib import Path
import sys

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.utils.markdown_parser import CategoryLoader


class ReviewCategory(Enum):
    """코드 리뷰 카테고리"""
    NULL_REFERENCE = "null_reference"  # Null 참조 체크
    EXCEPTION_HANDLING = "exception_handling"  # Exception 처리 누락
    RESOURCE_MANAGEMENT = "resource_management"  # 리소스 해제
    PERFORMANCE = "performance"  # 성능 이슈
    SECURITY = "security"  # 보안 취약점
    NAMING_CONVENTION = "naming_convention"  # 네이밍 컨벤션
    CODE_DOCUMENTATION = "code_documentation"  # XML 문서 주석
    HARDCODING_TO_CONFIG = "hardcoding_to_config"  # 하드코딩 → Config 파일


class OutputFormat(Enum):
    """출력 형식"""
    IMPROVED_CODE = "improved_code"  # 개선된 코드
    CODE_COMMENTS = "code_comments"  # 코드 주석
    FLOW_DIAGRAM = "flow_diagram"  # 플로우 다이어그램


class PromptBuilder:
    """
    LLM 프롬프트 빌더 클래스

    C# 코드 리뷰를 위한 최적화된 프롬프트를 생성합니다.
    Few-shot 예제를 포함하며, 토큰 수를 1500개 이하로 유지합니다.
    """

    # 시스템 프롬프트 (역할 정의)
    SYSTEM_PROMPT = """당신은 C# 코드 리뷰 전문가입니다. 입력된 원본 코드를 분석하고, 문제점을 수정한 개선 버전을 작성합니다.

다음 원칙을 따르세요:
1. 클래스/메서드 이름은 유지하되, 내부 구조는 개선할 수 있습니다
2. 하드코딩을 제거하려면 IConfiguration, 생성자 주입 등 필요한 구조를 추가하세요
3. Null 체크, Exception 처리, using 문 등 필요한 코드를 추가하세요
4. 보안 문제(SQL Injection 등)는 반드시 수정하세요
5. 반드시 C# 문법으로만 출력 (Python, Java 등 다른 언어 사용 금지)
6. 순수 C# 코드만 출력하세요 (마크다운 코드 블록 ```csharp 등은 제외)
7. XML 문서 주석(///)은 코드의 일부이므로 모든 public 클래스/메서드에 반드시 추가하세요
8. 일반 설명문(자연어 텍스트)은 출력하지 마세요

⚠️ 중요: 개선을 위해 필요하다면 클래스에 필드, 생성자, 프로퍼티를 추가할 수 있습니다!"""

    # 6가지 리뷰 항목 템플릿
    REVIEW_TEMPLATES = {
        ReviewCategory.NULL_REFERENCE: {
            "name": "Null 참조 체크",
            "description": "null 참조 예외를 방지하는 검증 로직 추가",
            "rules": [
                "메서드 파라미터에 null 체크 추가",
                "null 조건 연산자 (?., ??) 활용",
                "ArgumentNullException 던지기"
            ]
        },
        ReviewCategory.EXCEPTION_HANDLING: {
            "name": "Exception 처리",
            "description": "적절한 예외 처리 및 에러 핸들링",
            "rules": [
                "try-catch 블록으로 예외 처리",
                "구체적인 예외 타입 사용",
                "예외 메시지 명확하게 작성",
                "finally 블록으로 정리 작업"
            ]
        },
        ReviewCategory.RESOURCE_MANAGEMENT: {
            "name": "리소스 관리",
            "description": "IDisposable 리소스의 올바른 해제",
            "rules": [
                "using 문으로 자동 해제",
                "IDisposable 구현 확인",
                "파일/DB 연결 명시적 닫기"
            ]
        },
        ReviewCategory.PERFORMANCE: {
            "name": "성능 최적화",
            "description": "불필요한 연산 제거 및 효율성 향상",
            "rules": [
                "LINQ 최적화 (ToList() 남용 방지)",
                "StringBuilder 사용 (문자열 연결)",
                "불필요한 반복문 제거",
                "캐싱 활용"
            ]
        },
        ReviewCategory.SECURITY: {
            "name": "보안",
            "description": "보안 취약점 제거",
            "rules": [
                "SQL Injection 방지 (파라미터화)",
                "입력 값 검증",
                "민감 정보 암호화",
                "권한 체크"
            ]
        },
        ReviewCategory.NAMING_CONVENTION: {
            "name": "네이밍 규칙",
            "description": "C# 네이밍 컨벤션 준수",
            "rules": [
                "PascalCase: 클래스, 메서드, 프로퍼티",
                "camelCase: 로컬 변수, 파라미터",
                "_camelCase: private 필드",
                "의미 있는 이름 사용"
            ]
        },
        ReviewCategory.CODE_DOCUMENTATION: {
            "name": "XML 문서 주석",
            "description": "C# XML 문서 주석 작성 (///, <summary>, <param>, <returns> 등)",
            "rules": [
                "모든 public 클래스/메서드에 /// 주석 추가",
                "<summary>: 한 줄 요약",
                "<param>: 매개변수 설명",
                "<returns>: 반환값 설명",
                "<exception>: 발생 가능한 예외",
                "<remarks>: 상세 설명 (옵션)",
                "<example>: 사용 예제 (옵션)"
            ]
        },
        ReviewCategory.HARDCODING_TO_CONFIG: {
            "name": "하드코딩 → Config 파일",
            "description": "하드코딩된 설정값을 외부 설정 파일(appsettings.json, .env)로 분리",
            "rules": [
                "연결 문자열은 appsettings.json의 ConnectionStrings 섹션으로",
                "API URL은 appsettings.json의 ApiSettings 섹션으로",
                "매직 넘버는 상수(const) 또는 enum으로 분리",
                "파일 경로는 IConfiguration으로 관리",
                "환경별 설정은 appsettings.{Environment}.json 활용",
                "IConfiguration 인터페이스를 통한 의존성 주입"
            ]
        }
    }

    # Few-shot 예제 (토큰 최적화)
    FEW_SHOT_EXAMPLES = [
        {
            "category": ReviewCategory.NULL_REFERENCE,
            "before": """public void ProcessData(string data)
{
    var result = data.ToUpper();
    Console.WriteLine(result);
}""",
            "after": """public void ProcessData(string data)
{
    if (string.IsNullOrEmpty(data))
        throw new ArgumentNullException(nameof(data));

    var result = data.ToUpper();
    Console.WriteLine(result);
}"""
        },
        {
            "category": ReviewCategory.RESOURCE_MANAGEMENT,
            "before": """public void ReadFile(string path)
{
    StreamReader reader = new StreamReader(path);
    string content = reader.ReadToEnd();
    Console.WriteLine(content);
}""",
            "after": """public void ReadFile(string path)
{
    using (var reader = new StreamReader(path))
    {
        string content = reader.ReadToEnd();
        Console.WriteLine(content);
    }
}"""
        },
        {
            "category": ReviewCategory.EXCEPTION_HANDLING,
            "before": """public int Divide(int a, int b)
{
    return a / b;
}""",
            "after": """public int Divide(int a, int b)
{
    if (b == 0)
        throw new DivideByZeroException("제수는 0이 될 수 없습니다.");

    return a / b;
}"""
        },
        {
            "category": ReviewCategory.CODE_DOCUMENTATION,
            "before": """public class UserService
{
    public User GetUser(int userId)
    {
        return database.Find(userId);
    }
}""",
            "after": """/// <summary>
/// 사용자 관리 서비스
/// </summary>
/// <remarks>
/// 데이터베이스에서 사용자 정보를 조회하고 관리합니다.
/// </remarks>
public class UserService
{
    /// <summary>
    /// 사용자 ID로 사용자 정보를 조회합니다.
    /// </summary>
    /// <param name="userId">조회할 사용자 ID</param>
    /// <returns>사용자 정보 객체, 없으면 null</returns>
    /// <exception cref="ArgumentException">userId가 0 이하인 경우</exception>
    public User GetUser(int userId)
    {
        if (userId <= 0)
            throw new ArgumentException("유효하지 않은 사용자 ID입니다.", nameof(userId));

        return database.Find(userId);
    }
}"""
        },
        {
            "category": ReviewCategory.HARDCODING_TO_CONFIG,
            "before": """public class UserService
{
    public async Task<User> GetUserAsync(int userId)
    {
        var apiUrl = "https://api.example.com/v1/users/" + userId;
        using var client = new HttpClient();
        client.Timeout = TimeSpan.FromSeconds(30);
        var response = await client.GetAsync(apiUrl);
        return await response.Content.ReadFromJsonAsync<User>();
    }
}

public class DatabaseHelper
{
    public SqlConnection GetConnection()
    {
        var connectionString = "Server=localhost;Database=MyDB;User Id=admin;Password=admin123;";
        return new SqlConnection(connectionString);
    }
}""",
            "after": """public class UserService
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _configuration;

    public UserService(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _configuration = configuration;
        var timeout = _configuration.GetValue<int>("ApiSettings:Timeout");
        _httpClient.Timeout = TimeSpan.FromSeconds(timeout);
    }

    public async Task<User> GetUserAsync(int userId)
    {
        var baseUrl = _configuration["ApiSettings:BaseUrl"];
        var apiUrl = $"{baseUrl}/users/{userId}";
        var response = await _httpClient.GetAsync(apiUrl);
        return await response.Content.ReadFromJsonAsync<User>();
    }
}

public class DatabaseHelper
{
    private readonly IConfiguration _configuration;

    public DatabaseHelper(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public SqlConnection GetConnection()
    {
        var connectionString = _configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("연결 문자열이 설정되지 않았습니다.");
        return new SqlConnection(connectionString);
    }
}"""
        }
    ]

    def __init__(self, use_markdown=True):
        """
        PromptBuilder 초기화

        Args:
            use_markdown: Markdown 파일에서 규칙/예제 로드 여부 (기본값: True)
        """
        self.system_prompt = self.SYSTEM_PROMPT

        if use_markdown:
            # Markdown 파일에서 카테고리 데이터 로드
            project_root = Path(__file__).parent.parent.parent
            categories_dir = project_root / "resources" / "templates" / "review_categories"

            loader = CategoryLoader(categories_dir)
            self.categories_data = loader.load_all()

            # REVIEW_TEMPLATES 동적 생성
            self.review_templates = self._build_templates_from_markdown()

            # FEW_SHOT_EXAMPLES 동적 생성
            self.few_shot_examples = self._build_examples_from_markdown()
        else:
            # 기존 하드코딩된 데이터 사용 (하위 호환성)
            self.review_templates = self.REVIEW_TEMPLATES
            self.few_shot_examples = self.FEW_SHOT_EXAMPLES

    def _build_templates_from_markdown(self) -> Dict:
        """Markdown 데이터에서 REVIEW_TEMPLATES 형식으로 변환"""
        templates = {}

        category_map = {
            'null_reference': ReviewCategory.NULL_REFERENCE,
            'exception_handling': ReviewCategory.EXCEPTION_HANDLING,
            'resource_management': ReviewCategory.RESOURCE_MANAGEMENT,
            'performance': ReviewCategory.PERFORMANCE,
            'security': ReviewCategory.SECURITY,
            'naming_convention': ReviewCategory.NAMING_CONVENTION,
            'code_documentation': ReviewCategory.CODE_DOCUMENTATION,
            'hardcoding_to_config': ReviewCategory.HARDCODING_TO_CONFIG,
        }

        for key, enum_value in category_map.items():
            if key in self.categories_data:
                data = self.categories_data[key]
                templates[enum_value] = {
                    'name': data['name'],
                    'description': data['description'],
                    'rules': data['rules']
                }

        return templates

    def _build_examples_from_markdown(self) -> List[Dict]:
        """Markdown 데이터에서 FEW_SHOT_EXAMPLES 형식으로 변환"""
        examples = []

        category_map = {
            'null_reference': ReviewCategory.NULL_REFERENCE,
            'exception_handling': ReviewCategory.EXCEPTION_HANDLING,
            'resource_management': ReviewCategory.RESOURCE_MANAGEMENT,
            'performance': ReviewCategory.PERFORMANCE,
            'security': ReviewCategory.SECURITY,
            'naming_convention': ReviewCategory.NAMING_CONVENTION,
            'code_documentation': ReviewCategory.CODE_DOCUMENTATION,
            'hardcoding_to_config': ReviewCategory.HARDCODING_TO_CONFIG,
        }

        for key, enum_value in category_map.items():
            if key in self.categories_data:
                data = self.categories_data[key]
                # 각 카테고리의 첫 번째 예제만 사용 (토큰 최적화)
                if data['examples']:
                    first_example = data['examples'][0]
                    examples.append({
                        'category': enum_value,
                        'before': first_example['before'],
                        'after': first_example['after']
                    })

        return examples

    def build_review_prompt(
        self,
        code: str,
        categories: List[ReviewCategory],
        output_format: OutputFormat = OutputFormat.IMPROVED_CODE,
        include_examples: bool = True
    ) -> str:
        """
        코드 리뷰 프롬프트 생성

        Args:
            code: 리뷰할 C# 코드
            categories: 리뷰 카테고리 목록
            output_format: 출력 형식
            include_examples: Few-shot 예제 포함 여부

        Returns:
            최적화된 프롬프트 문자열
        """
        prompt_parts = []

        # 1. 리뷰 카테고리 설명
        if categories:
            prompt_parts.append("다음 항목을 중점적으로 검토하세요:")
            for category in categories:
                template = self.review_templates[category]
                prompt_parts.append(f"\n• {template['name']}: {template['description']}")

        # 2. Few-shot 예제 (선택한 카테고리만)
        if include_examples and categories:
            relevant_examples = [
                ex for ex in self.few_shot_examples
                if ex["category"] in categories
            ]

            if relevant_examples:
                prompt_parts.append("\n\n예제:")
                for i, example in enumerate(relevant_examples[:2], 1):  # 최대 2개만
                    category_name = self.review_templates[example["category"]]["name"]
                    prompt_parts.append(f"\n[{category_name}]")
                    prompt_parts.append(f"Before:\n{example['before']}")
                    prompt_parts.append(f"\nAfter:\n{example['after']}\n")

        # 3. 사용자 코드
        prompt_parts.append(f"\n분석할 코드:\n```csharp\n{code}\n```")

        # 4. 출력 형식 지시
        prompt_parts.append(f"\n{self._get_output_instruction(output_format)}")

        return "\n".join(prompt_parts)

    def build_comment_prompt(self, code: str) -> str:
        """
        코드 주석 생성 프롬프트

        Args:
            code: 주석을 추가할 C# 코드

        Returns:
            주석 생성 프롬프트
        """
        prompt = f"""다음 C# 코드에 XML 문서 주석을 추가하세요.

규칙:
- 클래스/메서드에 /// <summary> 추가
- 파라미터에 /// <param> 추가
- 반환값에 /// <returns> 추가
- 한글로 명확하게 작성

코드:
```csharp
{code}
```

주석이 추가된 코드를 출력하세요."""

        return prompt

    def build_flow_diagram_prompt(self, code: str) -> str:
        """
        플로우 다이어그램 생성 프롬프트

        Args:
            code: 플로우를 분석할 C# 코드

        Returns:
            플로우 다이어그램 프롬프트
        """
        prompt = f"""다음 C# 코드의 실행 흐름을 Mermaid 다이어그램으로 표현하세요.

코드:
```csharp
{code}
```

출력 형식:
```mermaid
graph TD
    A[시작] --> B[...]
    B --> C[...]
```

조건문, 반복문, 메서드 호출을 명확히 표시하세요."""

        return prompt

    def _get_output_instruction(self, output_format: OutputFormat) -> str:
        """
        출력 형식별 지시사항 반환

        Args:
            output_format: 출력 형식

        Returns:
            지시사항 문자열
        """
        instructions = {
            OutputFormat.IMPROVED_CODE: """입력된 원본 코드를 개선하여 출력하세요.

개선 규칙:
1. 클래스/메서드/필드 이름은 유지하되, 필요하면 새로운 필드/생성자/프로퍼티를 추가하세요
2. 하드코딩 제거: 하드코딩된 값을 IConfiguration으로 변경하고, 생성자 주입을 추가하세요
3. Null 체크, using 문, try-catch 등 필요한 구조를 추가하세요
4. SQL Injection 방지: 문자열 연결 대신 파라미터화된 쿼리를 사용하세요
5. XML 문서 주석(///)을 모든 public 클래스/메서드에 추가하세요
6. 순수 C# 코드만 출력 (마크다운 코드 블록이나 설명 텍스트 제외)
7. 반드시 유효한 C# 문법으로만 출력

예시:
입력:
```
class UserService {
    string apiUrl = "https://api.com";
    void GetData() { /* ... */ }
}
```

출력:
```
/// <summary>
/// 사용자 서비스 클래스
/// </summary>
class UserService {
    private readonly IConfiguration _config;

    /// <summary>
    /// UserService 생성자
    /// </summary>
    /// <param name="config">설정 객체</param>
    public UserService(IConfiguration config) { _config = config; }

    /// <summary>
    /// 데이터를 가져옵니다
    /// </summary>
    void GetData() {
        string apiUrl = _config["ApiSettings:Url"];
        /* ... */
    }
}
```""",

            OutputFormat.CODE_COMMENTS: """원본 코드에 XML 문서 주석을 추가하여 출력하세요.""",

            OutputFormat.FLOW_DIAGRAM: """Mermaid 형식의 플로우 다이어그램을 출력하세요."""
        }

        return instructions.get(output_format, instructions[OutputFormat.IMPROVED_CODE])

    def estimate_tokens(self, text: str) -> int:
        """
        대략적인 토큰 수 추정 (1 토큰 ≈ 4 글자)

        Args:
            text: 추정할 텍스트

        Returns:
            예상 토큰 수
        """
        # 간단한 추정: 공백 기준 단어 수 + 코드 특수문자 보정
        words = len(text.split())
        chars = len(text)

        # 평균적으로 영어 1단어 = 1.3토큰, 한글 1글자 = 0.5토큰
        estimated = (words * 1.3) + (chars * 0.1)

        return int(estimated)

    def optimize_prompt(self, prompt: str, max_tokens: int = 1500) -> str:
        """
        프롬프트를 토큰 제한 내로 최적화

        Args:
            prompt: 원본 프롬프트
            max_tokens: 최대 토큰 수

        Returns:
            최적화된 프롬프트
        """
        current_tokens = self.estimate_tokens(prompt)

        if current_tokens <= max_tokens:
            return prompt

        # 토큰 초과 시 예제 제거 또는 축약
        # 실제로는 더 정교한 최적화 필요
        lines = prompt.split('\n')

        # 예제 섹션 제거
        optimized_lines = []
        skip_example = False

        for line in lines:
            if '예제:' in line:
                skip_example = True
                continue
            if skip_example and line.startswith('['):
                continue
            if skip_example and ('Before:' in line or 'After:' in line):
                continue
            if skip_example and line.strip().startswith('```'):
                continue
            if skip_example and not line.strip():
                skip_example = False
                continue

            optimized_lines.append(line)

        return '\n'.join(optimized_lines)


# 사용 예제
if __name__ == "__main__":
    # PromptBuilder 생성
    builder = PromptBuilder()

    # 테스트 코드
    test_code = """public void ProcessData(string data)
{
    var result = data.ToUpper();
    Console.WriteLine(result);
}"""

    # 1. 코드 리뷰 프롬프트 생성
    review_prompt = builder.build_review_prompt(
        code=test_code,
        categories=[
            ReviewCategory.NULL_REFERENCE,
            ReviewCategory.EXCEPTION_HANDLING
        ],
        output_format=OutputFormat.IMPROVED_CODE,
        include_examples=True
    )

    print("=== 코드 리뷰 프롬프트 ===")
    print(review_prompt)
    print(f"\n예상 토큰 수: {builder.estimate_tokens(review_prompt)}")

    # 2. 주석 생성 프롬프트
    print("\n\n=== 주석 생성 프롬프트 ===")
    comment_prompt = builder.build_comment_prompt(test_code)
    print(comment_prompt)
    print(f"\n예상 토큰 수: {builder.estimate_tokens(comment_prompt)}")

    # 3. 플로우 다이어그램 프롬프트
    print("\n\n=== 플로우 다이어그램 프롬프트 ===")
    flow_prompt = builder.build_flow_diagram_prompt(test_code)
    print(flow_prompt)
    print(f"\n예상 토큰 수: {builder.estimate_tokens(flow_prompt)}")
