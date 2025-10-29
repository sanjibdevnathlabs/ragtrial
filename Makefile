.PHONY: help install test test-verbose test-coverage clean setup-db populate-db cleanup-db lint format run-examples run-api run-rag-demo run-rag-cli check-env migrate-generate migrate-up migrate-down migrate-status migrate-reset setup-database

SHELL := /bin/bash

# Default target - show help
help:
	@echo "=================================="
	@echo "RAG Application - Makefile Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install all dependencies"
	@echo "  make install-dev      Install dev dependencies"
	@echo "  make setup-database   Run database migrations (setup DB)"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run unit tests with coverage (parallel, ~10s)"
	@echo "  make test-html        Run unit tests with HTML coverage report"
	@echo "  make test-ci          Run unit tests for CI (xml + term + html)"
	@echo "  make test-integration Run integration tests (parallel, ~1s)"
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
	@echo "  make run-api          Start FastAPI server (with auto-reload)"
	@echo "  make run-rag-cli      Interactive RAG terminal interface"
	@echo "  make run-rag-demo     Run RAG query demonstration"
	@echo "  make run-examples     Run demo examples"
	@echo "  make check-env        Check environment variables"
	@echo "  make check-python     Check Python version and packages"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Clean temporary files"
	@echo "  make clean-all        Clean everything (including storage)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build        Build Docker image"
	@echo "  make docker-build-base   Build base image (with all dependencies)"
	@echo "  make docker-push-base    Push base image to Docker Hub"
	@echo "  make docker-run          Start all services (API, MySQL, ChromaDB)"
	@echo "  make docker-stop         Stop all services"
	@echo "  make docker-restart      Restart all services"
	@echo "  make docker-logs         View API logs"
	@echo "  make docker-logs-all     View all service logs"
	@echo "  make docker-test         Run tests in Docker"
	@echo "  make docker-push         Push image to Docker Hub"
	@echo "  make docker-shell        Open shell in API container"
	@echo "  make docker-clean        Clean Docker resources"
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

install-dev:
	@echo "Installing dev dependencies..."
	@./venv/bin/pip install -r requirements.txt
	@./venv/bin/pip install pytest pytest-cov black ruff

# Testing
# Default: Run unit tests with terminal coverage (fast, no external dependencies)
test:
	@echo "Running unit tests with coverage (parallel execution)..."
	@APP_ENV=test ./venv/bin/python -m pytest \
		-m "not integration" \
		-n auto \
		--ff \
		--cov=. \
		--cov-report=term \
		--ignore=scripts \
		--ignore=examples \
		--ignore=venv \
		--ignore=models \
		--ignore=storage \
		--ignore=htmlcov \
		--ignore=migration/versions \
		--ignore=migration/templates

# Run unit tests with HTML coverage report (for detailed analysis)
test-html:
	@echo "Running unit tests with HTML coverage report (parallel execution)..."
	@APP_ENV=test ./venv/bin/python -m pytest \
		-m "not integration" \
		-n auto \
		--ff \
		--cov=. \
		--cov-report=html \
		--ignore=scripts \
		--ignore=examples \
		--ignore=venv \
		--ignore=models \
		--ignore=storage \
		--ignore=htmlcov \
		--ignore=migration/versions \
		--ignore=migration/templates

test-ci:
	@echo "Running unit tests for CI (with xml + term + html coverage)..."
	@APP_ENV=test ./venv/bin/python -m pytest \
		-m "not integration" \
		-n auto \
		--cov=. \
		--cov-report=xml \
		--cov-report=term-missing \
		--cov-report=html \
		--ignore=scripts \
		--ignore=examples \
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
	@echo "🧪 Running integration tests (parallel, ~1s)..."
	@APP_ENV=test ./venv/bin/python -m pytest \
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
	@./venv/bin/python scripts/setup_database.py

populate-db:
	@echo "Populating databases with sample data..."
	@./venv/bin/python scripts/populate_sample_data.py

cleanup-db:
	@echo "Cleaning up databases..."
	@./venv/bin/python scripts/cleanup_all_databases.py

