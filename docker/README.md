# Docker Development Guide

This guide explains how to use Docker for local development of the RAG application.

## Quick Start (Recommended)

### First Time Setup
```bash
# 1. Setup Docker environment (builds all images)
make docker-setup

# 2. Start all services
make docker-up

# 3. Visit the API docs
open http://localhost:8000/docs
```

### Daily Development
```bash
# Start services (auto-builds if code changed)
make docker-up

# Stop services when done
make docker-down
```

## 🎯 Key Commands

### Essential Commands
| Command | Description | When to Use |
|---------|-------------|-------------|
| `make docker-up` | Start all services | Every time you want to work with Docker |
| `make docker-down` | Stop all services | When you're done for the day |
| `make docker-status` | Check service health | To verify everything is running |
| `make docker-logs` | View API logs | To debug issues |
| `make docker-ingest` | Index uploaded files | After uploading documents via API |

### Working with Services
```bash
# View logs
make docker-logs              # API logs (live follow)
make docker-logs-all          # All services
make docker-logs-migration    # Migration status

# Enter containers
make docker-shell             # API container (Python shell)
make docker-db-shell          # MySQL database

# Run operations
make docker-ingest            # Index uploaded files into ChromaDB
```

### Maintenance Commands
```bash
# Rebuild everything (use when Dockerfile changes)
make docker-rebuild

# Clean up everything
make docker-clean

# Restart services
make docker-restart
```

## 📊 Services Overview

| Service | Port | Purpose | Database/User |
|---------|------|---------|---------------|
| **API** | 8000 | FastAPI application | - |
| **MySQL** | 3306 | Metadata storage | user: `ragtrial`, password: `ragtrial` |
| **ChromaDB** | 8001 | Vector store | - |
| **Migration** | - | Runs once on startup | - |

## 🔄 Complete Workflow Example

```bash
# 1. Start services
make docker-up

# 2. Upload a document
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@your_document.txt"

# 3. Run ingestion to index it
make docker-ingest

# 4. Query your document
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'

# 5. View logs if needed
make docker-logs

# 6. Stop when done
make docker-down
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Docker Stack                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │  Migration   │────▶│     API      │────▶│   ChromaDB   │   │
│  │  (one-shot)  │     │   (FastAPI)  │     │ (vectors)    │   │
│  └──────────────┘     └───────┬──────┘     └──────────────┘   │
│         │                     │                                │
│         └─────────────────────┼────────────────────────────┐   │
│                               │                            │   │
│                               ▼                            │   │
│                        ┌──────────────┐                    │   │
│                        │    MySQL     │                    │   │
│                        │ (metadata)   │◀───────────────────┘   │
│                        └──────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Startup Sequence
1. **MySQL** starts and becomes healthy
2. **ChromaDB** starts in parallel
3. **Migration** runs (creates database tables)
4. **API** starts after migration completes

## 🐛 Troubleshooting

### Services won't start
```bash
# Check status
make docker-status

# View logs
make docker-logs-all

# Force rebuild
make docker-rebuild
```

### Migration fails
```bash
# Check migration logs
make docker-logs-migration

# Common issue: database not ready
# Solution: Wait 10 seconds and run again:
make docker-down
make docker-up
```

### API returns 500 errors
```bash
# View API logs
make docker-logs

# Common issues:
# 1. ChromaDB not ready → wait 5 seconds
# 2. MySQL not ready → check docker-logs-all
# 3. Missing docker.toml → rebuild images
```

### Port already in use
```bash
# Check what's using the port
lsof -i :8000   # API
lsof -i :3306   # MySQL
lsof -i :8001   # ChromaDB

# Stop other services or change ports in docker-compose.yml
```

## 📁 File Structure

```
docker/
├── Dockerfile              # Main application image
├── Dockerfile.base         # Base image (dependencies)
├── Dockerfile.migration    # Migration runner
└── README.md              # This file

deployment/local/
└── docker-compose.yml     # Service orchestration

environment/
└── docker.toml            # Docker-specific config (APP_ENV=docker)
```

## 🔧 Configuration

### Environment Variables
Configured in `environment/docker.toml`:
- **Database**: MySQL (driver: mysql)
- **Vector Store**: ChromaDB (HTTP client)
- **Embeddings**: Google text-embedding-004
- **Storage**: Local filesystem

### Customization
To change configuration:
1. Edit `environment/docker.toml`
2. Rebuild: `make docker-rebuild`

### GEMINI_API_KEY
Set in your shell environment (docker-compose reads it):
```bash
export GEMINI_API_KEY="your-key-here"
make docker-up
```

## 💡 Best Practices

### Development Workflow
1. ✅ Use `make docker-up` for starting
2. ✅ Use `make docker-logs` to monitor
3. ✅ Use `make docker-ingest` after uploads
4. ✅ Use `make docker-down` to stop

### When to Rebuild
Rebuild when you change:
- Dependencies in `requirements.txt`
- Dockerfiles
- Configuration in `docker.toml`

```bash
# Quick rebuild (uses cache)
make docker-up

# Full rebuild (no cache)
make docker-rebuild
```

### Data Persistence
- **MySQL data**: Persisted in Docker volume `local_mysql_data`
- **ChromaDB data**: Persisted in Docker volume `local_chroma_data`
- **Uploaded files**: Persisted in `./storage/source_docs/`

To clean everything:
```bash
make docker-clean  # Removes volumes and all data
```

## 🚀 Performance Tips

1. **CPU-only PyTorch**: Already configured (saves ~1.9GB)
2. **Base image caching**: Builds once, reuses for all services
3. **Parallel testing**: Integration tests run with `pytest-xdist`
4. **Health checks**: Ensures services are ready before starting dependents

## 📚 Additional Resources

- [FastAPI Docs](http://localhost:8000/docs) - Interactive API documentation
- [ChromaDB UI](http://localhost:8001) - Vector store admin
- [Main README](../README.md) - Project overview
- [Makefile](../Makefile) - All available commands

