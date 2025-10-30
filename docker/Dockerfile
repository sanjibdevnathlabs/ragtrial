# Production image built on top of base image with pre-installed dependencies
# Base image (sanjibdevnath/ragtrial-base) already contains all Python packages
# Use ARG to accept base image tag from build command (commit SHA for isolation)

ARG BASE_IMAGE_TAG=latest
FROM sanjibdevnath/ragtrial-base:${BASE_IMAGE_TAG}

LABEL maintainer="sanjib.devnath@example.com"
LABEL org.opencontainers.image.source="https://github.com/username/ragtrial"
LABEL org.opencontainers.image.description="RAG Trial - Production-ready RAG application"

WORKDIR /app

# Copy application code (dependencies already in base image)
COPY . .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH"

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose FastAPI port (Streamlit runs internally on 8501)
EXPOSE 8000

# Run unified application (FastAPI with embedded Streamlit)
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

