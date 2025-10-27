# RAG Document Chat Application

A production-ready Retrieval-Augmented Generation (RAG) system with **ORM-like abstraction** for vector databases and embeddings. Switch providers with just configuration changes - **no code modifications needed**!

## 🎯 Project Goals

Build a "Chat with your Documents" application with two parallel implementations:
1. **Simple RAG Chain** (LangChain) - Straightforward implementation
2. **Agent-Based RAG** (LangGraph) - Advanced with loops and conditional logic

Both connect to the same indexed data for easy comparison of approaches.

---

## ✨ Key Features

### 🔄 Provider-Agnostic Architecture
- **ORM-like abstraction** similar to SQLAlchemy for databases
- **Zero code changes** to switch providers
- **16 provider combinations** supported out of the box

### 🎨 Flexible Provider Support

**Embeddings (4 providers):**
- ✅ Google (text-embedding-004)
- ✅ OpenAI (text-embedding-3-small/large)
- ✅ HuggingFace (sentence-transformers) - **Local, no API key!**
- ✅ Anthropic (Voyage AI - voyage-2)

**Vectorstores (4 providers):**
- ✅ ChromaDB (local persistent storage)
- ✅ Pinecone (managed cloud service)
- ✅ Qdrant (open-source vector search)
- ✅ Weaviate (cloud-native vector database)

### 🏗️ Production-Ready Infrastructure
- ✅ Type-safe configuration system (TOML-based)
- ✅ Structured JSON logging with `structlog`
- ✅ Zero string literals (trace codes for all events)
- ✅ Comprehensive error handling
- ✅ Batch processing for efficiency
- ✅ Complete test suite with pytest

---

## 📁 Project Structure

```
ragtrial/
├── README.md                       # This file
├── docs/                          # Documentation
│   └── PROVIDERS.md              # Provider switching guide
├── examples/                      # Example scripts
│   ├── demo_vectorstore.py       # Basic vectorstore usage
│   └── demo_provider_switching.py # Provider switching demo
├── config/                        # Configuration system
│   └── __init__.py               # Singleton config loader
├── embeddings/                    # Embeddings abstraction
│   ├── base.py                   # EmbeddingsProtocol interface
│   ├── factory.py                # Provider factory
│   └── implementations/          # Provider implementations
│       ├── google.py
│       ├── openai.py
│       ├── huggingface.py
│       └── anthropic.py
├── vectorstore/                   # Vectorstore abstraction
│   ├── base.py                   # VectorStoreProtocol interface
│   ├── factory.py                # Provider factory
│   └── implementations/          # Provider implementations
│       ├── chroma.py
│       ├── pinecone.py
│       ├── qdrant.py
│       └── weaviate.py
├── logger/                        # Logging system
│   ├── __init__.py
│   └── setup.py                  # Structlog configuration
├── trace/                         # Trace codes (zero string literals)
│   ├── __init__.py
│   └── codes.py                  # All trace codes
├── ingestion/                     # Document ingestion pipeline
│   ├── __init__.py
│   └── ingest.py                 # Entry point script
├── tests/                         # Test suite
│   ├── conftest.py
│   ├── test_config.py
│   └── test_logging.py
└── environment/                   # Configuration files
    └── default.toml              # Base configuration
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repo-url>
cd ragtrial

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export GEMINI_API_KEY="your-google-api-key"
```

**Get your free key:** https://aistudio.google.com/apikey

The default configuration uses:
- **Embeddings:** Google (text-embedding-004)
- **Vectorstore:** ChromaDB (local storage)

### 3. Run Database Setup

```bash
python scripts/setup_database.py
```

This automated script will:
- ✅ Check prerequisites
- ✅ Create storage directories
- ✅ Test embeddings connection
- ✅ Initialize ChromaDB
- ✅ Verify everything works

### 4. Run Examples

```bash
# Basic vectorstore demo
python examples/demo_vectorstore.py

# Provider switching demo
python examples/demo_provider_switching.py
```

**📚 Detailed Setup Guide:** See [docs/QUICKSTART.md](docs/QUICKSTART.md)

---

## 🔄 Switching Providers

### Example: Change from Google to OpenAI

**1. Edit `environment/default.toml`:**
```toml
[embeddings]
provider = "openai"  # Changed from "google"
```

**2. Set API key:**
```bash
export OPENAI_API_KEY="your-openai-key"
```

**3. Run your application - NO CODE CHANGES!**
```bash
python examples/demo_provider_switching.py
```

### Example: Change from ChromaDB to Pinecone

