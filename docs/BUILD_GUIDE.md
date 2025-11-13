# Build Guide - PyInstaller EXE Packaging

This guide explains how to build a standalone Windows executable (.exe) for C# Code Reviewer using PyInstaller.

## Prerequisites

### 1. Python Environment
```bash
# Ensure Python 3.11+ is installed
python --version

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
# Install all dependencies including PyInstaller
pip install -r requirements.txt

# Verify PyInstaller installation
pyinstaller --version
```

### 3. Test Application First
```bash
# Ensure app runs correctly before building
python app/main.py

# Test with Ollama
ollama serve  # In separate terminal
```

---

## Build Process

### Quick Build

```bash
# Default build (single EXE, no console)
python scripts/build_exe.py
```

### Clean Build

```bash
# Remove previous build artifacts first
python scripts/build_exe.py --clean
```

### Debug Build

```bash
# Build with console window visible (for debugging)
python scripts/build_exe.py --debug
```

---

## Build Configuration

### CodeReviewer.spec File

The `.spec` file controls PyInstaller behavior:

```python
# Key settings in CodeReviewer.spec

# 1. Entry point
['app/main.py']

# 2. Resource files to bundle
datas = [
    ('resources/styles', 'resources/styles'),
    ('resources/templates', 'resources/templates'),
]

# 3. Hidden imports (modules not auto-detected)
hiddenimports = [
    'markdown',
    'Pygments',
    'ollama',
    'matplotlib',
    # ... PySide6 modules
]

# 4. Modules to exclude (reduce size)
excludes = [
    'tkinter',
    'matplotlib.tests',
    'numpy.tests',
    'PIL',
    'scipy',
    'pandas',
]

# 5. EXE settings
exe = EXE(
    name='CodeReviewer',
    console=False,  # Hide console (GUI app)
    upx=True,       # UPX compression
    # icon='icon.ico'  # TODO: Add icon
)
```

### Customizing the Build

To modify build settings:

1. **Edit `CodeReviewer.spec`** for advanced options
2. **Run build script** to apply changes:
   ```bash
   python scripts/build_exe.py --clean
   ```

---

## Build Output

### File Structure

```
dist/
└── CodeReviewer.exe    # Standalone executable (~50-100MB)

build/                  # Temporary build files (can be deleted)
```

### Expected File Size

- **Without compression**: ~100-150 MB
- **With UPX compression**: ~50-100 MB

Includes:
- Python runtime
- PySide6 (Qt6)
- All dependencies (markdown, Pygments, ollama, matplotlib)
- Resource files (stylesheets, templates)

---

## Testing the EXE

### 1. Basic Execution Test

```bash
# Run the EXE
./dist/CodeReviewer.exe  # Windows
# or
wine dist/CodeReviewer.exe  # macOS/Linux (with Wine)
```

**Expected**: Application window should open with no errors.

### 2. Ollama Connection Test

```bash
# Start Ollama server first
ollama serve

# Run EXE and test:
# 1. Paste C# code in Before editor
# 2. Click "Analyze" button
# 3. Verify After code and report generation
```

**Expected**: LLM analysis completes and report displays.

### 3. File Upload Test

```bash
# Test single file upload
# 1. Click "파일 업로드" button
# 2. Select a .cs file
# 3. Verify analysis completes

# Test batch upload
# 1. Select multiple .cs files (5-10 files)
# 2. Verify progress dialog
# 3. Check report history
```

**Expected**: All files analyzed successfully.

### 4. Folder Selection Test

```bash
# Test folder analysis
# 1. Click "폴더 선택" tab
# 2. Select a C# project folder
# 3. Check multiple files
# 4. Run batch analysis
# 5. View integrated report
```

**Expected**: Folder tree displays, batch analysis completes, integrated report generated.

---

## Troubleshooting

### Issue 1: "Failed to execute script 'main'"

**Cause**: Missing dependency or resource file

**Fix**:
```bash
# Check .spec file includes all resources
# Add missing module to hiddenimports
hiddenimports.append('missing_module_name')

# Rebuild
python scripts/build_exe.py --clean
```

### Issue 2: EXE size too large (>200MB)

**Cause**: Unnecessary modules bundled

**Fix**:
```python
# Edit CodeReviewer.spec
excludes.extend([
    'unused_module_1',
    'unused_module_2',
])

# Enable UPX compression
upx=True
```

### Issue 3: Console window appears (GUI app)

**Cause**: `console=True` in .spec file

**Fix**:
```python
# Edit CodeReviewer.spec
exe = EXE(
    ...
    console=False,  # Hide console
)
```

### Issue 4: Stylesheet not loading (white background)

**Cause**: Resource file not bundled

**Fix**:
```python
# Check .spec file includes:
datas = [
    ('resources/styles', 'resources/styles'),
]

# Verify resources/styles/dark_theme.qss exists
ls resources/styles/dark_theme.qss
```

### Issue 5: "Ollama connection failed"

**Cause**: Ollama not running or wrong port

**Fix**:
```bash
# Start Ollama server
ollama serve

# Check port
curl http://localhost:11434/api/tags

# EXE should connect automatically
```

---

