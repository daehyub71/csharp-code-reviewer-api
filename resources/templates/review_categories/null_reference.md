# Null 참조 체크

## 설명
null 참조 예외(NullReferenceException)를 방지하는 검증 로직을 추가합니다.
메서드 파라미터, 반환값, 객체 참조에 대한 null 체크를 수행합니다.

## 규칙
- 모든 public 메서드 파라미터에 null 체크 추가
- ArgumentNullException 명시적으로 던지기
- null 조건 연산자 (?., ??, ?[]) 활용
- string은 IsNullOrEmpty 또는 IsNullOrWhiteSpace 사용
- 반환값이 null일 가능성 명시 (nullable reference types)

## Before 예제
```csharp
public void ProcessData(string data)
{
    var result = data.ToUpper();
    Console.WriteLine(result);
}

public User FindUser(string email)
{
    var user = database.Users.FirstOrDefault(u => u.Email == email);
    return user;
}
```

## After 예제
```csharp
public void ProcessData(string data)
{
    if (string.IsNullOrEmpty(data))
        throw new ArgumentNullException(nameof(data), "데이터는 null이거나 빈 문자열일 수 없습니다.");

    var result = data.ToUpper();
    Console.WriteLine(result);
}

public User? FindUser(string email)
{
    if (string.IsNullOrEmpty(email))
        throw new ArgumentNullException(nameof(email));

    var user = database.Users.FirstOrDefault(u => u.Email == email);
    return user; // nullable로 명시
}
```
