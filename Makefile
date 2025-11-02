.PHONY: help install install-cpu test test-verbose test-coverage test-integration test-ui-api test-all test-clean clean setup-db populate-db cleanup-db lint format run-examples run run-api run-dev-api run-dev-ui run-rag-demo run-rag-cli check-env migrate-generate migrate-up migrate-down migrate-status migrate-reset setup-database frontend-install frontend-dev frontend-build frontend-clean frontend-test frontend-test-run frontend-test-coverage frontend-test-ci

SHELL := /bin/bash

# Default target - show help
help:
	@echo "=================================="
	@echo "RAG Application - Makefile Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install all dependencies"
	@echo "  make install-cpu      Install with PyTorch CPU-only (RECOMMENDED, saves ~1.9GB)"
	@echo "  make install-dev      Install dev dependencies"
	@echo "  make setup-database   Run database migrations (setup DB)"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run unit tests with coverage (parallel, ~10s)"
	@echo "  make test-html        Run unit tests with HTML coverage report"
	@echo "  make test-ci          Run unit tests for CI (xml + term + html)"
	@echo "  make test-integration Run integration tests (parallel, ~1s)"
	@echo "  make test-ui-api      Run UI API integration tests (~2s)"
	@echo "  make test-all         Run ALL tests (unit + integration + UI API)"
	@echo "  make test-clean       Clean up test storage artifacts"
	@echo "  make setup-test-chromadb  Set up ChromaDB test collection"
	@echo ""
	@echo "Database Management:"
	@echo "  make populate-db      Populate databases with sample data"
	@echo "  make cleanup-db       Clean all data from databases"
	@echo "  make reset-db         Clean and re-populate databases"
	@echo ""
	@echo "Database Migrations:"
	@echo "  make migrate-generate Generate new migration (DESC='description')"
	@echo "  make migrate-up       Apply all pending migrations"
	@echo "  make migrate-down     Rollback last migration"
	@echo "  make migrate-status   Show migration status"
	@echo "  make migrate-reset    Reset database (rollback all & reapply)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format           Format code (black + isort)"
	@echo "  make lint-check       Check code formatting (no changes)"
	@echo "  make lint             Run flake8 linter (reports issues)"
	@echo "  make lint-all         Run all linting checks (format + lint)"
	@echo ""
	@echo "Development:"
	@echo "  make run              🚀 Start unified app (API + UI on port 8000)"
	@echo "  make run-api          Start FastAPI server only (with auto-reload)"
	@echo "  make run-dev-api      🔧 Start API dev mode (no UI embedded)"
	@echo "  make run-dev-ui       🎨 Start Streamlit UI standalone (port 8501)"
	@echo "  make run-rag-cli      Interactive RAG terminal interface"
	@echo "  make run-rag-demo     Run RAG query demonstration"
	@echo "  make run-examples     Run demo examples"
	@echo "  make check-env        Check environment variables"
	@echo "  make check-python     Check Python version and packages"
	@echo ""
	@echo "Frontend Development:"
	@echo "  make frontend-install 📦 Install Node.js dependencies"
	@echo "  make frontend-dev     🎨 Start frontend dev server (port 5173)"
	@echo "  make frontend-build   🏗️  Build frontend for production"
	@echo "  make frontend-clean   🧹 Clean frontend build artifacts"
	@echo ""
	@echo "Frontend Testing:"
	@echo "  make frontend-test    🧪 Run frontend tests (watch mode)"
	@echo "  make frontend-test-run      Run frontend tests once (CI mode)"
	@echo "  make frontend-test-coverage Run frontend tests with coverage"
	@echo "  make frontend-test-ci       Run frontend tests for CI (with reports)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Clean temporary files"
	@echo "  make clean-all        Clean everything (including storage)"
	@echo ""
	@echo "Docker (Recommended for Development):"
	@echo "  make docker-setup        🔧 First-time setup (build all images)"
	@echo "  make docker-up           🚀 Start all services + run frontend tests"
	@echo "  make docker-down         🛑 Stop all services"
	@echo "  make docker-status       📊 Check service health status"
	@echo ""
	@echo "Docker - Working with Services:"
	@echo "  make docker-logs         View API logs (follow mode)"
	@echo "  make docker-logs-all     View all service logs"
	@echo "  make docker-logs-migration View migration logs"
	@echo "  make docker-ingest       📥 Run ingestion for uploaded files"
	@echo "  make docker-shell        Enter API container shell"
	@echo "  make docker-db-shell     Enter MySQL shell"
	@echo ""
	@echo "Docker - Testing:"
	@echo "  make docker-frontend-test 🧪 Run frontend tests separately (also runs in docker-up)"
	@echo ""
	@echo "Docker - Build & Maintenance:"
	@echo "  make docker-build-base   Build base image (with all dependencies)"
	@echo "  make docker-rebuild      🔨 Force rebuild all images"
	@echo "  make docker-clean        🧹 Clean all Docker resources"
	@echo "  make docker-restart      Restart all services"
	@echo ""
	@echo "Pre-commit Hooks:"
	@echo "  make pre-commit-install   Install pre-commit hooks"
	@echo "  make pre-commit-run       Run pre-commit on all files"
	@echo "  make pre-commit-update    Update pre-commit hooks"
	@echo ""

