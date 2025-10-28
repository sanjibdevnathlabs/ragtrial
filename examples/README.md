# RAG System Usage Examples

This directory contains various examples and tools for interacting with the RAG system.

## 🎯 Quick Start Guide

### 1. Interactive Terminal Interface (Recommended for Testing)

**Easiest way to test queries:**

```bash
make run-rag-cli
```

Or directly:

```bash
APP_ENV=dev GEMINI_API_KEY=your_key python -m app.cli.main
```

**Features:**
- ✨ Interactive question-answer loop
- 📚 Source documents with each answer
- 💡 Built-in help command
- 🎨 Formatted, readable output
- ⌨️ Type `quit` or `exit` to leave

**Example Session:**
```
🔍 Your Question: What is Apache Kafka?

📝 ANSWER:
Apache Kafka is a streaming platform...

✅ Answer Found: True

📚 SOURCES (5 documents):
  [1] kafka_guide.pdf
  [2] kafka_guide.pdf
  ...
```

---

### 2. REST API (For Applications)

**Start the API server:**

```bash
make run-api
```

**Query via curl:**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Apache Kafka?"}'
```

**Query via Python:**

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What is Apache Kafka?"}
)

result = response.json()
print(result["answer"])
for source in result["sources"]:
    print(f"- {source['filename']}")
```

**Interactive API Docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### 3. Python Demo Script

**Single query demonstration:**

```bash
make run-rag-demo
```

Or:

```bash
python examples/demo_rag_query.py
```

This script demonstrates:
- RAG chain initialization
- Single query execution
- Response parsing
- Source document extraction

---

## 📁 Available Interfaces

### Interactive CLI (`app/cli/`) ⭐
Interactive terminal interface for RAG queries. Best for manual testing and exploration.

**Usage:**
```bash
make run-rag-cli
# or
python -m app.cli.main
```

**Commands:**
- Type any question and press Enter
- `help` - Show help information
- `quit` or `exit` - Exit the CLI

**Architecture:**
- Located in `app/cli/` alongside `app/api/`
- Follows project coding standards (guard clauses, no if/else)
- All constants properly defined
- Modular function design

---

## 📁 Demo Scripts (examples/)

---

### `demo_rag_query.py`
Simple demonstration of a single RAG query with formatted output.

**Usage:**
```bash
python examples/demo_rag_query.py
```

**Customization:**
Edit the script to change the query:
```python
query = "Your custom question here"
```

---

### `demo_vectorstore.py`
Demonstrates vector store operations (add, query, delete).

**Usage:**
```bash
python examples/demo_vectorstore.py
```

---

### `demo_provider_switching.py`
Shows how to switch between different embedding providers (Google, OpenAI, HuggingFace, Anthropic).

**Usage:**
```bash
python examples/demo_provider_switching.py
```

---

### `test_storage_upload.py`
Tests file upload functionality to storage backends.

**Usage:**
```bash
python examples/test_storage_upload.py
```

---

## 🔧 Configuration

All examples use the configuration from `environment/` directory:

```toml
# environment/dev.toml
[rag]
provider = "google"              # LLM provider
retrieval_k = 5                  # Number of documents to retrieve

[rag.google]
api_key = "$GEMINI_API_KEY"     # API key from environment
model = "gemini-2.5-flash"       # Gemini model
temperature = 0.1                # Low temp for factual answers
max_tokens = 1000                # Response length
```

**Override settings:**
- Edit `environment/dev.toml` for development
- Edit `environment/default.toml` for defaults
- Set environment variables: `APP_ENV=dev`, `GEMINI_API_KEY=xxx`

---

## 🎓 Choosing the Right Interface

| Use Case | Recommended Interface | Why? |
|----------|----------------------|------|
| Quick testing | `make run-rag-cli` | Interactive, easy to use |
| Manual exploration | Interactive CLI | Multiple queries, immediate feedback |
| Application integration | REST API | Standard HTTP interface |
| Learning/debugging | `demo_rag_query.py` | See the code, understand flow |
| Production | REST API | Scalable, standard |

---

## 🚀 Common Workflows

### Testing New Documents

1. **Upload documents via API:**
   ```bash
   curl -X POST http://localhost:8000/upload \
     -F "file=@your_document.pdf"
   ```

2. **Test queries in CLI:**
   ```bash
   make run-rag-cli
   ```

3. **Ask questions about the new documents**

---

### Switching LLM Providers

1. **Update configuration:**
   ```toml
   # environment/dev.toml
   [rag]
   provider = "openai"  # Change from "google"
   
   [rag.openai]
   api_key = "$OPENAI_API_KEY"
   model = "gpt-4o-mini"
   ```

2. **Set API key:**
   ```bash
   export OPENAI_API_KEY=your_key
   ```

3. **Restart and test:**
   ```bash
   make run-rag-cli
   ```

---

## 📊 Example Queries

Try these questions with your indexed documents:

**General:**
- "What is this document about?"
- "Summarize the key points"

**Kafka (if kafka_guide.pdf is indexed):**
- "What is Apache Kafka?"
- "How do Kafka producers work?"
- "Explain Kafka consumer groups"

**Technical:**
- "How do I configure X?"
- "What are the steps to do Y?"
- "What is the difference between A and B?"

**API-specific (if API docs are indexed):**
- "How do I authenticate?"
- "What endpoints are available?"
- "Show me an example request"

---

## 🐛 Troubleshooting

### "Config loaded" appears multiple times
- This is normal - config is a singleton but may initialize during imports

### "API key not set"
- Check: `echo $GEMINI_API_KEY`
- Set: `export GEMINI_API_KEY=your_key`

### "No documents found"
- Upload documents first via API
- Check: `curl http://localhost:8000/files`

### "RAG chain initialization failed"
- Verify API key is set
- Check `environment/dev.toml` configuration
- Ensure vector store has indexed documents

---

## 📚 Learn More

- **API Documentation**: http://localhost:8000/docs (when API is running)
- **Main README**: ../README.md
- **Configuration Guide**: ../docs/CONFIGURATION.md (if exists)
- **Provider Guide**: ../docs/PROVIDERS.md

---

**Need help?** Check the logs or run with verbose output:
```bash
APP_ENV=dev python examples/interactive_rag_cli.py
```

