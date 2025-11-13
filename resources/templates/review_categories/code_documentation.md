# XML 문서 주석

## 설명
C# XML 문서 주석 작성 (///, <summary>, <param>, <returns> 등)
모든 public 멤버에 표준 XML 주석을 추가하여 코드 가독성과 IntelliSense 지원을 향상시킵니다.

## 규칙
- 모든 public 클래스/메서드/프로퍼티에 /// 주석 추가
- `<summary>`: 한 줄 요약 (필수)
- `<param>`: 매개변수 설명 (메서드/생성자)
- `<returns>`: 반환값 설명 (메서드)
- `<exception>`: 발생 가능한 예외
- `<remarks>`: 상세 설명 (옵션)
- `<example>`: 사용 예제 (옵션)
- `<value>`: 프로퍼티 값 설명
- `<typeparam>`: 제네릭 타입 파라미터 설명

---

## 케이스 1: 클래스

### Before
```csharp
public class UserService
{
    private readonly IDatabase database;

    public UserService(IDatabase database)
    {
        this.database = database;
    }
}
```

### After
```csharp
/// <summary>
/// 사용자 관리 서비스
/// </summary>
/// <remarks>
/// 데이터베이스에서 사용자 정보를 조회하고 관리합니다.
/// 의존성 주입을 통해 데이터베이스 인스턴스를 받습니다.
/// </remarks>
public class UserService
{
    private readonly IDatabase database;

    /// <summary>
    /// UserService 클래스의 새 인스턴스를 초기화합니다.
    /// </summary>
    /// <param name="database">사용할 데이터베이스 인스턴스</param>
    /// <exception cref="ArgumentNullException">database가 null인 경우</exception>
    public UserService(IDatabase database)
    {
        if (database == null)
            throw new ArgumentNullException(nameof(database));

        this.database = database;
    }
}
```

---

## 케이스 2: 메서드

### Before
```csharp
public User GetUser(int userId)
{
    return database.Find(userId);
}
```

### After
```csharp
/// <summary>
/// 사용자 ID로 사용자 정보를 조회합니다.
/// </summary>
/// <param name="userId">조회할 사용자 ID (1 이상이어야 함)</param>
/// <returns>사용자 정보 객체, 찾을 수 없으면 null</returns>
/// <exception cref="ArgumentException">userId가 0 이하인 경우</exception>
/// <exception cref="DatabaseException">데이터베이스 연결 오류</exception>
public User GetUser(int userId)
{
    if (userId <= 0)
        throw new ArgumentException("유효하지 않은 사용자 ID입니다.", nameof(userId));

    return database.Find(userId);
}
```

---

## 케이스 3: 프로퍼티

### Before
```csharp
public class Product
{
    public string Name { get; set; }
    public decimal Price { get; set; }
    public int Stock { get; private set; }
}
```

### After
```csharp
public class Product
{
    /// <summary>
    /// 제품명을 가져오거나 설정합니다.
    /// </summary>
    /// <value>제품의 이름 (최대 100자)</value>
    public string Name { get; set; }

    /// <summary>
    /// 제품 가격을 가져오거나 설정합니다.
    /// </summary>
    /// <value>제품의 단위 가격 (원화 기준)</value>
    public decimal Price { get; set; }

    /// <summary>
    /// 현재 재고 수량을 가져옵니다.
    /// </summary>
    /// <value>현재 사용 가능한 제품 수량</value>
    public int Stock { get; private set; }
}
```

---

## 케이스 4: 인터페이스

### Before
```csharp
public interface IRepository<T>
{
    T GetById(int id);
    void Save(T entity);
    void Delete(int id);
}
```

### After
```csharp
/// <summary>
/// 제네릭 리포지토리 인터페이스
/// </summary>
/// <typeparam name="T">엔티티 타입</typeparam>
/// <remarks>
/// 데이터 액세스 계층의 기본 CRUD 작업을 정의합니다.
/// </remarks>
public interface IRepository<T>
{
    /// <summary>
    /// ID로 엔티티를 조회합니다.
    /// </summary>
    /// <param name="id">엔티티 ID</param>
    /// <returns>엔티티 객체, 없으면 null</returns>
    T GetById(int id);

    /// <summary>
    /// 엔티티를 저장합니다.
    /// </summary>
    /// <param name="entity">저장할 엔티티</param>
    void Save(T entity);

    /// <summary>
    /// ID로 엔티티를 삭제합니다.
    /// </summary>
    /// <param name="id">삭제할 엔티티 ID</param>
    void Delete(int id);
}
```

---

## 케이스 5: 열거형

### Before
```csharp
public enum OrderStatus
{
    Pending,
    Processing,
    Shipped,
    Delivered,
    Cancelled
}
```

### After
```csharp
/// <summary>
/// 주문 상태를 나타냅니다.
/// </summary>
public enum OrderStatus
{
    /// <summary>
    /// 대기 중 (결제 완료 대기)
    /// </summary>
    Pending,

    /// <summary>
    /// 처리 중 (상품 준비 중)
    /// </summary>
    Processing,

    /// <summary>
    /// 배송 중
    /// </summary>
    Shipped,

    /// <summary>
    /// 배송 완료
    /// </summary>
    Delivered,

    /// <summary>
    /// 취소됨 (사용자 또는 시스템에 의해)
    /// </summary>
    Cancelled
}
```

---

## 케이스 6: 델리게이트

### Before
```csharp
public delegate void DataChangedHandler(object sender, DataChangedEventArgs e);
```

### After
```csharp
/// <summary>
/// 데이터 변경 이벤트를 처리하는 델리게이트입니다.
/// </summary>
/// <param name="sender">이벤트를 발생시킨 객체</param>
/// <param name="e">데이터 변경 이벤트 인자</param>
public delegate void DataChangedHandler(object sender, DataChangedEventArgs e);
```

---

## 케이스 7: 이벤트

### Before
```csharp
public class DataManager
{
    public event DataChangedHandler DataChanged;

    protected virtual void OnDataChanged(DataChangedEventArgs e)
    {
        DataChanged?.Invoke(this, e);
    }
}
```

### After
```csharp
public class DataManager
{
    /// <summary>
    /// 데이터가 변경될 때 발생합니다.
    /// </summary>
    /// <remarks>
    /// 구독자는 이 이벤트를 통해 데이터 변경 알림을 받습니다.
    /// </remarks>
    public event DataChangedHandler DataChanged;

    /// <summary>
    /// DataChanged 이벤트를 발생시킵니다.
    /// </summary>
    /// <param name="e">이벤트 데이터</param>
    protected virtual void OnDataChanged(DataChangedEventArgs e)
    {
        DataChanged?.Invoke(this, e);
    }
}
```

---

## 케이스 8: 제네릭 메서드

### Before
```csharp
public T ConvertTo<T>(object value)
{
    return (T)Convert.ChangeType(value, typeof(T));
}
```

### After
```csharp
/// <summary>
/// 객체를 지정된 타입으로 변환합니다.
/// </summary>
/// <typeparam name="T">변환할 대상 타입</typeparam>
/// <param name="value">변환할 값</param>
/// <returns>변환된 값</returns>
/// <exception cref="InvalidCastException">변환할 수 없는 타입인 경우</exception>
/// <exception cref="ArgumentNullException">value가 null인 경우</exception>
public T ConvertTo<T>(object value)
{
    if (value == null)
        throw new ArgumentNullException(nameof(value));

    return (T)Convert.ChangeType(value, typeof(T));
}
```
