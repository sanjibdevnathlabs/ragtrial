# 🔌 Provider Guide - Complete Reference

This is the complete guide for all provider integrations in the RAG application. The system supports **3 LLM providers**, **4 embeddings providers**, and **4 vectorstore providers** with configuration-based switching.

## 🎯 Quick Start

**To switch any provider:**
1. Edit `environment/default.toml`
2. Change `provider = "..."` under the relevant section (`[rag]`, `[embeddings]`, or `[vectorstore]`)
3. Set required environment variables (API keys)
4. Run your application - **NO CODE CHANGES NEEDED!**

**Architecture:**
```
User Query
    ↓
[LLM Provider] ← Generates answer
    ↓ (needs context)
[Vectorstore Provider] ← Retrieves relevant documents
    ↓ (searches vectors)
[Embeddings Provider] ← Encodes text to vectors
```

---

## 📋 Table of Contents

1. [LLM Providers (RAG)](#-llm-providers-for-rag)
   - Google Gemini
   - OpenAI GPT
   - Anthropic Claude

2. [Embeddings Providers](#-embeddings-providers)
   - Google text-embedding-004
   - OpenAI text-embedding-3
   - HuggingFace (Local)
   - Anthropic (Voyage AI)

3. [Vectorstore Providers](#-vectorstore-providers)
   - ChromaDB (Local)
   - Pinecone (Cloud)
   - Qdrant (Self-hosted/Cloud)
   - Weaviate (Cloud)

---

## 🤖 LLM Providers (for RAG)

LLM providers generate natural language answers based on retrieved document context.

### Configuration

**Set provider in `environment/default.toml`:**
```toml
[rag]
provider = "google"  # Options: "google", "openai", "anthropic"
retrieval_k = 5      # Number of documents to retrieve
```

---

### 1. Google Gemini ⚡ (Recommended)

**Best for:** Production use, fast responses, cost-effective

**Models:**
- `gemini-2.0-flash-exp` - Latest experimental, fast
- `gemini-2.5-flash` - Balanced speed/quality
- `gemini-2.5-pro` - Highest quality, slower

**Configuration:**
```toml
[rag.google]
api_key = "$GEMINI_API_KEY"        # Environment variable
model = "gemini-2.0-flash-exp"     # Recommended
temperature = 0.1                   # Lower = more factual (0.0-2.0)
max_tokens = 1000                   # Maximum response length
```

**Environment Variables:**
```bash
export GEMINI_API_KEY="your-api-key"
```

**Get API Key:** https://ai.google.dev/

---

### 2. OpenAI GPT

**Best for:** Highest quality answers, extensive tooling

**Models:**
- `gpt-4o` - Latest, most capable
- `gpt-4o-mini` - Fast, cost-effective (recommended)
- `gpt-4-turbo` - Previous generation, still excellent

**Configuration:**
```toml
[rag.openai]
api_key = "$OPENAI_API_KEY"        # Environment variable
model = "gpt-4o-mini"              # Recommended
temperature = 0.1                   # Lower = more factual (0.0-2.0)
max_tokens = 1000                   # Maximum response length
verify_ssl = true                   # SSL certificate verification
```

**Installation:**
```bash
pip install openai
```

**Environment Variables:**
```bash
export OPENAI_API_KEY="your-api-key"
```

**Get API Key:** https://platform.openai.com/api-keys

---

### 3. Anthropic Claude

**Best for:** Advanced reasoning, long context windows

**Models:**
- `claude-3-5-sonnet-20241022` - Latest, most capable (recommended)
- `claude-3-opus-20240229` - Previous flagship
- `claude-3-haiku-20240307` - Fast, efficient

**Configuration:**
```toml
[rag.anthropic]
api_key = "$ANTHROPIC_API_KEY"     # Environment variable
model = "claude-3-5-sonnet-20241022"  # Recommended
temperature = 0.1                   # Lower = more factual (0.0-1.0)
max_tokens = 1000                   # Maximum response length
verify_ssl = true                   # SSL certificate verification
```

**Installation:**
```bash
pip install anthropic
```

**Environment Variables:**
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

**Get API Key:** https://console.anthropic.com/

---

## 🧬 Embeddings Providers

Embeddings providers convert text to numerical vectors for similarity search.

### Configuration

**Set provider in `environment/default.toml`:**
```toml
[embeddings]
provider = "google"  # Options: "google", "openai", "huggingface", "anthropic"
dimension = 768      # Vector dimension (provider-specific)
```

---

### 1. Google (text-embedding-004) ⚡ (Recommended)

**Already Installed** ✅

**Best for:** Production use, free tier available, good quality

**Configuration:**
```toml
[embeddings]
provider = "google"
dimension = 768

[embeddings.google]
model = "models/text-embedding-004"
task_type = "retrieval_document"  # or "retrieval_query"
batch_size = 100
title = ""
```

**Environment Variables:**
```bash
export GEMINI_API_KEY="your-api-key"
```

**Features:**
- Dimension: 768
- Max tokens: 2048
- Free tier: Generous limits

---

### 2. OpenAI (text-embedding-3)

**Best for:** High-quality embeddings, extensive model options

**Models:**
- `text-embedding-3-large` - Highest quality (3072 dimensions)
- `text-embedding-3-small` - Faster, cost-effective (1536 dimensions)

**Installation:**
```bash
pip install openai
```

**Configuration:**
```toml
[embeddings]
provider = "openai"
dimension = 1536  # 1536 for small, 3072 for large

[embeddings.openai]
model = "text-embedding-3-small"
batch_size = 100
```

**Environment Variables:**
```bash
export OPENAI_API_KEY="your-api-key"
```

---

### 3. HuggingFace (Local) 🏠

**Best for:** Offline usage, no API costs, privacy

**Installation:**
```bash
pip install sentence-transformers
```

**Configuration:**
```toml
[embeddings]
provider = "huggingface"
dimension = 384  # Depends on model

[embeddings.huggingface]
model = "all-MiniLM-L6-v2"  # Recommended for speed
device = "cpu"               # or "cuda" for GPU
normalize_embeddings = true
```

**Popular Models:**
- `all-MiniLM-L6-v2` - Fast, 384 dimensions (recommended)
- `all-mpnet-base-v2` - Better quality, 768 dimensions
- `all-distilroberta-v1` - Balanced, 768 dimensions

**Features:**
- ✅ No API key required
- ✅ Works offline
- ✅ Free
- ❌ Slower than cloud providers
- ❌ Requires local resources

**Model Downloads:** Models are automatically downloaded on first use to `models/huggingface/`

---

### 4. Anthropic (Voyage AI)

**Best for:** High-quality embeddings, optimized for RAG

**Installation:**
```bash
pip install voyageai
```

**Configuration:**
```toml
[embeddings]
provider = "anthropic"
dimension = 1024

[embeddings.anthropic]
model = "voyage-2"
batch_size = 128
input_type = "document"  # or "query"
```

**Environment Variables:**
```bash
export VOYAGE_API_KEY="your-api-key"
```

**Get API Key:** https://www.voyageai.com/

---

## 🗄️ Vectorstore Providers

Vectorstores store and efficiently retrieve document embeddings.

### Configuration

**Set provider in `environment/default.toml`:**
```toml
[vectorstore]
provider = "chroma"  # Options: "chroma", "pinecone", "qdrant", "weaviate"
collection_name = "documents"
```

---

### 1. ChromaDB (Local) 🏠 (Recommended)

**Already Installed** ✅

**Best for:** Development, local testing, no cloud costs

**Configuration:**
```toml
[vectorstore]
provider = "chroma"
collection_name = "documents"

[vectorstore.chroma]
persist_directory = "storage/chroma"
distance_metric = "cosine"  # or "l2", "ip"
```

**Features:**
- ✅ No API key required
- ✅ Works offline
- ✅ Free
- ✅ Fast for small-medium datasets
- ❌ Not suitable for production scale (>1M vectors)

**Storage Location:** `storage/chroma/`

---

### 2. Pinecone (Cloud)

**Best for:** Production scale, managed service, high performance

**Installation:**
```bash
pip install pinecone-client
```

**Configuration:**
```toml
[vectorstore]
provider = "pinecone"
collection_name = "documents"  # Index name in Pinecone

[vectorstore.pinecone]
environment = "us-west1-gcp"  # Your Pinecone environment
dimension = 768                # Must match embeddings dimension
metric = "cosine"              # or "euclidean", "dotproduct"
```

**Environment Variables:**
```bash
export PINECONE_API_KEY="your-api-key"
```

**Setup:**
1. Create account at https://www.pinecone.io/
2. Create an index with matching dimension
3. Note your environment and API key

**Features:**
- ✅ Production-ready scalability
- ✅ Fast queries even at millions of vectors
- ✅ Managed service (no DevOps)
- ❌ Costs money
- ❌ Requires internet connection

---

### 3. Qdrant

**Best for:** Self-hosted production, open-source, flexibility

**Installation:**
```bash
pip install qdrant-client
```

**Configuration:**
```toml
[vectorstore]
provider = "qdrant"
collection_name = "documents"

[vectorstore.qdrant]
url = "http://localhost:6333"  # or cloud URL
dimension = 768                 # Must match embeddings
distance = "Cosine"             # or "Euclid", "Dot"
on_disk = true                  # Store on disk (slower, more capacity)
```

**Environment Variables (for cloud):**
```bash
export QDRANT_API_KEY="your-api-key"  # Only for Qdrant Cloud
```

**Setup Options:**

**Option A: Docker (Recommended)**
```bash
docker run -p 6333:6333 -v $(pwd)/storage/qdrant:/qdrant/storage qdrant/qdrant
```

**Option B: Qdrant Cloud**
- Sign up at https://cloud.qdrant.io/
- Create cluster and get API key

**Features:**
- ✅ Open-source
- ✅ Self-hosted or cloud
- ✅ Good performance
- ✅ Rich filtering capabilities
- ❌ Requires setup/maintenance

---

### 4. Weaviate (Cloud)

**Best for:** Semantic search, GraphQL API, multi-modal

**Installation:**
```bash
pip install weaviate-client
```

**Configuration:**
```toml
[vectorstore]
provider = "weaviate"
collection_name = "documents"

[vectorstore.weaviate]
url = "https://your-instance.weaviate.network"
dimension = 768
distance_metric = "cosine"  # or "dot", "l2-squared"
```

**Environment Variables:**
```bash
export WEAVIATE_API_KEY="your-api-key"
```

**Setup:**
1. Create account at https://console.weaviate.cloud/
2. Create cluster
3. Get API key and URL

**Features:**
- ✅ GraphQL API
- ✅ Multi-modal search (text + images)
- ✅ Built-in ML models
- ❌ Costs money
- ❌ Learning curve

---

## 🔄 Switching Providers

### Example 1: Switch from Google to OpenAI (everything)

```toml
# Before (Google)
[rag]
provider = "google"

[embeddings]
provider = "google"

[vectorstore]
provider = "chroma"

# After (OpenAI)
[rag]
provider = "openai"

[embeddings]
provider = "openai"
dimension = 1536  # ⚠️ Different from Google (768)

[vectorstore]
provider = "chroma"  # Keep same, but MUST re-index with new embeddings!
```

**⚠️ Important:** When changing embeddings provider, you **MUST re-index all documents** because vector dimensions/values change!

### Example 2: Mix and match providers

```toml
# Google for LLM (fast, cheap)
[rag]
provider = "google"

# HuggingFace for embeddings (free, offline)
[embeddings]
provider = "huggingface"
dimension = 384

# Pinecone for vectorstore (production scale)
[vectorstore]
provider = "pinecone"
```

---

## 📊 Provider Comparison

### LLM Providers

| Provider | Speed | Quality | Cost | Context Window | Best For |
|----------|-------|---------|------|----------------|----------|
| Google Gemini | ⚡⚡⚡ | ⭐⭐⭐⭐ | $ | 1M tokens | Production |
| OpenAI GPT | ⚡⚡ | ⭐⭐⭐⭐⭐ | $$ | 128K tokens | Quality |
| Anthropic Claude | ⚡⚡ | ⭐⭐⭐⭐⭐ | $$ | 200K tokens | Reasoning |

### Embeddings Providers

| Provider | Quality | Speed | Cost | Offline | Best For |
|----------|---------|-------|------|---------|----------|
| Google | ⭐⭐⭐⭐ | ⚡⚡⚡ | Free tier | ❌ | Production |
| OpenAI | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | $ | ❌ | Quality |
| HuggingFace | ⭐⭐⭐ | ⚡⚡ | Free | ✅ | Offline/Dev |
| Anthropic (Voyage) | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | $$ | ❌ | RAG-optimized |

### Vectorstore Providers

| Provider | Scale | Speed | Cost | Setup | Best For |
|----------|-------|-------|------|-------|----------|
| ChromaDB | <100K | ⚡⚡⚡ | Free | Easy | Dev/Small |
| Pinecone | Millions | ⚡⚡⚡ | $$ | Easy | Production |
| Qdrant | Millions | ⚡⚡⚡ | Free (self) | Medium | Self-hosted |
| Weaviate | Millions | ⚡⚡⚡ | $$ | Medium | Semantic |

---

## 🐛 Troubleshooting

### "Provider not found" error

**Problem:** Selected provider not installed

**Solution:**
```bash
# Install missing provider
pip install openai          # For OpenAI
pip install anthropic       # For Anthropic Claude
pip install sentence-transformers  # For HuggingFace
pip install pinecone-client # For Pinecone
pip install qdrant-client   # For Qdrant
pip install weaviate-client # For Weaviate
pip install voyageai        # For Anthropic/Voyage embeddings
```

### "API key not found" error

**Problem:** Missing or incorrect environment variable

**Solution:**
```bash
# Check current environment variables
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Set permanently in ~/.bashrc or ~/.zshrc
export GEMINI_API_KEY="your-key-here"
```

### "Dimension mismatch" error

**Problem:** Vectorstore dimension doesn't match embeddings

**Solution:**
1. Delete existing vectorstore: `rm -rf storage/chroma` (or equivalent)
2. Update `dimension` in `[embeddings]` config
3. Re-index all documents

### Slow embeddings generation

**Problem:** Using HuggingFace on CPU

**Solutions:**
1. Switch to GPU: `device = "cuda"` (requires CUDA)
2. Switch to cloud provider (Google/OpenAI)
3. Use smaller model: `all-MiniLM-L6-v2`

---

## 📚 Additional Resources

- **LangChain Docs:** https://python.langchain.com/docs/integrations/
- **Google AI Studio:** https://ai.google.dev/
- **OpenAI Platform:** https://platform.openai.com/
- **Anthropic Console:** https://console.anthropic.com/
- **HuggingFace Models:** https://huggingface.co/models
- **ChromaDB Docs:** https://docs.trychroma.com/
- **Pinecone Docs:** https://docs.pinecone.io/
- **Qdrant Docs:** https://qdrant.tech/documentation/
- **Weaviate Docs:** https://weaviate.io/developers/weaviate
