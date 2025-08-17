# Makefile Documentation - Legal Retrieval System

## Overview

This Makefile provides a comprehensive set of commands for building, deploying, testing, and managing the Legal Retrieval System Docker environment. It simplifies the management of a multi-service architecture including backend API, frontend, databases, and Celery workers.

## Quick Start

```bash
# Check environment and start all services
make quick-start

# View help for all available commands
make help

# Start development environment
make dev-up

# Check service health
make health

# Stop all services
make stop-all
```

## Categories of Commands

### 📦 Build Commands

| Command | Description | Usage Example |
|---------|-------------|---------------|
| `make build` | Build all services | `make build` |
| `make build-backend` | Build backend service only | `make build-backend` |
| `make build-frontend` | Build frontend service only | `make build-frontend` |
| `make build-clean` | Build without Docker cache | `make build-clean` |

**Use Cases:**
- `build`: When you've made changes to multiple services
- `build-backend`: When only backend code has changed
- `build-frontend`: When only frontend code has changed  
- `build-clean`: When encountering caching issues or need fresh builds

### 🚀 Deploy Commands

| Command | Description | Port Mappings |
|---------|-------------|---------------|
| `make up` | Start all services in background | See service URLs below |
| `make down` | Stop all services | - |
| `make restart` | Restart all services | - |
| `make logs` | View all service logs | - |
| `make status` | Show service status | - |

**Service URLs after `make up`:**
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Celery Flower: http://localhost:5555
- Qdrant: http://localhost:6333

### 🔧 Development Commands

| Command | Description | Best For |
|---------|-------------|----------|
| `make dev-up` | Start development with build | Daily development work |
| `make dev-down` | Stop and remove volumes | Clean development restart |
| `make dev-logs` | Follow development logs | Debugging during development |
| `make dev-shell` | Access backend container shell | Debugging, manual operations |

**Development Workflow:**
1. `make dev-up` - Start development environment
2. Make code changes
3. `make dev-logs` - Monitor logs for issues
4. `make dev-shell` - Debug if needed
5. `make dev-down` - Clean stop when done

### 📊 Service Commands

| Command | Description | Monitors |
|---------|-------------|----------|
| `make backend-logs` | View backend API logs | FastAPI, Uvicorn |
| `make worker-logs` | View worker logs | Celery workers (RAG, embed, retrieval, link) |
| `make db-logs` | View database logs | MongoDB, Redis, Qdrant |

**Troubleshooting with Logs:**
- Use `backend-logs` for API issues
- Use `worker-logs` for task processing issues
- Use `db-logs` for data storage issues

### 🧪 Testing Commands

| Command | Description | Test Scope |
|---------|-------------|------------|
| `make test` | Run all tests | Full test suite |
| `make test-smoke` | Run smoke tests only | Basic functionality |
| `make test-api` | Run API tests only | API endpoints |
| `make test-health` | Check service health | Service availability |

**Testing Strategy:**
- `test-health`: Quick check (30 seconds)
- `test-smoke`: Basic functionality (2-3 minutes)
- `test-api`: API comprehensive (5-10 minutes)
- `test`: Full suite (10-15 minutes)

### 🧹 Cleanup Commands

| Command | Description | ⚠️ Data Impact |
|---------|-------------|----------------|
| `make clean` | Clean unused Docker resources | Safe - no data loss |
| `make clean-volumes` | Remove all volumes | **DANGEROUS** - Deletes all data |
| `make clean-all` | Deep clean everything | **DANGEROUS** - Complete wipe |

**Safety Measures:**
- `clean-volumes` requires typing "DELETE" to confirm
- `clean-all` requires typing "CONFIRM" to confirm
- Always backup important data before volume cleanup

### 🎯 Utility Commands

| Command | Description | Output |
|---------|-------------|--------|
| `make health` | Check service health | Health status for all services |
| `make show-urls` | Show service URLs | All accessible endpoints |
| `make check-env` | Check environment | Environment validation |

## Environment Variables

The Makefile supports several environment variables for customization:

```bash
# Default values (can be overridden)
REGISTRY=docker.io          # Docker registry
TAG=latest                  # Image tag
COMPOSE_FILE=docker-compose.yml  # Compose file to use
PROJECT_NAME=legal-retrieval     # Project name
```

**Usage Examples:**
```bash
# Build with custom tag
make build-backend TAG=v1.0.0

# Use different compose file
make up COMPOSE_FILE=docker-compose.prod.yml

# Use custom registry
make build REGISTRY=myregistry.com
```

