# C# Code Reviewer (API Version)

> AI 기반 C# 코드 리뷰 자동화 도구 - OpenAI GPT / Anthropic Claude API 버전

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.6+-green.svg)](https://pypi.org/project/PySide6/)

**C# Code Reviewer**는 OpenAI GPT 또는 Anthropic Claude API를 사용하여 C# 코드를 자동으로 분석하고 개선 제안을 제공하는 도구입니다.

---

## 주요 특징

- ⚡ **빠른 분석**: 1-3초 내 분석 완료 (클라우드 GPU 기반)
- 🎯 **8가지 리뷰 카테고리**: Null 참조, Exception 처리, 리소스 관리, 성능, 보안, 네이밍 컨벤션, XML 문서 주석, 하드코딩→Config
- 🔄 **다중 입력 모드**: 텍스트 직접 입력, 파일 업로드 (드래그 앤 드롭), 폴더 선택 (재귀 탐색)
- 📊 **통합 리포트**: 프로젝트 전체 통계, 카테고리별 분석, 우선순위 권장, 차트 생성
- 💾 **자동 저장**: Markdown + HTML 리포트 생성, SQLite DB 히스토리 관리
- 🎨 **사용자 친화적 GUI**: PySide6 네이티브 인터페이스, VS Code Dark 테마

---

## 빠른 시작 (5분)

### 1. 설치

```bash
# 프로젝트 클론 또는 다운로드
git clone <repository-url>
cd csharp-code-reviewer-api

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (아래 중 하나 선택)
# Option 1: OpenAI (추천)
OPENAI_API_KEY=sk-your-openai-key-here

# Option 2: Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# 기본 제공자 설정 (선택사항)
DEFAULT_PROVIDER=openai  # 또는 'anthropic'
```

**API 키 발급:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

### 3. 실행

```bash
python app/main.py
```

### 4. 코드 분석 시작

1. **텍스트 입력 모드**: C# 코드를 붙여넣고 "Analyze Code" 클릭
2. **파일 업로드 모드**: `.cs` 파일을 드래그 앤 드롭하거나 파일 선택
3. **폴더 선택 모드**: 프로젝트 폴더를 선택하고 분석할 파일 체크

---

## 8가지 코드 리뷰 카테고리

### 1. Null 참조 체크
```csharp
// ❌ Before
var result = myObject.ToString();

// ✅ After
var result = myObject?.ToString() ?? "N/A";
```

### 2. Exception 처리
```csharp
// ❌ Before
public void ReadFile(string path)
{
    var content = File.ReadAllText(path);
}

// ✅ After
public void ReadFile(string path)
{
    try
    {
        var content = File.ReadAllText(path);
    }
    catch (FileNotFoundException ex)
    {
        Console.WriteLine($"File not found: {ex.Message}");
    }
}
```

### 3. 리소스 관리
```csharp
// ❌ Before
var stream = new FileStream("file.txt", FileMode.Open);

// ✅ After
using (var stream = new FileStream("file.txt", FileMode.Open))
{
    // 자동 해제
}
```

### 4. 성능 최적화
```csharp
// ❌ Before
string result = "";
for (int i = 0; i < 1000; i++)
    result += i.ToString();

// ✅ After
var sb = new StringBuilder();
for (int i = 0; i < 1000; i++)
    sb.Append(i);
string result = sb.ToString();
```

### 5. 보안 (SQL Injection 방지)
```csharp
// ❌ Before
string query = $"SELECT * FROM Users WHERE Name = '{userName}'";

// ✅ After
string query = "SELECT * FROM Users WHERE Name = @name";
cmd.Parameters.AddWithValue("@name", userName);
```

### 6. 네이밍 컨벤션
```csharp
// ❌ Before
public class userService
{
    private string Logger;
}

// ✅ After
public class UserService
{
    private string _logger;
}
```

### 7. XML 문서 주석
```csharp
// ❌ Before
public bool ValidateUser(string name)
{
    return !string.IsNullOrEmpty(name);
}

// ✅ After
/// <summary>
/// 사용자 이름의 유효성을 검증합니다.
/// </summary>
/// <param name="name">검증할 사용자 이름</param>
/// <returns>유효하면 true, 그렇지 않으면 false</returns>
public bool ValidateUser(string name)
{
    return !string.IsNullOrEmpty(name);
}
```

### 8. 하드코딩 → Config 파일
```csharp
// ❌ Before
public void Connect()
{
    string connStr = "Server=localhost;Database=myDB;User=admin;Password=1234";
    var conn = new SqlConnection(connStr);
}

// ✅ After
public class DatabaseService
{
    private readonly IConfiguration _configuration;

    public DatabaseService(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public void Connect()
    {
        string connStr = _configuration.GetConnectionString("DefaultConnection");
        var conn = new SqlConnection(connStr);
    }
}

// appsettings.json:
// {
//   "ConnectionStrings": {
//     "DefaultConnection": "Server=localhost;Database=myDB;..."
//   }
// }
```

---

## 비용

### 지원 모델

| 제공자 | 모델 | 입력 비용 | 출력 비용 | 속도 | 품질 |
|--------|------|----------|----------|------|------|
| OpenAI | gpt-4o-mini | $0.15/1M | $0.60/1M | 빠름 | 좋음 |
| OpenAI | gpt-4o | $2.50/1M | $10.00/1M | 보통 | 최고 |
| Anthropic | claude-3-5-haiku | $0.80/1M | $4.00/1M | 빠름 | 좋음 |
| Anthropic | claude-3-5-sonnet | $3.00/1M | $15.00/1M | 보통 | 최고 |

### 예상 비용

| 코드 크기 | 입력 토큰 | 출력 토큰 | 비용 (gpt-4o-mini) | 비용 (claude-3-5-haiku) |
|----------|----------|----------|------------------|---------------------|
| 50 lines | ~500 | ~800 | $0.0006 | $0.0036 |
| 100 lines | ~800 | ~1200 | $0.0009 | $0.0052 |
| 500 lines | ~2500 | ~3000 | $0.0022 | $0.0140 |

💡 **권장**: 일반적인 코드 리뷰는 `gpt-4o-mini` (OpenAI) 사용 시 리뷰당 $0.001 미만

---

## 시스템 요구사항

### 최소 사양
- **OS**: Windows 10/11, macOS 10.15+, Linux
- **Python**: 3.11 이상
- **RAM**: 4GB
- **디스크 공간**: 500MB
- **네트워크**: 인터넷 연결 (API 호출용)

### 권장 사양
- **RAM**: 8GB 이상
- **디스크**: SSD 권장
- **네트워크**: 안정적인 인터넷 (API 호출용)

---

## 프로젝트 구조

```
csharp-code-reviewer-api/
├── app/
│   ├── main.py                   # 애플리케이션 진입점
│   ├── core/
│   │   ├── api_client.py         # OpenAI/Anthropic 통합 클라이언트
│   │   ├── prompt_builder.py     # 프롬프트 생성
│   │   ├── report_generator.py   # 리포트 생성
│   │   ├── batch_analyzer.py     # 배치 분석
│   │   └── integrated_report_generator.py  # 통합 리포트
│   ├── ui/
│   │   ├── main_window.py        # 메인 윈도우
│   │   ├── before_after_editor.py  # 코드 에디터
│   │   └── result_panel.py       # 결과 패널
│   ├── utils/
│   ├── db/
│   └── services/
├── resources/
│   └── templates/
│       └── review_categories/    # 8가지 카테고리 템플릿
├── scripts/
│   ├── build_exe.py              # 실행 파일 빌드
│   └── build_installer.py        # 설치 파일 생성
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 개발 명령어

```bash
# 테스트 실행
pytest

# 커버리지 리포트
pytest --cov=app --cov-report=html

# 특정 테스트 실행
pytest tests/test_api_client.py -v

# 실행 파일 빌드 (Windows)
python scripts/build_exe.py
```

---

## Ollama 버전과의 차이점

| 항목 | Ollama 버전 | API 버전 (이 프로젝트) |
|------|------------|----------------------|
| **LLM** | Phi-3-mini (로컬) | GPT-4o-mini / Claude 3.5 Haiku |
| **네트워크** | 오프라인 가능 | 인터넷 필요 |
| **설정** | Ollama 설치 + 모델 다운로드 | API 키만 설정 |
| **디스크 공간** | ~5GB (앱 + 모델) | ~500MB (앱만) |
| **RAM** | 8GB (모델 메모리) | 4GB (모델 없음) |
| **속도** | 10-20초/리뷰 | 1-3초/리뷰 |
| **품질** | 좋음 | 우수 |
| **비용** | 무료 | ~$0.001-0.02/리뷰 |
| **프라이버시** | 100% 로컬 | 코드가 외부 API로 전송 |

**언제 API 버전을 사용할까?**
- ✅ 인터넷 연결 가능
- ✅ 외부 API 사용 허용 (민감하지 않은 코드)
- ✅ 최고 품질의 결과 원함
- ✅ 빠른 분석 속도 필요
- ✅ API 비용 지불 가능 (~$0.001/리뷰)

**언제 Ollama 버전을 사용할까?**
- ✅ 오프라인 환경 (VDI, 에어갭 네트워크)
- ✅ 외부 API 사용 불가 (데이터 보안 정책)
- ✅ 완전 무료 사용 원함
- ✅ 느린 속도 감수 가능

---

## 문서

- **빠른 시작 가이드**: [QUICKSTART.md](QUICKSTART.md)
- **개발자 가이드**: [CLAUDE.md](CLAUDE.md)
- **변경 사항**: [CHANGES.md](CHANGES.md) (Ollama 버전과의 차이점)
- **프로젝트 계획**: [PROJECT_PLAN.md](PROJECT_PLAN.md)

---

## 문제 해결

### "No API keys configured"
→ `.env` 파일에 `OPENAI_API_KEY` 또는 `ANTHROPIC_API_KEY` 추가

### "API connection failed"
→ API 키 유효성 확인, 인터넷 연결 확인, API 크레딧 잔액 확인

### "Model not found"
→ `.env` 파일의 모델 이름 철자 확인 (기본값 사용 권장: `DEFAULT_MODEL=` 비워두기)

### 느린 분석 속도
→ 더 빠른 모델 사용 (`gpt-4o-mini` 또는 `claude-3-5-haiku`)

---

## 기여

버그 리포트, 기능 제안, Pull Request를 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 라이선스

이 프로젝트는 MIT License 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

- **PySide6**: LGPL v3 (상업용 무료)
- **OpenAI API**: OpenAI 서비스 약관
- **Anthropic API**: Anthropic 서비스 약관

---

## 관련 프로젝트

- **Original Ollama Version**: [csharp-code-reviewer](../csharp-code-reviewer) (오프라인 로컬 실행)

---

**버전**: 2.0.0 (API version)
**기반**: Ollama 버전 1.0.0
**포크 날짜**: 2025-11-13
**라이선스**: MIT
