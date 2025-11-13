# 문제 해결 가이드 (Troubleshooting)

## 목차
1. [Ollama 서버 관련 문제](#ollama-서버-관련-문제)
2. [모델 로딩 문제](#모델-로딩-문제)
3. [성능 및 타임아웃 문제](#성능-및-타임아웃-문제)
4. [파일 처리 문제](#파일-처리-문제)
5. [UI 관련 문제](#ui-관련-문제)

---

## Ollama 서버 관련 문제

### ❌ 문제: "timed out waiting for llama runner to start"

**증상:**
```
코드 분석 중 오류가 발생했습니다:
timed out waiting for llama runner to start - progress 0.00 - (status code: 500)
```

**원인:**
- Ollama 서버가 Phi-3-mini 모델을 로드하는 데 시간이 너무 오래 걸림
- 시스템 리소스(CPU/RAM) 부족
- 모델이 제대로 설치되지 않음

**해결 방법:**

#### Step 1: Ollama 서버 상태 확인

```bash
# Windows (PowerShell)
# Ollama 프로세스 확인
Get-Process ollama

# Ollama 서버 상태 확인
curl http://localhost:11434/api/tags
```

**정상 응답 예시:**
```json
{
  "models": [
    {
      "name": "phi3:mini",
      "modified_at": "2025-01-08T12:00:00Z",
      "size": 2200000000
    }
  ]
}
```

#### Step 2: Ollama 서버 수동 시작

```bash
# 기존 Ollama 프로세스 종료
taskkill /F /IM ollama.exe

# Ollama 서버 시작 (백그라운드)
start ollama serve
```

**또는 포터블 모드:**
```bash
cd CodeReviewer_Portable/ollama_portable
start ollama.exe serve
```

#### Step 3: Phi-3-mini 모델 확인 및 재다운로드

```bash
# 모델 리스트 확인
ollama list

# Phi-3-mini 모델 재다운로드 (필요 시)
ollama pull phi3:mini
```

#### Step 4: 모델 수동 로드 테스트

```bash
# 간단한 프롬프트로 모델 로드 테스트
ollama run phi3:mini "Hello, how are you?"
```

**정상 작동 시:**
```
Hello! I'm doing well, thank you for asking. How can I help you today?
```

**실패 시:**
- 메모리 부족 에러 → RAM 확보 필요 (최소 8GB)
- 모델 파일 손상 → `ollama rm phi3:mini` 후 재다운로드

#### Step 5: 프로그램 재시작

1. C# Code Reviewer 종료
2. Ollama 서버가 완전히 로드될 때까지 대기 (30초~1분)
3. 프로그램 재실행

---

### ❌ 문제: "Ollama 서버에 연결할 수 없습니다"

**증상:**
```
Ollama: ❌ 연결 실패
Cannot connect to Ollama server at http://localhost:11434
```

**원인:**
- Ollama 서버가 실행되지 않음
- 포트 11434가 다른 프로세스에 의해 사용 중
- 방화벽이 연결을 차단

**해결 방법:**

#### Step 1: 포트 사용 확인

```bash
# Windows
netstat -ano | findstr :11434
```

**다른 프로세스가 사용 중이면:**
```bash
# PID 확인 후 종료
taskkill /F /PID <PID번호>
```

#### Step 2: 방화벽 예외 추가

1. **Windows Defender 방화벽** 열기
2. **고급 설정** → **인바운드 규칙**
3. **새 규칙** 추가:
   - 프로그램: `ollama.exe`
   - 포트: TCP 11434
   - 작업: 연결 허용

#### Step 3: Ollama 재시작

```bash
# 완전히 종료
taskkill /F /IM ollama.exe

# 1분 대기

# 재시작
start ollama serve
```

---

## 모델 로딩 문제

### ❌ 문제: "Model phi3:mini not found"

**증상:**
```
에러: 모델을 찾을 수 없습니다 (phi3:mini)
```

**해결 방법:**

```bash
# 모델 다운로드
ollama pull phi3:mini

# 다운로드 완료 확인 (약 2.2GB)
ollama list
```

**예상 출력:**
```
NAME            ID              SIZE    MODIFIED
phi3:mini       abc123def456    2.2 GB  2 minutes ago
```

---

### ❌ 문제: 모델 다운로드가 너무 느림

**증상:**
- `ollama pull phi3:mini` 명령어가 10분 이상 소요

**해결 방법:**

#### 방법 A: 수동 다운로드 (권장)

1. **Ollama 모델 디렉토리 확인:**
```bash
# Windows
echo %USERPROFILE%\.ollama\models
# 예: C:\Users\YourName\.ollama\models
```

2. **모델 파일 직접 다운로드:**
   - [Ollama Library - phi3:mini](https://ollama.com/library/phi3:mini)
   - 또는 [Hugging Face - microsoft/Phi-3-mini](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf)

3. **파일 배치:**
```
C:\Users\YourName\.ollama\models\
├── blobs\
│   └── sha256-<hash>  (2.2GB GGUF 파일)
└── manifests\
    └── registry.ollama.ai\library\phi3\mini
```

4. **Ollama 서버 재시작:**
```bash
taskkill /F /IM ollama.exe
start ollama serve
```

5. **모델 확인:**
```bash
ollama list
```

---

## 성능 및 타임아웃 문제

### ❌ 문제: 코드 분석이 너무 느림 (30초 이상)

**증상:**
- 간단한 코드도 분석에 20~30초 이상 소요
- 프로그램이 멈춘 것처럼 보임

**원인:**
- CPU 기반 추론 (GPU 없음)
- 시스템 리소스 부족
- 프롬프트가 너무 김

**해결 방법:**

#### Step 1: 시스템 리소스 확인

**작업 관리자 (Ctrl+Shift+Esc) 확인:**
- **CPU 사용률**: Ollama가 80~100% 사용 중 (정상)
- **메모리**: 3~4GB 이상 사용 중 (정상)
- **디스크**: SSD 권장

**다른 프로그램 종료:**
- 브라우저 (Chrome, Edge)
- IDE (Visual Studio)
- 기타 무거운 애플리케이션

#### Step 2: 코드 크기 줄이기

- **100줄 이하**: 권장 (5~10초)
- **100~300줄**: 가능 (10~20초)
- **300줄 이상**: 분할 권장

**큰 파일 분할 방법:**
1. 클래스별로 파일 분리
2. 주요 메서드만 먼저 분석
3. 나머지는 별도 분석

#### Step 3: 프롬프트 최적화 (향후 버전)

현재는 자동으로 최적화되어 있지만, 필요 시 설정 파일 수정:

```json
// config/settings.json
{
  "ollama": {
    "timeout": 60,  // 60초로 증가
    "num_predict": 2048  // 출력 토큰 수 제한
  }
}
```

---

### ❌ 문제: 메모리 부족 에러

**증상:**
```
Ollama error: out of memory
```

**해결 방법:**

1. **다른 프로그램 종료**
2. **시스템 재시작** (메모리 정리)
3. **가상 메모리 증가:**
   - 제어판 → 시스템 → 고급 시스템 설정
   - 성능 → 설정 → 고급 → 가상 메모리
   - 페이징 파일 크기: 16384 MB (16GB) 설정

4. **더 작은 모델 사용 (선택적):**
```bash
# Phi-3-mini 대신 더 작은 모델
ollama pull phi3:3.8b  # 원래 phi3:mini와 동일
```

---

## 파일 처리 문제

### ❌ 문제: "파일 인코딩 오류"

**증상:**
```
파일을 읽을 수 없습니다: UnicodeDecodeError
```

**원인:**
- C# 파일이 UTF-8이 아닌 다른 인코딩 (EUC-KR, CP949 등)

**해결 방법:**

#### Visual Studio에서 인코딩 변경:

1. 파일 열기
2. **파일 → 다른 이름으로 저장**
3. **저장** 버튼 옆 화살표 클릭 → **인코딩하여 저장**
4. **유니코드(UTF-8, 서명 없음 - 코드 페이지 65001)** 선택
5. 저장

#### 또는 VS Code:

1. 파일 열기
2. 오른쪽 하단 인코딩 클릭 (예: "EUC-KR")
3. **인코딩하여 다시 열기** → **UTF-8**
4. **파일 저장**

---

### ❌ 문제: 파일 크기 제한 초과

**증상:**
```
파일이 너무 큽니다 (최대 1MB)
```

**해결 방법:**

1. **파일 분할**: 큰 클래스를 여러 파일로 나누기
2. **제한 해제** (권장하지 않음):

`app/ui/file_upload_widget.py` 수정:
```python
MAX_FILE_SIZE_MB = 5  # 1 → 5로 증가
```

---

## UI 관련 문제

### ❌ 문제: 프로그램이 실행되지 않음

**증상:**
- 더블클릭해도 아무 반응 없음
- 또는 즉시 종료됨

**해결 방법:**

#### Step 1: 콘솔 모드로 실행

```bash
# Windows (PowerShell)
cd "C:\path\to\CodeReviewer_Portable"
.\CodeReviewer.exe
```

에러 메시지 확인 후 아래 케이스 참고.

#### Step 2: 로그 파일 확인

```bash
# logs/app.log 파일 열기
notepad logs\app.log
```

**일반적인 에러:**

**"No module named 'PySide6'"**
→ EXE 빌드 실패, PyInstaller 재빌드 필요

**"Ollama not found"**
→ `ollama_portable/ollama.exe` 파일 확인

---

### ❌ 문제: UI가 깨져 보임 (High DPI)

**증상:**
- 텍스트가 흐릿함
- 버튼 크기가 이상함

**해결 방법:**

**Windows 11 호환성 설정:**

1. `CodeReviewer.exe` 우클릭 → **속성**
2. **호환성** 탭
3. **높은 DPI 설정 변경**
4. **높은 DPI 크기 조정 동작 재정의** 체크
5. **시스템(고급)** 선택
6. 확인

---

### ❌ 문제: Markdown 리포트가 제대로 렌더링되지 않음

**증상:**
- 코드 블록 하이라이팅 없음
- 표가 깨짐

**해결 방법:**

#### 방법 A: 리포트 파일 직접 열기

```bash
# HTML 버전 열기 (권장)
start reports\html\<파일명>.html
```

브라우저에서 열면 완벽하게 렌더링됩니다.

#### 방법 B: 리포트 히스토리에서 열기

1. **View → 리포트 히스토리 (Ctrl+H)**
2. 리포트 더블클릭
3. 브라우저에서 HTML 자동 열림

---

## 기타 문제

### ❌ 문제: "리포트 저장 실패"

**증상:**
```
리포트를 저장할 수 없습니다: Permission denied
```

**해결 방법:**

1. **관리자 권한 확인**:
   - 프로그램을 관리자 권한으로 실행하지 마세요 (일반 사용자 권한 권장)

2. **디렉토리 권한 확인**:
```bash
# reports/ 폴더에 쓰기 권한 확인
icacls reports
```

3. **다른 위치에 저장**:
   - 분석 후 **Save Report** 클릭
   - 다른 폴더 선택 (예: 내 문서)

---

### ❌ 문제: 프로그램 종료 시 Ollama가 종료되지 않음

**증상:**
- 프로그램 종료 후에도 Ollama 프로세스 남아있음
- 메모리 계속 사용 중

**해결 방법:**

#### 수동 종료:
```bash
taskkill /F /IM ollama.exe
```

#### 자동 종료 (향후 버전에서 개선 예정):
- 프로그램 종료 시 **5초 대기** 후 강제 종료
- 정상 종료되지 않으면 작업 관리자에서 수동 종료

---

## 성능 튜닝 팁

### 💡 추론 속도 향상

1. **SSD 사용**: 모델 로딩 속도 2배 향상
2. **RAM 16GB 이상**: 스왑 메모리 사용 방지
3. **CPU 코어 수**: 4코어 이상 권장
4. **백그라운드 앱 종료**: Chrome, Slack 등

### 💡 배치 분석 최적화

- **파일 개수 제한**: 한 번에 10~20개씩
- **작은 파일부터**: 큰 파일은 나중에
- **취소 기능 활용**: 문제 발생 시 즉시 중단

---

## 추가 지원

### 로그 파일 위치

```
CodeReviewer_Portable/
├── logs/
│   ├── app.log          # 애플리케이션 로그
│   └── ollama.log       # Ollama 서버 로그
└── reports/
    └── reports.db       # 리포트 히스토리 DB
```

### 디버그 모드 실행

```bash
# 디버그 모드 (콘솔 표시)
set DEBUG=1
CodeReviewer.exe
```

### 문제 리포트 시 포함할 정보

1. **에러 메시지** (스크린샷 또는 복사)
2. **로그 파일** (`logs/app.log`)
3. **시스템 정보**:
   - Windows 버전
   - CPU, RAM 사양
   - 디스크 공간
4. **재현 방법** (어떤 동작을 했을 때 발생했는지)

---

**마지막 업데이트**: 2025-01-08
**버전**: 1.0
