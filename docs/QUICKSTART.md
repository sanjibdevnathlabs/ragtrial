# Quick Start Guide - Local Database Setup

This guide walks you through setting up your local vector database for the RAG application.

---

## 🎯 Default Setup (ChromaDB + Google Embeddings)

The easiest way to get started is with the default configuration.

### Step 1: Set API Key

```bash
export GEMINI_API_KEY="your-google-api-key"
```

**Get your free API key:** https://aistudio.google.com/apikey

### Step 2: Run Setup Script

```bash
python scripts/setup_database.py
```

This script will:
- ✅ Check prerequisites (Python version, dependencies)
- ✅ Create storage directories
- ✅ Test embeddings connection
- ✅ Initialize ChromaDB
- ✅ Verify everything works

### Expected Output

```
======================================================================
🚀 RAG Application - Database Setup
======================================================================

🔍 Checking prerequisites...
   ✅ Python 3.13.x
   ✅ GEMINI_API_KEY is set
   ✅ environment/default.toml
   [...]

📁 Creating storage directories...
   ✅ Created: storage/chroma
   ✅ Created: source_docs

🔧 Testing embeddings provider...
   Provider: google
   ✅ Success! Generated embedding with 768 dimensions

🗄️  Testing vectorstore...
   Provider: chroma
   ✅ Collection initialized
   ✅ Test document added
   ✅ Query returned 1 result(s)

======================================================================
✅ DATABASE SETUP COMPLETE!
======================================================================
```

---

## 🔧 What Gets Created

After running the setup script:

```
ragtrial/
├── storage/                  # ← NEW: Database storage
│   ├── chroma/              # ChromaDB data files
│   ├── qdrant/              # (for future use)
│   └── weaviate/            # (for future use)
└── source_docs/             # ← NEW: Place your documents here
```

---

## 🧪 Verify Installation

Run the example scripts to confirm everything works:

### 1. Quick Local Test (No API)

```bash
python scripts/quick_test.py
```

Tests local setup only (< 2 seconds).

### 2. API Connection Test

```bash
python scripts/test_api.py
```

Tests just the Google API connection.

### 3. Basic Vectorstore Demo

```bash
python examples/demo_vectorstore.py
```

This will:
- Create embeddings from sample text
- Store them in ChromaDB
- Perform similarity search queries

### 4. Provider Switching Demo

```bash
python examples/demo_provider_switching.py
```

This demonstrates the ORM-like abstraction working with your configured providers.

---

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY not found"

**Solution:**
```bash
export GEMINI_API_KEY="your-api-key"
```

Make it permanent (add to `~/.bashrc` or `~/.zshrc`):
```bash
echo 'export GEMINI_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc
```

### Error: "No module named 'chromadb'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Error: "Failed to initialize ChromaDB"

**Check:**
1. Do you have write permissions in the project directory?
2. Is `storage/chroma` directory accessible?
3. Try deleting `storage/chroma` and running setup again

---

## 🔄 Alternative Setup Options

### Option 1: No API Key (HuggingFace - Local)

Want to avoid API keys? Use local embeddings!

**Edit `environment/default.toml`:**
```toml
[embeddings]
provider = "huggingface"  # Changed from "google"
dimension = 384

[embeddings.huggingface]
model_name = "sentence-transformers/all-MiniLM-L6-v2"
device = "cpu"
```

**Install:**
```bash
pip install sentence-transformers
```

**Run setup:**
```bash
python scripts/setup_database.py  # No API key needed!
```

### Option 2: Docker-based Vectorstores

Want to use Qdrant or Weaviate instead of ChromaDB?

#### Qdrant

```bash
# Start Qdrant
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/storage/qdrant:/qdrant/storage \
    qdrant/qdrant

# Edit environment/default.toml
[vectorstore]
provider = "qdrant"

# Install client
pip install qdrant-client

# Run setup
python scripts/setup_database.py
```

#### Weaviate

```bash
# Start Weaviate
docker run -d -p 8080:8080 \
    -v $(pwd)/storage/weaviate:/var/lib/weaviate \
    semitechnologies/weaviate:latest

# Edit environment/default.toml
[vectorstore]
provider = "weaviate"

# Install client
pip install weaviate-client

# Run setup
python scripts/setup_database.py
```

---

## 📊 Verify Database Contents

### Check ChromaDB

```python
import chromadb

# Connect to database
client = chromadb.PersistentClient(path="storage/chroma")

# List collections
collections = client.list_collections()
print(f"Collections: {[c.name for c in collections]}")

# Get collection
collection = client.get_collection("rag_documents")
print(f"Document count: {collection.count()}")
```

### Check Qdrant

```bash
# Using HTTP API
curl http://localhost:6333/collections
```

### Check Weaviate

```bash
# Using HTTP API
curl http://localhost:8080/v1/schema
```

---

## 🎯 Next Steps

Once setup is complete:

### 1. Add Your Documents

```bash
# Place documents in source_docs/
cp ~/my-documents/*.pdf source_docs/
```

### 2. Run Ingestion Pipeline

```bash
python ingestion/ingest.py
```

*(Note: Document loaders are coming soon)*

### 3. Query Your Data

Use the example scripts or build your own queries!

---

## 💡 Configuration Tips

### Development Setup
```toml
[embeddings]
provider = "huggingface"  # Free, local

[vectorstore]
provider = "chroma"       # Simple, local
```

### Production Setup
```toml
[embeddings]
provider = "openai"       # High quality

[vectorstore]
provider = "pinecone"     # Managed, scalable
```

See **[docs/PROVIDERS.md](PROVIDERS.md)** for complete provider comparison.

---

## 🔗 Resources

- **Setup Script:** `scripts/setup_database.py`
- **Test Scripts:** `scripts/quick_test.py`, `scripts/test_api.py`
- **Examples:** `examples/`
- **Provider Guide:** `docs/PROVIDERS.md`
- **Configuration:** `environment/default.toml`

---

## ❓ Need Help?

1. Check the error message carefully
2. Verify your API key is set correctly
3. Make sure all dependencies are installed
4. Try the example scripts to isolate the issue
5. Check `docs/PROVIDERS.md` for provider-specific setup

**Happy RAG building! 🚀**

