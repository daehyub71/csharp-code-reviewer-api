#!/usr/bin/env python3
"""
Windows 설치 파일 자동 빌드 스크립트

Usage:
    python scripts/build_installer.py
    python scripts/build_installer.py --clean
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from datetime import datetime

# 설정
PROJECT_ROOT = Path(__file__).parent.parent
ISS_FILE = PROJECT_ROOT / "scripts" / "CodeReviewer_Setup.iss"
OUTPUT_DIR = PROJECT_ROOT / "dist" / "installer"
PORTABLE_DIR = PROJECT_ROOT / "CodeReviewer_Portable"

# Windows 전용 경로
if sys.platform == "win32":
    ISCC_PATH = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
else:
    # macOS/Linux에서는 Wine 필요
    ISCC_PATH = "wine"  # wine "C:/Program Files (x86)/Inno Setup 6/ISCC.exe"


class Colors:
    """터미널 컬러 (ANSI)"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """헤더 출력"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text):
    """성공 메시지"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    """에러 메시지"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text):
    """경고 메시지"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text):
    """정보 메시지"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def check_inno_setup():
    """Inno Setup 설치 확인"""
    print_info("Inno Setup 확인 중...")

    if sys.platform != "win32":
        print_warning("Windows가 아닌 환경입니다. Wine이 필요합니다.")
        # Wine 체크
        result = subprocess.run(["which", "wine"], capture_output=True)
        if result.returncode != 0:
            print_error("Wine이 설치되지 않았습니다.")
            print_info("macOS: brew install wine-stable")
            print_info("Linux: sudo apt install wine")
            return False
        print_success("Wine 발견")
        return True

    if not Path(ISCC_PATH).exists():
        print_error(f"Inno Setup이 설치되지 않았습니다.")
        print_info(f"예상 경로: {ISCC_PATH}")
        print_info("다운로드: https://jrsoftware.org/isdl.php")
        return False

    print_success(f"Inno Setup 발견: {ISCC_PATH}")
    return True


def check_portable_package():
    """포터블 패키지 확인"""
    print_info("포터블 패키지 확인 중...")

    if not PORTABLE_DIR.exists():
        print_error(f"포터블 패키지가 없습니다: {PORTABLE_DIR}")
        print_info("먼저 포터블 패키지를 생성하세요:")
        print_info("  1. python scripts/build_exe.py")
        print_info("  2. python scripts/bundle_ollama.py")
        return False

    # 필수 파일 체크
    required_files = {
        "CodeReviewer.exe": PORTABLE_DIR / "CodeReviewer.exe",
        "ollama.exe": PORTABLE_DIR / "ollama_portable" / "ollama.exe",
        "settings.json": PORTABLE_DIR / "config" / "settings.json",
    }

    missing_files = []
    for name, file_path in required_files.items():
        if not file_path.exists():
            missing_files.append(name)
            print_error(f"필수 파일 없음: {name} ({file_path})")
        else:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print_success(f"{name} 확인 ({size_mb:.1f} MB)")

    if missing_files:
        return False

    # 모델 파일 체크 (선택적 경고)
    models_dir = PORTABLE_DIR / "ollama_portable" / "models"
    if models_dir.exists():
        model_size = sum(f.stat().st_size for f in models_dir.rglob('*') if f.is_file())
        model_size_gb = model_size / (1024 * 1024 * 1024)

        if model_size_gb < 1.0:
            print_warning(f"Ollama 모델 크기가 작습니다: {model_size_gb:.2f} GB")
            print_warning("Phi-3-mini 모델이 올바르게 설치되었는지 확인하세요.")
        else:
            print_success(f"Ollama 모델 확인 ({model_size_gb:.2f} GB)")
    else:
        print_warning("Ollama 모델 디렉토리가 없습니다.")

    return True


