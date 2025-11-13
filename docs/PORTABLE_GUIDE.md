# Portable Package Guide

Complete guide for creating and deploying C# Code Reviewer as a portable package with embedded Ollama.

## Overview

The portable package allows offline VDI deployment with:
- **No installation required**: Extract and run
- **No admin rights needed**: User-level execution only
- **No internet required**: All components bundled
- **100% offline**: LLM runs locally

### Package Contents

```
CodeReviewer_Portable/        (~2.5GB uncompressed, ~1.5GB ZIP)
├── CodeReviewer.exe           Main application (~50-100MB)
├── ollama_portable/           Ollama + model (~2.4GB)
│   ├── ollama.exe             Ollama server (~100MB)
│   └── models/                Model directory
│       └── phi3-mini-*.gguf   Phi-3-mini model (2.3GB)
├── config/
│   └── settings.json          User preferences
├── logs/
│   └── app.log                Application logs
├── reports/                   Generated reports
│   ├── markdown/
│   └── html/
└── README.txt                 User guide
```

---

## Step 1: Build the EXE

First, build the main application executable.

```bash
# Clean build (recommended)
python scripts/build_exe.py --clean

# Verify EXE created
ls -lh dist/CodeReviewer.exe
```

**Expected result**: `dist/CodeReviewer.exe` (~50-100MB)

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed build instructions.

---

## Step 2: Prepare Ollama Portable

### 2.1 Download Ollama for Windows

1. Visit: https://ollama.com/download
2. Download **OllamaSetup.exe** for Windows
3. Install Ollama on your system (temporary, for extraction)

### 2.2 Locate ollama.exe

After installation, find the Ollama executable:

**Typical locations**:
- `C:\Users\<YourName>\AppData\Local\Programs\Ollama\ollama.exe`
- `C:\Program Files\Ollama\ollama.exe`

**Size**: ~100MB

### 2.3 Pull Phi-3-mini Model

Before bundling, download the model:

```bash
# Start Ollama
ollama serve

# In another terminal, pull model
ollama pull phi3:mini
```

This downloads the Phi-3-mini model (~2.3GB).

### 2.4 Locate Model File

Find the model blob file:

**Windows**:
```
C:\Users\<YourName>\.ollama\models\blobs\
```

**macOS**:
```
~/.ollama/models/blobs/
```

Look for a file matching:
- Name: `sha256-*` (long hash)
- Size: ~2.3GB
- This is the GGUF model file

---

## Step 3: Bundle Portable Package

Use the bundler script to create the portable structure:

```bash
# Create portable package structure
python scripts/bundle_ollama.py --output-dir CodeReviewer_Portable

# This creates:
# - Directory structure
# - config/settings.json
# - README.txt
# - Guides you through manual steps
```

The script will prompt you to:
1. Copy `ollama.exe` to `CodeReviewer_Portable/ollama_portable/`
2. Copy model file to `CodeReviewer_Portable/ollama_portable/models/`

### 3.1 Copy ollama.exe

```bash
# Windows example
cp "C:\Users\YourName\AppData\Local\Programs\Ollama\ollama.exe" \
   CodeReviewer_Portable\ollama_portable\ollama.exe
```

### 3.2 Copy Model File

```bash
# Windows example
cp "C:\Users\YourName\.ollama\models\blobs\sha256-*" \
   CodeReviewer_Portable\ollama_portable\models\phi3-mini-4k-instruct-q4.gguf
```

**Important**: Rename the model file to a readable name like `phi3-mini-4k-instruct-q4.gguf`.

### 3.3 Copy CodeReviewer.exe

```bash
# Copy built EXE to portable package
cp dist/CodeReviewer.exe CodeReviewer_Portable/
```

---

## Step 4: Configure Portable Mode

### 4.1 Create Modelfile (Important)

Since we're using a raw GGUF file, we need to tell Ollama how to use it.

Create `CodeReviewer_Portable/ollama_portable/models/Modelfile`:

```modelfile
FROM ./phi3-mini-4k-instruct-q4.gguf

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 8192
PARAMETER num_predict 6144

TEMPLATE """{{ if .System }}<|system|>
{{ .System }}<|end|>
{{ end }}{{ if .Prompt }}<|user|>
{{ .Prompt }}<|end|>
{{ end }}<|assistant|>
{{ .Response }}<|end|>
"""

SYSTEM """You are a C# code review expert."""
```

### 4.2 Verify settings.json

Check `CodeReviewer_Portable/config/settings.json`:

