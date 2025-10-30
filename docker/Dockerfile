# Multi-stage production image with optimized caching
# =============================================================================
# Global ARG for base image tag (must be before first FROM)
ARG BASE_IMAGE_TAG=local

# =============================================================================
# Stage 1: Build frontend with Node.js
# =============================================================================
# Using specific Node.js version for security and reproducibility
# Update this version regularly to get security patches
FROM node:20.18.1-alpine3.20 AS frontend-builder

WORKDIR /app

# Install make and bash for consistent command execution
RUN apk add --no-cache make bash

# Copy Makefile and frontend files
COPY Makefile ./
COPY frontend/ ./frontend/

# Install dependencies using make (CI mode for Docker)
RUN make frontend-install-ci

# Build frontend using make
RUN make frontend-build

# Verify build output using make
RUN make frontend-verify

# =============================================================================
# Stage 2: Production Python image with built frontend
# =============================================================================
FROM sanjibdevnath/ragtrial-base:${BASE_IMAGE_TAG}

LABEL maintainer="sanjib.devnath@example.com"
LABEL org.opencontainers.image.source="https://github.com/sanjibdevnathlabs/ragtrial"
LABEL org.opencontainers.image.description="RAG Trial - Production-ready RAG application with React UI"

# Base image already sets WORKDIR /app, USER appuser, ENV variables, and Makefile
# No need to repeat them here

# CACHE OPTIMIZATION: Copy application code in layers
# Copy files that change less frequently first

# 1. Copy configuration and constants (rarely change)
COPY --chown=appuser:appuser config/ ./config/
COPY --chown=appuser:appuser constants/ ./constants/
COPY --chown=appuser:appuser environment/ ./environment/

# 2. Copy core modules (change occasionally)
COPY --chown=appuser:appuser database/ ./database/
COPY --chown=appuser:appuser logger/ ./logger/
COPY --chown=appuser:appuser trace/ ./trace/
COPY --chown=appuser:appuser utils/ ./utils/
COPY --chown=appuser:appuser migration/ ./migration/

# 3. Copy LLM and embeddings modules (change occasionally)
COPY --chown=appuser:appuser llm/ ./llm/
COPY --chown=appuser:appuser embeddings/ ./embeddings/
COPY --chown=appuser:appuser vectorstore/ ./vectorstore/
COPY --chown=appuser:appuser loader/ ./loader/
COPY --chown=appuser:appuser splitter/ ./splitter/
COPY --chown=appuser:appuser storage_backend/ ./storage_backend/

# 4. Copy ingestion module (change occasionally)
COPY --chown=appuser:appuser ingestion/ ./ingestion/

# 5. Copy application modules (change more frequently)
COPY --chown=appuser:appuser app/ ./app/

# Copy built frontend from builder stage
COPY --from=frontend-builder --chown=appuser:appuser /app/app/static/dist ./app/static/dist

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose port
EXPOSE 8000

# Run unified application using make command for consistency
CMD ["make", "run-api-prod"]
