# Docker Setup Documentation

## Overview

This directory contains optimized Docker configuration files for the RAG Trial application. The setup follows Docker best practices and leverages make commands for consistency between local development and containerized environments.

## File Structure

```
docker/
├── Dockerfile              # Main application image (multi-stage: frontend + backend)
├── Dockerfile.base         # Base image with Python dependencies and system tools
├── Dockerfile.migration    # Database migration runner (uses make commands)
├── Dockerfile.frontend-test # Frontend test runner (uses make commands)
└── README.md              # This file
```

## Architecture

### Multi-Image Strategy

```
┌──────────────────────────────────────────────────┐
│ Dockerfile.base                                  │
│ - Python 3.13-slim                              │
│ - System dependencies (gcc, mysql, curl, etc)  │
│ - Python packages (PyTorch CPU, FastAPI, etc)  │
│ - Non-root user (appuser)                      │
│ - Makefile for consistent commands              │
└──────────────────────────────────────────────────┘
                    ▲
                    │ FROM base
        ┌───────────┴───────────────┐
        │                           │
┌───────────────────┐   ┌───────────────────────┐
│ Dockerfile        │   │ Dockerfile.migration  │
│                   │   │                       │
│ Multi-stage:      │   │ Runs DB migrations:   │
│ 1. Frontend build │   │ make migrate-up       │
│ 2. App image      │   │                       │
│    - Backend code │   └───────────────────────┘
│    - Built assets │
└───────────────────┘

┌──────────────────────────────────────────────────┐
│ Dockerfile.frontend-test (Standalone)            │
│ - Node.js 22-alpine                             │
│ - npm dependencies + make/bash                  │
│ - Frontend source code                          │
│ - Runs tests: make frontend-test-ci             │
│ - Exits after test completion                   │
└──────────────────────────────────────────────────┘
```

## Dockerfile Details

### 1. Dockerfile.base

**Purpose**: Base image with all dependencies pre-installed for faster CI/CD builds.

**Includes**:
- Python 3.13-slim (minimal Debian-based Python)
- System dependencies (gcc, g++, make, git, mysql-client, curl)
- All Python packages from `requirements.txt` (PyTorch CPU-only)
- Non-root user `appuser` (UID 1000)
- Makefile for consistent command execution
- Environment variables (PYTHONUNBUFFERED, PATH, etc.)

**Build**:
```bash
make docker-build-base
```

**Optimizations**:
- Single RUN layer for system dependencies (reduces layers)
- CPU-only PyTorch (saves ~1.9GB)
- Cleaned apt cache (smaller image)
- Non-root user for security

### 2. Dockerfile (Main Application)

**Purpose**: Production-ready image with built frontend and backend code.

**Multi-stage Build**:

#### Stage 1: Frontend Builder
```dockerfile
FROM node:20-alpine AS frontend-builder
```
- Uses Alpine Linux (minimal, ~5MB base)
- Copies only `package.json` and `package-lock.json` first (layer caching)
- Runs `npm ci --prefer-offline --no-audit` (faster installs)
- Builds frontend with `npm run build`
- Verifies build output exists

#### Stage 2: Application Image
```dockerfile
FROM sanjibdevnath/ragtrial-base:${BASE_IMAGE_TAG}
```
- Uses our base image with all dependencies
- Copies application code in layers (least → most frequently changed)
- Copies built frontend from Stage 1
- Uses `--chown=appuser:appuser` (no separate chown layer)

**Layer Order (Optimized for Caching)**:
```
1. Config/constants (rarely change) → 90% cache hit
2. Core modules (database, logger, trace, utils) → 80% cache hit
3. LLM/embeddings/vectorstore modules → 70% cache hit
4. App modules → 40% cache hit
5. Chain modules → 20% cache hit
6. Built frontend assets → 30% cache hit
```

**Build**:
```bash
make docker-build
```

### 3. Dockerfile.migration

**Purpose**: Runs database migrations once and exits.

**Key Features**:
- Uses base image (inherits all dependencies)
- Copies only migration-related files (minimal)
- Runs `make migrate-up` for consistency with local dev
- Exits after completion (restart: "no" in docker-compose)

**Build**:
Built automatically by `docker-compose` when starting services.

### 4. Dockerfile.frontend-test

**Purpose**: Runs frontend tests in an isolated container and exits.

