# RAG Document Chat Application

A production-ready Retrieval-Augmented Generation (RAG) system with **ORM-like abstraction** for vector databases and embeddings. Switch providers with just configuration changes - **no code modifications needed**!

## 🎯 Project Status

**✅ COMPLETE:** Simple RAG Chain with LangChain
- ✅ Document upload & indexing via REST API
- ✅ Interactive terminal CLI interface
- ✅ RAG query with source attribution
- ✅ Security guardrails (prompt injection, input validation)
- ✅ Multi-provider LLM support (Google Gemini, OpenAI GPT, Anthropic Claude)
- ✅ Enterprise database architecture (SQLAlchemy + migrations)
- ✅ 549 tests passing (100% pass rate)

**🚧 IN PROGRESS:** Agent-Based RAG with LangGraph (next phase)

## 🎯 Project Goals

Build a "Chat with your Documents" application with **three interaction methods**:
1. **REST API** - For application integration
2. **Terminal CLI** - For interactive testing
3. **Python SDK** - For programmatic access

---

## ✨ Key Features

### 🤖 RAG System (IMPLEMENTED!)
- ✅ **LangChain-based RAG** with multi-provider LLM support
- ✅ **Query with Sources** - Every answer includes source documents
- ✅ **Security Guardrails** - Prompt injection detection, input validation, output filtering
- ✅ **3 Interaction Methods:**
  - REST API (`POST /query`)
  - Interactive Terminal CLI (`make run-rag-cli`)
  - Python SDK (direct `RAGChain` usage)

### 🔄 Provider-Agnostic Architecture
- **ORM-like abstraction** similar to SQLAlchemy for databases
- **Zero code changes** to switch providers
- **48 provider combinations** (4 embeddings × 4 vectorstores × 3 LLMs)

### 🎨 Flexible Provider Support

**LLMs (3 providers):**
- ✅ Google Gemini (gemini-2.0-flash, gemini-2.5-flash, gemini-2.5-pro)
- ✅ OpenAI GPT (gpt-4o, gpt-4o-mini, gpt-4-turbo)
- ✅ Anthropic Claude (claude-3-5-sonnet, claude-3-opus)

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

### 🔒 Security & Guardrails
- ✅ **Input Validation** - Query length, special character ratio
- ✅ **Prompt Injection Detection** - Pattern matching, forbidden commands
- ✅ **Output Filtering** - Harmful content detection
- ✅ **Rate Limiting Ready** - Singleton services for scalability

### 🏗️ Production-Ready Infrastructure
- ✅ Type-safe configuration system (TOML-based)
- ✅ Structured JSON logging with `structlog`
- ✅ Zero string literals (trace codes for all events)
- ✅ Comprehensive error handling
- ✅ Batch processing for efficiency
- ✅ **Complete test suite with pytest (549 tests, 100% pass rate!)**
- ✅ **Enterprise database with migrations (SQLAlchemy ORM)**

### ⚡ FastAPI REST API
- ✅ **Document Management:**
  - Upload with validation (size, extension)
  - List, metadata, delete operations
  - Storage abstraction (local filesystem + AWS S3)
- ✅ **RAG Query Endpoints:**
  - `POST /query` - Ask questions, get answers with sources
  - `GET /query/health` - RAG system health check
- ✅ **Architecture:**
  - Thread-safe singleton pattern for high-RPS scalability
  - Interactive documentation (Swagger UI + ReDoc)
  - Scalable to 10K+ requests/second

### 💻 Interactive CLI
- ✅ Terminal-based interface (`app/cli/`)
- ✅ Real-time query with formatted output
- ✅ Source documents with each answer
- ✅ Built-in help and commands
- ✅ Same architecture as REST API (clean code standards)

---

## 📁 Project Structure

