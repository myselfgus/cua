# CUA Backend Dockerfile
# Multi-stage build for optimal image size

ARG PYTHON_VERSION="3.11"

# Base image with Python
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base AS development

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 cuauser && \
    chown -R cuauser:cuauser /app

USER cuauser

# Expose port
EXPOSE 8000

# Development command with reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

WORKDIR /app

# Copy requirements and install production dependencies
COPY requirements.txt .
RUN pip install --no-dev -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 cuauser && \
    chown -R cuauser:cuauser /app

USER cuauser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Production command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]