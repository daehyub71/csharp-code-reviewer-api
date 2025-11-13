# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**C# Code Reviewer (API Version)** is an AI-powered code review automation tool that uses **OpenAI GPT** or **Anthropic Claude** APIs to analyze C# code and generate improvement suggestions across 8 review categories.

### Core Characteristics
- **Online API-Based**: Uses OpenAI GPT-4o-mini or Claude 3.5 Haiku (requires API keys and internet)
- **Fast Analysis**: 1-3 seconds per review (5-10x faster than local models)
- **High Quality**: Access to GPT-4o and Claude 3.5 Sonnet for best results
- **8 Review Categories**: Null reference, Exception handling, Resource management, Performance, Security, Naming conventions, XML Documentation, Hardcoding→Config
- **No Local Model**: No Ollama server required, minimal disk space (~500MB vs ~5GB)

### Tech Stack
- **Backend**: Python 3.11+, OpenAI Python SDK, Anthropic Python SDK
- **Frontend**: PySide6 (Qt6 Python bindings) - LGPL licensed
- **LLM**: OpenAI GPT (gpt-4o-mini, gpt-4o) OR Anthropic Claude (claude-3-5-haiku, claude-3-5-sonnet)
- **Markdown**: python-markdown, Pygments (syntax highlighting)
- **Diagrams**: Mermaid CLI (converted to PNG)
- **Database**: SQLite (report history)
- **Charting**: matplotlib (integrated reports)

---

## Quick Start (5 Minutes)

### 1. Setup Virtual Environment
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add ONE of these API keys:
# Option 1: OpenAI (recommended for beginners)
OPENAI_API_KEY=sk-your-openai-key-here

# Option 2: Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Set default provider (optional)
DEFAULT_PROVIDER=openai  # or 'anthropic'
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

### 3. Run Application
```bash
python app/main.py

# If error: "No API keys configured"
# → Check .env file exists and has valid API key
```

---

## Development Commands

### Running the Application
```bash
# Standard mode
python app/main.py

# With debug logging (check logs/app.log)
python app/main.py --debug  # (if implemented)

# Test with specific files
python test_app_with_files.py
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test files
pytest tests/test_api_client.py -v
pytest tests/test_prompt_builder.py -v
pytest tests/test_report_generator.py -v
pytest tests/test_batch_analyzer.py -v

# Run integration tests
pytest tests/test_integration.py -v

# UI tests (pytest-qt)
pytest tests/test_file_upload_widget.py -v
```

### Building Distributable Package
```bash
# Build standalone EXE (Windows)
python scripts/build_exe.py

# Build installer (Inno Setup required)
python scripts/build_installer.py

# Test built EXE
python scripts/test_exe.py
```

---

## Architecture Overview

### 3-Layer Architecture

```
┌─────────────────────────────────────┐
│    Presentation Layer (PySide6)     │
│  - Main Window (tabbed UI)          │
│  - Before/After Split Editor         │
│  - Result Panel (Markdown viewer)    │
│  - File Upload (drag & drop)         │
│  - Folder Select (tree view)         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Business Logic Layer             │
│  - Batch Analyzer (orchestration)    │
│  - Prompt Builder (8 templates)      │
│  - Report Generator (Markdown)       │
│  - Integrated Report Generator       │
│  - Diagram Converter (Mermaid→PNG)   │
│  - Syntax Highlighter (C# lexer)     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    API Integration Layer            │
│  - API Client (unified OpenAI/       │
│    Anthropic client)                 │
│  - Streaming Response Handler        │
│  - Retry Logic (3 attempts)          │
│  - Error Handling                    │
└─────────────────────────────────────┘
```

### Data Flow: Text Analysis Mode

```
1. User pastes C# code → Before Editor
2. Click "Analyze" button
3. Prompt Builder creates LLM prompt (8 review categories)
4. API Client sends request to OpenAI/Anthropic (streaming)
5. Report Generator parses LLM response → Markdown
6. Diagram Converter extracts Mermaid → PNG (mmdc CLI)
7. Markdown Renderer converts to HTML (Pygments highlighting)
8. UI updates: After Editor + Result Panel
9. Auto-save: Markdown + HTML files → reports/
10. Save to SQLite: report_history.db
```

### Key Components