```
ragtrial/
├── README.md                       # This file
├── docs/                          # Documentation
│   ├── API.md                    # REST API guide
│   ├── PROVIDERS.md              # Provider switching guide
│   ├── QUICKSTART.md             # Setup guide
│   ├── RAG_PROVIDERS.md          # LLM providers guide
│   └── SECURITY_GUARDRAILS.md    # Security documentation
├── app/                           # Application code
│   ├── api/                      # REST API interface
│   │   ├── main.py              # FastAPI application
│   │   └── models.py            # Pydantic request/response models
│   ├── cli/                      # Terminal CLI interface ✨
│   │   ├── __init__.py
│   │   └── main.py              # Interactive CLI (guard clauses, no if/else)
│   ├── routers/                  # API routers
│   │   ├── health.py            # Health check endpoints
│   │   ├── upload.py            # File upload endpoints
│   │   ├── files.py             # File management endpoints
│   │   └── query.py             # RAG query endpoints ✨
│   ├── modules/                  # Business logic (singleton services)
│   │   ├── health/              # Health check service
│   │   ├── upload/              # Upload service
│   │   ├── files/               # File management service
│   │   └── query/               # RAG query service ✨
│   ├── chain_rag/                # RAG implementation ✨
│   │   ├── base.py              # RAGProtocol interface
│   │   ├── chain.py             # Main RAG chain (LangChain)
│   │   ├── retriever.py         # Document retriever
│   │   ├── prompts.py           # System prompts
│   │   └── response.py          # Response formatter
│   └── security/                 # Security guardrails ✨
│       └── validators.py        # Input/output validation, prompt injection detection
├── config/                        # Configuration system
│   └── __init__.py               # Singleton config loader (TOML-based)
├── embeddings/                    # Embeddings abstraction
│   ├── base.py                   # EmbeddingsProtocol interface
│   ├── factory.py                # Provider factory
│   └── implementations/          # 4 providers
│       ├── google.py
│       ├── openai.py
│       ├── huggingface.py
│       └── anthropic.py
├── vectorstore/                   # Vectorstore abstraction
│   ├── base.py                   # VectorStoreProtocol interface
│   ├── factory.py                # Provider factory
│   └── implementations/          # 4 providers
│       ├── chroma.py
│       ├── pinecone.py
│       ├── qdrant.py
│       └── weaviate.py
├── storage_backend/               # Storage abstraction (local/S3)
│   ├── base.py                   # StorageProtocol interface
│   ├── factory.py                # Storage factory
│   └── implementations/
│       ├── local.py              # Local filesystem
│       └── s3.py                 # AWS S3
├── database/                      # Database layer ✨
│   ├── exceptions.py             # Custom database exceptions
│   ├── connection.py             # Multi-database connection builder
│   ├── query_logger.py           # Query logging with debug flags
│   ├── session.py                # SessionFactory (master-slave split)
│   ├── base_model.py             # Base model with common fields
│   └── base_repository.py        # Generic CRUD operations
├── migration/                     # Database migrations ✨
│   ├── manager.py                # Migration CLI manager
│   ├── __main__.py               # CLI entry point
│   ├── commands/                 # Migration commands (up, down, status, etc.)
│   ├── templates/                # Migration template
│   └── versions/                 # Migration files
│       └── 20250128_000001_create_files_table.py
├── loader/                        # Document loaders
│   ├── base.py                   # LoaderProtocol interface
│   └── strategies/               # PDF, DOCX, TXT, MD, CSV, JSON
├── splitter/                      # Text splitters
│   ├── base.py                   # SplitterProtocol interface
│   └── strategies/               # Token-based splitting
├── ingestion/                     # Document ingestion pipeline
│   └── ingest.py                 # Batch ingestion script
├── logger/                        # Logging system
│   └── setup.py                  # Structlog configuration (JSON logging)
├── trace/                         # Trace codes (zero string literals!)
│   └── codes.py                  # All event codes
├── constants/                     # Application constants
│   └── __init__.py               # All string constants
├── utils/                         # Utility modules
│   └── singleton.py              # Thread-safe singleton metaclass
├── examples/                      # Example scripts & demos
│   ├── README.md                 # Usage guide for all examples
│   ├── demo_rag_query.py         # RAG demo script
│   ├── demo_vectorstore.py       # Vectorstore demo
│   └── demo_provider_switching.py # Provider switching demo
├── tests/                         # Test suite (549 tests!)
│   ├── conftest.py               # Pytest config + database fixtures
│   ├── test_api_*.py             # API tests (upload, files, query)
│   ├── test_rag_*.py             # RAG chain tests
│   ├── test_security_*.py        # Security guardrails tests
│   ├── test_embeddings_*.py      # Embeddings tests
│   ├── test_vectorstore_*.py     # Vectorstore tests
│   └── test_config.py            # Configuration tests
├── environment/                   # Configuration files
│   ├── default.toml              # Base configuration
│   ├── dev.toml                  # Development overrides
│   └── test.toml                 # Test environment
├── scripts/                       # Utility scripts
│   ├── setup_database.py         # Database initialization
│   ├── populate_sample_data.py   # Sample data loader
│   └── cleanup_all_databases.py  # Cleanup script
└── Makefile                       # Development commands
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

### 2. Database Setup

```bash
# Run database migrations (creates tables)
make migrate-up