**1. Edit `environment/default.toml`:**
```toml
[vectorstore]
provider = "pinecone"  # Changed from "chroma"
```

**2. Set API key:**
```bash
export PINECONE_API_KEY="your-pinecone-key"
```

**3. Run your application - Same code works!**

---

## 📚 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Step-by-step setup instructions
  - Database initialization
  - Troubleshooting
  - Alternative setups (Docker, local embeddings)
  - Configuration tips

- **[Provider Guide](docs/PROVIDERS.md)** - Complete guide to all supported providers
  - Installation instructions
  - Configuration examples
  - Provider comparison
  - Recommendations by use case

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py
```

---

## 💡 Usage Example

```python
from config import Config
from embeddings import create_embeddings
from vectorstore import create_vectorstore

# Load configuration
app_config = Config()

# Create providers (automatically picks from config)
embeddings = create_embeddings(app_config)
vectorstore = create_vectorstore(app_config, embeddings)

# Initialize
vectorstore.initialize()

# Add documents
vectorstore.add_documents(
    texts=["Document 1", "Document 2"],
    metadatas=[{"source": "a.pdf"}, {"source": "b.pdf"}]
)

# Query
results = vectorstore.query("What is RAG?", n_results=5)
```

**Same code works with ANY provider combination!**

---

## 🛠️ Tech Stack

- **Language:** Python 3.13
- **Configuration:** TOML (type-safe, environment-aware)
- **Logging:** structlog (structured JSON logging)
- **Testing:** pytest
- **AI Framework:** LangChain / LangGraph (coming soon)
- **Vector DB:** ChromaDB / Pinecone / Qdrant / Weaviate
- **Embeddings:** Google / OpenAI / HuggingFace / Anthropic

---

## 🎯 Roadmap

### ✅ Completed
- [x] Configuration system (TOML-based, type-safe)
- [x] Structured logging with trace codes
- [x] Embeddings abstraction (5 providers)
- [x] Vectorstore abstraction (4 providers)
- [x] Test organization with pytest
- [x] Provider switching examples
- [x] Comprehensive documentation

### 🚧 In Progress
- [ ] Document loaders (PDF, TXT, MD, DOCX, etc.)
- [ ] Text splitter implementation
- [ ] Document ingestion pipeline

### 📋 Upcoming
- [ ] Simple RAG chain (LangChain)
- [ ] Agent-based RAG (LangGraph)
- [ ] Query interface
- [ ] Chat UI

---

## 📊 Provider Comparison

### Embeddings

| Provider | Dimension | API Key | Local/Cloud | Cost |
|----------|-----------|---------|-------------|------|
| Google | 768 | Yes | Cloud | Paid |
| OpenAI | 1536/3072 | Yes | Cloud | Paid |
| HuggingFace | 384 | No | **Local** | **Free** |
| Anthropic | 1024 | Yes | Cloud | Paid |

### Vectorstores

| Provider | Type | Setup | Scalability | Cost |
|----------|------|-------|-------------|------|
| ChromaDB | Local | Easy | Single machine | **Free** |
| Pinecone | Managed | Easy | Auto-scaling | Paid |
| Qdrant | Self-hosted/Cloud | Medium | High | Free/Paid |
| Weaviate | Self-hosted/Cloud | Medium | High | Free/Paid |

---

## 🎓 Recommendations

### For Development
- **Embeddings:** HuggingFace (free, runs locally)
- **Vectorstore:** ChromaDB (simple, local)

### For Production (Small Scale)
- **Embeddings:** Google or OpenAI (high quality)
- **Vectorstore:** Qdrant self-hosted (open-source)

### For Production (Large Scale)
- **Embeddings:** OpenAI or Google (reliable)
- **Vectorstore:** Pinecone or Weaviate Cloud (managed)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Follow existing code patterns
2. Add tests for new features
3. Update documentation
4. Use trace codes (no string literals)

---

## 📄 License

[Add your license here]

---

## 🔗 Resources

- **Google AI:** https://ai.google.dev/docs/embeddings_guide
- **OpenAI:** https://platform.openai.com/docs/guides/embeddings
- **HuggingFace:** https://huggingface.co/sentence-transformers
- **ChromaDB:** https://docs.trychroma.com/
- **Pinecone:** https://docs.pinecone.io/
- **Qdrant:** https://qdrant.tech/documentation/
- **Weaviate:** https://weaviate.io/developers/weaviate

---

## 💬 Questions?

See [docs/PROVIDERS.md](docs/PROVIDERS.md) for detailed provider information or run the examples to see the system in action!

**Happy RAG building! 🚀**