#### API Client (app/core/api_client.py)
Unified client for OpenAI and Anthropic APIs with:
- Multi-provider support (switch between OpenAI/Anthropic)
- Streaming responses (50-token chunks)
- Automatic retry logic (3 attempts with exponential backoff)
- Error handling (APIConnectionError, ModelNotFoundError, etc.)
- Token counting and validation

**Supported Models:**
```python
# OpenAI
'gpt-4o-mini'      # Fast, cheap ($0.15/1M tokens)
'gpt-4o'           # Best quality ($2.50/1M tokens)
'gpt-4-turbo'      # Balanced
'gpt-3.5-turbo'    # Legacy

# Anthropic
'claude-3-5-haiku-20241022'   # Fast, cheap ($0.80/1M tokens)
'claude-3-5-sonnet-20241022'  # Best quality ($3.00/1M tokens)
'claude-3-opus-20240229'      # Legacy high-quality
```

#### Prompt Builder (app/core/prompt_builder.py)
Template-based prompt generation with:
- 8 review category templates (in resources/templates/review_categories/)
- Few-shot examples for better accuracy
- Token optimization (target <2000 tokens per prompt)
- Configurable category selection

**8 Review Categories:**
1. **Null Reference Check** - null safety, null-coalescing operators
2. **Exception Handling** - try-catch blocks, specific exception types
3. **Resource Management** - using statements, IDisposable, memory leaks
4. **Performance** - StringBuilder, LINQ optimization, async/await
5. **Security** - SQL injection, input validation, secure coding
6. **Naming Conventions** - PascalCase, camelCase, _privateFields
7. **XML Documentation** - /// comments, param/returns tags
8. **Hardcoding to Config** - appsettings.json, environment variables

#### Batch Analyzer (app/core/batch_analyzer.py)
Handles multi-file analysis with:
- Progress tracking and callbacks
- Error recovery (3 retries per file)
- Parallel processing (future optimization)
- Result aggregation

#### Report Generator (app/core/report_generator.py)
Markdown report creation with:
- LLM response parsing
- Section extraction (Summary, Issues, Improvements, After Code)
- Mermaid diagram extraction
- HTML conversion with Pygments syntax highlighting

#### Integrated Report Generator (app/core/integrated_report_generator.py)
Project-wide analysis with:
- Category-based statistics
- Priority recommendations (high/medium/low)
- matplotlib chart generation (pie charts)
- Summary report (success rate, avg time, issue distribution)

---

## File Structure

```
app/
├── main.py                      # Application entry point
├── ui/
│   ├── main_window.py           # Main window (tabbed UI)
│   ├── before_after_editor.py   # Split editor with C# syntax highlighting
│   ├── file_upload_widget.py    # File upload + drag-and-drop
│   ├── folder_select_widget.py  # Tree view for folder selection
│   └── result_panel.py          # QTextBrowser for Markdown
├── core/
│   ├── api_client.py            # Unified OpenAI/Anthropic API client ⭐
│   ├── batch_analyzer.py        # Multi-file analysis orchestration
│   ├── prompt_builder.py        # Template-based prompt generation
│   ├── report_generator.py      # Markdown report creation
│   ├── integrated_report_generator.py  # Project-wide statistics
│   └── diagram_converter.py     # Mermaid CLI wrapper (mmdc)
├── utils/
│   ├── syntax_highlighter.py    # QSyntaxHighlighter for C#
│   ├── markdown_renderer.py     # Markdown→HTML (python-markdown)
│   └── markdown_parser.py       # Section extraction utilities
├── db/
│   └── report_history.py        # SQLite database for report history
├── services/
│   └── report_saver.py          # Save reports to disk + DB
└── config/
    └── __init__.py              # Configuration (from .env)

resources/
├── templates/
│   ├── report_template.md       # Markdown report template
│   └── review_categories/       # 8 category prompt templates
│       ├── null_reference.md
│       ├── exception_handling.md
│       ├── resource_management.md
│       ├── performance.md
│       ├── security.md
│       ├── naming_convention.md
│       ├── code_documentation.md
│       └── hardcoding_to_config.md
└── styles/
    └── (future: dark_theme.qss, icons)

scripts/
├── build_exe.py                 # PyInstaller build script
├── build_installer.py           # Inno Setup installer creation
└── test_exe.py                  # Test built executable

tests/
├── test_api_client.py           # API client tests (mocked responses)
├── test_prompt_builder.py       # Prompt generation tests
├── test_report_generator.py     # Report parsing tests
├── test_batch_analyzer.py       # Batch processing tests
├── test_diagram_converter.py    # Mermaid conversion tests
├── test_file_upload_widget.py   # UI tests (pytest-qt)
├── test_integration.py          # End-to-end integration tests
└── test_ollama_performance.py   # Legacy (from Ollama version)

reports/                         # Auto-generated reports (gitignored)
logs/                           # Application logs (gitignored)
```

