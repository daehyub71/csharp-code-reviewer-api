# 네이밍 컨벤션

## 설명
C# 네이밍 컨벤션을 준수하여 코드의 가독성과 일관성을 향상시킵니다.
Microsoft의 공식 C# 코딩 표준을 따릅니다.

## 규칙
- **PascalCase**: 클래스, 메서드, 프로퍼티, 상수, 네임스페이스
- **camelCase**: 로컬 변수, 메서드 파라미터
- **_camelCase**: private 필드 (언더스코어 접두사)
- **I**PascalCase: 인터페이스 (I 접두사)
- 의미 있는 이름 사용 (약어 최소화)
- 불린 변수는 is/has/can 접두사
- 비동기 메서드는 Async 접미사
- 컬렉션은 복수형 (Users, Orders)

## Before 예제
```csharp
public class userservice
{
    private string un;
    private bool f;

    public void getdata(int id)
    {
        var u = repository.FindUser(id);
        if (u != null)
        {
            this.un = u.name;
            this.f = true;
        }
    }

    public async Task<List<User>> GetUsers()
    {
        return await database.QueryAsync<User>("SELECT * FROM Users");
    }
}

public interface repository
{
    User find(int i);
}
```

## After 예제
```csharp
public class UserService
{
    private string _userName;
    private bool _isFound;

    public void LoadUserData(int userId)
    {
        var user = repository.FindUser(userId);
        if (user != null)
        {
            _userName = user.Name;
            _isFound = true;
        }
    }

    public async Task<List<User>> GetUsersAsync()
    {
        return await database.QueryAsync<User>("SELECT * FROM Users");
    }
}

public interface IRepository
{
    User FindById(int userId);
}

// 추가 예제
public class OrderManager
{
    // Constants: PascalCase
    public const int MaxOrderCount = 100;

    // Private fields: _camelCase
    private readonly ILogger _logger;
    private List<Order> _pendingOrders;

    // Properties: PascalCase
    public int TotalOrders { get; private set; }
    public bool IsProcessing { get; private set; }

    // Methods: PascalCase
    public void ProcessOrder(Order order)
    {
        // Local variables: camelCase
        int orderCount = _pendingOrders.Count;
        bool canProcess = orderCount < MaxOrderCount;

        if (canProcess)
        {
            _pendingOrders.Add(order);
        }
    }

    // Async methods: Async suffix
    public async Task<bool> SaveOrderAsync(Order order)
    {
        await _database.SaveAsync(order);
        return true;
    }
}
```
