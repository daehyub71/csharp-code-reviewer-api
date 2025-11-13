# 리소스 관리

## 설명
IDisposable 리소스(파일, DB 연결, 네트워크 소켓 등)의 올바른 해제를 보장합니다.
using 문을 사용하여 자동으로 리소스를 정리하고 메모리 누수를 방지합니다.

## 규칙
- using 문으로 IDisposable 리소스 자동 해제
- IDisposable 구현 시 Dispose 패턴 준수
- 파일, DB 연결, HttpClient 등 명시적으로 닫기
- async/await 사용 시 ConfigureAwait(false) 고려
- Stream, Reader, Writer 등은 항상 using으로 감싸기
- 대용량 객체는 즉시 해제

## Before 예제
```csharp
public void ReadFile(string path)
{
    StreamReader reader = new StreamReader(path);
    string content = reader.ReadToEnd();
    Console.WriteLine(content);
    reader.Close();
}

public void QueryDatabase(string sql)
{
    SqlConnection conn = new SqlConnection(connectionString);
    conn.Open();
    SqlCommand cmd = new SqlCommand(sql, conn);
    var result = cmd.ExecuteScalar();
    Console.WriteLine(result);
}
```

## After 예제
```csharp
public void ReadFile(string path)
{
    using (var reader = new StreamReader(path))
    {
        string content = reader.ReadToEnd();
        Console.WriteLine(content);
    } // reader가 자동으로 Dispose됨
}

public void QueryDatabase(string sql)
{
    using (var conn = new SqlConnection(connectionString))
    using (var cmd = new SqlCommand(sql, conn))
    {
        conn.Open();
        var result = cmd.ExecuteScalar();
        Console.WriteLine(result);
    } // conn과 cmd가 자동으로 Dispose됨
}

// C# 8.0+ using 선언 스타일
public void ReadFileModern(string path)
{
    using var reader = new StreamReader(path);
    string content = reader.ReadToEnd();
    Console.WriteLine(content);
} // 스코프 끝에서 자동 Dispose
```