---

## Configuration

### Environment Variables (.env)

```bash
# API Provider (choose ONE or both)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Default provider: 'openai' or 'anthropic'
DEFAULT_PROVIDER=openai

# Default model (leave empty for provider defaults)
# OpenAI: gpt-4o-mini, gpt-4o, gpt-4-turbo
# Anthropic: claude-3-5-haiku-20241022, claude-3-5-sonnet-20241022
DEFAULT_MODEL=

# LLM Parameters
TEMPERATURE=0.7        # 0.0-1.0 (lower = more deterministic)
MAX_TOKENS=4096        # Maximum tokens to generate
TIMEOUT=60             # Request timeout in seconds
```

### Settings (CodeReviewer_Portable/config/settings.json)

```json
{
  "api": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "timeout": 60,
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "ui": {
    "theme": "dark",
    "font_family": "Consolas",
    "font_size": 12,
    "sync_scroll": true
  },
  "analysis": {
    "check_null_reference": true,
    "check_exception": true,
    "check_resource": true,
    "check_performance": true,
    "check_security": true,
    "check_naming": true,
    "check_documentation": true,
    "check_hardcoding": true,
    "generate_diagram": true
  },
  "files": {
    "max_file_size_mb": 1,
    "max_file_count": 100
  }
}
```

---

## Error Handling

### Custom Exception Hierarchy

```python
class APIClientError(Exception):
    """Base exception"""
    pass

class APIConnectionError(APIClientError):
    """API server unreachable"""
    pass

class ModelNotFoundError(APIClientError):
    """Model not available"""
    pass

class APIKeyMissingError(APIClientError):
    """API key not configured"""
    pass

class PromptTooLongError(APIClientError):
    """Prompt exceeds context window"""
    pass
```

### Retry Logic
- API calls: 3 retries with exponential backoff (1s, 2s, 4s)
- File I/O errors: Skip file and log error
- Mermaid conversion failure: Fallback to text representation

---

## Testing Strategy

### Unit Tests (pytest)
```bash
# Test API client with mocked responses
pytest tests/test_api_client.py -v

# Test prompt template generation
pytest tests/test_prompt_builder.py -v

# Test Markdown parsing and report structure
pytest tests/test_report_generator.py -v

# Test batch processing
pytest tests/test_batch_analyzer.py -v
```

### UI Tests (pytest-qt)
```bash
# Test file upload widget
pytest tests/test_file_upload_widget.py -v
```

### Integration Tests
```bash
# Test full workflow (code → API → report)
pytest tests/test_integration.py -v
```

### Performance Expectations
- 10 lines: <2 seconds (API latency + processing)
- 100 lines: <3 seconds
- 500 lines: <5 seconds
- Memory usage: <1GB (no local model)

---

## Cost Structure

### Typical Usage Costs

| Code Size | Input Tokens | Output Tokens | Cost (gpt-4o-mini) | Cost (claude-3-5-haiku) |
|-----------|-------------|---------------|-------------------|------------------------|
| 50 lines  | ~500        | ~800          | $0.0006           | $0.0036                |
| 100 lines | ~800        | ~1200         | $0.0009           | $0.0052                |
| 500 lines | ~2500       | ~3000         | $0.0022           | $0.0140                |

**Model Recommendations:**
- **For cost-conscious users**: gpt-4o-mini ($0.15/1M input tokens)
- **For best quality**: gpt-4o ($2.50/1M) or claude-3-5-sonnet ($3.00/1M)

---

## Key Differences from Ollama Version

