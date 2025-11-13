; Inno Setup Script for C# Code Reviewer
; Inno Setup 6.0 이상 필요
; 다운로드: https://jrsoftware.org/isdl.php

[Setup]
; 기본 정보
AppName=C# Code Reviewer
AppVersion=1.0.0
AppPublisher=Your Company Name
AppPublisherURL=https://github.com/yourusername/csharp-code-reviewer
AppSupportURL=https://github.com/yourusername/csharp-code-reviewer/issues
AppUpdatesURL=https://github.com/yourusername/csharp-code-reviewer/releases
DefaultDirName={autopf}\CSharpCodeReviewer
DefaultGroupName=C# Code Reviewer
AllowNoIcons=yes
LicenseFile=..\LICENSE
InfoBeforeFile=..\docs\INSTALLATION_NOTES.txt
OutputDir=..\dist\installer
OutputBaseFilename=CSharpCodeReviewer_Setup_v1.0.0
SetupIconFile=..\resources\icons\app_icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; 최소 시스템 요구사항
MinVersion=10.0.22000
; Windows 11 (Build 22000) 이상

; 권한 설정
PrivilegesRequired=lowest
; 관리자 권한 불필요 (사용자 프로그램 폴더에 설치)

; 설치 제거 옵션
UninstallDisplayIcon={app}\CodeReviewer.exe
UninstallDisplayName=C# Code Reviewer

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; 메인 실행 파일
Source: "..\CodeReviewer_Portable\CodeReviewer.exe"; DestDir: "{app}"; Flags: ignoreversion

; Ollama 포터블
Source: "..\CodeReviewer_Portable\ollama_portable\*"; DestDir: "{app}\ollama_portable"; Flags: ignoreversion recursesubdirs createallsubdirs

; 설정 파일
Source: "..\CodeReviewer_Portable\config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs

; 문서
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\USER_GUIDE.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\docs\TROUBLESHOOTING.md"; DestDir: "{app}\docs"; Flags: ignoreversion

; 주의: 여기서 파일 추가 시 주의사항
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Dirs]
; 사용자 데이터 디렉토리 생성
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\reports"; Permissions: users-full
Name: "{app}\reports\markdown"; Permissions: users-full
Name: "{app}\reports\html"; Permissions: users-full

[Icons]
; 시작 메뉴 바로가기
Name: "{group}\C# Code Reviewer"; Filename: "{app}\CodeReviewer.exe"
Name: "{group}\{cm:UninstallProgram,C# Code Reviewer}"; Filename: "{uninstallexe}"

; 바탕화면 바로가기 (선택 사항)
Name: "{autodesktop}\C# Code Reviewer"; Filename: "{app}\CodeReviewer.exe"; Tasks: desktopicon

; 빠른 실행 바로가기 (선택 사항)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\C# Code Reviewer"; Filename: "{app}\CodeReviewer.exe"; Tasks: quicklaunchicon

[Run]
; 설치 완료 후 실행 옵션
Filename: "{app}\CodeReviewer.exe"; Description: "{cm:LaunchProgram,C# Code Reviewer}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 제거 시 생성된 파일도 삭제
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\reports"

[Code]
// Pascal Script 코드 (고급 기능)

// 설치 전 체크
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;

  // 디스크 공간 체크 (최소 5GB)
  if GetSpaceOnDisk(ExpandConstant('{app}')) < 5 * 1024 * 1024 * 1024 then
  begin
    MsgBox('설치에 필요한 디스크 공간이 부족합니다. 최소 5GB가 필요합니다.', mbError, MB_OK);
    Result := False;
    Exit;
  end;

  // Windows 버전 체크
  if not (CheckForWindows11OrLater()) then
  begin
    if MsgBox('이 프로그램은 Windows 11에서 테스트되었습니다. ' +
              '계속하시겠습니까?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;
end;

function CheckForWindows11OrLater(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  // Windows 11: Build 22000 이상
  Result := (Version.Major >= 10) and (Version.Build >= 22000);
end;

// 설치 진행 중 페이지
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpInstalling then
  begin
    WizardForm.StatusLabel.Caption := 'C# Code Reviewer를 설치하고 있습니다...';
  end;
end;

// 설치 완료 후
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 여기서 추가 설정 작업 가능
    // 예: 환경 변수 설정, 레지스트리 등록 등
  end;
end;

[Messages]
; 한글 메시지 커스터마이징
korean.WelcomeLabel2=이 프로그램은 [name/ver]을(를) 설치합니다.%n%n설치를 계속하기 전에 다른 모든 응용 프로그램을 닫는 것이 좋습니다.%n%n주의: 이 프로그램은 약 2.5GB의 디스크 공간이 필요합니다.
korean.FinishedHeadingLabel=C# Code Reviewer 설치 완료
korean.FinishedLabelNoIcons=C# Code Reviewer 설치가 완료되었습니다.%n%n시작 메뉴에서 프로그램을 실행할 수 있습니다.
korean.FinishedLabel=C# Code Reviewer 설치가 완료되었습니다.%n%n바로가기 아이콘을 사용하여 프로그램을 실행할 수 있습니다.

[CustomMessages]
; 커스텀 메시지
korean.LaunchProgram=설치 후 C# Code Reviewer 실행
english.LaunchProgram=Launch C# Code Reviewer after installation
korean.AdditionalIcons=추가 아이콘:
english.AdditionalIcons=Additional icons:
