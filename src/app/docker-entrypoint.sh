#!/bin/bash
# Legal Retrieval Backend - Docker Entrypoint Script
# =================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    log "Waiting for $service_name at $host:$port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" >/dev/null 2>&1; then
            log_success "$service_name is ready!"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "$service_name is not available after $max_attempts attempts"
    return 1
}

# Function to check environment variables
check_environment() {
    log "Checking environment configuration..."
    
    # Required environment variables
    local required_vars=(
        "MONGODB_URL"
        "REDIS_URL"
        "QDRANT_URL"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        else
            log_success "$var is set"
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    # Optional environment variables with defaults
    export ENVIRONMENT=${ENVIRONMENT:-development}
    export LOG_LEVEL=${LOG_LEVEL:-INFO}
    export WORKERS=${WORKERS:-1}
    export HOST=${HOST:-0.0.0.0}
    export PORT=${PORT:-8000}
    
    log_success "Environment configuration complete"
}

# Function to run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Add your migration commands here
    # python -m alembic upgrade head
    
    log_success "Database migrations completed"
}

# Function to start API server
start_api() {
    log "Starting Legal Retrieval API server..."
    log "Environment: $ENVIRONMENT"
    log "Host: $HOST:$PORT"
    log "Workers: $WORKERS"
    log "Log Level: $LOG_LEVEL"
    
    if [ "$ENVIRONMENT" = "development" ]; then
        # Development mode with auto-reload
        exec uvicorn src.app.main:app \
            --host "$HOST" \
            --port "$PORT" \
            --reload \
            --log-level "$LOG_LEVEL"
    else
        # Production mode with multiple workers
        exec uvicorn src.app.main:app \
            --host "$HOST" \
            --port "$PORT" \
            --workers "$WORKERS" \
            --log-level "$LOG_LEVEL" \
            --access-log \
            --use-colors
    fi
}

# Function to start Celery worker
start_worker() {
    log "Starting Legal Retrieval Celery worker..."
    
    export CELERY_WORKER_POOL=${CELERY_WORKER_POOL:-eventlet}
    export CELERY_WORKER_CONCURRENCY=${CELERY_WORKER_CONCURRENCY:-4}
    export CELERY_WORKER_LOGLEVEL=${CELERY_WORKER_LOGLEVEL:-INFO}
    
    log "Pool: $CELERY_WORKER_POOL"
    log "Concurrency: $CELERY_WORKER_CONCURRENCY"
    log "Log Level: $CELERY_WORKER_LOGLEVEL"
    
    exec celery -A src.app.celery_config worker \
        --pool="$CELERY_WORKER_POOL" \
        --concurrency="$CELERY_WORKER_CONCURRENCY" \
        --loglevel="$CELERY_WORKER_LOGLEVEL" \
        --queues=rag,default \
        --hostname=worker@%h
}

# Function to start Celery beat scheduler
start_beat() {
    log "Starting Legal Retrieval Celery beat scheduler..."
    
    exec celery -A src.app.celery_config beat \
        --loglevel=INFO \
        --schedule=/app/data/celerybeat-schedule
}

# Function to run tests
run_tests() {
    log "Running Legal Retrieval tests..."
    
    # Install test dependencies if needed
    pip install pytest pytest-asyncio pytest-cov
    
    # Run tests
    exec pytest src/app/test/ -v --cov=src/app --cov-report=html --cov-report=term
}

# Function to run one-time tasks
run_task() {
    local task_name=$2
    log "Running one-time task: $task_name"
    
    case $task_name in
        "init-db")
            log "Initializing database..."
            python -c "from src.app.db import init_database; init_database()"
            ;;
        "create-vectors")
            log "Creating vector embeddings..."
            python -m src.app.tasks.create_vector_task
            ;;
        "health-check")
            log "Running health check..."
            python -c "
import requests
import sys
try:
    response = requests.get('http://localhost:8000/health', timeout=10)
    if response.status_code == 200:
        print('✅ Health check passed')
        sys.exit(0)
    else:
        print(f'❌ Health check failed: {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Health check error: {e}')
    sys.exit(1)
"
            ;;
        *)
            log_error "Unknown task: $task_name"
            echo "Available tasks: init-db, create-vectors, health-check"
            exit 1
            ;;
    esac
}

# Main script logic
main() {
    log "🚀 Legal Retrieval Backend - Docker Entrypoint"
    log "=============================================="
    
    # Check environment
    if ! check_environment; then
        log_error "Environment check failed"
        exit 1
    fi
    
    # Wait for dependencies
    if [ -n "$MONGODB_URL" ]; then
        # Extract host and port from MongoDB URL
        mongo_host=$(echo "$MONGODB_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        mongo_port=$(echo "$MONGODB_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        if [ -n "$mongo_host" ] && [ -n "$mongo_port" ]; then
            wait_for_service "$mongo_host" "$mongo_port" "MongoDB"
        fi
    fi
    
    if [ -n "$REDIS_URL" ]; then
        # Extract host and port from Redis URL
        redis_host=$(echo "$REDIS_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p' | sed 's/redis:\/\///')
        redis_port=$(echo "$REDIS_URL" | sed -n 's/.*:\([0-9]*\)$/\1/p')
        if [ -n "$redis_host" ] && [ -n "$redis_port" ]; then
            wait_for_service "$redis_host" "$redis_port" "Redis"
        fi
    fi
    
    # Handle different startup modes
    case "${1:-api}" in
        "api")
            start_api
            ;;
        "worker")
            start_worker
            ;;
        "beat")
            start_beat
            ;;
        "test")
            run_tests
            ;;
        "task")
            run_task "$@"
            ;;
        "shell")
            log "Starting interactive shell..."
            exec /bin/bash
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Available commands: api, worker, beat, test, task, shell"
            exit 1
            ;;
    esac
}

# Install netcat if not available (for service checks)
if ! command -v nc >/dev/null 2>&1; then
    log "Installing netcat for service checks..."
    apt-get update && apt-get install -y netcat-openbsd
fi

# Run main function
main "$@"
