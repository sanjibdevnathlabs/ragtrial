# Scripts Directory

This directory contains utility scripts for database setup, management, and testing.

## Available Scripts

### 1. `setup_database.py`
**Purpose:** Automated setup and validation of local vector databases.

**What it does:**
- Checks prerequisites (Python version, config files)
- Creates necessary storage directories
- Tests embeddings provider connection
- Initializes and validates vector database
- Provides next steps guidance

**Usage:**
```bash
python scripts/setup_database.py
```

**When to use:**
- First-time setup of the project
- Setting up a new development environment
- Validating database configuration

---

### 2. `populate_sample_data.py`
**Purpose:** Populate all configured vector databases with sample data.

**What it does:**
- Adds 8 predefined sample documents to ChromaDB, Qdrant, Weaviate, and Pinecone
- Each document includes text, metadata (source, type, category), and unique ID
- Validates that documents were successfully added
- Tests basic query functionality

**Sample documents include:**
- RAG (Retrieval-Augmented Generation) overview
- Deep Learning explanation
- Neural Networks basics
- Transformer Architecture
- Attention Mechanism
- Fine-Tuning guide
- Prompt Engineering tips
- Vector Embeddings explanation

**Usage:**
```bash
# Use with APP_ENV for environment-specific config
APP_ENV=dev ./venv/bin/python3 scripts/populate_sample_data.py
```

**When to use:**
- After initial database setup
- Testing queries with real data
- Demonstrating the system to others
- Development and testing

---

### 3. `cleanup_all_databases.py`
**Purpose:** Remove all data from all configured vector databases.

**What it does:**
- Connects to ChromaDB, Qdrant, Weaviate, and Pinecone
- Deletes all documents/vectors from each database
- Handles provider-specific cleanup logic:
  - **ChromaDB:** Direct document deletion
  - **Qdrant:** Collection-level deletion
  - **Weaviate:** Class deletion and recreation
  - **Pinecone:** Namespace-aware deletion (handles default and named namespaces)
- Verifies cleanup was successful
- Reports before/after document counts

**Usage:**
```bash
# Use with APP_ENV for environment-specific config
APP_ENV=dev ./venv/bin/python3 scripts/cleanup_all_databases.py
```

**When to use:**
- Before re-populating with fresh data
- Clearing test data
- Resetting databases to clean state
- Development and testing

**Note:** This is a destructive operation - all data will be permanently deleted!

---

## Environment Configuration

All scripts respect the `APP_ENV` environment variable:
- `APP_ENV=dev` - Uses `environment/dev.toml` (overrides default.toml)
- `APP_ENV=prod` - Uses `environment/prod.toml` (overrides default.toml)
- No `APP_ENV` - Uses `environment/default.toml` only

## Prerequisites

1. **Virtual Environment:** Activate the venv before running scripts
   ```bash
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate   # Windows
   ```

2. **Environment Variables:** Set required API keys
   ```bash
   export GEMINI_API_KEY="your-key"
   export PINECONE_API_KEY="your-key"
   export QDRANT_API_KEY="your-key"
   export WEAVIATE_API_KEY="your-key"
   ```

3. **Local Databases:** For Qdrant and Weaviate, ensure Docker containers are running
   ```bash
   docker-compose up -d
   ```

## Running Tests

For comprehensive testing, use pytest instead of individual scripts:
```bash
# Run all tests
APP_ENV=dev ./venv/bin/python -m pytest tests/ -v

# Run specific test file
APP_ENV=dev ./venv/bin/python -m pytest tests/test_config_advanced.py -v
```

## Common Workflows

### Initial Setup
```bash
# 1. Setup database
python scripts/setup_database.py

# 2. Populate with sample data
APP_ENV=dev ./venv/bin/python3 scripts/populate_sample_data.py

# 3. Run tests to verify
APP_ENV=dev ./venv/bin/python -m pytest tests/ -v
```

### Development Cycle
```bash
# Clean databases
APP_ENV=dev ./venv/bin/python3 scripts/cleanup_all_databases.py

# Make changes to code...

# Populate with fresh data
APP_ENV=dev ./venv/bin/python3 scripts/populate_sample_data.py

# Run tests
APP_ENV=dev ./venv/bin/python -m pytest tests/ -v
```

### Database Reset
```bash
# Remove all data
APP_ENV=dev ./venv/bin/python3 scripts/cleanup_all_databases.py

# Re-populate
APP_ENV=dev ./venv/bin/python3 scripts/populate_sample_data.py
```

---

## Notes

- All scripts use structured logging (see `logger/` package)
- Scripts follow the same configuration system as the main application
- Log output includes trace codes for debugging
- Scripts are safe to run multiple times (idempotent where possible)