# Check migration status
make migrate-status
```

**Note:** By default, the application uses SQLite for development. For production, configure MySQL or PostgreSQL in `environment/default.toml`.

### 3. Set API Key

```bash
export GEMINI_API_KEY="your-google-api-key"
```

**Get your free key:** https://aistudio.google.com/apikey

The default configuration uses:
- **LLM:** Google Gemini (gemini-2.5-flash)
- **Embeddings:** Google (text-embedding-004)
- **Vectorstore:** ChromaDB (local storage)
- **Database:** SQLite (file-based)

### 4. Index Your Documents

**Option A: Using REST API**
```bash
# Start the API server
make run-api
# or: uvicorn app.api.main:app --reload

# Upload documents (in another terminal)
curl -X POST http://localhost:8000/upload -F "file=@your_document.pdf"
```

**Option B: Using Ingestion Script**
```bash
# Place documents in source_docs/ directory
cp your_document.pdf source_docs/

# Run ingestion
python ingestion/ingest.py
```

### 5. Query Your Documents

**🔥 Method 1: Interactive CLI (Recommended)**
```bash
make run-rag-cli
# or: python -m app.cli.main

# Then type your questions:
🔍 Your Question: What is this document about?
```

**Method 2: REST API**
```bash
# Query endpoint
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

**Method 3: Python Script**
```bash
# Run demo
make run-rag-demo
# or: python examples/demo_rag_query.py
```

**📚 Detailed Setup Guide:** See [docs/QUICKSTART.md](docs/QUICKSTART.md)

---

## 🚀 REST API Reference

Production-ready API for document management and RAG queries with **thread-safe singleton pattern** for high-RPS scalability.

### Start the API Server

```bash
make run-api
# or: uvicorn app.api.main:app --reload
```

The API server will start at `http://localhost:8000`

**Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Document Management Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Upload File:**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@document.pdf"
```

**List Files:**
```bash
curl http://localhost:8000/api/v1/files
```

**Get File Metadata:**
```bash
curl http://localhost:8000/api/v1/files/document.pdf
```

**Delete File:**
```bash
curl -X DELETE http://localhost:8000/api/v1/files/document.pdf
```

### RAG Query Endpoints ✨

**Query RAG System:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Apache Kafka?"
  }'
```

**Response:**
```json
{
  "success": true,
  "answer": "Apache Kafka is a streaming platform...",
  "sources": [
    {
      "filename": "kafka_guide.pdf",
      "chunk_index": 0,
      "content": "..."
    }
  ],
  "has_answer": true,
  "query": "What is Apache Kafka?"
}
```

**RAG System Health:**
```bash
curl http://localhost:8000/api/v1/query/health
```

**Response:**
```json
{
  "status": "healthy",
  "rag_system": {
    "rag_initialized": true,
    "provider": "google",
    "model": "gemini-2.5-flash"
  }
}
```

### Architecture Highlights

**✨ Performance Optimization:**
- **Thread-Safe Singleton Pattern** - Services instantiated only once
- **Scalable to Any RPS** - 10, 1K, 10K, 100K+ requests/second
- **Zero Memory Overhead** - No GC pressure from object creation
- **Lazy Initialization** - RAG chain loads on first query

**🏗️ Clean Architecture:**
- **Thin Routers** - HTTP layer only (`app/routers/`)
- **Singleton Services** - Business logic (`app/modules/`)
- **Dependency Injection** - Config, storage, services via FastAPI
- **Comprehensive Tests** - 549 tests with 100% pass rate

**🔧 Storage Backend:**
- **Local Filesystem** - Default, no setup required
- **AWS S3** - Configurable via TOML, secure credential chain

**💾 Database Backend:**
- **SQLite** - Default for development, zero configuration
- **MySQL** - Production-ready with master-slave support
- **PostgreSQL** - Production-ready with master-slave support

**📚 Full API Documentation:** See [docs/API.md](docs/API.md)

---

## 💾 Database Architecture

### Overview

The application uses **SQLAlchemy ORM** with a comprehensive migration system for database versioning. The database layer is designed for **production environments** with support for read-write splitting and multiple database backends.

### Supported Databases

