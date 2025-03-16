FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    CHROMIUM_PATH=/usr/bin/chromium \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for Chromium and scraping
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic-dev \
    wget \
    gnupg \
    chromium \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    # Install packages one by one to better handle dependency conflicts
    pip install --no-cache-dir pydantic==2.10.6 && \
    pip install --no-cache-dir pydantic-settings==2.8.1 && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# Create non-root user before copying application code
RUN useradd -m sahluser && \
    mkdir -p /data/files && \
    chown -R sahluser:sahluser /app /data

# Copy application code
COPY --chown=sahluser:sahluser . .

# Switch to non-root user
USER sahluser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]