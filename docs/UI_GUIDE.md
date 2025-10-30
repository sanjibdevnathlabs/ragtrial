# 🎨 UI Guide - Streamlit Web Interface

## Overview

This project includes a **unified Streamlit web interface** for interacting with your RAG system, embedded within the FastAPI application for a seamless single-application experience.

**Architecture:**
- **FastAPI** serves as the main server (port 8000)
- **Streamlit UI** runs as an embedded subprocess (internal port 8501)
- **Access via** http://localhost:8000/langchain/chat

---

## 🚀 Quick Start

### Prerequisites

```bash
# Streamlit is already in requirements.txt
# No separate installation needed
```

### Launch the Application

**Unified Application (Recommended):**
```bash
make run
# Starts FastAPI + Streamlit on port 8000
```

**Access the UI:**
```
http://localhost:8000/langchain/chat
```

**Development Modes:**
```bash
# Standalone UI (for UI-only development)
make run-dev-ui
# Opens at http://localhost:8501

# API without UI
make run-dev-api
# API only on port 8000
```

---

## ✨ UI Features

**Complete Feature Set:**
- ✅ **Chat Interface** - Clean Q&A with AI
- ✅ **File Upload** - Drag & drop documents (PDF, TXT, MD, DOCX, CSV, JSON)
- ✅ **Document Management** - View indexed files
- ✅ **Source Citations** - Expandable source documents
- ✅ **Multi-tab Interface** - Chat, Analytics, About
- ✅ **Analytics Dashboard** - Usage statistics and metrics
- ✅ **Chat Export** - Download chat history as Markdown
- ✅ **Configuration Display** - Current LLM/embeddings settings
- ✅ **Session Statistics** - Track questions and sources
- ✅ **Clear Chat** - Reset conversation

**Use Cases:**
- Production deployments
- End-user applications
- Document Q&A
- Team collaboration
- Demo/presentations

**Screenshot Flow:**
```
┌───────────────────────────────────────────────────┐
│  🚀 RAG Document Chat - Advanced                 │
├───────────────────────────────────────────────────┤
│  [ 💬 Chat ] [ 📊 Analytics ] [ ℹ️ About ]       │
│                                                   │
│  Sidebar:                     Main Chat Area:    │
│  ┌──────────────┐            ┌──────────────┐   │
│  │ 📤 Upload    │            │ Messages...  │   │
│  │ 📚 Documents │            │              │   │
│  │ ⚙️ Config    │            │ Sources...   │   │
│  │ 📊 Stats     │            │              │   │
│  │ 🛠️ Actions   │            │ Chat Input   │   │
│  └──────────────┘            └──────────────┘   │
└───────────────────────────────────────────────────┘
```

---

## 📚 Feature Details

### 1. File Upload (Advanced Only)

**Upload Documents:**
1. Click sidebar "Upload Documents" section
2. Click "Browse files" or drag & drop
3. Select file (PDF, TXT, MD, DOCX, CSV, JSON)
4. Click "Upload & Index"
5. Run ingestion to index: `python ingestion/ingest.py`

**Supported Formats:**
- PDF documents
- Text files (.txt)
- Markdown (.md)
- Word documents (.docx)
- CSV files
- JSON files

### 2. Chat Interface

**Ask Questions:**
- Type question in input box at bottom
- Press Enter or click send
- AI generates answer with sources
- Sources are expandable for details

**Source Display:**
- Each answer includes source documents
- Click "View Sources" to expand
- Shows filename and content snippet
- Multiple sources per answer

### 3. Chat History Management

**Features:**
- All messages persist during session
- Scroll through history
- Clear all with one button
- Export as Markdown file

**Export Format:**
```markdown
# RAG Chat History Export

**Exported:** 2025-01-30 10:30:00

## User

What is Apache Kafka?

## Assistant

Apache Kafka is a distributed streaming platform...

**Sources:**
1. kafka_guide.pdf
2. streaming_architecture.pdf
```

### 4. Analytics (Advanced Only)

**Metrics Tracked:**
- Total messages in session
- Questions asked
- Average sources per answer
- Recent questions list

**View Analytics:**
- Click "Analytics" tab
- See real-time statistics
- Track usage patterns

### 5. Configuration Display

**Shows Current Setup:**
- LLM provider and model
- Embeddings provider
- Vector store type
- Database backend

**Example Display:**
```yaml
LLM: google
Model: gemini-2.5-flash
Embeddings: google
Vector Store: chroma
```

---

## ⚙️ Configuration

### Enable/Disable UI

Edit `environment/default.toml`:

```toml
[ui]
enabled = true                    # Set to false to disable UI embedding
host = "localhost"                # Streamlit host
port = 8501                       # Streamlit internal port
headless = true                   # Run without browser popup
enable_cors = false               # CORS settings
enable_xsrf_protection = false    # XSRF settings
startup_timeout = 10              # Startup wait time (seconds)
shutdown_timeout = 5              # Graceful shutdown time (seconds)
```

### UI Port Configuration

The UI configuration is managed automatically:
- **External Access:** Port 8000 via `/langchain/chat`
- **Internal Streamlit:** Port 8501 (not exposed)
- **No Port Conflicts:** Streamlit runs as subprocess

### Development vs Production

