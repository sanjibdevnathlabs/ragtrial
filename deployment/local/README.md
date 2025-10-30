# Local Docker Compose Deployment

Complete local development environment using Docker Compose with all services containerized.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   MySQL DB   │  │   ChromaDB   │  │  Migration   │      │
│  │   Port 3306  │  │   Port 8001  │  │  (Run once)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            ↓                                 │
│                  ┌──────────────────┐                        │
│                  │   RAG API + UI   │                        │
│                  │   Port 8000      │                        │
│                  │  (React + FastAPI)│                       │
│                  └──────────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Services

### 1. **app** - Main Application
- **Image**: `ragtrial:dev`
- **Dockerfile**: `docker/Dockerfile` (multi-stage build)
- **Port**: `8000` (FastAPI + React UI)
- **Features**:
  - React frontend (built automatically in Docker stage 1)
  - FastAPI backend (stage 2)
  - Health checks
  - Auto-restart
- **Depends on**: MySQL, ChromaDB, Migration

### 2. **migration** - Database Setup
- **Image**: `ragtrial-migration:dev`
- **Dockerfile**: `docker/Dockerfile.migration`
- **Purpose**: Runs database migrations once and exits
- **Depends on**: MySQL

### 3. **db** - MySQL Database
- **Image**: `mysql:8.0`
- **Port**: `3306`
- **Credentials**:
  - Root password: `root`
  - Database: `ragtrial`
  - User: `ragtrial`
  - Password: `ragtrial`
- **Persistence**: Volume `mysql_data`

### 4. **chromadb** - Vector Database
- **Image**: `chromadb/chroma:latest`
- **Port**: `8001` (mapped from internal 8000)
- **Persistence**: Volume `chroma_data`
- **Features**:
  - Persistent storage
  - Telemetry disabled

## 🚀 Quick Start

### Prerequisites

1. **Docker & Docker Compose** installed
2. **GEMINI_API_KEY** environment variable set

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### Start All Services

```bash
# From project root
cd deployment/local

# Start all services (builds images if needed)
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
```

### Access the Application

- **Landing Page**: http://localhost:8000
- **Chat UI**: http://localhost:8000/langchain/chat
- **API Docs**: http://localhost:8000/docs
- **Dev Docs**: http://localhost:8000/dev-docs
- **API Health**: http://localhost:8000/api/v1/health

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## 🔧 Development Workflow

### Rebuild After Code Changes

```bash
# Rebuild and restart app service
docker-compose up -d --build app

# Rebuild specific service
docker-compose build app
docker-compose up -d app
```

### Frontend Development

The frontend is **built automatically inside Docker** (multi-stage build). If you change frontend code:

```bash
# Rebuild Docker image (includes frontend build)
docker-compose up -d --build app
```

**Note**: The main `Dockerfile` has 2 stages:
1. **Stage 1**: Builds React frontend with Node.js
2. **Stage 2**: Copies built frontend + runs Python backend

This means you don't need to manually run `npm run build` - Docker does it for you!

### Database Operations

```bash
# Access MySQL shell
docker exec -it ragtrial-db mysql -u ragtrial -pragtrial ragtrial

# Run migrations manually
docker-compose run --rm migration

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### View Container Status

```bash
# List all containers
docker-compose ps

# View resource usage
docker stats ragtrial-app ragtrial-db ragtrial-chroma

# Check health status
docker inspect ragtrial-app | grep -A 10 Health
```

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs app

# Check if port is already in use
lsof -i :8000
lsof -i :3306
lsof -i :8001

# Restart specific service
docker-compose restart app
```

### Database Connection Issues

```bash
# Verify MySQL is healthy
docker-compose ps db

# Check MySQL logs
docker-compose logs db

# Wait for health check
docker-compose up -d db
docker-compose logs -f db  # Wait for "ready for connections"
```

### Frontend Not Loading

```bash
# Verify build output exists in container
docker exec ragtrial-app ls -la /app/app/static/dist/

# Rebuild with frontend (no-cache ensures fresh build)
docker-compose build --no-cache app
docker-compose up -d app
```

### ChromaDB Issues

```bash
# Check ChromaDB logs
docker-compose logs chromadb

# Reset ChromaDB data
docker-compose down
docker volume rm local_chroma_data
docker-compose up -d
```

## 🔍 Useful Commands

### Inspect Services

```bash
# Enter app container shell
docker exec -it ragtrial-app /bin/bash

# View environment variables
docker exec ragtrial-app env

# Test API health
curl http://localhost:8000/api/v1/health

# Test database connection
docker exec ragtrial-db mysqladmin ping -h localhost
```

### Clean Up

```bash
# Remove all containers and networks
docker-compose down

# Remove all containers, networks, and volumes
docker-compose down -v

# Remove images as well
docker-compose down -v --rmi all

# Clean up everything (nuclear option)
docker system prune -a --volumes
```

## 📊 Resource Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB

**Recommended**:
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB

## 🔐 Security Notes

1. **Default Credentials**: Change MySQL passwords in production
2. **API Keys**: Never commit `GEMINI_API_KEY` to git
3. **Network**: Services are isolated in `ragtrial-network`
4. **Volumes**: Data persists in Docker volumes

## 📝 Environment Variables

### Using env.example

The `env.example` file is a **template** showing all available environment variables. It's for documentation purposes only - Docker Compose doesn't use it directly.

**To use it**:

```bash
# Option 1: Export to shell (recommended for local dev)
export GEMINI_API_KEY="your-api-key-here"
docker-compose up -d

# Option 2: Create .env file (optional)
cp env.example .env
# Edit .env with your values
docker-compose up -d  # Automatically reads .env

# Option 3: Inline (quick testing)
GEMINI_API_KEY="your-key" docker-compose up -d
```

**Required**:
- `GEMINI_API_KEY` - Your Google Gemini API key

**Optional** (have sensible defaults):
- `APP_ENV` - Environment name (default: `docker`)
- `MYSQL_*` - Database credentials (defaults work for local dev)
- `LOG_LEVEL` - Logging verbosity (default: `INFO`)

**Why env.example exists**:
- 📖 Documents all available variables
- 🔒 Never committed with real secrets
- 📋 Template for new developers
- ✅ Shows expected format

## 🎯 Production Considerations

This setup is for **local development only**. For production:

1. Use secrets management (Docker secrets, Vault, AWS Secrets Manager)
2. Add reverse proxy (Nginx, Traefik) with HTTPS
3. Use managed databases (AWS RDS, Google Cloud SQL)
4. Add monitoring (Prometheus, Grafana)
5. Configure log aggregation (ELK, Loki)
6. Set resource limits (CPU, memory)
7. Use container orchestration (Kubernetes, ECS, Docker Swarm)
8. Implement backup strategies

## 📚 Related Documentation

- [Main README](../../README.md) - Project overview
- [Docker Files](../../docker/) - Dockerfile details
- [Deployment Guide](../README.md) - Other deployment options

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify health: `docker-compose ps`
3. Review this README
4. Check [GitHub Issues](https://github.com/sanjibdevnathlabs/ragtrial/issues)