reset-db: cleanup-db populate-db
	@echo "Database reset complete!"

# Database Migrations
migrate-generate:
	@if [ -z "$(DESC)" ]; then \
		echo "Usage: make migrate-generate DESC='create_users_table'"; \
		exit 1; \
	fi
	@echo "Generating migration: $(DESC)"
	@./venv/bin/python -m migration generate $(DESC)

migrate-up:
	@echo "Applying pending migrations..."
	@./venv/bin/python -m migration up

migrate-down:
	@echo "Rolling back last migration..."
	@./venv/bin/python -m migration down

migrate-status:
	@echo "Checking migration status..."
	@./venv/bin/python -m migration status

migrate-reset:
	@echo "Resetting database migrations..."
	@./venv/bin/python -m migration reset --yes

setup-database: migrate-up
	@echo "✅ Database setup complete!"

# ==============================================================================
# Code Quality Commands
# ==============================================================================

# Variables for code quality tools
LINT_EXCLUDE := --exclude='/(venv|htmlcov|tests|scripts|examples)/'
FLAKE8_EXCLUDE := --exclude=venv,htmlcov,tests,scripts,examples
ISORT_SKIP := --skip-gitignore --skip tests --skip scripts --skip examples --skip venv --skip htmlcov

# Python command (use venv if available, otherwise use system python)
PYTHON := $(shell if [ -f ./venv/bin/python ]; then echo "./venv/bin/python"; else echo "python"; fi)
BLACK := $(shell if [ -f ./venv/bin/black ]; then echo "./venv/bin/black"; else echo "black"; fi)
ISORT := $(shell if [ -f ./venv/bin/isort ]; then echo "./venv/bin/isort"; else echo "isort"; fi)
FLAKE8 := $(shell if [ -f ./venv/bin/flake8 ]; then echo "./venv/bin/flake8"; else echo "flake8"; fi)

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
	@$(FLAKE8) . --max-line-length=88 --extend-ignore=E203,W503 \
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

run-rag-cli:
	@echo "Starting Interactive RAG CLI..."
	@echo ""
	@./venv/bin/python -m app.cli.main

run-rag-demo:
	@echo "Running RAG query demonstration..."
	@echo ""
	@./venv/bin/python examples/demo_rag_query.py

run-examples:
	@echo "Running demo examples..."
	@echo ""
	@echo "1. Running vectorstore demo..."
	@./venv/bin/python examples/demo_vectorstore.py
	@echo ""
	@echo "2. Running provider switching demo..."
	@./venv/bin/python examples/demo_provider_switching.py

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
	@echo "Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.log" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete
	@echo "Cleanup complete!"

clean-all: clean
	@echo "Cleaning all files including storage..."
	@rm -rf storage/chroma/* 2>/dev/null || true
	@rm -rf storage/qdrant/* 2>/dev/null || true
	@rm -rf storage/weaviate/* 2>/dev/null || true
	@echo "All cleanup complete!"

# Python version check
check-python:
	@echo "Python version:"
	@./venv/bin/python --version
	@echo ""
	@echo "Installed packages:"
	@./venv/bin/pip list | grep -E "(pytest|structlog|chroma|pinecone|qdrant|weaviate)" || echo "No matching packages found"

# ==============================================================================
# Docker Commands
# ==============================================================================

.PHONY: docker-build docker-run docker-stop docker-logs docker-test docker-push docker-clean

docker-build:
	@echo "🐳 Building Docker image..."
	@docker build -f docker/Dockerfile -t ragtrial:local .
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

docker-run:
	@echo "🚀 Starting Docker Compose services..."
	@docker-compose -f deployment/local/docker-compose.yml up -d
	@echo ""
	@echo "✅ Services running:"
	@echo "   📡 API:      http://localhost:8000"
	@echo "   📊 API Docs: http://localhost:8000/docs"
	@echo "   🔍 Health:   http://localhost:8000/api/v1/health"
	@echo "   💾 ChromaDB: http://localhost:8001"
	@echo ""
	@docker-compose -f deployment/local/docker-compose.yml ps

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
