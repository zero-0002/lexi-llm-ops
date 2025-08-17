# Legal Retrieval System
# =====================

**Hệ thống tra cứu pháp luật thông minh với AI và RAG (Retrieval-Augmented Generation)**

## 🎯 Tổng quan

Legal Retrieval System là một hệ thống tra cứu pháp luật hiện đại sử dụng công nghệ AI để cung cấp thông tin pháp luật chính xác và phù hợp. Hệ thống kết hợp:

- **Frontend**: React.js với giao diện chat thân thiện
- **Backend**: FastAPI với architecture scalable
- **AI/ML**: OpenAI GPT models với RAG system
- **Vector DB**: Qdrant cho semantic search
- **Workflow**: Celery workers cho xử lý bất đồng bộ
- **Database**: MongoDB cho data persistence, Redis cho caching

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- Make (optional)

### Khởi chạy nhanh
```bash
# Clone repository
git clone <repository-url>
cd Legal-Retrieval

# Make scripts executable
find scripts tests -name "*.sh" -exec chmod +x {} \;

# Quick start với make
make quick-start

# Hoặc manual
./scripts/build-docker.sh
docker-compose up -d
```

### Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Celery Monitor**: http://localhost:5555

## 📁 Cấu trúc dự án

```
Legal-Retrieval/
├── src/                          # Source code
│   ├── app/                      # Backend FastAPI
│   └── legal-chatbot-fe/         # Frontend React
├── scripts/                      # Deployment scripts
│   ├── build-docker.sh          # Build Docker images
│   ├── system-check.sh          # System validation
│   └── update-helm-values.sh    # Kubernetes deployment
├── tests/                        # Test suite
│   ├── run_docker_tests.sh      # Test runner
│   └── DOCKER_TESTING_GUIDE.md  # Testing documentation
├── helm/                         # Kubernetes manifests
├── deployment/                   # Deployment configs
├── docs/                         # Documentation
├── docker-compose.yml           # Development environment
├── docker-compose.test.yml      # Test environment
├── Makefile                     # Convenience commands
└── DEPLOYMENT_GUIDE.md          # Complete deployment guide
```

## 🛠️ Phát triển

### Development Commands
```bash
# Start development environment
make dev-up

# View logs
make logs

# Run tests
make test-smoke      # Quick tests
make test           # Full test suite

# Build images
./scripts/build-docker.sh -s backend
./scripts/build-docker.sh -s frontend

# System check
./scripts/system-check.sh
```

### Environment Setup
```bash
# Copy environment template
cp .env.docker.example .env

# Edit .env và set API keys
# OPENAI_API_KEY=your_openai_api_key
```

## 🧪 Testing

Hệ thống có test suite toàn diện:

```bash
# Smoke tests (2-3 phút)
make test-smoke

# Specific test types
make test-api         # API endpoints
make test-db          # Database integration  
make test-ws          # WebSocket functionality
make test-integration # End-to-end tests

# Test với Docker isolation
./tests/run_docker_tests.sh --command test --test-type smoke
```

Xem chi tiết tại: `tests/DOCKER_TESTING_GUIDE.md`

## 🐳 Docker Deployment

### Local Development
```bash
# Build và start all services
docker-compose up --build -d

# Scale workers
docker-compose up --scale celery-worker-rag=3 -d

# View service status
docker-compose ps
```

### Production
```bash
# Build production images
./scripts/build-docker.sh --tag production

# Deploy với production settings
docker-compose -f docker-compose.yml --env-file .env.production up -d
```

## ☸️ Kubernetes

### Local với Kind
```bash
# Create Kind cluster
kind create cluster --name legal-retrieval

# Build và load images
./scripts/build-docker.sh --tag k8s
kind load docker-image legal-retrieval/backend:k8s --name legal-retrieval
kind load docker-image legal-retrieval/frontend:k8s --name legal-retrieval

# Deploy với Helm
./scripts/update-helm-values.sh --tag k8s --load-to-kind --update-kind
```

### Production Kubernetes
See `DEPLOYMENT_GUIDE.md` for detailed instructions.

