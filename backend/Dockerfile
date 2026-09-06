# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements-optional.txt ./

# Install Python dependencies (fail fast — do not hide errors)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-optional.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check (uses $PORT when set by the platform, e.g. Railway)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the application (single worker: safe for in-memory limiter / Chroma file store).
# Shell form so $PORT injected by the platform (Railway) is honored; defaults to 8000 locally.
# Scale workers only when using Postgres + Redis rate-limit storage.
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