## Service Architecture

The system consists of these services:

### Core Services
- **backend-api**: FastAPI application (Port 8000)
- **frontend**: React/Next.js application (Port 3000)

### Data Services
- **mongodb**: Document database (Port 27017)
- **redis**: Cache and message broker (Port 6379)
- **qdrant**: Vector database (Port 6333)

### Worker Services
- **celery-worker-rag**: RAG processing tasks
- **celery-worker-embed**: Embedding generation
- **celery-worker-retrieval**: Document retrieval
- **celery-worker-link**: Link processing

### Monitoring
- **celery-flower**: Celery monitoring (Port 5555)

## Common Workflows

### Daily Development
```bash
# Morning startup
make dev-up
make health

# During development
make dev-logs  # In separate terminal

# Code changes
make build-backend  # If backend changed
make restart

# End of day
make dev-down
```

### Testing Workflow
```bash
# Quick health check
make test-health

# Before committing
make test-smoke

# Full testing
make test

# Cleanup after testing
make clean
```

### Production Deployment
```bash
# Environment check
make check-env

# Build all services
make build-clean

# Start production
make up

# Health verification
make health
make show-urls

# Monitor
make logs
```

### Troubleshooting Workflow
```bash
# Check service status
make status

# View specific logs
make backend-logs
make worker-logs
make db-logs

# Access container for debugging
make dev-shell

# Clean restart
make down
make clean
make up
```

## File Dependencies

The Makefile expects these files to exist:

### Required Files
- `docker-compose.yml`: Main compose configuration
- `.env`: Environment variables (copy from `.env.example`)

### Optional Files
- `tests/run_docker_tests.sh`: Test execution script
- `tests/api/comprehensive_backend_test.py`: API test suite

### Generated Files
- `Makefile.old`: Backup of previous Makefile

## Error Handling

The Makefile includes error handling for common scenarios:

### Missing Dependencies
- Commands check for required scripts before execution
- Fallback to basic health checks if test scripts missing
- Clear error messages for missing files

### Service Health
- Health checks with proper error reporting
- Curl commands with failure detection
- Service-specific health endpoints

### Confirmation Prompts
- Destructive operations require explicit confirmation
- Clear warnings about data loss
- Safe defaults for all operations

## Advanced Usage

### Custom Compose Files
```bash
# Use test compose file
make up COMPOSE_FILE=docker-compose.test.yml

# Development with custom settings
make dev-up COMPOSE_FILE=docker-compose.dev.yml
```

### Multiple Environments
```bash
# Set project name to avoid conflicts
make up PROJECT_NAME=legal-retrieval-dev

# Use environment-specific settings
make build TAG=dev-$(date +%Y%m%d)
```

### Debugging Techniques
```bash
# Follow specific service logs
make backend-logs | grep ERROR

# Check container resource usage
docker stats $(docker-compose ps -q)

# Access database directly
make dev-shell
# Inside container: mongo mongodb://localhost:27017
```

## Performance Tips

### Build Optimization
- Use `build-backend` or `build-frontend` for targeted builds
- Use `build-clean` only when necessary (slower)
- Leverage Docker layer caching with regular `build`

### Resource Management
- Use `clean` regularly to free disk space
- Monitor logs size with service-specific log commands
- Use `dev-down` to release resources during breaks

### Development Efficiency
- Keep `dev-logs` running in separate terminal
- Use `health` command for quick status checks
- Leverage `dev-shell` for debugging without rebuilds

## Security Considerations

### Environment Variables
- Never commit `.env` files with secrets
- Use `.env.example` as template
- Rotate secrets regularly

### Network Security
- Services exposed only on localhost by default
- Use proper authentication in production
- Consider firewall rules for production deployment

### Data Protection
- Always backup before `clean-volumes`
- Use version control for configuration changes
- Test backups regularly

## Maintenance

### Regular Tasks
- Weekly: `make clean` to free disk space
- Monthly: Review and update service versions
- Quarterly: Update base images and dependencies

### Monitoring
- Monitor disk usage with regular cleanup
- Check service health daily in production
- Review logs for unusual patterns

### Updates
- Test new versions in development first
- Use tagged versions for production
- Maintain rollback procedures

This documentation provides comprehensive guidance for using the Makefile effectively in different scenarios, from daily development to production deployment and maintenance.
