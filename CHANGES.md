# Changes from Original (Ollama Version)

## Summary

이 프로젝트는 원본 [csharp-code-reviewer](../csharp-code-reviewer)의 **API 버전**입니다.
로컬 sLLM (Ollama + Phi-3-mini) 대신 **OpenAI GPT** 또는 **Anthropic Claude** API를 사용합니다.

## Major Changes

### 1. LLM Backend
- **Before**: Ollama + Phi-3-mini (로컬 실행, 오프라인)
- **After**: OpenAI GPT / Anthropic Claude (온라인 API)

### 2. Core Files Changed

| File | Changes |
|------|---------|
| `app/core/api_client.py` | **NEW** - Unified API client for GPT/Claude |
| `app/core/ollama_client.py` | **REMOVED** |
| `app/services/ollama_manager.py` | **REMOVED** (no auto-start needed) |
| `app/main.py` | API key validation, no Ollama startup |
| `app/ui/main_window.py` | API client instead of Ollama client |
| `requirements.txt` | `ollama` → `openai`, `anthropic` |
| `.env.example` | **NEW** - API key configuration |

### 3. System Requirements

| Requirement | Before | After |
|-------------|--------|-------|
| **Network** | ❌ Offline (VDI) | ✅ Online (API access) |
| **API Key** | ❌ Not required | ✅ Required (OpenAI or Anthropic) |
| **Local Model** | ✅ Phi-3-mini (2.3GB) | ❌ Not needed |
| **Disk Space** | ~5GB (app + model) | ~500MB (app only) |
| **RAM** | 8GB (model loading) | 4GB (UI only) |
| **Admin Rights** | ❌ Not required | ❌ Not required |

### 4. Cost Structure

| Model | Cost per 1M tokens (input / output) | Speed | Quality |
|-------|-------------------------------------|-------|---------|
| **gpt-4o-mini** | $0.15 / $0.60 | Fast | Good |
| **gpt-4o** | $2.50 / $10.00 | Medium | Excellent |
| **claude-3-5-haiku** | $0.80 / $4.00 | Fast | Good |
| **claude-3-5-sonnet** | $3.00 / $15.00 | Medium | Excellent |

**Typical usage**: 100-line code review = ~500 tokens input + ~1000 tokens output = **$0.001-0.05** per review

### 5. Removed Features

- ❌ Ollama portable packaging
- ❌ Offline VDI support
- ❌ Auto-start Ollama server
- ❌ Portable EXE bundling (with model)

### 6. Added Features

- ✅ Multi-provider support (OpenAI + Anthropic)
- ✅ Environment variable configuration (.env)
- ✅ API key validation on startup
- ✅ Provider switching (OpenAI ⇄ Anthropic)

## Quick Start

### 1. Install Dependencies

```bash
cd csharp-code-reviewer-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your API key
# Option 1: OpenAI
OPENAI_API_KEY=sk-your-key-here

# Option 2: Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Run Application

```bash
python app/main.py
```

## Migration Guide (Ollama → API)

If you're migrating from the Ollama version:

### Code Changes

```python
# OLD (Ollama)
from app.core.ollama_client import OllamaClient
client = OllamaClient(model_name="phi3:mini")

# NEW (API)
from app.core.api_client import APIClient
client = APIClient(provider="openai", model_name="gpt-4o-mini")
# or
client = APIClient(provider="anthropic", model_name="claude-3-5-haiku-20241022")
```

### Environment Setup

```bash
# OLD: No configuration needed (Ollama runs locally)

# NEW: Requires API key in .env
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
```

## Pros & Cons

### Advantages (API Version)

1. **No Local Setup**: No need to install/run Ollama
2. **Better Quality**: GPT-4o, Claude 3.5 Sonnet > Phi-3-mini
3. **Faster Inference**: Cloud GPUs > CPU inference
4. **Lower Disk/RAM**: No 2.3GB model file
5. **Latest Models**: Always use newest versions

### Disadvantages (API Version)

1. **Requires Internet**: Can't work offline
2. **API Costs**: $0.001-0.05 per review (vs free)
3. **Privacy**: Code sent to external APIs
4. **API Key Management**: Must secure keys

## Use Case Recommendations

### Use **Ollama Version** (Original) if:
- ❌ No internet access (VDI, airgapped networks)
- ❌ Can't use external APIs (data privacy, security policy)
- ✅ Want 100% free operation
- ✅ OK with slower inference (10-20s per review)

### Use **API Version** (This Fork) if:
- ✅ Have internet access
- ✅ Can use external APIs (non-sensitive code)
- ✅ Want best quality results
- ✅ Want fast inference (1-3s per review)
- ✅ Budget allows API costs ($0.001-0.05/review)

## Development History

| Date | Version | Description |
|------|---------|-------------|
| 2025-01-08 ~ 2025-01-19 | 1.0.0 | Original Ollama version (Week 1-5 complete) |
| 2025-11-13 | 2.0.0 | API version fork (GPT/Claude support) |

## Future Plans

- [ ] Azure OpenAI support (enterprise deployments)
- [ ] Google Gemini support
- [ ] Local LLM fallback (llama.cpp, no Ollama dependency)
- [ ] Cost tracking dashboard
- [ ] Prompt optimization for each provider

---

**Original Project**: [csharp-code-reviewer](../csharp-code-reviewer)
**API Fork**: csharp-code-reviewer-api (this directory)
**License**: MIT License (same as original)