# Installation
install:
	@echo "Installing dependencies..."
	@./venv/bin/pip install -r requirements.txt

install-cpu:
	@echo "Installing dependencies with PyTorch CPU-only (no NVIDIA CUDA packages)..."
	@./venv/bin/pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
	@echo "✅ Installed successfully! (Saved ~1.9GB by avoiding CUDA packages)"

install-dev:
	@echo "Installing dev dependencies..."
	@./venv/bin/pip install -r requirements.txt
	@./venv/bin/pip install pytest pytest-cov black ruff

# Testing
# Default: Run unit tests with terminal coverage (fast, no external dependencies)
test:
	@echo "Running unit tests with coverage (parallel execution)..."
	@APP_ENV=test $(PYTHON) -m pytest \
		-m "not integration and not ui" \
		-n auto \
		--ff \
		--cov=. \
		--cov-config=pytest.ini \
		--cov-report=term \
		--ignore=scripts \
		--ignore=examples \
		--ignore=cli \
		--ignore=app/cli \
		--ignore=venv \
		--ignore=models \
		--ignore=storage \
		--ignore=htmlcov \
		--ignore=migration/versions \
		--ignore=migration/templates

# Run unit tests with HTML coverage report (for detailed analysis)
test-html:
	@echo "Running unit tests with HTML coverage report (parallel execution)..."
	@APP_ENV=test $(PYTHON) -m pytest \
		-m "not integration and not ui" \
		-n auto \
		--ff \
		--cov=. \
		--cov-config=pytest.ini \
		--cov-report=html \
		--ignore=scripts \
		--ignore=examples \
		--ignore=cli \
		--ignore=app/cli \
		--ignore=venv \
		--ignore=models \
		--ignore=storage \
		--ignore=htmlcov \
		--ignore=migration/versions \
		--ignore=migration/templates

test-ci:
	@echo "Running unit tests for CI (with xml + term + html coverage)..."
	@$(PYTHON) -m pytest \
		-m "not integration and not ui" \
		-n auto \
		--cov=. \
		--cov-config=pytest.ini \
		--cov-report=xml \
		--cov-report=term-missing \
		--cov-report=html \
		--ignore=scripts \
		--ignore=examples \
		--ignore=cli \
		--ignore=app/cli \
		--ignore=venv \
		--ignore=models \
		--ignore=storage \
		--ignore=htmlcov \
		--ignore=migration/versions \
		--ignore=migration/templates
	@echo ""
	@echo "📊 HTML coverage report generated: htmlcov/index.html"
	@echo "💡 Open with: open htmlcov/index.html"

setup-test-chromadb:
	@echo "📦 Setting up ChromaDB test collection..."
	@mkdir -p storage/chroma_test
	@echo "✅ ChromaDB test directory ready at: storage/chroma_test/"