**Development:**
```bash
make run-dev-ui    # Standalone UI on 8501
make run-dev-api   # API only, no UI
```

**Production:**
```bash
make run           # Unified app on 8000
# or
docker-compose up  # Docker deployment
```

---

## 🎨 Customization

### Change Theme

**Light/Dark Mode:**
```bash
# Streamlit auto-detects system theme
# Or click ⚙️ menu → Settings → Theme
```

### Custom Configuration

Edit `~/.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#31333F"
font = "sans serif"

[server]
port = 8501
headless = true
```

### Modify UI

**Edit UI File:**
- Main UI: `app/ui/main.py`

**Add Custom Features:**
```python
# Add to sidebar
with st.sidebar:
    st.subheader("My Custom Section")
    custom_option = st.selectbox("Choose:", ["A", "B", "C"])
```

**Use Constants:**
```python
import constants

# All UI strings are constants (zero string literals)
st.title(constants.UI_PAGE_TITLE)
st.button(constants.UI_BUTTON_CLEAR_CHAT)
```

---

## 🔧 Troubleshooting

### UI Won't Start

**Error: "streamlit: command not found"**
```bash
pip install streamlit
# or
pip install -r requirements.txt
```

**Error: "Port 8501 already in use"**
```bash
# Kill existing process
lsof -ti:8501 | xargs kill -9

# Or disable UI in config
# Edit environment/default.toml: enabled = false
```

**UI Shows "Not Available" Message:**
- Check `enabled = true` in `environment/default.toml`
- Verify Streamlit is installed
- Check logs for startup errors: `make run` shows Streamlit logs

### Services Not Initialized

**Error: "RAG chain initialization failed"**
- Check API keys are set (GEMINI_API_KEY, etc.)
- Verify configuration in `environment/default.toml`
- Check database is running
- Run migrations: `make migrate-up`

### File Upload Issues

**Files Not Appearing:**
1. Ensure `source_docs/` directory exists
2. Check file permissions
3. Verify file format is supported
4. Run ingestion after upload: `python ingestion/ingest.py`

### Empty Responses

**No Documents Found:**
1. Upload documents via UI or place in `source_docs/`
2. Run ingestion: `python ingestion/ingest.py`
3. Check vectorstore has data
4. Verify embeddings are working

---

## 📊 Performance Tips

### For Better Response Time

1. **Use Cached Services:**
   - Services cached with `@st.cache_resource`
   - No re-initialization on rerun
   - Singleton pattern ensures efficiency

2. **Optimize Document Loading:**
   - Index documents before starting UI
   - Use smaller chunks for faster retrieval
   - Limit retrieval to top-k results

3. **Reduce Re-renders:**
   - Use `st.session_state` for persistence
   - Avoid expensive operations in main loop
   - Cache data transformations

### For Better UX

1. **Add Loading Indicators:**
   ```python
   with st.spinner("Processing..."):
       result = expensive_operation()
   ```

2. **Show Progress:**
   ```python
   progress = st.progress(0)
   for i in range(100):
       progress.progress(i + 1)
   ```

3. **Display Errors Gracefully:**
   ```python
   try:
       result = risky_operation()
   except Exception as e:
       st.error(f"Operation failed: {str(e)}")
   ```

---

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. **Push to GitHub**
2. **Go to:** https://streamlit.io/cloud
3. **Click:** "New app"
4. **Select:** Your repository
5. **Set:** Main file (`app/ui/main.py` or `app/ui/advanced.py`)
6. **Configure:** Environment variables (API keys)
7. **Deploy!**

### Deploy with Docker

```dockerfile
# In your Dockerfile
EXPOSE 8501

# Streamlit command
CMD ["streamlit", "run", "app/ui/advanced.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Environment Variables

**Required:**
```bash
export GEMINI_API_KEY="your-api-key"
# Or set in Streamlit secrets: .streamlit/secrets.toml
```

**Optional:**
```bash
export APP_ENV="production"
export DATABASE_URL="postgresql://..."
```

---

## 🎯 Next Steps

### Enhance Basic UI
- Add streaming responses
- Add conversation memory
- Add multi-turn dialogue

### Enhance Advanced UI
- Batch document upload
- Document deletion from UI
- Advanced search filters
- User authentication
- Chat room/workspace concept

### Create Custom UI
- Use React/Vue + FastAPI backend
- Build mobile app
- Create Slack/Discord bot
- Integrate with existing tools

---

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit Components](https://streamlit.io/components)
- [FastAPI Integration](https://docs.streamlit.io/knowledge-base/tutorials/databases)

---

## 💡 Pro Tips

1. **Use Session State Wisely:**
   ```python
   if "counter" not in st.session_state:
       st.session_state.counter = 0
   ```

2. **Cache Expensive Operations:**
   ```python
   @st.cache_data
   def expensive_computation(param):
       return result
   ```

3. **Handle Errors Gracefully:**
   ```python
   try:
       result = risky_operation()
   except Exception as e:
       st.error(f"Error: {str(e)}")
       result = default_value
   ```

4. **Provide User Feedback:**
   ```python
   st.success("✅ Operation completed!")
   st.warning("⚠️ Please note...")
   st.error("❌ Operation failed")
   st.info("ℹ️ Did you know...")
   ```

---

**Happy UI Building! 🎨**

