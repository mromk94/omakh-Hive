# Production Dockerfile for Queen AI

FROM python:3.13-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.13-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code (this layer will be invalidated on code changes)
COPY . .

# Create non-root user
RUN useradd -m -u 1001 queenai && \
    chown -R queenai:queenai /app

USER queenai

# Cloud Run uses PORT env var (default 8080)
ENV PORT 8080
ENV PYTHONUNBUFFERED 1
EXPOSE 8080

# Start with uvicorn, binding to Cloud Run's PORT (default 8080)
# Use sh -c so ${PORT} is expanded at runtime
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