| Aspect | Ollama Version | API Version (This) |
|--------|---------------|-------------------|
| **LLM** | Phi-3-mini (local) | GPT-4o-mini / Claude 3.5 Haiku |
| **Network** | ❌ Offline | ✅ Online (required) |
| **Setup** | Install Ollama + pull model | Configure API keys |
| **Disk Space** | ~5GB (app + model) | ~500MB (app only) |
| **RAM** | 8GB (model in memory) | 4GB (no model) |
| **Speed** | 10-20s per review | 1-3s per review |
| **Quality** | Good | Excellent |
| **Cost** | Free | ~$0.001-0.02 per review |
| **Review Categories** | 6 | 8 (added XML docs + hardcoding) |
| **Privacy** | 100% local | Code sent to external APIs |
| **VDI Support** | ✅ Yes | ❌ No (requires internet) |

**When to use API version:**
- ✅ Have internet access
- ✅ Can use external APIs (non-sensitive code)
- ✅ Want best quality results
- ✅ Want fast inference
- ✅ Budget allows API costs

**When to use Ollama version:**
- ❌ No internet access (VDI, airgapped networks)
- ❌ Can't use external APIs (data privacy, security policy)
- ✅ Want 100% free operation
- ✅ OK with slower inference

---

## Troubleshooting

### "No API keys configured"
```bash
# Check .env file exists
ls -la .env

# Verify content
cat .env

# Should have ONE of:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

### "API connection failed"
**Possible causes:**
1. Invalid API key (check for typos, expired keys)
2. No internet connection (ping api.openai.com / api.anthropic.com)
3. API rate limit reached (check your account dashboard)
4. Insufficient API credits (add payment method)

### "Model not found: gpt-4o-mini"
```bash
# Check model name spelling in .env
# Valid OpenAI models: gpt-4o-mini, gpt-4o, gpt-4-turbo, gpt-3.5-turbo
# Valid Anthropic models: claude-3-5-haiku-20241022, claude-3-5-sonnet-20241022

# Leave DEFAULT_MODEL empty to use provider defaults
DEFAULT_MODEL=
```

### "ModuleNotFoundError: No module named 'openai'"
```bash
# Install dependencies
pip install -r requirements.txt

# If still fails, reinstall
pip uninstall openai anthropic -y
pip install openai>=1.0.0 anthropic>=0.40.0
```

### Slow performance
- Use faster models: `gpt-4o-mini` (OpenAI) or `claude-3-5-haiku` (Anthropic)
- Check internet connection speed
- Reduce code size (split large files)

---

## Project Status

**Current Version**: 2.0.0 (API version)
**Based on**: Original Ollama version 1.0.0 (Weeks 1-5 complete)
**Forked**: 2025-11-13

### Completed Features
- ✅ Text input mode with Before/After split editor
- ✅ 8 review categories (added XML docs + hardcoding)
- ✅ OpenAI GPT integration (gpt-4o-mini, gpt-4o)
- ✅ Anthropic Claude integration (claude-3-5-haiku, claude-3-5-sonnet)
- ✅ Streaming responses (50-token chunks)
- ✅ File upload mode (drag & drop, multiple files)
- ✅ Folder select mode (tree view, recursive traversal)
- ✅ Batch processing with progress tracking
- ✅ Integrated project-wide reports
- ✅ Report history (SQLite database)
- ✅ Auto-save reports (Markdown + HTML)
- ✅ Mermaid diagram generation (PNG conversion)
- ✅ matplotlib charts (category statistics)
- ✅ Error recovery (3 retries per file)

### Future Enhancements
- [ ] Azure OpenAI support (enterprise deployments)
- [ ] Google Gemini support
- [ ] Cost tracking dashboard
- [ ] Prompt optimization per provider
- [ ] Unit tests >80% coverage
- [ ] Performance benchmarking

---

## Additional Resources

- **Quick Start Guide**: [QUICKSTART.md](QUICKSTART.md)
- **Changes from Ollama Version**: [CHANGES.md](CHANGES.md)
- **Main README**: [README.md](README.md)
- **Project Plan**: [PROJECT_PLAN.md](PROJECT_PLAN.md) (original Ollama version)
- **Development Timeline**: [DEVELOPMENT_TIMELINE.md](DEVELOPMENT_TIMELINE.md) (original)
- **OpenAI Docs**: https://platform.openai.com/docs/
- **Anthropic Docs**: https://docs.anthropic.com/
- **PySide6 Docs**: https://doc.qt.io/qtforpython-6/
- **Mermaid Syntax**: https://mermaid.js.org/

---

**Original Project**: [csharp-code-reviewer](../csharp-code-reviewer) (Ollama version)
**This Fork**: csharp-code-reviewer-api (API version)
**License**: MIT License