# Run integration tests (requires MySQL test database)
# Note: Parallel execution with SELECT FOR UPDATE deadlock prevention
test-integration:
	@echo "🧪 Running integration tests (parallel execution with transaction isolation)..."
	@$(PYTHON) -m pytest \
		-m "integration" \
		-n auto \
		-vv \
		--ignore=scripts \
		--ignore=examples \
		--ignore=venv \
		--ignore=models \
		--ignore=storage \
		--ignore=htmlcov \
		--ignore=migration/versions \
		--ignore=migration/templates

test-ui-api:
	@echo "🎨 Running UI API integration tests (~2s)..."
	@$(PYTHON) -m pytest \
		-m "ui" \
		-vv

# Run all tests (unit + integration + UI API)
test-all:
	@echo "🧪 Running ALL tests..."
	@make test
	@make test-integration
	@make test-ui-api
	@make frontend-test-run
	@echo "✅ All tests passed!"

# Clean up test artifacts (storage directories only)
# Note: Database test data is automatically cleaned after each test
test-clean:
	@echo "🧹 Cleaning up test artifacts..."
	@rm -rf storage/chroma_test && echo "  ✓ Removed storage/chroma_test/" || true
	@rm -rf storage/test_documents && echo "  ✓ Removed storage/test_documents/" || true
	@echo "  ℹ️  Database test data auto-cleaned (see clean_database fixture)"
	@echo "✅ Test cleanup complete!"

# Database Management
setup-db:
	@echo "Setting up database..."
	@$(PYTHON) scripts/setup_database.py

populate-db:
	@echo "Populating databases with sample data..."
	@$(PYTHON) scripts/populate_sample_data.py

cleanup-db:
	@echo "Cleaning up databases..."
	@$(PYTHON) scripts/cleanup_all_databases.py

reset-db: cleanup-db populate-db
	@echo "Database reset complete!"

# Database Migrations
migrate-generate:
	@if [ -z "$(DESC)" ]; then \
		echo "Usage: make migrate-generate DESC='create_users_table'"; \
		exit 1; \
	fi
	@echo "Generating migration: $(DESC)"
	@$(PYTHON) -m migration generate $(DESC)

migrate-up:
	@echo "Applying pending migrations..."
	@$(PYTHON) -m migration up

migrate-down:
	@echo "Rolling back last migration..."
	@$(PYTHON) -m migration down

migrate-status:
	@echo "Checking migration status..."
	@$(PYTHON) -m migration status

migrate-reset:
	@echo "Resetting database migrations..."
	@$(PYTHON) -m migration reset --yes

seed:
	@echo "🌱 Seeding database with initial data..."
	@echo ""
	@$(PYTHON) -m migration.seed

setup-database: migrate-up
	@echo "✅ Database setup complete!"

# ==============================================================================
# Code Quality Commands
# ==============================================================================

# Variables for code quality tools
LINT_EXCLUDE := --exclude='/(venv|htmlcov|tests|scripts|examples|frontend|node_modules)/'
FLAKE8_EXCLUDE := --exclude=venv,htmlcov,tests,scripts,examples,frontend,node_modules
ISORT_SKIP := --skip-gitignore --skip tests --skip scripts --skip examples --skip venv --skip htmlcov --skip frontend --skip node_modules

# Python command (use venv if available, otherwise use system python)
PYTHON := $(shell if [ -f ./venv/bin/python ]; then echo "./venv/bin/python"; else echo "python"; fi)
BLACK := $(shell if [ -f ./venv/bin/black ]; then echo "./venv/bin/black"; else echo "black"; fi)
ISORT := $(shell if [ -f ./venv/bin/isort ]; then echo "./venv/bin/isort"; else echo "isort"; fi)
FLAKE8 := $(shell if [ -f ./venv/bin/flake8 ]; then echo "./venv/bin/flake8"; else echo "flake8"; fi)
UVICORN := $(shell if [ -f ./venv/bin/uvicorn ]; then echo "./venv/bin/uvicorn"; else echo "uvicorn"; fi)
STREAMLIT := $(shell if [ -f ./venv/bin/streamlit ]; then echo "./venv/bin/streamlit"; else echo "streamlit"; fi)

# Frontend commands
NPM := $(shell which npm)
FRONTEND_DIR := frontend