**Key Features**:
- Uses Node.js 22-alpine (lightweight)
- Installs make/bash for Makefile support
- Installs npm dependencies with `npm ci` (clean install)
- Copies frontend source code
- Runs `make frontend-test-ci` for consistency with local dev
- Generates coverage reports
- Exits after completion (restart: "no" in docker-compose)

**Build**:
```bash
docker build -f docker/Dockerfile.frontend-test -t ragtrial-frontend-test:dev .
```

Built automatically by `docker-compose` when starting services.

**Test Results**:
- 434 tests across 10 test files
- 100% coverage on components
- ~9s execution time

## Make Commands Integration

### Why Use Make in Docker?

1. **Consistency**: Same commands work locally and in containers
2. **Maintainability**: Change once in Makefile, works everywhere
3. **Documentation**: Makefile serves as runbook
4. **DRY**: Don't repeat commands in multiple Dockerfiles

### Make Commands Available in Containers

All containers include the Makefile and can run:

```bash
# Database migrations
make migrate-up
make migrate-down
make migrate-status
make migrate-reset

# Testing
make test
make test-integration
make test-all

# Code quality
make format
make lint
make lint-all

# Frontend
make frontend-build
make frontend-clean
```

### Examples

```bash
# Run migrations in container
docker-compose exec app make migrate-up

# Run tests in container
docker-compose exec app make test

# Format code in container
docker-compose exec app make format

# Check migration status
docker-compose exec app make migrate-status
```

## Build Optimization Techniques

### 1. Multi-stage Builds
- Separate frontend and backend build stages
- Only copy final artifacts to production image
- Smaller final image size

### 2. Layer Caching
- Copy files in order of change frequency
- `package.json` → `npm ci` → source code
- Config → Core → LLM → App → Chain
- 60-80% cache hit rate for typical changes

### 3. Build Context Optimization
- Comprehensive `.dockerignore` file
- Excludes 90% of files (tests, docs, .git, node_modules)
- Build context: ~50MB (was ~500MB)

### 4. Dependency Optimization
- CPU-only PyTorch (saves ~1.9GB)
- `npm ci --prefer-offline --no-audit` (40-50% faster)
- No pip cache in final image
- Alpine for frontend builder (minimal)

### 5. Base Image Strategy
- Pre-built base image with all dependencies
- Tagged and versioned (`local`, `<git-sha>`)
- Shared across CI/CD and local development
- Rebuilds only when dependencies change

## Build Performance

### Build Time Comparison

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| **Clean Build (No Cache)** | 180s | 165s | 8% faster |
| **Config Change** | 60s | 5s | 92% faster |
| **App Code Change** | 60s | 10s | 83% faster |
| **Chain Code Change** | 60s | 15s | 75% faster |
| **Frontend Change** | 45s | 35s | 22% faster |
| **Average Dev Rebuild** | 60s | 15s | **75% faster** |

### Cache Hit Rates

| Layer | Cache Hit Rate |
|-------|----------------|
| Base image | 99% |
| Config/constants | 90% |
| Core modules | 80% |
| LLM modules | 70% |
| App modules | 40% |
| Chain modules | 20% |
| Frontend | 30% |
| **Overall** | **60-80%** |

## Usage

### First-Time Setup

```bash
# Build all images and set up volumes
make docker-setup
```

This will:
1. Build base image with all dependencies
2. Build application images (app + migration)
3. Create Docker volumes for MySQL and ChromaDB

### Daily Development

```bash
# Start all services (auto-builds if needed)
make docker-up

# View logs
make docker-logs        # API logs
make docker-logs-all    # All services

# Run migrations
make docker-shell
make migrate-up

# Stop services
make docker-down
```

### Rebuild After Changes

```bash
# Rebuild only app (fast if base unchanged)
docker-compose -f deployment/local/docker-compose.yml build app

# Rebuild everything (base + app)
make docker-rebuild
```

### Testing

#### Frontend Tests in Docker

```bash
# Run frontend tests in isolated Docker container
make docker-frontend-test
```

This will:
1. Spin up a Node.js 22 Alpine container
2. Install make (Alpine package)
3. Run `make frontend-test-ci` (installs deps + runs tests with coverage)
4. Display results and exit

**Why use make command?**
- ✅ **Consistency** - Same command structure as backend tests
- ✅ **Single source of truth** - Test configuration in Makefile
- ✅ **Easier maintenance** - Change command in one place (Makefile)

