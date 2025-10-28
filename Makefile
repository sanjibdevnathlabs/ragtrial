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
	@echo "  make test             Run all tests"
	@echo "  make test-verbose     Run tests with verbose output"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo "  make test-config      Run config tests only"
	@echo "  make test-logging     Run logging tests only"
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
	@echo "  make lint             Run linter (ruff)"
	@echo "  make format           Format code (black)"
	@echo "  make check            Run lint + format check"
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

# Installation
install:
	@echo "Installing dependencies..."
	@./venv/bin/pip install -r requirements.txt

install-dev:
	@echo "Installing dev dependencies..."
	@./venv/bin/pip install -r requirements.txt
	@./venv/bin/pip install pytest pytest-cov black ruff

# Testing
test:
	@echo "Running all tests..."
	@./venv/bin/python -m pytest tests/ -v

test-verbose:
	@echo "Running tests with verbose output..."
	@./venv/bin/python -m pytest tests/ -vv

test-coverage:
	@echo "Running tests with coverage..."
	@./venv/bin/python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

test-config:
	@echo "Running config tests..."
	@./venv/bin/python -m pytest tests/test_config.py tests/test_config_advanced.py -v

test-logging:
	@echo "Running logging tests..."
	@./venv/bin/python -m pytest tests/test_logging.py -v

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

# Code Quality
lint:
	@echo "Running linter..."
	@which ruff > /dev/null 2>&1 || (echo "ruff not installed. Run: make install-dev" && exit 1)
	@./venv/bin/ruff check . --fix

format:
	@echo "Formatting code..."
	@which black > /dev/null 2>&1 || (echo "black not installed. Run: make install-dev" && exit 1)
	@./venv/bin/black .

check: lint format
	@echo "Code quality check complete!"

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