.PHONY: format lint-check lint lint-all black-check isort-check flake8-check

# Format code with black and isort (production code only)
format:
	@echo "🎨 Formatting code with Black..."
	@$(BLACK) . $(LINT_EXCLUDE)
	@echo "📦 Sorting imports with isort..."
	@$(ISORT) . --profile=black $(ISORT_SKIP)
	@echo "✅ Code formatting complete!"

# Check code formatting without making changes
black-check:
	@echo "🔍 Checking code formatting with Black..."
	@$(BLACK) --check --diff . $(LINT_EXCLUDE)

isort-check:
	@echo "🔍 Checking import sorting with isort..."
	@$(ISORT) --check-only --diff --profile=black . $(ISORT_SKIP)

flake8-check:
	@echo "🔍 Running Flake8 linter..."
	@$(FLAKE8) . --max-line-length=120 --extend-ignore=E203,W503 \
		--count --show-source --statistics $(FLAKE8_EXCLUDE)

# Check formatting (for CI/CD and pre-push)
lint-check: black-check isort-check
	@echo "✅ All formatting checks passed!"

# Run flake8 linter (reports issues, doesn't block)
lint: flake8-check

# Run all linting checks
lint-all: lint-check lint
	@echo "✅ All code quality checks complete!"

# Development
run-api:
	@echo "Starting FastAPI server..."
	@echo "Server will be available at http://localhost:8000"
	@echo "API docs: http://localhost:8000/docs"
	@echo ""
	@./venv/bin/uvicorn app.api.main:app --reload --workers 4 --host 0.0.0.0 --port 8000

run-api-prod:
	@echo "🚀 Starting FastAPI server (production mode)..."
	@echo "Server will be available at http://0.0.0.0:8000"
	@echo ""
	@$(UVICORN) app.api.main:app --host 0.0.0.0 --port 8000 --workers 1

run-rag-cli:
	@echo "Starting Interactive RAG CLI..."
	@echo ""
	@$(PYTHON) -m app.cli.main

run: frontend-build
	@echo "🚀 Starting Unified RAG Application..."
	@echo ""
	@echo "Services:"
	@echo "  - Landing Page: http://localhost:8000"
	@echo "  - FastAPI server: http://localhost:8000"
	@echo "  - API docs: http://localhost:8000/docs"
	@echo "  - LangChain Chat UI: http://localhost:8000/langchain/chat"
	@echo ""
	@echo "Note: Streamlit UI embedded automatically"
	@echo ""
	@$(UVICORN) app.api.main:app --host 0.0.0.0 --port 8000 --reload

# Alias for 'run' command
serve: run

run-dev-api:
	@echo "🔧 Starting FastAPI (dev mode, no UI)..."
	@echo "Open browser: http://localhost:8000/docs"
	@echo ""
	@echo "Note: Set UI_ENABLED=false in config to disable Streamlit"
	@echo ""
	@$(UVICORN) app.api.main:app --host 0.0.0.0 --port 8000 --reload

run-dev-ui:
	@echo "🎨 Starting Streamlit UI (standalone dev mode)..."
	@echo "Open browser: http://localhost:8501"
	@echo ""
	@echo "Note: For testing UI independently of FastAPI"
	@echo ""
	@$(STREAMLIT) run app/ui/main.py

# Frontend Development Commands
.PHONY: frontend-install frontend-dev frontend-build frontend-clean frontend-test frontend-test-run frontend-test-coverage frontend-test-ci

frontend-install:
	@echo "📦 Installing frontend dependencies..."
	@cd $(FRONTEND_DIR) && $(NPM) install
	@echo "✅ Frontend dependencies installed"

frontend-install-ci:
	@echo "📦 Installing frontend dependencies (CI mode)..."
	@cd $(FRONTEND_DIR) && $(NPM) ci --prefer-offline --no-audit
	@echo "✅ Frontend dependencies installed (CI)"

frontend-dev:
	@echo "🎨 Starting frontend dev server..."
	@echo "Open browser: http://localhost:5173"
	@echo ""
	@echo "Note: API proxy configured to http://localhost:8000"
	@echo ""
	@cd $(FRONTEND_DIR) && $(NPM) run dev

