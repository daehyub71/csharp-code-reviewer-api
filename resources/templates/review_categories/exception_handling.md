# Exception 처리

## 설명
적절한 예외 처리 및 에러 핸들링을 통해 프로그램의 안정성을 향상시킵니다.
예외를 명확하게 처리하고 사용자에게 의미 있는 에러 메시지를 제공합니다.

## 규칙
- try-catch 블록으로 예외 처리
- 구체적인 예외 타입 사용 (Exception보다 DivideByZeroException 등)
- 예외 메시지를 명확하게 작성
- finally 블록으로 정리 작업 수행
- 예외를 무시하지 않기 (빈 catch 블록 금지)
- 필요시 예외를 다시 던지기 (throw;)
- 커스텀 예외 클래스 사용 고려

## Before 예제
```csharp
public int Divide(int a, int b)
{
    return a / b;
}

public void ReadConfig()
{
    var config = File.ReadAllText("config.json");
    ProcessConfig(config);
}
```

## After 예제
```csharp
public int Divide(int a, int b)
{
    if (b == 0)
        throw new DivideByZeroException("제수는 0이 될 수 없습니다.");

    return a / b;
}

public void ReadConfig()
{
    try
    {
        var config = File.ReadAllText("config.json");
        ProcessConfig(config);
    }
    catch (FileNotFoundException ex)
    {
        logger.LogError($"설정 파일을 찾을 수 없습니다: {ex.Message}");
        throw new ConfigurationException("설정 파일이 존재하지 않습니다.", ex);
    }
    catch (JsonException ex)
    {
        logger.LogError($"설정 파일 파싱 오류: {ex.Message}");
        throw new ConfigurationException("설정 파일 형식이 잘못되었습니다.", ex);
    }
}
```
