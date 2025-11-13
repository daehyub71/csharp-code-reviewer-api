#!/usr/bin/env python3
"""
PyInstaller Build Script for C# Code Reviewer

Automates the EXE build process with pre-checks and post-build verification.

Usage:
    python scripts/build_exe.py [--clean] [--debug]

Options:
    --clean: Remove build artifacts before building
    --debug: Build with debug console enabled
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


class BuildError(Exception):
    """Build process failed"""
    pass


class EXEBuilder:
    """PyInstaller EXE builder"""

    def __init__(self, clean: bool = False, debug: bool = False):
        self.project_root = Path(__file__).parent.parent
        self.spec_file = self.project_root / "CodeReviewer.spec"
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.clean = clean
        self.debug = debug

    def pre_check(self):
        """Pre-build checks"""
        print("=" * 80)
        print("Pre-build checks")
        print("=" * 80)

        # Check spec file exists
        if not self.spec_file.exists():
            raise BuildError(f"Spec file not found: {self.spec_file}")
        print(f"✓ Spec file found: {self.spec_file}")

        # Check app/main.py exists
        main_py = self.project_root / "app" / "main.py"
        if not main_py.exists():
            raise BuildError(f"Entry point not found: {main_py}")
        print(f"✓ Entry point found: {main_py}")

        # Check resources directory
        resources_dir = self.project_root / "resources"
        if not resources_dir.exists():
            raise BuildError(f"Resources directory not found: {resources_dir}")
        print(f"✓ Resources directory found: {resources_dir}")

        # Check PyInstaller installed
        try:
            result = subprocess.run(
                ["pyinstaller", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            print(f"✓ PyInstaller installed: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise BuildError("PyInstaller not installed. Run: pip install pyinstaller")

        print()

    def clean_build(self):
        """Remove build artifacts"""
        if not self.clean:
            return

        print("=" * 80)
        print("Cleaning build artifacts")
        print("=" * 80)

        dirs_to_clean = [self.dist_dir, self.build_dir]

        for dir_path in dirs_to_clean:
            if dir_path.exists():
                print(f"Removing: {dir_path}")
                shutil.rmtree(dir_path)

        print("✓ Clean complete")
        print()

    def build(self):
        """Run PyInstaller build"""
        print("=" * 80)
        print("Building EXE with PyInstaller")
        print("=" * 80)

        # Modify spec file if debug mode
        if self.debug:
            print("⚠️  Debug mode: Console will be visible")
            # TODO: Modify spec file to set console=True

        # Run PyInstaller
        cmd = [
            "pyinstaller",
            "--clean",  # Clean cache
            "--noconfirm",  # Overwrite without asking
            str(self.spec_file)
        ]

        print(f"Running: {' '.join(cmd)}")
        print()

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                check=True,
                text=True
            )
            print()
            print("✓ Build successful")
        except subprocess.CalledProcessError as e:
            raise BuildError(f"PyInstaller build failed: {e}")

        print()

    def post_check(self):
        """Post-build verification"""
        print("=" * 80)
        print("Post-build verification")
        print("=" * 80)

        # Check EXE exists
        exe_path = self.dist_dir / "CodeReviewer.exe"
        if not exe_path.exists():
            raise BuildError(f"EXE not found: {exe_path}")
        print(f"✓ EXE created: {exe_path}")

        # Check file size
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ EXE size: {size_mb:.1f} MB")

        if size_mb > 200:
            print(f"⚠️  Warning: EXE is large (>{size_mb:.1f} MB)")
            print("   Consider excluding unused modules in .spec file")

        print()
        print("=" * 80)
        print("Build Summary")
        print("=" * 80)
        print(f"Output: {exe_path}")
        print(f"Size: {size_mb:.1f} MB")
        print()
        print("📦 Next steps:")
        print("   1. Test the EXE: ./dist/CodeReviewer.exe")
        print("   2. Ensure Ollama is running (ollama serve)")
        print("   3. Test all features (text mode, file upload, folder selection)")
        print()

    def run(self):
        """Execute full build process"""
        try:
            self.pre_check()
            self.clean_build()
            self.build()
            self.post_check()

            print("✅ Build completed successfully!")
            return 0

        except BuildError as e:
            print()
            print("=" * 80)
            print("❌ Build failed")
            print("=" * 80)
            print(f"Error: {e}")
            print()
            return 1
        except KeyboardInterrupt:
            print()
            print("Build cancelled by user")
            return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Build C# Code Reviewer EXE with PyInstaller"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove build artifacts before building"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Build with debug console enabled"
    )

    args = parser.parse_args()

    builder = EXEBuilder(clean=args.clean, debug=args.debug)
    sys.exit(builder.run())


if __name__ == "__main__":
    main()