frontend-build:
	@echo "🏗️  Building frontend for production..."
	@cd $(FRONTEND_DIR) && $(NPM) run build
	@echo "✅ Frontend built to app/static/dist/"

frontend-verify:
	@echo "🔍 Verifying frontend build output..."
	@test -f app/static/dist/index.html || \
		(echo "❌ Frontend build failed - index.html not found!" && exit 1)
	@echo "✅ Frontend build verified"

frontend-clean:
	@echo "🧹 Cleaning frontend build artifacts..."
	@rm -rf $(FRONTEND_DIR)/node_modules $(FRONTEND_DIR)/dist app/static/dist
	@echo "✅ Frontend cleaned"

# Frontend Testing Commands
frontend-test:
	@echo "🧪 Running frontend tests (watch mode)..."
	@cd $(FRONTEND_DIR) && $(NPM) test

frontend-test-run:
	@echo "🧪 Running frontend tests (single run)..."
	@cd $(FRONTEND_DIR) && $(NPM) test -- --run
	@echo "✅ Frontend tests completed"

frontend-test-coverage:
	@echo "🧪 Running frontend tests with coverage..."
	@cd $(FRONTEND_DIR) && $(NPM) test -- --run --coverage
	@echo "✅ Frontend coverage report generated"

frontend-test-ci:
	@echo "🧪 Running frontend tests for CI..."
	@cd $(FRONTEND_DIR) && $(NPM) test -- --run --coverage --reporter=verbose
	@echo "✅ Frontend tests completed (CI mode)"

run-rag-demo:
	@echo "Running RAG query demonstration..."
	@echo ""
	@$(PYTHON) examples/demo_rag_query.py

run-examples:
	@echo "Running demo examples..."
	@echo ""
	@echo "1. Running vectorstore demo..."
	@$(PYTHON) examples/demo_vectorstore.py
	@echo ""
	@echo "2. Running provider switching demo..."
	@$(PYTHON) examples/demo_provider_switching.py

check-env:
	@echo "Checking environment variables..."
	@echo ""
	@echo "Required API Keys:"
	@if [ -z "$$GEMINI_API_KEY" ]; then echo "  GEMINI_API_KEY: NOT SET"; else echo "  GEMINI_API_KEY: SET"; fi
	@if [ -z "$$PINECONE_API_KEY" ]; then echo "  PINECONE_API_KEY: NOT SET (optional for local dev)"; else echo "  PINECONE_API_KEY: SET"; fi
	@if [ -z "$$QDRANT_API_KEY" ]; then echo "  QDRANT_API_KEY: NOT SET (optional for local dev)"; else echo "  QDRANT_API_KEY: SET"; fi
	@if [ -z "$$WEAVIATE_API_KEY" ]; then echo "  WEAVIATE_API_KEY: NOT SET (optional for local dev)"; else echo "  WEAVIATE_API_KEY: SET"; fi
	@echo ""

# Cleanup
clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.log" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete
	@find . -type f -name ".DS_Store" -delete
	@echo "✅ Cleanup complete!"

