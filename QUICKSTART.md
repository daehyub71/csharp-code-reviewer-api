# Quick Start Guide - C# Code Reviewer (API Version)

## 5분 안에 시작하기

### 1. Prerequisites

- Python 3.11+ installed
- OpenAI API key OR Anthropic API key
- Internet connection

### 2. Installation

```bash
# Clone or copy the project
cd csharp-code-reviewer-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or your favorite editor

# Add ONE of these API keys:
# Option 1: OpenAI (recommended for beginners)
OPENAI_API_KEY=sk-your-openai-key-here

# Option 2: Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Set default provider (optional)
DEFAULT_PROVIDER=openai  # or 'anthropic'
```

### 4. Get API Keys

#### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Sign up / Log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. Paste into `.env` file

#### Anthropic
1. Go to https://console.anthropic.com/
2. Sign up / Log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-...`)
6. Paste into `.env` file

### 5. Run Application

```bash
# Make sure virtual environment is activated
python app/main.py

# If error occurs, check:
# 1. .env file exists and has valid API key
# 2. Virtual environment is activated
# 3. All dependencies are installed
```

### 6. Test Code Review

1. **Paste code** in the "Before" editor:
   ```csharp
   public class Example
   {
       public void ProcessData(string data)
       {
           var result = data.ToUpper();
           Console.WriteLine(result);
       }
   }
   ```

2. **Click "Analyze Code"** button (or press F5)

3. **Wait 1-3 seconds** for analysis

4. **View results** in the "Result" panel:
   - Issues found
   - Improved code in "After" editor
   - Detailed report

## Common Issues

### Error: "No API keys configured"
**Solution**: Check your `.env` file. Make sure it has `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.

### Error: "API connection failed"
**Possible causes**:
1. Invalid API key (check for typos)
2. No internet connection
3. API rate limit reached
4. Insufficient API credits

### Error: "ModuleNotFoundError: No module named 'openai'"
**Solution**: Install dependencies: `pip install -r requirements.txt`

### Slow performance
**Solution**:
- Use faster models: `gpt-4o-mini` (OpenAI) or `claude-3-5-haiku` (Anthropic)
- Set `DEFAULT_MODEL` in `.env` file

## Model Recommendations

### For Cost-Conscious Users
- **OpenAI**: `gpt-4o-mini` ($0.15/1M input tokens)
- **Anthropic**: `claude-3-5-haiku-20241022` ($0.80/1M input tokens)

### For Best Quality
- **OpenAI**: `gpt-4o` ($2.50/1M input tokens)
- **Anthropic**: `claude-3-5-sonnet-20241022` ($3.00/1M input tokens)

### Typical Cost
- 100-line code review: **$0.001-0.005** (mini/haiku models)
- 500-line code review: **$0.005-0.02** (mini/haiku models)

## Next Steps

1. Try the **File Upload** mode (drag & drop `.cs` files)
2. Try the **Folder Select** mode (analyze entire projects)
3. Check the **Report History** (Ctrl+H)
4. Customize review categories in `resources/templates/review_categories/`

## Getting Help

- Documentation: [README.md](README.md)
- Changes from Ollama version: [CHANGES.md](CHANGES.md)
- API client code: [app/core/api_client.py](app/core/api_client.py)

---

**Need Offline Version?** Check [../csharp-code-reviewer](../csharp-code-reviewer) for the Ollama-based version.