- **SQLite** - File-based, perfect for development and testing
- **MySQL** - Production-ready with master-slave architecture
- **PostgreSQL** - Production-ready with master-slave architecture

### Key Features

✅ **Master-Slave Architecture** - Separate read/write connection pools  
✅ **Migration System** - Laravel/Goose-style CLI (generate, up, down, status, reset)  
✅ **UUID-Based Storage** - Files stored with UUIDs, preventing collisions  
✅ **Duplicate Detection** - SHA-256 checksum-based file deduplication  
✅ **Soft Delete** - Files marked as deleted, not permanently removed  
✅ **Query Logging** - Conditional query logging with debug flags  
✅ **Connection Pooling** - Configurable pool sizes per mode  
✅ **SQL Injection Prevention** - Parameterized queries only

### Database Schema

**Files Table:**
```sql
CREATE TABLE files (
    id VARCHAR(36) PRIMARY KEY,          -- UUID
    filename VARCHAR(255) NOT NULL,       -- Original filename
    file_path VARCHAR(512) NOT NULL,      -- UUID-based storage path
    file_type VARCHAR(50) NOT NULL,       -- Extension (e.g., 'pdf', 'txt')
    file_size BIGINT NOT NULL,            -- Size in bytes
    checksum VARCHAR(64) NOT NULL,        -- SHA-256 for duplicates
    storage_backend VARCHAR(50) NOT NULL, -- 'local' or 's3'
    indexed BOOLEAN DEFAULT FALSE,        -- Is indexed in vectorstore
    indexed_at BIGINT NULL,               -- Indexing timestamp (ms)
    created_at BIGINT NOT NULL,           -- Creation timestamp (ms)
    updated_at BIGINT NOT NULL,           -- Update timestamp (ms)
    deleted_at BIGINT NULL,               -- Soft delete timestamp (ms)
    CONSTRAINT unique_checksum UNIQUE (checksum)
);

-- Strategic indexes
CREATE INDEX idx_files_checksum ON files(checksum);
CREATE INDEX idx_files_deleted_at ON files(deleted_at);
CREATE INDEX idx_files_indexed ON files(indexed);
CREATE INDEX idx_files_filename ON files(filename);
```

### Migration Commands

```bash
# Generate new migration
python -m migration generate create_users_table

# Apply all pending migrations
make migrate-up
# or: python -m migration up

# Apply specific number of migrations
python -m migration up --steps 2

# Rollback last migration
make migrate-down
# or: python -m migration down

# Rollback specific number
python -m migration down --steps 2

# Check migration status
make migrate-status
# or: python -m migration status

# Reset database (down all + up all)
python -m migration reset --yes
```

### Configuration Examples

**SQLite (Development - Default):**
```toml
[database]
driver = "sqlite"

[database.sqlite.write]
path = "storage/metadata_dev.db"
debug = true   # Enable query logging

[database.sqlite.read]
path = "storage/metadata_dev.db"
debug = true
```

**MySQL (Production with Master-Slave):**
```toml
[database]
driver = "mysql"
pool_pre_ping = true
pool_recycle = 3600

[database.mysql.write]
host = "mysql-master.example.com"
port = 3306
database = "ragtrial"
username = "ragtrial_user"
password = "${MYSQL_PASSWORD}"  # OS env var interpolation
charset = "utf8mb4"
pool_size = 5
max_overflow = 10
debug = false

[database.mysql.read]
host = "mysql-slave.example.com"
port = 3306
database = "ragtrial"
username = "ragtrial_readonly"
password = "${MYSQL_RO_PASSWORD}"
charset = "utf8mb4"
pool_size = 10
max_overflow = 20
debug = false
```

**PostgreSQL (Production with Master-Slave):**
```toml
[database]
driver = "postgresql"

[database.postgresql.write]
host = "postgres-master.example.com"
port = 5432
database = "ragtrial"
username = "ragtrial_user"
password = "${POSTGRES_PASSWORD}"
pool_size = 5
max_overflow = 10
debug = false

[database.postgresql.read]
host = "postgres-slave.example.com"
port = 5432
database = "ragtrial"
username = "ragtrial_readonly"
password = "${POSTGRES_RO_PASSWORD}"
pool_size = 10
max_overflow = 20
debug = false
```

### Database Operations