## Advanced: Cross-Platform Builds

### ⭐ Building on macOS → Windows (Recommended: GitHub Actions)

**PyInstaller cannot cross-compile** (macOS → Windows EXE not possible).

**Best Solution**: Use GitHub Actions to build on Windows automatically.

#### Setup GitHub Actions Workflow

1. **Ensure workflow file exists**:
   ```bash
   ls .github/workflows/build-windows.yml
   ```

2. **Commit and push**:
   ```bash
   git add .github/workflows/build-windows.yml
   git commit -m "feat: Add GitHub Actions Windows build workflow"
   git push origin main
   ```

3. **Workflow runs automatically** on:
   - Every push to `main` branch
   - Every pull request
   - Manual trigger (Actions tab → Run workflow)
   - Git tags (e.g., `v1.0.0` → creates GitHub Release)

#### Download Built EXE

**Option 1: From GitHub Actions Artifacts**

```bash
# 1. Go to: https://github.com/YOUR_USERNAME/csharp-code-reviewer/actions
# 2. Click latest workflow run
# 3. Download "CodeReviewer-Windows-EXE" artifact
# 4. Extract ZIP → CodeReviewer.exe
```

**Option 2: From GitHub Releases (for tagged versions)**

```bash
# 1. Create version tag
git tag v1.0.0
git push origin v1.0.0

# 2. Workflow builds and creates release automatically
# 3. Download from: https://github.com/YOUR_USERNAME/csharp-code-reviewer/releases
```

#### Manual Trigger

```bash
# 1. Go to: https://github.com/YOUR_USERNAME/csharp-code-reviewer/actions
# 2. Select "Build Windows EXE" workflow
# 3. Click "Run workflow" → Choose branch → Run
# 4. Wait 5-10 minutes
# 5. Download artifact
```

---

### Building Directly on Windows

If you have access to a Windows machine:

```bash
# On Windows machine
python scripts/build_exe.py --clean

# Output: dist/CodeReviewer.exe (Windows native)
```

---

### Building on macOS with Virtual Machine

If GitHub Actions is not suitable, use a VM:

1. **Install VM software**:
   ```bash
   # Parallels (paid, best performance)
   # VMware Fusion (paid)
   # VirtualBox (free)
   brew install --cask virtualbox
   ```

2. **Create Windows 10/11 VM**:
   - Download Windows ISO from Microsoft
   - Install Python 3.11
   - Clone repository
   - Run build script

3. **Build inside VM**:
   ```bash
   python scripts/build_exe.py --clean
   ```

---

### Building on macOS (Wine) - ⚠️ Not Recommended

Wine-based cross-compilation is **experimental and unreliable**:

```bash
# Install Wine (if not installed)
brew install wine-stable

# Install Windows Python in Wine (complex)
# https://www.python.org/downloads/windows/

# Cross-compile for Windows (may fail)
wine python scripts/build_exe.py
```

**Issues**:
- Complex setup
- Frequent build failures
- Missing DLLs
- Hard to debug

**Recommendation**: Use GitHub Actions instead.

---

### Building for macOS (App Bundle)

To build macOS native app:

```bash
# 1. Edit CodeReviewer.spec
# Change EXE to BUNDLE:

app = BUNDLE(
    exe,
    name='CodeReviewer.app',
    icon=None,
    bundle_identifier='com.csharp.coderereviewer',
)

# 2. Build
python scripts/build_exe.py --clean

# 3. Output
# dist/CodeReviewer.app

# 4. Test
open dist/CodeReviewer.app
```

**Note**: macOS builds require code signing for distribution.

---

## Optimization Tips

### 1. Reduce EXE Size

```python
# Exclude test modules
excludes = [
    'test',
    'tests',
    'unittest',
    '*.tests',
]

# Use UPX compression
upx=True
upx_exclude=[]  # Don't exclude anything from UPX
```

### 2. Faster Build Times

```bash
# Use incremental build (no --clean)
python scripts/build_exe.py

# PyInstaller caches analysis results
```

### 3. Debug Build Issues

```bash
# Build with console visible
python scripts/build_exe.py --debug

# Check console output for errors
./dist/CodeReviewer.exe
```

---

## Deployment

### Portable Package Structure

```
CodeReviewer_Portable/
├── CodeReviewer.exe         # Main executable
├── README.txt               # Quick start guide
└── config/                  # Optional: User settings
    └── settings.json
```

### Distribution

1. **Test thoroughly** on target machines (Windows 10/11)
2. **Create ZIP archive**:
   ```bash
   cd dist
   zip -r CodeReviewer_v1.0.0.zip CodeReviewer.exe README.txt
   ```
3. **Upload to release page** (GitHub Releases)

---

## Next Steps

After successful EXE build:

1. ✅ Test all features in EXE
2. ⏭️ Bundle Ollama portable (Day 17)
3. ⏭️ Create installer script (optional)
4. ⏭️ Add application icon (optional)

---

## References

- **PyInstaller Docs**: https://pyinstaller.org/en/stable/
- **PySide6 Packaging**: https://doc.qt.io/qtforpython-6/deployment.html
- **UPX Compression**: https://upx.github.io/