def check_iss_file():
    """ISS 파일 확인"""
    print_info("ISS 스크립트 확인 중...")

    if not ISS_FILE.exists():
        print_error(f"ISS 파일이 없습니다: {ISS_FILE}")
        return False

    print_success(f"ISS 파일 발견: {ISS_FILE}")

    # ISS 파일 내용 간단히 검증
    with open(ISS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

        # 필수 섹션 체크
        required_sections = ["[Setup]", "[Files]", "[Icons]"]
        for section in required_sections:
            if section not in content:
                print_error(f"ISS 파일에 {section} 섹션이 없습니다.")
                return False

    print_success("ISS 파일 구조 정상")
    return True


def clean_build_artifacts():
    """이전 빌드 아티팩트 삭제"""
    print_info("이전 빌드 아티팩트 정리 중...")

    if OUTPUT_DIR.exists():
        try:
            shutil.rmtree(OUTPUT_DIR)
            print_success(f"삭제됨: {OUTPUT_DIR}")
        except Exception as e:
            print_warning(f"삭제 실패: {e}")

    # Inno Setup 임시 파일
    temp_files = [
        PROJECT_ROOT / "Output",  # 기본 출력 디렉토리
    ]

    for temp_file in temp_files:
        if temp_file.exists():
            try:
                shutil.rmtree(temp_file)
                print_success(f"삭제됨: {temp_file}")
            except Exception as e:
                print_warning(f"삭제 실패: {e}")


def build_installer():
    """설치 파일 빌드"""
    print_header("설치 파일 빌드 시작")

    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 빌드 명령어
    if sys.platform == "win32":
        cmd = [ISCC_PATH, str(ISS_FILE)]
    else:
        # Wine 사용
        wine_iss_path = str(ISS_FILE).replace("/", "\\")
        cmd = [ISCC_PATH, f'C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe', wine_iss_path]

    print_info(f"명령어: {' '.join(cmd)}")
    print_info(f"ISS 파일: {ISS_FILE}")
    print_info(f"출력 디렉토리: {OUTPUT_DIR}")

    try:
        # 시작 시간
        start_time = datetime.now()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=PROJECT_ROOT
        )

        # 종료 시간
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 출력 표시
        if result.stdout:
            print("\n" + result.stdout)

        print_success(f"설치 파일 생성 완료! (소요 시간: {duration:.1f}초)")

        # 생성된 파일 목록
        if OUTPUT_DIR.exists():
            print_info("\n생성된 파일:")
            for file in OUTPUT_DIR.glob("*.exe"):
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  📦 {file.name} ({size_mb:.1f} MB)")
                print(f"     경로: {file.absolute()}")

        return True

    except subprocess.CalledProcessError as e:
        print_error("빌드 실패!")
        if e.stdout:
            print("\nStdout:")
            print(e.stdout)
        if e.stderr:
            print("\nStderr:")
            print(e.stderr)
        return False
    except Exception as e:
        print_error(f"빌드 중 예외 발생: {e}")
        return False


def verify_installer():
    """설치 파일 검증"""
    print_header("설치 파일 검증")

    if not OUTPUT_DIR.exists():
        print_error("출력 디렉토리가 없습니다.")
        return False

    exe_files = list(OUTPUT_DIR.glob("*.exe"))

    if not exe_files:
        print_error("생성된 설치 파일(.exe)이 없습니다.")
        return False

    for exe_file in exe_files:
        size_mb = exe_file.stat().st_size / (1024 * 1024)

        # 크기 검증 (예상: 1.5GB ~ 3GB)
        if size_mb < 100:
            print_warning(f"{exe_file.name} 크기가 너무 작습니다 ({size_mb:.1f} MB)")
            print_warning("Ollama 모델이 포함되지 않았을 수 있습니다.")
        elif size_mb > 3000:
            print_warning(f"{exe_file.name} 크기가 너무 큽니다 ({size_mb:.1f} MB)")
        else:
            print_success(f"파일 크기 정상: {size_mb:.1f} MB")

    return True


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="C# Code Reviewer 설치 파일 빌드")
    parser.add_argument("--clean", action="store_true", help="이전 빌드 아티팩트 삭제 후 빌드")
    parser.add_argument("--no-verify", action="store_true", help="빌드 검증 생략")
    args = parser.parse_args()

    print_header("C# Code Reviewer - Windows 설치 파일 빌드")

    # 1. Inno Setup 확인
    if not check_inno_setup():
        sys.exit(1)

    # 2. ISS 파일 확인
    if not check_iss_file():
        sys.exit(1)

    # 3. 포터블 패키지 확인
    if not check_portable_package():
        sys.exit(1)

    # 4. 클린 빌드 (선택)
    if args.clean:
        clean_build_artifacts()

    # 5. 빌드
    if not build_installer():
        sys.exit(1)

    # 6. 검증
    if not args.no_verify:
        if not verify_installer():
            print_warning("검증 단계에서 경고가 발생했습니다.")

    print_header("빌드 완료!")
    print_info("다음 단계:")
    print("  1. 생성된 설치 파일 테스트")
    print("  2. 깨끗한 Windows 11 환경에서 설치 테스트")
    print("  3. Ollama 자동 시작 확인")
    print("  4. 코드 분석 기능 테스트")
    print("  5. 제거 프로그램 테스트")


if __name__ == "__main__":
    main()