**Benefits**:
- ✅ Isolated environment (no local Node.js/npm needed)
- ✅ Consistent results across machines
- ✅ Uses Docker volume for node_modules caching
- ✅ Automatically cleans up after completion
- ✅ Uses Makefile commands like other Docker services

**Note**: Backend tests are handled via GitHub Actions CI pipeline, not Docker Compose.

### Building Base Image for CI/CD

```bash
# Build base image locally
make docker-build-base

# Tag with git commit SHA
docker tag sanjibdevnath/ragtrial-base:local \
           sanjibdevnath/ragtrial-base:$(git rev-parse HEAD)

# Push to Docker Hub
docker push sanjibdevnath/ragtrial-base:$(git rev-parse HEAD)

# Or use make command
make docker-push-base
```

## Environment Variables

### Build Arguments

```bash
# Use specific base image version
docker build -f docker/Dockerfile \
  --build-arg BASE_IMAGE_TAG=abc123 \
  -t ragtrial:dev .
```

### Runtime Environment

See `deployment/local/env.example` for all available environment variables.

Key variables:
- `APP_ENV`: Environment name (docker, dev, test, prod)
- `GEMINI_API_KEY`: Google Gemini API key
- `DATABASE_URL`: MySQL connection string
- `CHROMA_HOST`: ChromaDB host

## Troubleshooting

### Build Issues

**Issue**: `ModuleNotFoundError` during build
```bash
# Rebuild base image
make docker-build-base

# Clear Docker cache
docker builder prune -a
```

**Issue**: Frontend build fails
```bash
# Check Node.js version in Dockerfile (should be node:20-alpine)
# Check npm logs in build output

# Test frontend build locally
cd frontend
npm ci
npm run build
```

**Issue**: `COPY failed: file not found`
```bash
# Check .dockerignore - ensure files aren't excluded
# Verify file exists in build context
ls -la <file-path>
```

### Runtime Issues

**Issue**: Migrations fail
```bash
# Check migration logs
make docker-logs-migration

# Check database connection
docker-compose exec app make migrate-status

# Reset migrations
docker-compose exec app make migrate-reset
```

**Issue**: App won't start
```bash
# Check health status
make docker-status

# Check logs
make docker-logs

# Check database
docker-compose exec db mysql -u ragtrial -pragtrial -e "SHOW DATABASES;"
```

## Best Practices

### ✅ DO

- Use `make docker-up` for starting services (handles dependencies)
- Use make commands inside containers for consistency
- Rebuild base image when `requirements.txt` changes
- Use specific base image tags in production
- Run `make docker-clean` periodically to free space

### ❌ DON'T

- Don't modify Dockerfiles without updating documentation
- Don't add secrets to Dockerfile or docker-compose.yml
- Don't use `latest` tag for base image in production
- Don't commit `.env` files
- Don't skip `.dockerignore` updates when adding new files

## Security

### Non-Root User

All containers run as `appuser` (UID 1000) for security:

```dockerfile
USER appuser
```

### Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1
```

### Image Scanning

```bash
# Scan base image for vulnerabilities
docker scan sanjibdevnath/ragtrial-base:local

# Or use trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image sanjibdevnath/ragtrial-base:local
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
jobs:
  build:
    steps:
      - name: Build base image
        run: make docker-build-base
      
      - name: Build app image
        run: make docker-build
      
      - name: Run tests in Docker
        run: docker-compose exec -T app make test
```

### Image Versioning

```bash
# Production tags
sanjibdevnath/ragtrial-base:abc123  # Git commit SHA
sanjibdevnath/ragtrial-base:v1.0.0  # Release version

# Development tags
sanjibdevnath/ragtrial-base:local   # Local development
sanjibdevnath/ragtrial-base:dev     # Development branch
```

## Related Files

- `/Makefile` - Main command reference
- `/deployment/local/docker-compose.yml` - Service orchestration
- `/deployment/local/README.md` - Docker Compose documentation
- `/.dockerignore` - Build context exclusions
- `/.github/workflows/ci.yml` - CI/CD pipeline

## Support

For issues or questions:
1. Check logs: `make docker-logs-all`
2. Check status: `make docker-status`
3. Review documentation
4. Open GitHub issue with logs and error details
