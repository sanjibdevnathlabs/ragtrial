# RAG Multi-Provider Guide

## Overview

The RAG application supports **3 LLM providers** with easy switching via configuration:
- **Google Gemini** - Fast, efficient, good for production
- **OpenAI GPT** - High quality, widely supported
- **Anthropic Claude** - Advanced reasoning, long context

---

## Configuration

### 1. Set Provider in `environment/default.toml`

```toml
[rag]
provider = "google"  # Options: "google", "openai", "anthropic"
retrieval_k = 5      # Number of documents to retrieve
```

### 2. Provider-Specific Settings

#### Google (Gemini)
```toml
[rag.google]
api_key = "$GEMINI_API_KEY"        # Environment variable
model = "gemini-1.5-flash"         # or gemini-1.5-pro, gemini-1.0-pro
temperature = 0.1                   # Lower = more factual (0.0-2.0)
max_tokens = 1000                   # Maximum response length
```

#### OpenAI (GPT)
```toml
[rag.openai]
api_key = "$OPENAI_API_KEY"        # Environment variable
model = "gpt-4o-mini"              # or gpt-4o, gpt-4-turbo, gpt-3.5-turbo
temperature = 0.1                   # Lower = more factual (0.0-2.0)
max_tokens = 1000                   # Maximum response length
verify_ssl = true                   # SSL certificate verification
```

#### Anthropic (Claude)
```toml
[rag.anthropic]
api_key = "$ANTHROPIC_API_KEY"     # Environment variable
model = "claude-3-5-sonnet-20241022"  # or claude-3-opus, claude-3-haiku
temperature = 0.1                   # Lower = more factual (0.0-1.0)
max_tokens = 1000                   # Maximum response length
verify_ssl = true                   # SSL certificate verification
```

---

## Setup

### 1. Set Environment Variables

```bash
# Google Gemini
export GEMINI_API_KEY="your-gemini-api-key"

# OpenAI GPT
export OPENAI_API_KEY="your-openai-api-key"

# Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 2. Verify Configuration

```bash
python -c "from config import Config; c = Config(); print(f'Provider: {c.rag.provider}'); print(f'Model: {c.rag.google.model if c.rag.provider == \"google\" else c.rag.openai.model if c.rag.provider == \"openai\" else c.rag.anthropic.model}')"
```

---

## Usage

### Basic Usage

```python
from config import Config
from app import RAGChain

# Load configuration (provider set in default.toml)
config = Config()

# Initialize RAG chain
chain = RAGChain(config)

# Query documents
response = chain.query("What is retrieval-augmented generation?")

# Access response
print(response['answer'])
print(f"Sources: {len(response['sources'])}")
print(f"Retrieved {response['retrieval_count']} documents")
```

### Switching Providers

```python
from config import Config
from app import RAGChain

config = Config()

# Option 1: Change in code (for testing)
config.rag.provider = "openai"
config.rag.openai.api_key = "your-key"

# Option 2: Change in environment/default.toml (recommended)
# [rag]
# provider = "openai"

chain = RAGChain(config)
response = chain.query("Your question here")
```

---

## Provider Comparison

| Feature | Google Gemini | OpenAI GPT | Anthropic Claude |
|---------|---------------|------------|------------------|
| **Speed** | ⚡⚡⚡ Very Fast | ⚡⚡ Fast | ⚡⚡ Fast |
| **Cost** | 💰 Low | 💰💰 Medium | 💰💰 Medium |
| **Quality** | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Excellent |
| **Context** | 32K tokens | 128K tokens | 200K tokens |
| **Best For** | Production, Speed | General purpose | Long documents |

---

## Model Options

### Google Gemini Models
- `gemini-1.5-flash` - **Recommended** - Fast, efficient
- `gemini-1.5-pro` - Higher quality, slower
- `gemini-1.0-pro` - Legacy model

### OpenAI GPT Models
- `gpt-4o-mini` - **Recommended** - Fast, cost-effective
- `gpt-4o` - Highest quality
- `gpt-4-turbo` - Fast GPT-4
- `gpt-3.5-turbo` - Fastest, cheapest

### Anthropic Claude Models
- `claude-3-5-sonnet-20241022` - **Recommended** - Best balance
- `claude-3-opus` - Highest quality, slowest
- `claude-3-haiku` - Fastest, cheapest

---

## Configuration Best Practices

### Temperature Settings

```toml
temperature = 0.0   # Deterministic, factual (recommended for RAG)
temperature = 0.1   # Mostly factual, slight variation
temperature = 0.5   # Balanced creativity and factual
temperature = 1.0   # Creative, less predictable
temperature = 2.0   # Very creative (only Gemini/OpenAI)
```

### Max Tokens

```toml
max_tokens = 500    # Short answers
max_tokens = 1000   # Medium answers (recommended)
max_tokens = 2000   # Long, detailed answers
max_tokens = 4000   # Very detailed, uses more API credits
```

### Retrieval K

```toml
retrieval_k = 3     # Faster, less context
retrieval_k = 5     # Good balance (recommended)
retrieval_k = 10    # More context, slower
retrieval_k = 20    # Maximum context (may hit token limits)
```

---

## API Key Management

### Secure Storage

**✅ Recommended:**
```bash
# Store in environment
export GEMINI_API_KEY="your-key"

# Or use .env file (gitignored)
echo "GEMINI_API_KEY=your-key" >> .env
```

**❌ Never:**
```toml
# Don't hardcode in TOML!
api_key = "hardcoded-key-here"  # ❌ Security risk!
```

### Loading from .env

```python
from dotenv import load_dotenv
load_dotenv()

from config import Config
config = Config()  # API keys loaded from environment
```

---

## Testing

### Test Configuration Loading

```bash
python -c "from config import Config; c = Config(); print(f'✅ Config loaded: {c.rag.provider}')"
```

### Test All Providers

```bash
pytest tests/test_rag_*.py -v
```

### Run Example

```bash
python examples/demo_rag_query.py
```

---

## Troubleshooting

### Issue: "API key not found"

**Solution:** Set environment variable
```bash
export GEMINI_API_KEY="your-key"
```

### Issue: "Unsupported LLM provider"

**Solution:** Check provider name in `default.toml`
```toml
[rag]
provider = "google"  # Must be: google, openai, or anthropic
```

### Issue: "Module not found: langchain_openai"

**Solution:** Install missing dependency
```bash
pip install langchain-openai langchain-anthropic
```

---

## Cost Estimation

### Per 1M Tokens (Approximate)

| Provider | Input | Output |
|----------|-------|--------|
| **Gemini Flash** | $0.075 | $0.30 |
| **GPT-4o-mini** | $0.15 | $0.60 |
| **Claude Sonnet** | $3.00 | $15.00 |

**Example:** 1000 queries × 500 tokens each = 500K tokens ≈ $0.04 (Gemini) to $1.50 (Claude)

---

## Next Steps

1. ✅ Set up API keys in environment
2. ✅ Choose provider in `default.toml`
3. ✅ Ingest documents: `python -m ingestion.ingest`
4. ✅ Test RAG: `python examples/demo_rag_query.py`
5. ✅ Build your application!