clean-all: clean
	@echo "Cleaning all files including storage..."
	@rm -rf storage/chroma/* 2>/dev/null || true
	@rm -rf storage/qdrant/* 2>/dev/null || true
	@rm -rf storage/weaviate/* 2>/dev/null || true
	@echo "All cleanup complete!"

# Python version check
check-python:
	@echo "Python version:"
	@$(PYTHON) --version
	@echo ""
	@echo "Installed packages:"
	@./venv/bin/pip list | grep -E "(pytest|structlog|chroma|pinecone|qdrant|weaviate)" || echo "No matching packages found"

# ==============================================================================
# Docker Commands
# ==============================================================================

.PHONY: docker-build docker-build-base docker-setup docker-up docker-down docker-stop docker-restart \
        docker-logs docker-logs-all docker-logs-migration docker-ingest docker-test docker-push \
        docker-clean docker-shell docker-db-shell docker-rebuild docker-status docker-frontend-test

docker-build:
	@echo "🐳 Building Docker image..."
	@echo "Using base image: sanjibdevnath/ragtrial-base:local"
	@docker build -f docker/Dockerfile --build-arg BASE_IMAGE_TAG=local -t ragtrial:local .
	@echo "✅ Docker image built: ragtrial:local"

docker-build-base:
	@echo "🐳 Building base image with all dependencies..."
	@docker build -f docker/Dockerfile.base -t sanjibdevnath/ragtrial-base:local .
	@echo "✅ Base image built: sanjibdevnath/ragtrial-base:local"
	@echo ""
	@echo "💡 To push to Docker Hub:"
	@echo "   make docker-push-base"

docker-push-base:
	@echo "📤 Pushing base image to Docker Hub..."
	@docker tag sanjibdevnath/ragtrial-base:local sanjibdevnath/ragtrial-base:$$(git rev-parse HEAD)
	@docker push sanjibdevnath/ragtrial-base:$$(git rev-parse HEAD)
	@echo "✅ Base image pushed: sanjibdevnath/ragtrial-base:$$(git rev-parse HEAD)"

docker-setup:
	@echo "🔧 Setting up Docker environment for first-time use..."
	@echo ""
	@echo "Step 1/3: Building base image with dependencies..."
	@$(MAKE) docker-build-base
	@echo ""
	@echo "Step 2/3: Building application images..."
	@docker-compose -f deployment/local/docker-compose.yml build
	@echo ""
	@echo "Step 3/3: Creating Docker volumes..."
	@docker volume create local_mysql_data 2>/dev/null || true
	@docker volume create local_chroma_data 2>/dev/null || true
	@echo ""
	@echo "════════════════════════════════════════════════════════════════════════"
	@echo "✅ Docker setup complete!"
	@echo "════════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run: make docker-up      # Start all services"
	@echo "  2. Visit: http://localhost:8000/docs"
	@echo ""

docker-up:
	@echo "🚀 Starting Docker stack (with automatic setup if needed)..."
	@echo ""
	@# Check if base image exists, if not, build it
	@if ! docker images | grep -q "sanjibdevnath/ragtrial-base.*local"; then \
		echo "⚠️  Base image not found. Building it first..."; \
		echo ""; \
		$(MAKE) docker-build-base; \
		echo ""; \
	fi
	@# Build and start services
	@echo "📦 Building and starting services..."
	@docker-compose -f deployment/local/docker-compose.yml up -d --build
	@echo ""
	@echo "⏳ Waiting for services to be healthy..."
	@sleep 5
	@echo ""
	@# Show migration logs
	@echo "📋 Migration Status:"
	@docker logs ragtrial-migration 2>&1 | tail -5 || echo "Migration container not found"
	@echo ""
	@# Check if API is healthy
	@echo "🏥 Health Check:"
	@for i in 1 2 3 4 5; do \
		if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then \
			echo "✅ API is healthy!"; \
			break; \
		else \
			echo "⏳ Waiting for API... ($$i/5)"; \
			sleep 2; \
		fi; \
	done
	@echo ""
	@echo "════════════════════════════════════════════════════════════════════════"
	@echo "✅ Docker stack is running!"
	@echo "════════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "📡 Services:"
	@echo "   API:      http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"
	@echo "   Health:   http://localhost:8000/api/v1/health"
	@echo "   ChromaDB: http://localhost:8001"
	@echo "   MySQL:    localhost:3306 (user: ragtrial, password: ragtrial)"
	@echo ""
	@echo "🧪 Frontend tests ran automatically (see logs above)"
	@echo ""
	@echo "🛠️  Useful commands:"
	@echo "   make docker-logs        # View API logs"
	@echo "   make docker-logs-all    # View all logs"
	@echo "   make docker-ingest      # Run ingestion for uploaded files"
	@echo "   make docker-shell       # Enter API container"
	@echo "   make docker-down        # Stop all services"
	@echo ""
	@docker-compose -f deployment/local/docker-compose.yml ps

docker-down:
	@echo "🛑 Stopping Docker Compose services..."
	@docker-compose -f deployment/local/docker-compose.yml down
	@echo "✅ Services stopped"

docker-stop:
	@echo "🛑 Stopping Docker Compose services..."
	@docker-compose -f deployment/local/docker-compose.yml down
	@echo "✅ Services stopped"

docker-restart:
	@echo "🔄 Restarting Docker Compose services..."
	@docker-compose -f deployment/local/docker-compose.yml restart
	@echo "✅ Services restarted"

docker-logs:
	@echo "📋 Following API logs (Ctrl+C to exit)..."
	@docker-compose -f deployment/local/docker-compose.yml logs -f api

docker-logs-all:
	@echo "📋 Following all service logs (Ctrl+C to exit)..."
	@docker-compose -f deployment/local/docker-compose.yml logs -f

docker-test:
	@echo "🧪 Running tests in Docker..."
	@docker-compose -f deployment/local/docker-compose.yml exec api pytest -v

docker-push:
	@echo "📤 Pushing to Docker Hub..."
	@docker tag ragtrial:local yourusername/ragtrial:local
	@docker push yourusername/ragtrial:local
	@echo "✅ Pushed to Docker Hub"

docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	@docker-compose -f deployment/local/docker-compose.yml down -v
	@docker system prune -f
	@echo "✅ Docker cleaned"

docker-shell:
	@echo "🐚 Opening shell in API container..."
	@docker-compose -f deployment/local/docker-compose.yml exec api /bin/bash

docker-ingest:
	@echo "📥 Running ingestion for uploaded files..."
	@docker-compose -f deployment/local/docker-compose.yml exec api python -m ingestion.ingest
	@echo ""
	@echo "✅ Ingestion complete!"

docker-frontend-test:
	@echo "🧪 Running frontend tests in Docker..."
	@echo ""
	@docker-compose -f deployment/local/docker-compose.yml run --rm frontend-test
	@echo ""
	@echo "✅ Frontend tests completed!"

docker-logs-migration:
	@echo "📋 Migration logs:"
	@docker logs ragtrial-migration 2>&1 || echo "Migration container not found"

docker-rebuild:
	@echo "🔨 Forcing rebuild of all images..."
	@echo ""
	@echo "Step 1/3: Rebuilding base image..."
	@$(MAKE) docker-build-base
	@echo ""
	@echo "Step 2/3: Rebuilding application images..."
	@docker-compose -f deployment/local/docker-compose.yml build --no-cache
	@echo ""
	@echo "Step 3/3: Restarting services..."
	@docker-compose -f deployment/local/docker-compose.yml down
	@docker-compose -f deployment/local/docker-compose.yml up -d
	@echo ""
	@echo "✅ Rebuild complete!"

docker-db-shell:
	@echo "💾 Opening MySQL shell..."
	@docker-compose -f deployment/local/docker-compose.yml exec db mysql -u ragtrial -pragtrial ragtrial

docker-status:
	@echo "📊 Docker Stack Status:"
	@echo ""
	@docker-compose -f deployment/local/docker-compose.yml ps
	@echo ""
	@echo "🏥 Health Checks:"
	@if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then \
		echo "✅ API: Healthy"; \
	else \
		echo "❌ API: Down"; \
	fi
	@if docker ps | grep -q ragtrial-db; then \
		echo "✅ MySQL: Running"; \
	else \
		echo "❌ MySQL: Down"; \
	fi
	@if docker ps | grep -q ragtrial-chroma; then \
		echo "✅ ChromaDB: Running"; \
	else \
		echo "❌ ChromaDB: Down"; \
	fi

# ==============================================================================
# Pre-commit Hooks
# ==============================================================================

.PHONY: pre-commit-install pre-commit-run pre-commit-update

pre-commit-install:
	@echo "🔧 Installing pre-commit hooks..."
	@pip install pre-commit
	@pre-commit install
	@echo "✅ Pre-commit hooks installed"

pre-commit-run:
	@echo "🔍 Running pre-commit on all files..."
	@pre-commit run --all-files

pre-commit-update:
	@echo "⬆️  Updating pre-commit hooks..."
	@pre-commit autoupdate
	@echo "✅ Pre-commit hooks updated"
