# 하드코딩 → Config 파일

## 설명
하드코딩된 설정값(URL, 경로, 연결 문자열, 상수 등)을 외부 설정 파일(appsettings.json, .env, Web.config)이나 환경 변수로 분리합니다.
이를 통해 환경별(개발/스테이징/프로덕션) 설정 관리가 용이해지고, 보안이 향상됩니다.

## 규칙
- 데이터베이스 연결 문자열은 appsettings.json의 ConnectionStrings 섹션으로
- API 엔드포인트 URL은 appsettings.json의 ApiSettings 섹션으로
- 매직 넘버(Magic Number)는 상수(const) 또는 enum으로 분리
- 파일 경로는 IConfiguration 또는 환경 변수로 관리
- 환경별 설정은 appsettings.{Environment}.json 활용
- IConfiguration 인터페이스를 통한 의존성 주입
- 타임아웃, 재시도 횟수 등 정책 값도 설정 파일로 관리

## Before 예제
```csharp
public class UserService
{
    public async Task<User> GetUserAsync(int userId)
    {
        // 하드코딩된 API URL
        var apiUrl = "https://api.example.com/v1/users/" + userId;

        using var client = new HttpClient();
        client.Timeout = TimeSpan.FromSeconds(30); // 하드코딩된 타임아웃

        var response = await client.GetAsync(apiUrl);
        return await response.Content.ReadFromJsonAsync<User>();
    }

    public void SaveLog(string message)
    {
        // 하드코딩된 파일 경로
        var logPath = "C:\\Logs\\app.log";
        File.AppendAllText(logPath, message);
    }
}

public class DatabaseHelper
{
    public SqlConnection GetConnection()
    {
        // 하드코딩된 연결 문자열
        var connectionString = "Server=localhost;Database=MyDB;User Id=admin;Password=admin123;";
        return new SqlConnection(connectionString);
    }
}

public class PaymentProcessor
{
    public decimal CalculateFee(decimal amount)
    {
        // 매직 넘버 (0.025 = 2.5% 수수료)
        return amount * 0.025m;
    }

    public bool IsValidAmount(decimal amount)
    {
        // 매직 넘버
        return amount >= 100 && amount <= 1000000;
    }
}
```

## After 예제
```csharp
// appsettings.json
// {
//   "ConnectionStrings": {
//     "DefaultConnection": "Server=localhost;Database=MyDB;User Id=admin;Password=***;"
//   },
//   "ApiSettings": {
//     "BaseUrl": "https://api.example.com/v1",
//     "Timeout": 30
//   },
//   "LogSettings": {
//     "LogPath": "C:\\Logs\\app.log"
//   },
//   "PaymentSettings": {
//     "FeeRate": 0.025,
//     "MinAmount": 100,
//     "MaxAmount": 1000000
//   }
// }

public class UserService
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _configuration;

    public UserService(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _configuration = configuration;

        // 설정에서 타임아웃 로드
        var timeout = _configuration.GetValue<int>("ApiSettings:Timeout");
        _httpClient.Timeout = TimeSpan.FromSeconds(timeout);
    }

    public async Task<User> GetUserAsync(int userId)
    {
        // 설정에서 API URL 로드
        var baseUrl = _configuration["ApiSettings:BaseUrl"];
        var apiUrl = $"{baseUrl}/users/{userId}";

        var response = await _httpClient.GetAsync(apiUrl);
        return await response.Content.ReadFromJsonAsync<User>();
    }

    public void SaveLog(string message)
    {
        // 설정에서 파일 경로 로드
        var logPath = _configuration["LogSettings:LogPath"];
        File.AppendAllText(logPath, message);
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
        // 설정에서 연결 문자열 로드
        var connectionString = _configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("연결 문자열이 설정되지 않았습니다.");

        return new SqlConnection(connectionString);
    }
}

public class PaymentProcessor
{
    private readonly IConfiguration _configuration;

    // 상수로 분리 (설정 키 이름)
    private const string FeeRateKey = "PaymentSettings:FeeRate";
    private const string MinAmountKey = "PaymentSettings:MinAmount";
    private const string MaxAmountKey = "PaymentSettings:MaxAmount";

    public PaymentProcessor(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public decimal CalculateFee(decimal amount)
    {
        // 설정에서 수수료율 로드
        var feeRate = _configuration.GetValue<decimal>(FeeRateKey);
        return amount * feeRate;
    }

    public bool IsValidAmount(decimal amount)
    {
        // 설정에서 최소/최대 금액 로드
        var minAmount = _configuration.GetValue<decimal>(MinAmountKey);
        var maxAmount = _configuration.GetValue<decimal>(MaxAmountKey);

        return amount >= minAmount && amount <= maxAmount;
    }
}
```
