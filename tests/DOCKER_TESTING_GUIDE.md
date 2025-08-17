# Docker Testing Guide - Legal Retrieval System

Hướng dẫn chi tiết về việc triển khai và chạy tests API sử dụng Docker Compose.

## 🏗️ Kiến trúc Test Environment

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Runner   │    │   Test API      │    │  Test Databases │
│   (PyTest)      │◄──►│   (FastAPI)     │◄──►│   MongoDB-Test  │
│   Port: N/A     │    │   Port: 8001    │    │   Redis-Test    │
│                 │    │                 │    │   Qdrant-Test   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Test Workers   │
                       │  - Test Queue   │
                       │  - RAG Testing  │
                       │  - Embed Test   │
                       └─────────────────┘
```

## 📦 Test Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| `test-runner` | - | PyTest container cho việc chạy tests |
| `backend-api-test` | 8001 | FastAPI test server |
| `celery-worker-test` | - | Celery worker cho test tasks |
| `celery-flower-test` | 5556 | Monitoring cho test workers |
| `mongodb-test` | 27018 | Test database (isolated) |
| `redis-test` | 6380 | Test cache & message broker |
| `qdrant-test` | 6335 | Test vector database |

## 🚀 Quick Start Guide

### 1. Chuẩn bị Environment

```bash
# Đảm bảo .env file tồn tại
cp .env.example .env

# Chỉnh sửa OPENAI_API_KEY trong .env
nano .env
```

### 2. Chạy Full Test Suite

**Windows (PowerShell):**
```powershell
# Chạy tất cả tests
.\tests\run_docker_tests.ps1 -Command full

# Hoặc sử dụng Makefile
make test
```

**Linux/Mac (Bash):**
```bash
# Chạy tất cả tests
./tests/run_docker_tests.sh full

# Hoặc sử dụng Makefile
make test
```

### 3. Chạy Tests Specific

```bash
# Smoke tests (basic functionality)
make test-smoke

# API endpoint tests
make test-api

# Database integration tests
make test-db

# WebSocket tests
make test-ws

# Integration tests
make test-integration
```

## 🧪 Test Categories

### 1. Smoke Tests (`make test-smoke`)
**Mục đích:** Kiểm tra basic functionality
**Thời gian:** ~2-3 phút

- Health check endpoints
- Root endpoint response
- API documentation availability
- Basic service connectivity

### 2. API Tests (`make test-api`)
**Mục đích:** Test tất cả API endpoints
**Thời gian:** ~5-10 phút

- Conversation CRUD operations
- Message sending/receiving
- RAG query processing
- Document search functionality
- Error handling & validation
- Performance checks

### 3. Database Tests (`make test-db`)
**Mục đích:** Test database integrations
**Thời gian:** ~3-5 phút

- MongoDB CRUD operations
- Redis cache functionality
- Qdrant vector operations
- Cross-database consistency
- Transaction simulation

### 4. WebSocket Tests (`make test-ws`)
**Mục đích:** Test real-time communication
**Thời gian:** ~3-5 phút

- WebSocket connections
- Real-time messaging
- Multi-user scenarios
- Error handling
- Performance tests

### 5. Integration Tests (`make test-integration`)
**Mục đích:** Test complete workflows
**Thời gian:** ~10-15 phút

- End-to-end conversation flows
- Celery task processing
- RAG system integration
- Multi-service interaction

## 🔧 Test Configuration

### Environment Variables

Test environment sử dụng separate configuration:

```env
# Test API URLs
API_BASE_URL=http://backend-api-test:8000
API_TEST_URL=http://backend-api-test:8000/api
WS_TEST_URL=ws://backend-api-test:8000/ws

# Test Database URLs
MONGO_TEST_URL=mongodb://admin:testpass123@mongodb-test:27017/legaldb_test?authSource=admin
REDIS_TEST_URL=redis://redis-test:6379
QDRANT_TEST_URL=http://qdrant-test:6333

