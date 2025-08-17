# Minimal Dockerfile for Legal Retrieval Backend
# Commands and environment variables managed by docker-compose
# ===========================================================
FROM python:3.11-slim

# Basic environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    procps \
    dnsutils \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . ./app/

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/data /app/temp /app/cache \
    && chmod -R 755 /app

# Create wait-for-services script
COPY wait-for-services.py /app/wait-for-services.py
RUN chmod +x /app/wait-for-services.py

# Expose ports (will be managed by docker-compose)
EXPOSE 8000 5555

# Default command (will be overridden by docker-compose)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