## 📊 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Celery        │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Workers       │
│   Port: 3000    │    │   Port: 8000    │    │   (4 workers)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
              ┌──────────────────────────────────────┐
              │              Databases               │
              │  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
              │  │ MongoDB │ │  Redis  │ │ Qdrant  │ │
              │  │ :27017  │ │ :6379   │ │ :6333   │ │
              │  └─────────┘ └─────────┘ └─────────┘ │
              └──────────────────────────────────────┘
```

### Services
- **backend-api**: FastAPI server với authentication, WebSocket
- **celery-worker-rag**: RAG processing và document retrieval
- **celery-worker-embed**: Document embedding và vectorization  
- **celery-worker-retrieval**: Search và content retrieval
- **celery-worker-link**: Web scraping và link extraction
- **celery-flower**: Task monitoring dashboard

## 🔧 Configuration

### Environment Variables
Key environment variables trong `.env`:

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Database URLs
MONGO_URL=mongodb://admin:password123@mongodb:27017/legaldb?authSource=admin
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333

# Application settings
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000"]
```

### Scaling Configuration
```bash
# Worker concurrency
CELERY_CONCURRENCY=2           # Per worker process
UVICORN_WORKERS=1             # API server processes

# Database settings  
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password123
```

## 📚 Documentation

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**: Complete deployment instructions
- **[tests/DOCKER_TESTING_GUIDE.md](tests/DOCKER_TESTING_GUIDE.md)**: Testing framework guide
- **[docs/flow.md](docs/flow.md)**: System architecture overview
- **[LINUX_MIGRATION_REPORT.md](LINUX_MIGRATION_REPORT.md)**: Migration to Linux bash scripts

## 🔍 Monitoring & Debugging

### Health Checks
```bash
# Quick system overview
./scripts/docker-summary.sh

# Service health
curl http://localhost:8000/health    # Backend
curl http://localhost:3000/health    # Frontend
curl http://localhost:6333/health    # Qdrant

# Database connectivity
docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"
docker-compose exec redis redis-cli ping
```

### Logs
```bash
# All services
make logs

# Specific services
make backend-logs     # Backend API
make worker-logs      # All workers  
make flower-logs      # Celery monitoring
make db-logs          # Databases

# Follow logs real-time
docker-compose logs -f backend-api celery-worker-rag
```

### Performance Monitoring
- **Celery Tasks**: http://localhost:5555
- **Resource Usage**: `docker stats`
- **Database Metrics**: MongoDB/Redis/Qdrant admin interfaces

## 🛡️ Security

### Production Checklist
- [ ] Change default database passwords
- [ ] Set production OPENAI_API_KEY
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS với reverse proxy
- [ ] Set up firewall rules
- [ ] Use Kubernetes secrets for sensitive data

## 🚨 Troubleshooting

### Common Issues

**Services won't start**
```bash
# Check Docker daemon
docker ps

# Check service logs
docker-compose logs backend-api

# Rebuild images
docker-compose build --no-cache
```

**Database connection errors**
```bash
# Test MongoDB
docker-compose exec mongodb mongosh "mongodb://admin:password123@localhost:27017/legaldb?authSource=admin"

# Test Redis
docker-compose exec redis redis-cli ping

# Check environment variables
docker-compose exec backend-api env | grep -E "(MONGO|REDIS|QDRANT)"
```

**API not responding**
```bash
# Check backend health
curl -v http://localhost:8000/health

# Check worker status
docker-compose exec celery-worker-rag celery -A app.celery inspect ping

# Monitor tasks
open http://localhost:5555
```

## 🔄 Development Workflow

### Code Changes
```bash
# Backend changes
docker-compose restart backend-api

# Frontend changes (with hot reload)
docker-compose restart frontend

# Worker changes
docker-compose restart celery-worker-rag celery-worker-embed
```

### Testing Changes
```bash
# Run smoke tests after changes
make test-smoke

# Full integration test
make test-integration

# Test specific functionality
./tests/run_docker_tests.sh --command test --test-type api
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes và test: `make test-smoke`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Create Pull Request

## 📄 License

[Specify your license here]

## 🆘 Support

For issues và questions:
- Check `DEPLOYMENT_GUIDE.md` for detailed instructions
- Review `tests/DOCKER_TESTING_GUIDE.md` for testing help
- Run `./scripts/system-check.sh` for system validation

---

✅ **Ready to deploy your Legal Retrieval System!** 🚀

Made with ❤️ using Docker, FastAPI, React, và AI technologies.
