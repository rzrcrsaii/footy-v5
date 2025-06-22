# Footy-Brain v5 API Server Dockerfile
# Multi-stage build for production-ready FastAPI application

# =============================================================================
# Base stage with Python and system dependencies
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# =============================================================================
# Development stage
# =============================================================================
FROM base as dev

# Install Poetry
RUN pip install poetry==1.7.1

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev

# Copy application code
COPY . .

# Change ownership to app user
RUN chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "apps.api_server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# Production stage
# =============================================================================
FROM base as prod

# Install Poetry
RUN pip install poetry==1.7.1

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install only production dependencies
RUN poetry install --only=main --no-dev

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/footy-brain && \
    chown -R appuser:appuser /var/log/footy-brain

# Change ownership to app user
RUN chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with multiple workers
CMD ["uvicorn", "apps.api_server.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# =============================================================================
# Worker stage (for Celery workers)
# =============================================================================
FROM prod as worker

# Override command for Celery worker
CMD ["celery", "-A", "apps.api_server.tasks", "worker", "--loglevel=info", "--concurrency=4"]

# =============================================================================
# Beat stage (for Celery beat scheduler)
# =============================================================================
FROM prod as beat

# Override command for Celery beat
CMD ["celery", "-A", "apps.api_server.tasks", "beat", "--loglevel=info", "--scheduler=celery.schedulers:DatabaseScheduler"]
