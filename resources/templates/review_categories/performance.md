# 성능 최적화

## 설명
불필요한 연산을 제거하고 효율적인 알고리즘과 자료구조를 사용하여 성능을 향상시킵니다.
LINQ 최적화, 문자열 연산 개선, 캐싱 등을 통해 실행 속도를 개선합니다.

## 규칙
- LINQ 최적화 (불필요한 ToList() 호출 제거)
- StringBuilder 사용 (반복적인 문자열 연결)
- 루프 내 불변 연산을 밖으로 이동
- 적절한 컬렉션 타입 선택 (List vs HashSet vs Dictionary)
- async/await를 적절히 사용하여 비동기 처리
- 불필요한 객체 생성 최소화
- 캐싱 활용 (자주 사용되는 데이터)

## Before 예제
```csharp
public string BuildMessage(List<string> items)
{
    string message = "";
    for (int i = 0; i < items.Count; i++)
    {
        message += items[i] + ", ";
    }
    return message;
}

public List<User> GetActiveUsers()
{
    return database.Users
        .ToList()
        .Where(u => u.IsActive)
        .ToList();
}

public bool ContainsEmail(List<string> emails, string target)
{
    for (int i = 0; i < emails.Count; i++)
    {
        if (emails[i] == target)
            return true;
    }
    return false;
}
```

## After 예제
```csharp
public string BuildMessage(List<string> items)
{
    var sb = new StringBuilder();
    for (int i = 0; i < items.Count; i++)
    {
        sb.Append(items[i]);
        sb.Append(", ");
    }
    return sb.ToString();

    // 또는 더 간단하게:
    // return string.Join(", ", items);
}

public IEnumerable<User> GetActiveUsers()
{
    return database.Users
        .Where(u => u.IsActive); // ToList() 제거로 지연 실행
}

public bool ContainsEmail(HashSet<string> emails, string target)
{
    return emails.Contains(target); // O(1) 조회
}

// List를 HashSet으로 변경
private readonly HashSet<string> _emailSet = new HashSet<string>();
```