```json
{
  "ollama": {
    "host": "http://localhost:11434",
    "model": "phi3:mini",
    "portable_path": "./ollama_portable/ollama.exe"
  }
}
```

**Key setting**: `portable_path` tells the app where to find portable Ollama.

---

## Step 5: Test Portable Package

### 5.1 Test Locally

Before distribution, test the portable package:

```bash
# Navigate to portable directory
cd CodeReviewer_Portable

# Run the executable
./CodeReviewer.exe  # Windows
# or
wine CodeReviewer.exe  # macOS/Linux with Wine
```

**Expected behavior**:
1. Application starts
2. Popup: "Starting Ollama..." (5-10 seconds)
3. Main window appears
4. Check logs: `logs/app.log` for "Ollama started successfully"

### 5.2 Test Analysis

1. Paste sample C# code in editor
2. Click "Analyze" button
3. Verify AI analysis completes
4. Check report generation

### 5.3 Test Cleanup

1. Close application normally
2. Check logs: Should show "Ollama process stopped"
3. Verify no orphaned `ollama.exe` processes

```powershell
# Windows: Check no Ollama processes remain
tasklist | findstr ollama

# Should return nothing
```

---

## Step 6: Create Distributable Package

### 6.1 Verify Bundle Completeness

```bash
# Run bundler again to verify
python scripts/bundle_ollama.py --output-dir CodeReviewer_Portable

# Should show:
# ✅ All files present!
# Package size summary
```

### 6.2 Create ZIP Archive

```bash
# Windows (PowerShell)
Compress-Archive -Path CodeReviewer_Portable -DestinationPath CodeReviewer_Portable_v1.0.0.zip

# macOS/Linux
zip -r CodeReviewer_Portable_v1.0.0.zip CodeReviewer_Portable

# With better compression (7-Zip)
7z a -mx=9 CodeReviewer_Portable_v1.0.0.7z CodeReviewer_Portable
```

**Expected compressed size**: ~1.5GB (ZIP) or ~1.2GB (7z)

---

## Deployment to VDI

### Prerequisites on Target System

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 3GB free
- **Permissions**: User-level (no admin rights needed)
- **Internet**: Not required

### Deployment Steps

1. **Copy ZIP to VDI**:
   - Via network drive, USB, or internal file transfer

2. **Extract to user folder**:
   ```
   C:\Users\<Username>\CodeReviewer_Portable\
   ```

3. **Run CodeReviewer.exe**:
   - Double-click to launch
   - Wait 5-10 seconds for Ollama initialization
   - Use normally

### Firewall Considerations

Ollama binds to `localhost:11434`. This should work without firewall changes since it's local-only.

If firewall blocks:
- Add exception for `ollama.exe` (localhost only)
- Or use alternative port in `settings.json`

---

## Troubleshooting

### Issue 1: "Ollama startup failed"

**Symptoms**: Error dialog on launch

**Causes**:
- Port 11434 already in use
- Antivirus blocking ollama.exe
- Missing model file

**Solutions**:
```bash
# Check if port is in use
netstat -an | findstr 11434

# Kill existing Ollama
taskkill /F /IM ollama.exe

# Retry application
```

### Issue 2: Slow performance

**Symptoms**: Analysis takes >30 seconds

**Causes**:
- Phi-3-mini running on CPU (no GPU)
- Low RAM (<8GB)
- Slow CPU (<4 cores)

**Solutions**:
- Upgrade to 16GB RAM if possible
- Close other applications
- Reduce code size (analyze smaller files)
- This is expected behavior on low-end systems

### Issue 3: Model not found

**Symptoms**: "Model 'phi3:mini' not found"

**Causes**:
- Model file not copied correctly
- Modelfile not created
- Wrong model name in settings.json

**Solutions**:
```bash
# Check model file exists
ls ollama_portable/models/phi3-mini-*.gguf

# Verify Modelfile exists
ls ollama_portable/models/Modelfile

# Check settings.json
cat config/settings.json
```

### Issue 4: Process doesn't stop on exit

**Symptoms**: `ollama.exe` remains in Task Manager after closing app

**Causes**:
- Crash before cleanup
- Force-kill of CodeReviewer.exe

**Solutions**:
```bash
# Manually kill Ollama
taskkill /F /IM ollama.exe

# Check logs for errors
cat logs/app.log
```

### Issue 5: Permission denied

**Symptoms**: "Access denied" when starting ollama.exe

