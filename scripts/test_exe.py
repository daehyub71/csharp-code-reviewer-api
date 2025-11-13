#!/usr/bin/env python3
"""
EXE Test Script

Verifies that the built executable works correctly.

Usage:
    python scripts/test_exe.py [--exe-path PATH]
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


class ExeTestError(Exception):
    """Test failed"""
    pass


class ExeTester:
    """Test built EXE"""

    def __init__(self, exe_path: Path):
        self.exe_path = exe_path
        self.project_root = Path(__file__).parent.parent

    def check_exe_exists(self):
        """Check EXE file exists"""
        print("=" * 80)
        print("Test 1: EXE File Existence")
        print("=" * 80)

        if not self.exe_path.exists():
            raise ExeTestError(f"EXE not found: {self.exe_path}")

        size_mb = self.exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ EXE found: {self.exe_path}")
        print(f"✓ Size: {size_mb:.1f} MB")

        if size_mb < 10:
            raise ExeTestError(f"EXE too small ({size_mb:.1f} MB), likely incomplete")

        print()

    def check_ollama_running(self):
        """Check if Ollama is accessible"""
        print("=" * 80)
        print("Test 2: Ollama Server Check")
        print("=" * 80)

        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print("✓ Ollama server is running")
            else:
                print("⚠️  Warning: Ollama server returned unexpected status")
        except Exception as e:
            print("⚠️  Warning: Ollama server not accessible")
            print(f"   Error: {e}")
            print("   Start Ollama with: ollama serve")

        print()

    def test_exe_launch(self):
        """Test if EXE launches without errors"""
        print("=" * 80)
        print("Test 3: EXE Launch Test")
        print("=" * 80)

        print(f"Launching: {self.exe_path}")
        print("⚠️  This will open the application window")
        print("   Please close the window after verifying it opened correctly")
        print()

        try:
            # Launch EXE (non-blocking)
            # On Windows: will launch GUI
            # On macOS/Linux: may need Wine
            if sys.platform == "win32":
                process = subprocess.Popen([str(self.exe_path)])
                print("✓ EXE launched (Windows)")
            else:
                print("⚠️  Note: Running on non-Windows platform")
                print("   You may need Wine to test Windows EXE")
                print("   Install Wine: brew install wine-stable")
                print()
                print("Skipping launch test on non-Windows platform")
                return

            print()
            print("Please verify:")
            print("   1. Application window opened")
            print("   2. Dark theme applied")
            print("   3. No error dialogs appeared")
            print("   4. Editor is visible")
            print()
            input("Press Enter after closing the application window...")

            print("✓ Launch test completed")

        except Exception as e:
            raise ExeTestError(f"Failed to launch EXE: {e}")

        print()

    def test_resources(self):
        """Test if resources are bundled"""
        print("=" * 80)
        print("Test 4: Resource Files Check")
        print("=" * 80)

        # Check if original resources exist
        resources_dir = self.project_root / "resources"

        expected_files = [
            resources_dir / "styles" / "dark_theme.qss",
            resources_dir / "templates" / "review_categories" / "null_reference.md",
            resources_dir / "templates" / "review_categories" / "exception_handling.md",
            resources_dir / "templates" / "review_categories" / "hardcoding_to_config.md",
        ]

        for file_path in expected_files:
            if file_path.exists():
                print(f"✓ Resource exists: {file_path.relative_to(self.project_root)}")
            else:
                print(f"⚠️  Warning: Resource missing: {file_path.relative_to(self.project_root)}")

        print()
        print("Note: These resources should be bundled in the EXE")
        print("      If the app runs correctly, resources were bundled successfully")
        print()

    def run_all_tests(self):
        """Run all tests"""
        try:
            print()
            print("╔" + "=" * 78 + "╗")
            print("║" + " " * 20 + "C# Code Reviewer - EXE Test Suite" + " " * 24 + "║")
            print("╚" + "=" * 78 + "╝")
            print()

            self.check_exe_exists()
            self.check_ollama_running()
            self.test_resources()
            self.test_exe_launch()

            print("=" * 80)
            print("✅ All tests completed!")
            print("=" * 80)
            print()
            print("Next steps:")
            print("   1. Manually test all features:")
            print("      - Text editor mode (paste code → analyze)")
            print("      - File upload mode (single + batch)")
            print("      - Folder selection mode")
            print("      - Report history")
            print("   2. Test on target VDI environment (Windows, no admin)")
            print()

            return 0

        except ExeTestError as e:
            print()
            print("=" * 80)
            print("❌ Test failed")
            print("=" * 80)
            print(f"Error: {e}")
            print()
            return 1
        except KeyboardInterrupt:
            print()
            print("Tests cancelled by user")
            return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test C# Code Reviewer EXE"
    )
    parser.add_argument(
        "--exe-path",
        type=Path,
        default=Path("dist/CodeReviewer.exe"),
        help="Path to EXE file (default: dist/CodeReviewer.exe)"
    )

    args = parser.parse_args()

    tester = ExeTester(exe_path=args.exe_path)
    sys.exit(tester.run_all_tests())


if __name__ == "__main__":
    main()