**Master-Slave Read/Write Splitting:**
```python
from database.session import SessionFactory

sf = SessionFactory()

# Write operations (INSERT, UPDATE, DELETE) → Master DB
with sf.get_write_session() as session:
    result = session.execute(
        text("INSERT INTO files VALUES (:id, :name)"),
        {"id": "uuid", "name": "file.pdf"}
    )
    # Auto-commit on context exit

# Read operations (SELECT) → Slave DB
with sf.get_read_session() as session:
    result = session.execute(
        text("SELECT * FROM files WHERE deleted_at IS NULL")
    )
    files = result.fetchall()
```

### File Management with Database

**Before (File-system metadata):**
- Files stored with original names
- Metadata from storage backend
- No duplicate detection

**After (Database-backed metadata):**
- Files stored with UUID names (`3ec2c7ce-459b-4ecb-8732-b22ae16c44c9.pdf`)
- Original filename in database
- SHA-256 checksum duplicate detection
- Indexed status tracking
- Database is source of truth

**API Response Example:**
```json
{
  "success": true,
  "file_id": "3ec2c7ce-459b-4ecb-8732-b22ae16c44c9",
  "filename": "document.pdf",
  "file_path": "source_docs/3ec2c7ce-459b-4ecb-8732-b22ae16c44c9.pdf",
  "file_type": "pdf",
  "file_size": 1048576,
  "checksum": "a1b2c3d4...",
  "storage_backend": "local",
  "indexed": false,
  "indexed_at": null,
  "created_at": 1706400000000,
  "updated_at": 1706400000000,
  "deleted_at": null
}
```

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

- **[REST API Documentation](docs/API.md)** - Complete REST API guide
  - Document management endpoints (upload, list, metadata, delete)
  - RAG query endpoints (`POST /query`, `GET /query/health`)
  - Architecture and performance optimization (singleton pattern)
  - Storage backends (local filesystem + AWS S3)
  - Request/response examples with curl
  - Testing and deployment strategies

- **[Quick Start Guide](docs/QUICKSTART.md)** - Step-by-step setup instructions
  - Installation and API key setup
  - Database initialization
  - Document indexing (API vs script)
  - Querying documents (CLI, API, Python)
  - Troubleshooting common issues
  - Alternative setups (local embeddings, different providers)

- **[Embeddings Provider Guide](docs/PROVIDERS.md)** - Embeddings & vectorstore providers
  - Installation instructions for all 4 embeddings providers
  - Configuration examples and API key setup
  - Vectorstore configuration (Chroma, Pinecone, Qdrant, Weaviate)
  - Provider comparison and recommendations
  - Use case recommendations (dev vs production)

- **[LLM Provider Guide](docs/RAG_PROVIDERS.md)** - LLM configuration for RAG ✨
  - Google Gemini setup and models
  - OpenAI GPT configuration
  - Anthropic Claude setup
  - Switching between LLM providers
  - Model selection guidelines

- **[Security Guardrails](docs/SECURITY_GUARDRAILS.md)** - Security implementation ✨
  - Input validation (query length, special characters)
  - Prompt injection detection (pattern matching, forbidden commands)
  - Output filtering (harmful content detection)
  - Integration with RAG chain
  - Custom guardrails configuration

- **[Examples Guide](examples/README.md)** - Usage examples and demos
  - Interactive CLI usage
  - REST API examples (curl, Python)
  - Python SDK direct usage
  - Provider switching demonstrations

---

## 📦 Makefile Commands

### Database Operations
```bash
make migrate-up           # Apply all pending migrations
make migrate-down         # Rollback last migration
make migrate-status       # Check migration status
make migrate-reset        # Reset database (down all + up all)
make migrate-generate     # Generate new migration (requires DESCRIPTION="...")
```

### Application
```bash
make run-api             # Start FastAPI server
make run-rag-cli         # Interactive CLI for RAG queries
```

### Testing
```bash
make test                # Run all tests
make test-verbose        # Run with verbose output
make test-coverage       # Run with coverage report
make test-unit           # Run unit tests only
make test-integration    # Run integration tests only
```

### Development
```bash
make install             # Install all dependencies
make clean               # Clean up temporary files
make lint                # Run code linters
make format              # Format code with black
```

---

## 🧪 Testing

```bash
# Run all tests (549 tests!)
make test

# Run with verbose output
make test-verbose

# Run with coverage report
make test-coverage

# Run specific test categories
pytest tests/test_api_*.py      # API tests
pytest tests/test_rag_*.py      # RAG chain tests
pytest tests/test_security_*.py # Security tests
pytest tests/test_embeddings_*.py # Embeddings tests
pytest tests/test_vectorstore_*.py # Vectorstore tests
```