# Test Settings
TEST_TIMEOUT=300
MAX_RETRIES=3
PARALLEL_TESTS=false
```

### Test Data

Test database được populate với sample data:

- **Users:** 3 test users
- **Documents:** 4 legal documents với Vietnamese content
- **Conversations:** Sample conversations
- **Messages:** Test messages với different roles

## 📊 Test Reports

### Location
- **Results:** `./tests/results/`
- **Logs:** `./tests/logs/`
- **Reports:** HTML và JSON formats

### Files Generated
```
tests/results/
├── test_summary.md          # Overall summary
├── smoke_test_results.xml   # JUnit XML format
├── api_report.html         # HTML report
├── api_report.json         # JSON report
├── database_report.html    # Database test report
└── websocket_report.html   # WebSocket test report
```

### Reading Reports

**HTML Reports:** Mở trong browser để xem detailed results
```bash
# Windows
start tests/results/api_report.html

# Linux/Mac
open tests/results/api_report.html
```

**JSON Reports:** Programmatic access cho CI/CD
```bash
# View test summary
cat tests/results/api_report.json | jq '.summary'
```

## 🐛 Troubleshooting

### Common Issues

**1. Test Infrastructure Won't Start**
```bash
# Check Docker status
docker ps
docker-compose -f docker-compose.test.yml ps

# View startup logs
make test-logs
```

**2. Tests Failing Due to Timeouts**
```bash
# Increase timeout in pytest.ini
timeout = 600  # 10 minutes

# Or set environment variable
export TEST_TIMEOUT=600
```

**3. Database Connection Errors**
```bash
# Check database health
make test-health

# Reset test databases
make test-clean
make test-up
```

**4. OpenAI API Errors**
```bash
# Verify API key in .env
grep OPENAI_API_KEY .env

# Test API key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### Debug Mode

Chạy tests với debug information:

```bash
# Verbose output
pytest tests/ -v -s --tb=long

# With logging
pytest tests/ --log-cli-level=DEBUG

# Stop on first failure
pytest tests/ -x
```

### Manual Container Access

```bash
# Access test runner container
docker-compose -f docker-compose.test.yml exec test-runner bash

# Access test API container
docker-compose -f docker-compose.test.yml exec backend-api-test bash

# Check test database
docker-compose -f docker-compose.test.yml exec mongodb-test mongosh
```

## 📈 Performance Benchmarks

### Expected Performance

| Test Category | Duration | Acceptable Range |
|---------------|----------|------------------|
| Smoke Tests | 2-3 min | 1-5 min |
| API Tests | 5-10 min | 3-15 min |
| Database Tests | 3-5 min | 2-8 min |
| WebSocket Tests | 3-5 min | 2-8 min |
| Integration Tests | 10-15 min | 8-20 min |
| **Total Full Suite** | **25-35 min** | **20-45 min** |

### Performance Issues

Nếu tests chạy chậm hơn expected:

1. **Check system resources:**
   ```bash
   docker stats
   ```

2. **Reduce parallel tests:**
   ```bash
   export PARALLEL_TESTS=false
   ```

3. **Increase container resources:**
   ```yaml
   # In docker-compose.test.yml
   deploy:
     resources:
       limits:
         memory: 1G
         cpus: '1.0'
   ```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Create .env file
        run: |
          echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" > .env
          cat .env.example >> .env
      
      - name: Run Docker Tests
        run: |
          chmod +x tests/run_docker_tests.sh
          ./tests/run_docker_tests.sh full
      
      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: tests/results/
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                script {
                    sh 'make test'
                }
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'tests/results',
                        reportFiles: 'api_report.html',
                        reportName: 'API Test Report'
                    ])
                }
            }
        }
    }
}
```

## 🎯 Best Practices

### 1. Test Organization
- Separate test categories với markers
- Use fixtures cho data setup
- Clean test isolation

### 2. Data Management
- Use test-specific databases
- Reset data between test runs
- Avoid hardcoded test data

### 3. Error Handling
- Expect và handle service unavailability
- Use retries cho flaky tests
- Proper timeout management

### 4. Maintainability
- Keep tests simple và focused
- Use page object pattern cho API tests
- Document test dependencies

## 📞 Support & Contributing

- **Documentation:** `/docs` trong repository
- **Test Results:** `./tests/results/`
- **Issues:** GitHub Issues
- **Logs:** `./tests/logs/`

### Adding New Tests

1. **Create test file:** `tests/test_new_feature.py`
2. **Add markers:** `@pytest.mark.new_feature`
3. **Update pytest.ini:** Add marker description
4. **Add to CI:** Update test scripts

---

**💡 Pro Tip:** Sử dụng `make test-smoke` trước khi commit để đảm bảo basic functionality hoạt động.
