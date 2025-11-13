# 보안

## 설명
보안 취약점을 식별하고 수정하여 안전한 코드를 작성합니다.
SQL Injection, XSS, 민감 정보 노출 등 OWASP Top 10 취약점을 방지합니다.

## 규칙
- SQL Injection 방지 (파라미터화된 쿼리 사용)
- 사용자 입력 값 항상 검증 및 살균(sanitization)
- 민감 정보 암호화 (비밀번호, API 키 등)
- HTTPS 사용 강제
- 권한 체크 (인증/인가)
- 하드코딩된 자격 증명 제거
- 안전한 랜덤 생성기 사용 (RNGCryptoServiceProvider)
- 파일 업로드 시 파일 타입/크기 검증

## Before 예제
```csharp
public void Login(string username, string password)
{
    string sql = $"SELECT * FROM Users WHERE Username='{username}' AND Password='{password}'";
    var result = database.Execute(sql);
}

public class Config
{
    public const string ApiKey = "sk-1234567890abcdef";
    public const string DbPassword = "admin123";
}

public void SaveFile(IFormFile file)
{
    var path = Path.Combine("uploads", file.FileName);
    file.CopyTo(new FileStream(path, FileMode.Create));
}
```

## After 예제
```csharp
public void Login(string username, string password)
{
    // 파라미터화된 쿼리로 SQL Injection 방지
    string sql = "SELECT * FROM Users WHERE Username=@username AND Password=@password";
    var parameters = new[]
    {
        new SqlParameter("@username", username),
        new SqlParameter("@password", HashPassword(password)) // 비밀번호 해싱
    };
    var result = database.Execute(sql, parameters);
}

public class Config
{
    // 환경 변수 또는 Key Vault에서 로드
    public static string ApiKey => Environment.GetEnvironmentVariable("API_KEY")
        ?? throw new InvalidOperationException("API_KEY not configured");

    public static string DbPassword => GetSecurePassword();
}

public void SaveFile(IFormFile file)
{
    // 입력 검증
    if (file == null || file.Length == 0)
        throw new ArgumentException("유효하지 않은 파일입니다.");

    // 파일 크기 제한 (10MB)
    if (file.Length > 10 * 1024 * 1024)
        throw new ArgumentException("파일 크기가 너무 큽니다.");

    // 허용된 확장자만 허용
    var allowedExtensions = new[] { ".jpg", ".png", ".pdf" };
    var extension = Path.GetExtension(file.FileName).ToLower();
    if (!allowedExtensions.Contains(extension))
        throw new ArgumentException("허용되지 않은 파일 형식입니다.");

    // 안전한 파일명 생성
    var safeFileName = $"{Guid.NewGuid()}{extension}";
    var path = Path.Combine("uploads", safeFileName);

    using (var stream = new FileStream(path, FileMode.Create))
    {
        file.CopyTo(stream);
    }
}
```