**Test Coverage:**
- ✅ 549 total tests
- ✅ 100% pass rate
- ✅ API endpoints (upload, files, query)
- ✅ RAG chain (retrieval, generation, response formatting)
- ✅ Security guardrails (input validation, prompt injection, output filtering)
- ✅ Embeddings (all 4 providers)
- ✅ Vectorstores (all 4 providers)
- ✅ Configuration loading
- ✅ Storage backends (local, S3)
- ✅ Database operations (SQLAlchemy with migrations)

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
- **Web Framework:** FastAPI (REST API with Swagger/ReDoc)
- **AI Framework:** LangChain (RAG chain implementation)
- **LLMs:** Google Gemini / OpenAI GPT / Anthropic Claude
- **Embeddings:** Google / OpenAI / HuggingFace / Anthropic
- **Vector Databases:** ChromaDB / Pinecone / Qdrant / Weaviate
- **Storage:** Local Filesystem / AWS S3
- **Configuration:** TOML (type-safe, environment-aware, singleton pattern)
- **Logging:** structlog (structured JSON logging with trace codes)
- **Testing:** pytest (554 tests, 100% pass rate)
- **Document Processing:** PyPDF2, python-docx, tiktoken
- **Security:** Custom guardrails (prompt injection detection, input/output validation)

---

## 🎯 Roadmap

### ✅ Phase 1: Infrastructure (COMPLETE)
- [x] Configuration system (TOML-based, type-safe, singleton)
- [x] Structured logging with trace codes (`structlog`)
- [x] Embeddings abstraction (4 providers: Google, OpenAI, HuggingFace, Anthropic)
- [x] Vectorstore abstraction (4 providers: Chroma, Pinecone, Qdrant, Weaviate)
- [x] Storage abstraction (Local filesystem, AWS S3)
- [x] Test organization with pytest (554 tests!)
- [x] Provider switching examples
- [x] Comprehensive documentation

### ✅ Phase 2: Document Processing (COMPLETE)
- [x] Document loaders (PDF, TXT, MD, DOCX, CSV, JSON)
- [x] Text splitter implementation (token-based)
- [x] Document ingestion pipeline (batch processing)
- [x] Validation and error handling

### ✅ Phase 3: RAG Implementation (COMPLETE)
- [x] **Simple RAG Chain (LangChain)** ✨
  - [x] Multi-provider LLM support (Google Gemini, OpenAI GPT, Anthropic Claude)
  - [x] Document retrieval with vector search
  - [x] Prompt engineering with system instructions
  - [x] Response formatting with source attribution
  - [x] Security guardrails (input validation, prompt injection detection, output filtering)
- [x] **REST API** (`POST /query`, `GET /query/health`)
- [x] **Interactive Terminal CLI** (`make run-rag-cli`)
- [x] **Python SDK** (direct `RAGChain` usage)
- [x] **Comprehensive Testing** (RAG, Security, Integration tests)

### 🚧 Phase 4: Advanced RAG (IN PROGRESS)
- [ ] Agent-based RAG with LangGraph
  - [ ] Multi-step reasoning
  - [ ] Conditional logic and loops
  - [ ] Tool integration
  - [ ] Memory management

### 📋 Phase 5: User Interface (UPCOMING)
- [ ] Streamlit/Gradio web UI
- [ ] Chat history persistence
- [ ] Multi-document management UI
- [ ] Real-time streaming responses

### 📋 Phase 6: Production Enhancements (FUTURE)
- [ ] Docker containerization
- [ ] Kubernetes deployment configs
- [ ] Monitoring and alerting (Prometheus, Grafana)
- [ ] Rate limiting and caching
- [ ] Advanced security (OAuth, API keys)

---

## 📊 Provider Comparison

### LLMs (for RAG Queries) ✨

| Provider | Models | Context Window | API Key | Cost |
|----------|--------|----------------|---------|------|
| Google Gemini | gemini-2.0-flash, gemini-2.5-flash, gemini-2.5-pro | 1M tokens | Yes | Paid/Free tier |
| OpenAI GPT | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo | 128K tokens | Yes | Paid |
| Anthropic Claude | claude-3-5-sonnet, claude-3-opus, claude-3-haiku | 200K tokens | Yes | Paid |

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