**Causes**:
- VDI policy blocking unknown executables
- Antivirus quarantine
- Incorrect file permissions

**Solutions**:
- Request IT to whitelist ollama.exe
- Extract to different directory (e.g., `D:\temp\`)
- Check file is not marked as "blocked":
  - Right-click → Properties → Unblock

---

## Performance Tuning

### Reduce Memory Usage

Edit `config/settings.json`:

```json
{
  "ollama": {
    "num_ctx": 4096,     # Reduce from 8192
    "num_predict": 2048  # Reduce from 6144
  }
}
```

**Trade-off**: Shorter output, may truncate large files.

### Speed Up Analysis

1. **Reduce code size**: Analyze files <500 lines
2. **Disable diagram generation**: Set `generate_diagram: false`
3. **Use batch mode**: Analyze multiple files in one session

---

## Maintenance

### Updating the Model

To update Phi-3-mini to a newer version:

1. Pull new model on development machine:
   ```bash
   ollama pull phi3:mini
   ```

2. Copy new model blob to `ollama_portable/models/`

3. Update Modelfile if needed

4. Redistribute updated package

### Updating the Application

To update CodeReviewer.exe:

1. Rebuild with new code:
   ```bash
   python scripts/build_exe.py --clean
   ```

2. Replace old EXE:
   ```bash
   cp dist/CodeReviewer.exe CodeReviewer_Portable/
   ```

3. Test thoroughly before redistribution

### Log Rotation

Logs grow over time. To clear:

```bash
# Delete old logs
rm logs/app.log

# Application will create new log on next start
```

---

## Security Considerations

### Data Privacy

- **Code never leaves the system**: All analysis is local
- **No network requests**: Ollama runs offline
- **No telemetry**: Application doesn't phone home

### Executable Signing (Optional)

For enterprise deployment, consider code signing:

```bash
# Windows (requires certificate)
signtool sign /f certificate.pfx /p password CodeReviewer.exe
```

### Virus Scanner False Positives

PyInstaller EXEs sometimes trigger AV false positives. Solutions:

1. Submit to AV vendors for whitelisting
2. Sign the executable (reduces false positives)
3. Request IT to whitelist the file hash

---

## Advanced: Custom Model

To use a different model (e.g., CodeLlama):

1. **Pull model**:
   ```bash
   ollama pull codellama:7b
   ```

2. **Copy model blob** to `ollama_portable/models/`

3. **Update settings.json**:
   ```json
   {
     "ollama": {
       "model": "codellama:7b"
     }
   }
   ```

4. **Create new Modelfile** for the model

5. **Test thoroughly** (prompts may need adjustment)

---

## File Size Breakdown

| Component | Size | Compressed |
|-----------|------|------------|
| CodeReviewer.exe | 50-100 MB | 40-80 MB |
| ollama.exe | ~100 MB | ~80 MB |
| Phi-3-mini GGUF | 2.3 GB | 1.2 GB |
| Config/docs | <1 MB | <1 MB |
| **TOTAL** | **~2.5 GB** | **~1.5 GB** |

---

## FAQ

### Q: Can I run this on macOS/Linux?

**A**: The portable package is Windows-only. For macOS/Linux:
- Install Ollama directly: `brew install ollama`
- Run from source: `python app/main.py`

### Q: Why is the package so large?

**A**: The LLM model (Phi-3-mini) is 2.3GB. This is a quantized (compressed) version—the original is larger.

### Q: Can I use a cloud LLM instead?

**A**: This app is designed for offline use. For cloud LLMs, you'd need to modify `app/core/ollama_client.py` to support OpenAI/Azure APIs.

### Q: Does it support GPU acceleration?

**A**: Yes, if Ollama detects compatible GPU. Portable Ollama will use GPU automatically if available (CUDA/ROCm/Metal).

### Q: Can I uninstall Ollama after bundling?

**A**: Yes! The portable package is self-contained. System Ollama can be uninstalled after extracting model files.

---

## Next Steps

After successful deployment:

1. ✅ **Train users** on basic usage
2. ✅ **Monitor logs** for issues
3. ✅ **Collect feedback** for improvements
4. ⏭️ **Automate updates** (future enhancement)

For issues or questions, refer to:
- `logs/app.log` - Application logs
- [BUILD_GUIDE.md](BUILD_GUIDE.md) - Build documentation
- [DEVELOPMENT_TIMELINE.md](../DEVELOPMENT_TIMELINE.md) - Project timeline

---

**Last Updated**: 2025-01-19
**Version**: 1.0.0
