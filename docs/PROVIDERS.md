# Provider Support - Embeddings & Vectorstores

This document lists all supported embeddings and vectorstore providers, how to install them, and how to configure them.

## 🎯 Quick Start

**To switch providers:**
1. Edit `environment/default.toml`
2. Change `provider = "..."` under `[embeddings]` or `[vectorstore]`
3. Run your application - **NO CODE CHANGES NEEDED!**

---

## 📦 Embeddings Providers

### 1. Google (text-embedding-004)

**Already Installed** ✅

**Configuration:**
```toml
[embeddings]
provider = "google"
dimension = 768

[embeddings.google]
model = "models/text-embedding-004"
task_type = "retrieval_document"
batch_size = 100
title = ""
```

**Environment Variables:**
```bash
export GEMINI_API_KEY="your-api-key"
```

---

### 2. OpenAI (text-embedding-3)

**Installation:**
```bash
pip install openai
```

**Configuration:**
```toml
[embeddings]
provider = "openai"
dimension = 1536  # 1536 for text-embedding-3-small, 3072 for 3-large

[embeddings.openai]
api_key = "$OPENAI_API_KEY"
model = "text-embedding-3-small"  # or text-embedding-3-large
batch_size = 100
dimensions = 1536  # Can reduce for efficiency
```

**Environment Variables:**
```bash
export OPENAI_API_KEY="your-api-key"
```

---

### 3. HuggingFace (sentence-transformers)

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
model_name = "sentence-transformers/all-MiniLM-L6-v2"
cache_folder = "models/huggingface"
device = "cpu"  # or "cuda" for GPU
```

**Popular Models:**
- `all-MiniLM-L6-v2` (384 dim) - Fast, good quality
- `all-mpnet-base-v2` (768 dim) - Better quality
- `all-MiniLM-L12-v2` (384 dim) - Balanced

**No API key needed** - runs locally!

---

### 4. Cohere (embed-english-v3.0)

**Installation:**
```bash
pip install cohere
```

**Configuration:**
```toml
[embeddings]
provider = "cohere"
dimension = 1024

[embeddings.cohere]
api_key = "$COHERE_API_KEY"
model = "embed-english-v3.0"  # or embed-multilingual-v3.0
input_type = "search_document"  # or search_query
batch_size = 96
```

**Environment Variables:**
```bash
export COHERE_API_KEY="your-api-key"
```

---

### 5. Anthropic (Voyage AI - voyage-2)

**Installation:**
```bash
pip install voyageai
```

**Configuration:**
```toml
[embeddings]
provider = "anthropic"
dimension = 1024  # 1024 for voyage-2, 1536 for voyage-large-2

[embeddings.anthropic]
api_key = "$VOYAGE_API_KEY"
model = "voyage-2"  # or voyage-large-2
input_type = "document"  # or query
batch_size = 128
```

**Environment Variables:**
```bash
export VOYAGE_API_KEY="your-api-key"
```

---

## 🗄️ Vectorstore Providers

### 1. ChromaDB (Local Persistent Storage)

**Already Installed** ✅

**Configuration:**
```toml
[vectorstore]
provider = "chroma"
collection_name = "rag_documents"

[vectorstore.chroma]
persist_directory = "storage/chroma"
distance_function = "cosine"  # cosine, l2, ip
anonymized_telemetry = false
```

**Setup:**
- No additional setup needed
- Data stored locally in `storage/chroma/`

---

### 2. Pinecone (Managed Cloud Service)

**Installation:**
```bash
pip install pinecone-client
```

**Configuration:**
```toml
[vectorstore]
provider = "pinecone"
collection_name = "rag_documents"

[vectorstore.pinecone]
api_key = "$PINECONE_API_KEY"
environment = "us-west1-gcp"  # Check Pinecone console
index_name = "rag-documents"
dimension = 768
metric = "cosine"  # cosine, euclidean, dotproduct
```

**Environment Variables:**
```bash
export PINECONE_API_KEY="your-api-key"
```

**Setup:**
1. Sign up at https://www.pinecone.io/
2. Create a project
3. Get your API key and environment from console

---

### 3. Qdrant (Open-Source Vector Search)

**Installation:**
```bash
pip install qdrant-client
```

**Configuration (Local):**
```toml
[vectorstore]
provider = "qdrant"
collection_name = "rag_documents"

[vectorstore.qdrant]
host = "localhost"
port = 6333
grpc_port = 6334
prefer_grpc = false
api_key = ""  # Leave empty for local
distance = "Cosine"  # Cosine, Euclid, Dot
```

**Setup (Docker):**
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/storage/qdrant:/qdrant/storage \
    qdrant/qdrant
```

