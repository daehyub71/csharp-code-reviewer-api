# Windows 설치 파일 생성 가이드

## 개요

이 가이드는 C# Code Reviewer 포터블 패키지를 Windows 설치 파일(.exe)로 변환하는 방법을 설명합니다.

**설치 파일 특징:**
- 사용자 친화적 설치 마법사
- 자동 바탕화면/시작 메뉴 바로가기 생성
- 깔끔한 제거 프로그램
- 압축된 단일 설치 파일 (~1.5GB)
- 관리자 권한 불필요 (사용자 폴더에 설치)

---

## 필수 준비물

### 1. Inno Setup 설치

**다운로드:**
- [Inno Setup 6.3.3 다운로드](https://jrsoftware.org/isdl.php)
- 파일: `innosetup-6.3.3.exe` (약 3.5MB)

**설치 방법:**
1. `innosetup-6.3.3.exe` 실행
2. 기본 설정으로 설치 진행
3. "Inno Setup Preprocessor" 옵션 체크 (권장)
4. 설치 완료 후 실행 → `ISCC.exe` 위치 확인
   - 기본 경로: `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`

### 2. 포터블 패키지 준비

설치 파일을 만들기 전에 포터블 패키지가 완성되어 있어야 합니다.

**필수 구조:**
```
CodeReviewer_Portable/
├── CodeReviewer.exe           # PyInstaller로 빌드된 메인 실행 파일
├── ollama_portable/
│   ├── ollama.exe             # Ollama 실행 파일
│   └── models/
│       ├── blobs/             # Phi-3-mini 모델 파일
│       └── manifests/
├── config/
│   └── settings.json          # 기본 설정
└── (기타 리소스 파일)
```

**준비 체크리스트:**
- [ ] `CodeReviewer.exe` 파일 존재 (약 50-100MB)
- [ ] `ollama_portable/ollama.exe` 존재
- [ ] `ollama_portable/models/` 에 Phi-3-mini 모델 존재 (~2.2GB)
- [ ] `config/settings.json` 존재
- [ ] 프로그램 실행 테스트 완료

---

## 설치 파일 생성 프로세스

### Step 1: 프로젝트 파일 준비

```bash
cd /Users/sunchulkim/src/csharp-code-reviewer

# 디렉토리 구조 확인
ls -la CodeReviewer_Portable/
```

**예상 크기:**
- CodeReviewer.exe: ~50-100MB
- ollama_portable/: ~2.3GB
- 총 합계: ~2.5GB
- 설치 파일 (압축 후): ~1.5GB

### Step 2: Inno Setup 스크립트 수정

`scripts/CodeReviewer_Setup.iss` 파일을 열고 필요 시 수정:

```ini
[Setup]
AppVersion=1.0.0                    ; 버전 번호 수정
AppPublisher=Your Company Name      ; 회사명 수정
DefaultDirName={autopf}\CSharpCodeReviewer  ; 설치 경로

; 아이콘 설정 (선택 사항)
SetupIconFile=..\resources\icons\app_icon.ico
```

**주요 설정 항목:**

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `AppVersion` | 1.0.0 | 버전 번호 |
| `DefaultDirName` | `{autopf}\CSharpCodeReviewer` | 설치 경로 (Program Files) |
| `OutputBaseFilename` | `CSharpCodeReviewer_Setup_v1.0.0` | 출력 파일명 |
| `Compression` | lzma2/max | 압축 알고리즘 (최대 압축) |
| `ArchitecturesAllowed` | x64 | 64비트 전용 |
| `MinVersion` | 10.0.22000 | Windows 11 이상 |

### Step 3: 설치 파일 빌드

#### 방법 1: Inno Setup GUI 사용 (초보자 권장)

1. **Inno Setup Compiler** 실행
2. **File → Open** → `scripts/CodeReviewer_Setup.iss` 선택
3. **Build → Compile** 클릭 (또는 F9)
4. 진행 상황 확인 (약 5-10분 소요)
5. 완료 후 `dist/installer/` 폴더에 생성됨

#### 방법 2: 명령줄 사용 (자동화)

**Windows (cmd):**
```cmd
cd C:\path\to\csharp-code-reviewer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" scripts\CodeReviewer_Setup.iss
```

**macOS/Linux (Wine 필요):**
```bash
cd /Users/sunchulkim/src/csharp-code-reviewer
wine "C:/Program Files (x86)/Inno Setup 6/ISCC.exe" scripts/CodeReviewer_Setup.iss
```

#### 방법 3: Python 자동화 스크립트

```bash
python scripts/build_installer.py
```

### Step 4: 설치 파일 테스트

생성된 설치 파일 위치:
```
dist/installer/CSharpCodeReviewer_Setup_v1.0.0.exe
```

**테스트 체크리스트:**
1. [ ] 파일 크기 확인 (~1.5GB)
2. [ ] 더블클릭으로 실행 가능
3. [ ] 설치 마법사 UI 정상 표시
4. [ ] 설치 진행률 표시 정상
5. [ ] 설치 완료 후 바로가기 생성 확인
6. [ ] 프로그램 실행 테스트
7. [ ] Ollama 자동 시작 확인
8. [ ] 제거 프로그램 동작 확인

---

## 설치 파일 커스터마이징

### 1. 설치 아이콘 변경

**필요 파일:** `resources/icons/app_icon.ico` (256x256, ICO 형식)

```ini
[Setup]
SetupIconFile=..\resources\icons\app_icon.ico
```

**아이콘 생성 도구:**
- [IcoFX](https://icofx.ro/) (무료)
- [ConvertICO](https://convertico.com/) (온라인)

### 2. 라이선스 파일 추가

```ini
[Setup]
LicenseFile=..\LICENSE
```

사용자가 설치 중 라이선스에 동의해야 설치 진행 가능.

### 3. 설치 전 안내 메시지

`docs/INSTALLATION_NOTES.txt` 파일 생성:

```text
C# Code Reviewer 설치를 시작합니다.

시스템 요구사항:
- Windows 11 (64-bit)
- CPU: 4코어 이상
- RAM: 8GB 이상
- 디스크 공간: 5GB 이상

설치 후 Ollama 서버가 자동으로 시작됩니다.
```

```ini
[Setup]
InfoBeforeFile=..\docs\INSTALLATION_NOTES.txt
```

### 4. 바탕화면 바로가기 기본 생성

```ini
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked
; Flags: checked → 기본적으로 체크됨
```

### 5. 설치 언어 추가

```ini
[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
```

---

## 고급 기능

### 1. 환경 변수 설정

Ollama 경로를 환경 변수에 추가:

```pascal
[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  OllamaPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    // OLLAMA_MODELS 환경 변수 설정
    OllamaPath := ExpandConstant('{app}\ollama_portable\models');
    RegWriteStringValue(HKCU, 'Environment', 'OLLAMA_MODELS', OllamaPath);
  end;
end;
```

### 2. 기존 버전 자동 제거

```pascal
[Code]
function InitializeSetup(): Boolean;
var
  UninstallPath: String;
  ResultCode: Integer;
begin
  Result := True;

  // 기존 버전 확인
  if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1', 'UninstallString', UninstallPath) then
  begin
    if MsgBox('기존 버전이 설치되어 있습니다. 제거하시겠습니까?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec(RemoveQuotes(UninstallPath), '/SILENT', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;
```

### 3. 설치 중 진행률 상세 표시

```pascal
[Code]
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpInstalling then
  begin
    WizardForm.ProgressGauge.Style := npbstMarquee;
    WizardForm.StatusLabel.Caption := 'Ollama 및 Phi-3-mini 모델을 설치하고 있습니다...';
  end;
end;
```

---

## 자동화 스크립트

`scripts/build_installer.py` 파일 생성:

```python
#!/usr/bin/env python3
"""
Windows 설치 파일 자동 빌드 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

# 설정
PROJECT_ROOT = Path(__file__).parent.parent
ISS_FILE = PROJECT_ROOT / "scripts" / "CodeReviewer_Setup.iss"
ISCC_PATH = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
OUTPUT_DIR = PROJECT_ROOT / "dist" / "installer"

def check_inno_setup():
    """Inno Setup 설치 확인"""
    if not Path(ISCC_PATH).exists():
        print(f"❌ Inno Setup이 설치되지 않았습니다.")
        print(f"   다운로드: https://jrsoftware.org/isdl.php")
        return False
    print(f"✅ Inno Setup 발견: {ISCC_PATH}")
    return True

def check_portable_package():
    """포터블 패키지 확인"""
    portable_dir = PROJECT_ROOT / "CodeReviewer_Portable"

    if not portable_dir.exists():
        print(f"❌ 포터블 패키지가 없습니다: {portable_dir}")
        return False

    # 필수 파일 체크
    required_files = [
        portable_dir / "CodeReviewer.exe",
        portable_dir / "ollama_portable" / "ollama.exe",
    ]

    for file_path in required_files:
        if not file_path.exists():
            print(f"❌ 필수 파일 없음: {file_path}")
            return False
        print(f"✅ {file_path.name} 확인")

    return True

def build_installer():
    """설치 파일 빌드"""
    print(f"\n📦 설치 파일 빌드 시작...")
    print(f"   ISS 파일: {ISS_FILE}")

    try:
        result = subprocess.run(
            [ISCC_PATH, str(ISS_FILE)],
            capture_output=True,
            text=True,
            check=True
        )

        print(result.stdout)
        print(f"\n✅ 설치 파일 생성 완료!")
        print(f"   위치: {OUTPUT_DIR}")

        # 생성된 파일 목록
        if OUTPUT_DIR.exists():
            for file in OUTPUT_DIR.glob("*.exe"):
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"   - {file.name} ({size_mb:.1f} MB)")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패:")
        print(e.stderr)
        return False

def main():
    print("=" * 60)
    print("C# Code Reviewer - Windows 설치 파일 빌드")
    print("=" * 60)

    # 1. Inno Setup 확인
    if not check_inno_setup():
        sys.exit(1)

    # 2. 포터블 패키지 확인
    if not check_portable_package():
        sys.exit(1)

    # 3. 빌드
    if not build_installer():
        sys.exit(1)

    print("\n🎉 완료!")

if __name__ == "__main__":
    main()
```

**사용법:**
```bash
python scripts/build_installer.py
```

---

## 트러블슈팅

### 문제 1: "Inno Setup을 찾을 수 없습니다"

**원인**: ISCC.exe 경로가 잘못됨

**해결책**:
```bash
# Windows에서 ISCC.exe 찾기
where iscc

# 스크립트에서 경로 수정
ISCC_PATH = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

### 문제 2: "파일을 찾을 수 없습니다 (Source path not found)"

**원인**: .iss 파일의 Source 경로가 잘못됨

**해결책**:
```ini
; 상대 경로 확인
Source: "..\CodeReviewer_Portable\CodeReviewer.exe"; DestDir: "{app}"
; → CodeReviewer_Portable 폴더가 scripts/ 상위에 있어야 함
```

### 문제 3: 빌드는 되지만 크기가 너무 작음 (~100MB)

**원인**: Ollama 모델 파일이 포함되지 않음

**해결책**:
```ini
; recursesubdirs 플래그 확인
Source: "..\CodeReviewer_Portable\ollama_portable\*"; DestDir: "{app}\ollama_portable"; Flags: ignoreversion recursesubdirs createallsubdirs
```

### 문제 4: 설치 후 Ollama 실행 안 됨

**원인**: 실행 권한 또는 경로 문제

**해결책**:
```ini
[Dirs]
Name: "{app}\ollama_portable"; Permissions: users-full
```

### 문제 5: "관리자 권한이 필요합니다"

**원인**: `PrivilegesRequired=admin` 설정

**해결책**:
```ini
[Setup]
PrivilegesRequired=lowest
; 사용자 프로그램 폴더에 설치 (관리자 권한 불필요)
```

---

## 배포 체크리스트

설치 파일 배포 전 최종 확인:

### 1. 빌드 검증
- [ ] 설치 파일 크기: 1.5GB ~ 2GB
- [ ] 파일명: `CSharpCodeReviewer_Setup_v1.0.0.exe`
- [ ] 디지털 서명 (선택 사항)

### 2. 기능 테스트
- [ ] 깨끗한 Windows 11 VM에서 설치 테스트
- [ ] 설치 중 에러 없음
- [ ] 설치 완료 후 바로가기 생성됨
- [ ] 프로그램 실행 시 Ollama 자동 시작
- [ ] 코드 분석 기능 정상 동작
- [ ] 리포트 생성 및 저장 정상
- [ ] 제거 프로그램 정상 동작

### 3. 문서 준비
- [ ] README.md 업데이트 (다운로드 링크)
- [ ] INSTALLATION_NOTES.txt 작성
- [ ] 릴리즈 노트 작성
- [ ] 스크린샷 준비

### 4. 릴리즈
- [ ] GitHub Release 생성
- [ ] 설치 파일 업로드
- [ ] 체크섬(SHA256) 제공
- [ ] 사용자 가이드 링크

---

## 참고 자료

### Inno Setup 공식 문서
- [Inno Setup 다운로드](https://jrsoftware.org/isdl.php)
- [Inno Setup 문서](https://jrsoftware.org/ishelp/)
- [Pascal Scripting 레퍼런스](https://jrsoftware.org/ishelp/index.php?topic=scriptintro)

### 예제 스크립트
- [Inno Setup 예제 모음](https://github.com/jrsoftware/issrc/tree/main/Examples)
- [대용량 파일 압축 최적화](https://stackoverflow.com/questions/tagged/inno-setup)

---

**마지막 업데이트**: 2025-01-08
**작성자**: AI Assistant
**버전**: 1.0
