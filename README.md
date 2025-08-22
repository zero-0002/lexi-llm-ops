# LexiOps - Intelligent Legal AI Platform

**Advanced AI-powered legal information retrieval and DevOps automation platform with RAG (Retrieval-Augmented Generation) and MCP (Model Context Protocol)**

[![GitHub Stars](https://img.shields.io/github/stars/tinhnguyen0110/LexiOps?style=for-the-badge&logo=github&logoColor=white&color=yellow)](https://github.com/tinhnguyen0110/LexiOps/stargazers) [![GitHub Forks](https://img.shields.io/github/forks/tinhnguyen0110/LexiOps?style=for-the-badge&logo=github&logoColor=white&color=blue)](https://github.com/tinhnguyen0110/LexiOps/network/members) [![Live Demo](https://img.shields.io/badge/Live_Demo-joblytics.io.vn-brightgreen?style=for-the-badge&logo=react)](http://joblytics.io.vn) [![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?style=for-the-badge&logo=kubernetes)](https://kubernetes.io) [![License](https://img.shields.io/github/license/tinhnguyen0110/LexiOps?style=for-the-badge&logo=opensourceinitiative&logoColor=white&color=green)](https://github.com/tinhnguyen0110/LexiOps/blob/main/LICENSE) [![Profile Views](https://komarev.com/ghpvc/?username=tinhnguyen0110&color=brightgreen&style=for-the-badge&label=PROFILE+VIEWS)](https://github.com/tinhnguyen0110)

## 📊 **[Live Project Tracker - Architecture, Kanban & Development Progress →](https://successful-vanadium-dde.notion.site/flow-24e2418089ee80a6b652d76b53e2abcb)**

---

## 🏗️ System Architecture

<div align="center">

#### 📊 Complete System Overview
<img src="./docs/lexiops.svg" alt="LexiOps Complete System Architecture" width="100%"/>

#### 🤖 DevOps Copilot Architecture  
<img src="./lexiops-copilot/docs/agentic.svg" alt="LexiOps DevOps Copilot" width="100%"/>

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [🛠️ Development](#️-development)
- [🐳 Deployment](#-deployment)
- [🧪 Testing](#-testing)
- [🔧 Configuration](#-configuration)
- [📊 Monitoring](#-monitoring)

---

## 🎯 Overview

**LexiOps** is a cutting-edge dual-platform system that revolutionizes both legal information access and DevOps automation through advanced AI technologies. The platform combines RAG (Retrieval-Augmented Generation) with MCP (Model Context Protocol) to deliver precise legal insights and intelligent Kubernetes cluster management.

### 🌟 Dual Platform Architecture

#### 🏛️ **Legal AI Platform**
- **Intelligent RAG System**: Advanced retrieval-augmented generation for legal document analysis
- **Real-time Legal Chat**: WebSocket-powered instant legal assistance with streaming responses
- **Multi-Source Integration**: Legal databases, web search, and knowledge APIs
- **Vietnamese Legal Focus**: Specialized for Vietnamese legal corpus with 180k+ documents
- **Vector Search**: Semantic search with Qdrant database and OpenAI embeddings

#### 🤖 **DevOps AI Copilot** 
- **Agentic Workflow System**: GPT-4 powered automation for Kubernetes operations
- **MCP Integration**: Model Context Protocol with 51+ dynamic Kubernetes tools
- **3-Tier Architecture**: FastAPI + MCP Client + Tools Server
- **Intelligent Decision Making**: LangGraph-based workflow orchestration
- **Cluster Management**: AI-powered infrastructure automation

### 🚀 Key Innovations
- **Dual AI Engines**: Legal RAG + DevOps Automation in unified platform
- **Real-time Processing**: Sub-second response times with intelligent caching
- **Microservices Design**: Scalable, containerized architecture with specialized workers
- **Production Ready**: Enterprise-grade security, monitoring, and deployment
- **Open Source**: MIT licensed with comprehensive documentation

### 🏷️ Technology Stack

**AI & Machine Learning:**
![OpenAI](https://img.shields.io/badge/OpenAI_GPT--4-412991.svg?style=for-the-badge&logo=OpenAI&logoColor=white)
![RAG](https://img.shields.io/badge/RAG_Pipeline-00D4AA.svg?style=for-the-badge&logo=Databricks&logoColor=white)
![AI Agent](https://img.shields.io/badge/AI_Agent-FF6B6B.svg?style=for-the-badge&logo=Robot&logoColor=white)
![MCP Tools](https://img.shields.io/badge/MCP_Tools-326CE5.svg?style=for-the-badge&logo=Tools&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C1C1C.svg?style=for-the-badge&logo=Graph&logoColor=white)

**Backend & Infrastructure:**
![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=for-the-badge&logo=FastAPI&logoColor=white)
![React](https://img.shields.io/badge/React_18-61DAFB.svg?style=for-the-badge&logo=React&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248.svg?style=for-the-badge&logo=MongoDB&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D.svg?style=for-the-badge&logo=Redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED.svg?style=for-the-badge&logo=Docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5.svg?style=for-the-badge&logo=Kubernetes&logoColor=white)

---

## 🚀 Quick Start

### Prerequisites
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **OpenAI API Key** for AI functionality

### Installation

```bash
# 1. Clone repository
git clone https://github.com/tinhnguyen0110/LexiOps.git
cd LexiOps

# 2. Setup environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 3. Start system
make quick-start
# OR: docker-compose up -d

# 4. Verify health
make health-check
```

### Access Points
| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main chat interface |
| **API Docs** | http://localhost:8000/docs | Backend documentation |
| **Monitor** | http://localhost:5555 | Celery task monitor |

---

## 📁 Project Structure

```
LexiOps/
├── 📁 src/                           # Main legal retrieval system
│   ├── 📁 app/                       # 🚀 FastAPI Backend
│   │   ├── brain.py                  # 🧠 AI reasoning engine
│   │   ├── main.py                   # 🌐 API server entry
│   │   ├── celery_config.py          # 🔄 Task queue config
│   │   ├── 📁 api/                   # API endpoints
│   │   ├── 📁 config/                # Configuration
│   │   └── 📁 utils/                 # Utilities
│   │
│   ├── 📁 legal-chatbot-fe/          # ⚛️ React Frontend
│   │   ├── src/App.jsx               # Main component
│   │   ├── 📁 components/            # UI components
│   │   └── 📁 hooks/                 # Custom hooks
│   │
│   └── 📁 streamlit-fe/              # 🎯 Alternative frontend
│
├── 📁 lexiops-copilot/               # 🤖 DevOps AI Copilot System
│   ├── 📁 agent/                     # Core AI agent
│   │   ├── main.py                   # FastAPI copilot server
│   │   ├── graph.py                  # LangGraph workflow
│   │   ├── mcp_server.py             # MCP server configuration
│   │   └── 📁 nodes/                 # AI processing nodes
│   ├── 📁 k8s/                       # Kubernetes deployments
│   │   └── mcp-k8s-deployment.yaml   # MCP tools server
│   ├── 📁 scripts/                   # Deployment scripts
│   │   ├── run.sh                    # Start copilot system
│   │   └── deploy-3tier.sh           # 3-tier deployment
│   ├── 📁 test/                      # Integration tests
│   ├── 📁 docs/                      # Architecture docs
│   └── 📁 notebooks/                 # Development notebooks
│
├── 📁 scripts/                       # 🔧 Deployment scripts
│   ├── build-docker.sh               # Docker builder
│   ├── system-check.sh               # Health validator
│   └── deploy-pipeline.sh            # Deployment automation
│
├── 📁 tests/                         # 🧪 Test suite
│   ├── run_docker_tests.sh           # Test runner
│   ├── DOCKER_TESTING_GUIDE.md       # Testing docs
│   └── test_*.py                     # Test files
│
├── 📁 helm/                          # ☸️ Kubernetes deployment
│   ├── helmfile.yaml                 # Helm orchestration
│   ├── 📁 charts/                    # Custom charts
│   └── 📁 values/                    # Environment configs
│
├── 📁 data/                          # 📚 Legal corpus
│   ├── 📁 data_corpus/               # 180k+ legal documents
│   ├── 📁 mongo_data/                # Database storage
│   └── 📁 qdrant_storage/            # Vector database
│
├── 📁 deployment/                    # 🚀 Deployment configs
├── 📁 terraform/                     # 🌩️ Infrastructure as Code
├── 📁 reports/                       # 📈 System reports
├── docker-compose.yml               # 🐳 Container orchestration
├── Makefile                          # 🛠️ Commands
└── README.md                         # 📖 Documentation
```

### Core Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **brain.py** | AI reasoning engine | Query analysis, tool selection, response generation |
| **legal_chat.py** | WebSocket API | Real-time chat, conversation management |
| **App.jsx** | Frontend app | Chat interface, message handling |
| **useChat.js** | Chat logic | WebSocket management, state handling |
| **Copilot System** | DevOps automation | K8s management, AI-powered operations |

---

## 🛠️ Development

### Backend Development
```bash
# Docker development (recommended)
make dev-up

# Local development
cd src/app
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Development
```bash
cd src/legal-chatbot-fe
npm install
npm run dev          # Development server
npm run build        # Production build
```

### DevOps Copilot
```bash
# Start copilot system
cd lexiops-copilot
./scripts/run.sh

# Test copilot functionality
python test/test_fastapi_mcp.py
```

### Environment Setup
```bash
# Required in .env file
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URL=mongodb://admin:password123@localhost:27017/legaldb?authSource=admin
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
```

---

## 🐳 Deployment

### Docker Deployment
```bash
# Local deployment
docker-compose up --build -d

# Production deployment
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Scale workers
docker-compose up --scale celery-worker-rag=3 -d
```

### Kubernetes Deployment
```bash
# Deploy with Helm
helmfile -e development apply    # Development
helmfile -e production apply     # Production

# Deploy copilot MCP server
kubectl apply -f lexiops-copilot/k8s/mcp-k8s-deployment.yaml

# Monitor deployment
kubectl get pods -n legal-retrieval-prod
```

### Available Commands
```bash
make quick-start     # Quick setup and start
make health-check    # System health verification
make test            # Run test suite
make clean-all       # Complete cleanup
make help            # Show all commands
```

---

## 🧪 Testing

### Test Categories
- **Smoke Tests**: Quick validation (2-3 minutes)
- **API Tests**: Endpoint validation
- **Integration Tests**: Service interaction
- **Performance Tests**: Load and stress testing

### Running Tests
```bash
# Quick smoke tests
make test-smoke

# Full test suite
make test

# Docker-isolated testing
./tests/run_docker_tests.sh --command test --test-type smoke

# Copilot system tests
cd lexiops-copilot
python test/test_fastapi_mcp.py
```

For detailed testing: [`tests/DOCKER_TESTING_GUIDE.md`](tests/DOCKER_TESTING_GUIDE.md)

---

## 🔧 Configuration

### Core Settings
```bash
# API Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
DEBUG=true

# AI Configuration
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_SIZE=1536

# Worker Configuration
CELERY_CONCURRENCY=2
CELERY_BROKER_URL=redis://localhost:6379/3
```

### Service Scaling
The system supports horizontal scaling:
- **RAG Workers**: CPU-intensive AI processing
- **Embed Workers**: Vector embedding generation
- **Retrieval Workers**: Web search and content retrieval

### System Architecture

#### **Legal Retrieval System**
- **Frontend**: React chat interface (port 3000)
- **Backend**: FastAPI with WebSocket (port 8000) 
- **Workers**: Celery for RAG processing
- **Databases**: MongoDB + Redis + Qdrant

#### **DevOps Copilot (3-Tier Architecture)**
- **Tier 1**: FastAPI main server (lexiops-copilot/agent/main.py)
- **Tier 2**: MCP client adapter (langchain_mcp_adapters)
- **Tier 3**: MCP tools server (Kubernetes deployment)

---

## 📊 Monitoring

### Dashboards
- **Celery Monitor**: http://localhost:5555 - Task monitoring
- **API Health**: http://localhost:8000/health - System status
- **Qdrant Dashboard**: http://localhost:6333/dashboard - Vector DB

### Performance Metrics
- **Response Time**: < 2s simple queries, < 5s complex queries
- **Throughput**: 100+ concurrent users, 50+ RPS
- **Resource Usage**: 2-4GB RAM, 2-4 CPU cores

### Troubleshooting
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend-api

# System health check
./scripts/system-check.sh
```

---

## 🏆 Production Ready

**LexiOps** includes enterprise-grade features:

✅ **Legal AI System** - RAG-powered legal information retrieval  
✅ **DevOps Copilot** - AI-powered Kubernetes cluster management  
✅ **Scalable Architecture** - Microservices with auto-scaling  
✅ **Real-time Chat** - WebSocket-powered interface  
✅ **Comprehensive Testing** - Full test coverage  
✅ **DevOps Ready** - Docker, Kubernetes, CI/CD  
✅ **Performance Optimized** - Sub-second response times  

### Additional Resources
- 📈 **Reports**: [`reports/OPTIMIZATION_REPORT.md`](reports/OPTIMIZATION_REPORT.md)
- 🚀 **Deployment**: [`deployment/`](deployment/) configs
- 📚 **Documentation**: [`docs/`](docs/) guides
- 🤖 **Copilot Docs**: [`lexiops-copilot/docs`](lexiops-copilot/docs/)

---

**LexiOps - Transforming Legal Information Access with AI** 🏛️🤖

*Built with ❤️ using FastAPI, React, OpenAI, Docker, and modern DevOps practices*