**Configuration (Cloud):**
```toml
[vectorstore.qdrant]
host = "your-cluster.qdrant.io"
port = 6333
api_key = "$QDRANT_API_KEY"
```

---

### 4. Weaviate (Cloud-Native Vector Database)

**Installation:**
```bash
pip install weaviate-client
```

**Configuration (Local):**
```toml
[vectorstore]
provider = "weaviate"
collection_name = "rag_documents"

[vectorstore.weaviate]
url = "http://localhost:8080"
api_key = ""  # Leave empty for local
class_name = "RagDocument"
distance = "cosine"  # cosine, l2-squared, dot, hamming, manhattan
```

**Setup (Docker):**
```bash
docker run -p 8080:8080 \
    -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
    -v $(pwd)/storage/weaviate:/var/lib/weaviate \
    semitechnologies/weaviate:latest
```

**Configuration (Cloud):**
```toml
[vectorstore.weaviate]
url = "https://your-cluster.weaviate.cloud"
api_key = "$WEAVIATE_API_KEY"
```

---

## 🔄 Provider Switching Examples

### Example 1: Switch from Google to OpenAI Embeddings

**Before:**
```toml
[embeddings]
provider = "google"
```

**After:**
```toml
[embeddings]
provider = "openai"
```

**That's it!** Run your app - no code changes needed.

---

### Example 2: Switch from ChromaDB to Pinecone

**Before:**
```toml
[vectorstore]
provider = "chroma"
```

**After:**
```toml
[vectorstore]
provider = "pinecone"
```

**That's it!** Run your app - no code changes needed.

---

### Example 3: Complete Provider Switch

Switch from **Google + ChromaDB** to **OpenAI + Pinecone**:

```toml
[embeddings]
provider = "openai"  # Changed from "google"

[vectorstore]
provider = "pinecone"  # Changed from "chroma"
```

**Same application code works perfectly!**

---

## 📊 Provider Comparison

### Embeddings

| Provider | Dimension | API Key | Local/Cloud | Speed | Quality |
|----------|-----------|---------|-------------|-------|---------|
| Google | 768 | Yes | Cloud | Fast | Excellent |
| OpenAI | 1536/3072 | Yes | Cloud | Fast | Excellent |
| HuggingFace | 384-768 | No | Local | Medium | Good |
| Cohere | 1024 | Yes | Cloud | Fast | Excellent |
| Anthropic | 1024/1536 | Yes | Cloud | Fast | Excellent |

### Vectorstores

| Provider | Type | Setup | Scalability | Cost |
|----------|------|-------|-------------|------|
| ChromaDB | Local | Easy | Single machine | Free |
| Pinecone | Managed | Easy | Auto-scaling | Paid |
| Qdrant | Self-hosted/Cloud | Medium | High | Free/Paid |
| Weaviate | Self-hosted/Cloud | Medium | High | Free/Paid |

---

## 🎯 Recommendations

### For Development
- **Embeddings:** HuggingFace (free, no API needed)
- **Vectorstore:** ChromaDB (simple, local)

### For Production (Small Scale)
- **Embeddings:** Google or OpenAI (high quality)
- **Vectorstore:** Qdrant self-hosted (open-source, powerful)

### For Production (Large Scale)
- **Embeddings:** OpenAI or Cohere (reliable, scalable)
- **Vectorstore:** Pinecone or Weaviate Cloud (managed, auto-scaling)

---

## 🚀 Testing Providers

Use example scripts to test different provider combinations:

```bash
# Test basic vectorstore operations
python examples/demo_vectorstore.py

# Test provider switching
python examples/demo_provider_switching.py

# Edit environment/default.toml to change providers
# Then test again - same code, different providers!
```

---

## 💡 Tips

1. **Start with defaults** (Google + ChromaDB) - already configured
2. **Test locally** with HuggingFace + ChromaDB before using paid APIs
3. **Match dimensions** between embeddings and vectorstore configs
4. **Use environment variables** for API keys (never commit them!)
5. **Check provider limits** (rate limits, batch sizes, etc.)

---

## 🔗 Provider Documentation

- **Google:** https://ai.google.dev/docs/embeddings_guide
- **OpenAI:** https://platform.openai.com/docs/guides/embeddings
- **HuggingFace:** https://huggingface.co/sentence-transformers
- **Cohere:** https://docs.cohere.com/docs/embeddings
- **Voyage AI:** https://docs.voyageai.com/
- **ChromaDB:** https://docs.trychroma.com/
- **Pinecone:** https://docs.pinecone.io/
- **Qdrant:** https://qdrant.tech/documentation/
- **Weaviate:** https://weaviate.io/developers/weaviate

