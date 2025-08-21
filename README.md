# LexiOps - AI-Powered Legal Retrieval System

**Intelligent legal information retrieval system powered by AI and RAG (Retrieval-Augmented Generation)**

[![Live Demo](https://img.shields.io/badge/Live_Demo-joblytics.io.vn-brightgreen?style=for-the-badge&logo=react)](http://joblytics.io.vn)
[![Docker](https://img.shields.io/badge/Docker-Compose_Ready-2496ED?style=for-the-badge&logo=docker)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Deployment_Ready-326CE5?style=for-the-badge&logo=kubernetes)](https://kubernetes.io)

---

## 📋 Table of Contents

- [🎯 Project Overview](#-project-overview)
- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [🛠️ Development](#️-development)
- [🐳 Docker Deployment](#-docker-deployment)
- [☸️ Kubernetes Deployment](#️-kubernetes-deployment)
- [🧪 Testing](#-testing)
- [📊 System Architecture](#-system-architecture-deep-dive)
- [🔧 Configuration](#-configuration)
- [📚 Data Management](#-data-management)
- [🔍 Monitoring & Debugging](#-monitoring--debugging)
- [🛡️ Security & Performance](#️-security--performance)
- [🤝 Contributing](#-contributing)

---

## 🎯 Project Overview

**LexiOps** is a modern AI-powered legal information retrieval system that combines cutting-edge technologies to provide accurate, contextual, and up-to-date legal information. The system leverages Retrieval-Augmented Generation (RAG) to deliver precise answers to legal queries with source verification.

### 🏗️ System Architecture

<img src="./docs/lexiops.svg" alt="System Architecture"/>

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│    Frontend React   │    │   FastAPI Backend   │    │   AI Processing     │
│   - Chat Interface  │◄──►│   - WebSocket API   │◄──►│   - OpenAI GPT      │
│   - Real-time UI    │    │   - REST Endpoints  │    │   - RAG Pipeline    │
│   - Conversation    │    │   - Authentication  │    │   - Query Analysis  │
│   Port: 3000        │    │   Port: 8000        │    │   - Tool Selection  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Load Balancer     │    │   Message Queue     │    │   Vector Database   │
│   - Nginx Proxy     │    │   - Redis Broker    │    │   - Qdrant Storage  │
│   - SSL Termination │    │   - Task Queue      │    │   - Semantic Search │
│                     │    │   - Caching         │    │   - Embeddings      │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Celery Workers    │    │   Document Store    │    │   External APIs     │
│   - RAG Processing  │◄──►│   - MongoDB         │◄──►│   - Web Search      │
│   - Embedding Gen   │    │   - Conversations   │    │   - Legal DBs       │
│   - Web Retrieval   │    │   - User Sessions   │    │   - Knowledge APIs  │
│   - Link Processing │    │   - Analysis Cache  │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### 🌟 Key Features

#### 🤖 AI-Powered Legal Assistant
- **Intelligent Chatbot**: Uses OpenAI GPT models for natural language understanding
- **RAG System**: Retrieval-Augmented Generation for high accuracy responses
- **Semantic Search**: Advanced vector search with Qdrant database
- **Multi-Tool Integration**: Combines web search and legal database retrieval
- **Query Analysis**: Intelligent query rewriting and context understanding
- **Streaming Responses**: Real-time response generation with progress indicators

#### 💬 Modern User Interface
- **Responsive Chat Interface**: Mobile-first design with desktop optimization
- **Real-time Messaging**: WebSocket-powered instant communication
- **Conversation Management**: Persistent chat history with search and organization
- **Rich Content Display**: Markdown support with syntax highlighting
- **Typing Indicators**: Visual feedback during AI processing
- **Progressive Disclosure**: Step-by-step AI reasoning visualization

#### 🔍 Advanced Search Capabilities
- **Multi-Source Integration**: Web search + Legal database + Knowledge APIs
- **Context-Aware Retrieval**: Understanding query intent and legal context
- **Source Verification**: Citations and references for all information
- **Confidence Scoring**: Reliability indicators for search results
- **Real-time Updates**: Fresh information from multiple sources

#### ⚡ Performance & Scalability
- **Asynchronous Processing**: Non-blocking operations with Celery workers
- **Horizontal Scaling**: Multiple worker types for different tasks
- **Intelligent Caching**: Redis-powered response and data caching
- **Load Balancing**: Distributed processing across worker pools
- **Resource Optimization**: Efficient memory and CPU usage patterns

### 🏷️ Technology Stack

**Backend Technologies:**
![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=flat-square&logo=FastAPI&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.8+-3776AB.svg?style=flat-square&logo=Python&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37B24D.svg?style=flat-square&logo=Celery&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-010101.svg?style=flat-square&logo=Socket.io&logoColor=white)

**Frontend Technologies:**
![React](https://img.shields.io/badge/React_18-61DAFB.svg?style=flat-square&logo=React&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF.svg?style=flat-square&logo=Vite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript_ES6+-F7DF1E.svg?style=flat-square&logo=JavaScript&logoColor=black)
![Axios](https://img.shields.io/badge/Axios-5A29E4.svg?style=flat-square&logo=Axios&logoColor=white)

**Databases & Storage:**
![MongoDB](https://img.shields.io/badge/MongoDB-47A248.svg?style=flat-square&logo=MongoDB&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D.svg?style=flat-square&logo=Redis&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-FF6B6B.svg?style=flat-square&logo=Qdrant&logoColor=white)

**AI & ML:**
![OpenAI](https://img.shields.io/badge/OpenAI_GPT-412991.svg?style=flat-square&logo=OpenAI&logoColor=white)
![Vector DB](https://img.shields.io/badge/Vector_Embeddings-FF6B6B.svg?style=flat-square&logo=TensorFlow&logoColor=white)
![RAG](https://img.shields.io/badge/RAG_Pipeline-00D4AA.svg?style=flat-square&logo=Databricks&logoColor=white)

**DevOps & Infrastructure:**
![Docker](https://img.shields.io/badge/Docker-2496ED.svg?style=flat-square&logo=Docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5.svg?style=flat-square&logo=Kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689.svg?style=flat-square&logo=Helm&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-844FBA.svg?style=flat-square&logo=Terraform&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF.svg?style=flat-square&logo=GitHub-Actions&logoColor=white)

---

## 🚀 Quick Start

### Prerequisites
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Git** for version control
- **Make** (optional, for convenience commands)
- **Node.js** 16+ (for local frontend development)
- **Python** 3.8+ (for local backend development)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/tinhnguyen0110/LexiOps.git
cd LexiOps

# 2. Make scripts executable (Linux/Mac)
find scripts tests -name "*.sh" -exec chmod +x {} \;

# 3. Quick start with make (recommended)
make quick-start

# OR manual startup
./scripts/build-docker.sh
docker-compose up -d

# 4. Check system health
make health-check
```

### Access Points
Once the system is running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend Chat** | http://localhost:3000 | Main chat interface |
| **Backend API** | http://localhost:8000/docs | FastAPI documentation |
| **Celery Monitor** | http://localhost:5555 | Task monitoring dashboard |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | Vector database UI |
| **System Health** | http://localhost:8000/health | System status endpoint |

---

## 📁 Project Structure

### Core Components

```
LexiOps/
├── 📁 src/                           # Source code
│   ├── 📁 app/                       # Backend FastAPI application
│   │   ├── brain.py                  # 🧠 AI reasoning engine
│   │   ├── main.py                   # 🚀 FastAPI application entry
│   │   ├── celery_config.py          # 🔄 Celery configuration
│   │   ├── 📁 api/                   # API endpoints
│   │   │   ├── legal_chat.py         # 💬 Chat WebSocket API
│   │   │   ├── rag.py                # 🔍 RAG processing endpoint
│   │   │   ├── web_search.py         # 🌐 Web search API
│   │   │   └── system.py             # ⚙️ System monitoring
│   │   ├── 📁 config/                # Configuration management
│   │   │   ├── settings.py           # 🎛️ Environment settings
│   │   │   ├── database.py           # 🗄️ Database connections
│   │   │   └── api_client.py         # 🔌 API client setup
│   │   └── 📁 utils/                 # Utility modules
│   │       ├── logging_config.py     # 📝 Structured logging
│   │       └── utils_essential.py    # 🛠️ Helper functions
│   │
│   ├── 📁 legal-chatbot-fe/          # Frontend React application
│   │   ├── src/
│   │   │   ├── App.jsx               # 🎨 Main application component
│   │   │   ├── 📁 components/        # React components
│   │   │   │   ├── ChatMessage.jsx   # 💭 Message display component
│   │   │   │   ├── ChatInput.jsx     # ⌨️ Message input component
│   │   │   │   ├── ConversationSidebar.jsx # 📋 Chat history sidebar
│   │   │   │   ├── AnalysisMessage.jsx     # 📊 AI analysis display
│   │   │   │   ├── ThinkingMessage.jsx     # 🤔 AI thinking indicator
│   │   │   │   └── Toast.jsx         # 🔔 Notification system
│   │   │   └── 📁 hooks/             # Custom React hooks
│   │   │       └── useChat.js        # 💬 Chat state management
│   │   ├── package.json              # 📦 Frontend dependencies
│   │   └── vite.config.js            # ⚡ Vite configuration
│   │
│   └── 📁 streamlit-fe/              # Alternative Streamlit frontend
│       └── app.py                    # 🎯 Streamlit application
│
├── 📁 scripts/                       # Deployment & utility scripts
│   ├── build-docker.sh              # 🐳 Docker image builder
│   ├── system-check.sh              # ✅ System health validator
│   ├── setup.sh                     # 🔧 Initial system setup
│   ├── deploy-pipeline.sh           # 🚀 Deployment orchestrator
│   └── 📁 build-docker/             # Docker build utilities
│
├── 📁 tests/                         # Comprehensive test suite
│   ├── run_docker_tests.sh          # 🧪 Docker test runner
│   ├── DOCKER_TESTING_GUIDE.md      # 📖 Testing documentation
│   ├── test_api_comprehensive.py    # 🔄 API integration tests
│   ├── test_database.py             # 🗄️ Database tests
│   ├── test_websocket.py            # 🌐 WebSocket tests
│   └── 📁 integration/              # End-to-end tests
│
├── 📁 helm/                          # Kubernetes deployment
│   ├── helmfile.yaml                # 📊 Helm orchestration config
│   ├── 📁 charts/                   # Custom Helm charts
│   ├── 📁 values/                   # Environment-specific values
│   └── 📁 environments/             # Multi-environment configs
│
├── 📁 deployment/                    # Deployment configurations
│   ├── deploy_legal_chatbot_k8s.sh  # ☸️ Kubernetes deployment
│   └── step_deploy_aws.txt          # 🌩️ AWS deployment guide
│
├── 📁 data/                          # Legal corpus and datasets
│   ├── 📁 data_corpus/              # Legal document corpus
│   │   ├── corpus.csv               # 📚 180k+ legal document segments
│   │   ├── train.csv                # 🎓 Training questions with context
│   │   ├── public_test.csv          # 🧪 8k+ test questions
│   │   └── readme.txt               # 📝 Data format documentation
│   ├── 📁 mongo_data/               # MongoDB persistence
│   └── 📁 qdrant_storage/           # Vector database storage
│
├── 📁 docs/                          # Project documentation
│   ├── flow.md                      # 🔄 System workflow documentation
│   ├── LEXIOPS_System.svg           # 🏗️ System architecture diagram
│   └── 📁 guides/                   # User and developer guides
│
├── 📁 reports/                       # System analysis reports
│   ├── OPTIMIZATION_REPORT.md       # 📈 Performance optimization
│   ├── DEPLOYMENT_SUCCESS_REPORT.md # ✅ Deployment verification
│   └── API_TEST_REPORT.md           # 🧪 API testing results
│
├── 📁 terraform/                     # Infrastructure as Code
│   ├── main.tf                      # 🌩️ AWS infrastructure definition
│   ├── variables.tf                 # 🎛️ Terraform variables
│   └── outputs.tf                   # 📤 Infrastructure outputs
│
├── docker-compose.yml               # 🐳 Development environment
├── docker-compose.dev.yml           # 🔧 Development-specific config
├── Makefile                         # 🛠️ Convenience commands
├── .env.example                     # 🔒 Environment template
└── README.md                        # 📖 This documentation
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/api/chat` | WebSocket | Real-time chat communication |
| `/api/rag/process` | POST | RAG processing endpoint |
| `/api/search/web` | POST | Web search functionality |
| `/api/conversations` | GET/POST | Conversation management |
| `/api/system/status` | GET | System status and metrics |

### Frontend Components

| Component | Purpose | Features |
|-----------|---------|----------|
| `App.jsx` | Main application | Routing, state management, responsive layout |
| `ChatMessage.jsx` | Message display | Markdown rendering, message types, timestamps |
| `ChatInput.jsx` | User input | Auto-resize, send shortcuts, file upload |
| `ConversationSidebar.jsx` | Chat history | Search, organize, delete conversations |
| `AnalysisMessage.jsx` | AI analysis | Step-by-step reasoning, tool usage display |
| `ThinkingMessage.jsx` | Loading states | Animated thinking indicators, progress bars |
| `useChat.js` | Chat logic | WebSocket management, message handling |

---

## 🛠️ Development

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/tinhnguyen0110/LexiOps.git
cd LexiOps

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Backend Development

```bash
# Option 1: Docker development (recommended)
make dev-up

# Option 2: Local development
cd src/app
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run specific workers
celery -A main.celery worker --loglevel=info -Q rag_queue
celery -A main.celery worker --loglevel=info -Q embed_queue
celery -A main.celery worker --loglevel=info -Q retrieval_queue
```

### Frontend Development

```bash
# React development server
cd src/legal-chatbot-fe
npm install
npm run dev

# Build for production
npm run build
npm run preview
```

### Environment Configuration

Create `.env` file with required configuration:

```bash
# Core API Configuration
OPENAI_API_KEY=your_openai_api_key_here
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
DEBUG=true

# Database Configuration
MONGODB_URL=mongodb://admin:password123@localhost:27017/legaldb?authSource=admin
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333

# AI Configuration
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_SIZE=1536

# Worker Configuration
CELERY_BROKER_URL=redis://localhost:6379/3
CELERY_RESULT_BACKEND=redis://localhost:6379/4
CELERY_CONCURRENCY=2

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_ENVIRONMENT=development
```

---

## 🐳 Docker Deployment

### Local Development

```bash
# Build and start all services
docker-compose up --build -d

# Scale workers based on load
docker-compose up --scale celery-worker-rag=3 -d
docker-compose up --scale celery-worker-embed=2 -d
docker-compose up --scale celery-worker-retrieval=2 -d

# View service status
docker-compose ps

# View logs from specific services
docker-compose logs -f backend-api
docker-compose logs -f celery-worker-rag
```

### Production Deployment

```bash
# Build production images
./scripts/build-docker.sh --tag production

# Deploy with production configuration
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Health check and system validation
./scripts/system-check.sh
```

### Service Scaling

The system supports horizontal scaling for different worker types:

```bash
# Scale RAG processing workers (CPU intensive)
docker-compose up --scale celery-worker-rag=5 -d

# Scale embedding workers (GPU/CPU intensive)
docker-compose up --scale celery-worker-embed=3 -d

# Scale web retrieval workers (I/O intensive)
docker-compose up --scale celery-worker-retrieval=4 -d

# Scale link processing workers
docker-compose up --scale celery-worker-link=2 -d
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

```bash
# Install required tools
kubectl version --client
helm version
helmfile version

# Install helm plugins
helm plugin install https://github.com/databus23/helm-diff
```

### Helm Deployment

```bash
# Deploy to development environment
helmfile -e development apply

# Deploy to production
helmfile -e production apply

# Update specific services
helmfile -l app=backend-api apply
helmfile -l app=celery-worker apply

# Monitor deployment status
kubectl get pods -n legal-retrieval-prod
kubectl get services -n legal-retrieval-prod
```

### Monitoring

```bash
# Check pod status
kubectl get pods -n legal-retrieval-prod

# View pod logs
kubectl logs -f deployment/legal-backend-api -n legal-retrieval-prod

# Port forward for local access
kubectl port-forward service/legal-backend-api 8000:8000 -n legal-retrieval-prod
```

---

## 🧪 Testing

### Test Categories

The system includes comprehensive testing at multiple levels:

#### **Unit Tests**
- Component and function testing
- Isolated module testing
- Mock and stub validation

#### **Integration Tests**
- Service integration validation
- Database connectivity testing
- API endpoint validation

#### **E2E Tests**
- Complete user workflow testing
- Browser automation testing
- Cross-component interaction testing

#### **Performance Tests**
- Load testing and benchmarking
- Stress testing under high load
- Memory and CPU profiling

### Running Tests

```bash
# Quick smoke tests (2-3 minutes)
make test-smoke

# Full test suite
make test

# Specific test categories
make test-api          # API endpoint tests
make test-db           # Database tests
make test-ws           # WebSocket tests
make test-integration  # Integration tests
```

### Docker Testing

```bash
# Test with complete Docker isolation
./tests/run_docker_tests.sh --command test --test-type smoke

# Full test suite with Docker
./tests/run_docker_tests.sh --command full

# Specific test types
./tests/run_docker_tests.sh --command test --test-type api
./tests/run_docker_tests.sh --command test --test-type integration
./tests/run_docker_tests.sh --command test --test-type performance
```

For detailed testing documentation, see: [`tests/DOCKER_TESTING_GUIDE.md`](tests/DOCKER_TESTING_GUIDE.md)

---

## 📊 System Architecture Deep Dive

### Microservices Overview

#### **Core Services**

1. **backend-api**: 
   - FastAPI server with JWT authentication
   - WebSocket support for real-time chat
   - REST API endpoints for system management
   - Request routing and input validation
   - Structured logging and monitoring

2. **celery-worker-rag**: 
   - RAG processing engine with OpenAI integration
   - Document retrieval and context ranking
   - Query analysis and rewriting
   - Response generation and streaming

3. **celery-worker-embed**: 
   - Document embedding generation
   - Vector database operations with Qdrant
   - Similarity search processing
   - Batch embedding operations

4. **celery-worker-retrieval**: 
   - Web search query processing
   - Content retrieval from multiple sources
   - Result aggregation and filtering
   - Source validation and ranking

5. **celery-worker-link**: 
   - Web scraping capabilities
   - Link extraction and validation
   - External content processing
   - Content sanitization and parsing

6. **celery-flower**: 
   - Real-time task monitoring dashboard
   - Worker health and performance metrics
   - Queue management and monitoring
   - Task retry and failure handling

### AI Components

#### **Brain System** ([`src/app/brain.py`](src/app/brain.py))
The core AI reasoning engine that orchestrates the entire AI pipeline:

- **Query Analysis**: Understanding user intent and context
- **Tool Selection**: Deciding which tools to use (web_search, laws_retrieval)
- **Response Generation**: Creating contextual, accurate responses
- **Streaming Support**: Real-time response delivery
- **Error Handling**: Graceful failure recovery

#### **Chat Interface** ([`src/legal-chatbot-fe/src/hooks/useChat.js`](src/legal-chatbot-fe/src/hooks/useChat.js))
Advanced chat management with real-time features:

- **WebSocket Integration**: Real-time bidirectional communication
- **Message State Management**: Complex message state handling
- **Conversation Persistence**: Chat history management
- **Streaming Response Handling**: Real-time response updates
- **Tool Execution Visualization**: Step-by-step AI process display

### Data Flow

```
User Query → Frontend → WebSocket → FastAPI → Brain Analysis
                                        ↓
                                  Tool Selection
                                        ↓
                           ┌─────────────────────────┐
                           │    Parallel Workers     │
                           ├─────────────────────────┤
                           │ • RAG Processing        │
                           │ • Web Search            │
                           │ • Document Retrieval    │
                           │ • Context Assembly      │
                           └─────────────────────────┘
                                        ↓
                              Response Generation
                                        ↓
                            Streaming Response → Frontend
```

---

## 🔧 Configuration

### Environment Variables

#### **Core Application**
```bash
APP_NAME="Legal Retrieval System"
APP_VERSION="1.0.0"
DEBUG=true
LOG_LEVEL=INFO
API_V1_STR="/api"
```

#### **Server Configuration**
```bash
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
WORKERS=1
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
```

#### **Database Connections**
```bash
MONGODB_URL=mongodb://admin:password123@mongodb:27017/legaldb?authSource=admin
REDIS_URL=redis://redis:6379/0
REDIS_URL_WS=redis://redis:6379/1
REDIS_URL_RETRIEVAL=redis://redis:6379/2
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION_NAME=legal_documents
```

#### **AI Configuration**
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_SIZE=1536
MAX_TOKENS=2000
TEMPERATURE=0.7
```

#### **Celery Workers**
```bash
CELERY_BROKER_URL=redis://redis:6379/3
CELERY_RESULT_BACKEND=redis://redis:6379/4
CELERY_CONCURRENCY=2
CELERY_LOGLEVEL=info
CELERY_POOL=eventlet
```

### Service Configuration

#### **FastAPI Settings** ([`src/app/config/settings.py`](src/app/config/settings.py))
- Environment-based configuration
- Validation with Pydantic
- Service discovery for Kubernetes
- Security and CORS settings

#### **React Configuration** ([`src/legal-chatbot-fe/vite.config.js`](src/legal-chatbot-fe/vite.config.js))
- Vite build optimization
- Development proxy settings
- Environment variable handling
- Build target configuration

### Database Setup

#### **MongoDB Collections**
- `conversations`: Chat history and metadata
- `messages`: Individual chat messages
- `analysis_results`: AI analysis cache
- `user_sessions`: User session management

#### **Redis Databases**
- Database 0: General caching
- Database 1: WebSocket sessions
- Database 2: Retrieval cache
- Database 3: Celery message broker
- Database 4: Celery result backend

---

## 📚 Data Management

### Legal Corpus

The system uses a comprehensive Vietnamese legal corpus:

#### **Dataset Statistics**
- **corpus.csv**: 180,000+ legal document segments
- **train.csv**: Training questions with relevant context
- **public_test.csv**: 8,000+ test questions for evaluation

#### **Data Format**
```csv
# corpus.csv
text: "Legal document text segment"
cid: Document segment ID (integer)

# train.csv / public_test.csv
question: "Legal question text"
qid: Question ID (string)
context: ["Related legal text segments"]
cid: [Context segment IDs]
```

### Data Processing Pipeline

1. **Document Ingestion**: Parse and clean legal documents
2. **Text Preprocessing**: Normalize and segment text
3. **Embedding Generation**: Create vector representations using OpenAI embeddings
4. **Vector Storage**: Store embeddings in Qdrant vector database
5. **Index Building**: Build optimized search indices
6. **Quality Validation**: Verify data integrity and search quality

### Vector Database

#### **Qdrant Configuration**
- **Collection**: `legal_documents`
- **Vector Size**: 1536 (text-embedding-3-small)
- **Distance Metric**: Cosine similarity
- **Indexing**: HNSW for fast similarity search
- **Sharding**: Multi-shard setup for horizontal scaling

---

## 🔍 Monitoring & Debugging

### Application Monitoring

#### **Real-time Dashboards**
```bash
# Celery task monitoring
open http://localhost:5555  # Flower dashboard

# API documentation and testing
open http://localhost:8000/docs  # FastAPI docs

# Vector database monitoring
open http://localhost:6333/dashboard  # Qdrant dashboard

# System health monitoring
curl http://localhost:8000/health
```

#### **Log Analysis**
```bash
# View application logs
docker-compose logs -f backend-api
docker-compose logs -f celery-worker-rag

# System health check
./scripts/system-check.sh

# Performance monitoring
./scripts/monitor-deployment.sh
```

### Performance Metrics

#### **Response Time Benchmarks**
- **Simple queries**: < 2 seconds average
- **Complex queries**: < 5 seconds average
- **Web search integration**: < 8 seconds average
- **Vector search**: < 1 second average

#### **Throughput Capacity**
- **Concurrent users**: 100+ simultaneous users
- **Requests per second**: 50+ RPS sustained
- **Worker capacity**: 20+ parallel tasks
- **Database operations**: 1000+ ops/second

#### **Resource Usage**
- **Memory**: 2-4GB total system memory
- **CPU**: 2-4 cores recommended
- **Storage**: 10GB+ for complete data corpus
- **Network**: < 100MB/day typical usage

### Troubleshooting

#### **Common Issues and Solutions**

**Docker Port Conflicts:**
```bash
# Check port usage
netstat -tulpn | grep :3000

# Kill processes using ports
lsof -ti:3000 | xargs kill -9

# Restart services
docker-compose down && docker-compose up -d
```

**Database Connection Issues:**
```bash
# Test MongoDB connection
docker-compose exec mongodb mongo --eval "db.runCommand('ping')"

# Test Redis connection
docker-compose exec redis redis-cli ping

# Test Qdrant connection
curl http://localhost:6333/health
```

**Worker Performance Issues:**
```bash
# Check worker status
docker-compose exec celery-worker-rag celery inspect active

# Monitor worker performance
open http://localhost:5555

# Restart workers
docker-compose restart celery-worker-rag
```

---

## 🛡️ Security & Performance

### Security Features

#### **Authentication & Authorization**
- JWT token-based authentication
- User session management
- Role-based access control
- API key rotation and management

#### **Data Security**
- Environment variable encryption
- Database connection security
- CORS policy enforcement
- Input validation and sanitization
- SQL injection protection

#### **Infrastructure Security**
- Docker container isolation
- Network segmentation
- Kubernetes secrets management
- SSL/TLS termination
- Security header enforcement

### Performance Optimization

#### **Caching Strategy**
- **Redis Multi-level Caching**:
  - Response caching for frequent queries
  - Session data caching
  - Database query result caching
  - Vector search result caching

#### **Database Optimization**
- **MongoDB Indexing**: Optimized indices for query patterns
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized aggregation pipelines
- **Sharding**: Horizontal scaling for large datasets

#### **Worker Optimization**
- **Queue Optimization**: Separate queues for different task types
- **Resource Allocation**: CPU and memory optimization per worker
- **Batch Processing**: Efficient batch operations
- **Connection Reuse**: Persistent connections for external APIs

### Best Practices

#### **Development**
- Environment-based configuration
- Structured logging with correlation IDs
- Error handling with proper HTTP status codes
- API versioning and backward compatibility
- Comprehensive testing at all levels

#### **Deployment**
- Blue-green deployment strategy
- Health checks and readiness probes
- Resource limits and requests
- Monitoring and alerting setup
- Backup and disaster recovery planning

---

## 🤝 Contributing

### Development Workflow

#### **Getting Started**
1. Fork the repository
2. Clone your fork locally
3. Create a feature branch
4. Setup development environment
5. Make your changes with proper testing
6. Submit a pull request

#### **Branch Strategy**
```bash
main              # Production-ready code
├── develop       # Integration branch
├── feature/*     # Feature development
├── bugfix/*      # Bug fixes
├── hotfix/*      # Critical production fixes
└── release/*     # Release preparation
```

### Code Standards

#### **Python Standards**
- **PEP 8**: Code style compliance
- **Type Hints**: Full type annotation
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Proper exception handling
- **Testing**: Unit tests for all functions

#### **JavaScript Standards**
- **ESLint**: Code style enforcement
- **Prettier**: Code formatting
- **JSDoc**: Function documentation
- **Error Boundaries**: Proper error handling
- **Testing**: Component and integration tests

#### **Commit Standards**
```bash
feat: add new feature
fix: bug fix
docs: documentation update
style: formatting changes
refactor: code refactoring
test: add or modify tests
chore: maintenance tasks
```

### Documentation

#### **Code Documentation**
- Inline comments for complex logic
- Function and class docstrings
- API endpoint documentation
- Configuration documentation

#### **User Documentation**
- Setup and installation guides
- API usage examples
- Troubleshooting guides
- Performance tuning guides

---

## 🏆 System Capabilities

### **AI-Powered Features**
- ✅ Multi-language support (Vietnamese focus)
- ✅ Context-aware conversation management
- ✅ Real-time response streaming
- ✅ Source citation and verification
- ✅ Query intent understanding
- ✅ Multi-tool orchestration

### **Technical Features**
- ✅ Microservices architecture
- ✅ Horizontal auto-scaling
- ✅ Real-time WebSocket communication
- ✅ Vector similarity search
- ✅ Distributed task processing
- ✅ Comprehensive monitoring

### **Enterprise Features**
- ✅ Kubernetes deployment ready
- ✅ Multi-environment support
- ✅ Infrastructure as Code (Terraform)
- ✅ CI/CD pipeline integration
- ✅ Comprehensive testing suite
- ✅ Performance monitoring and alerting

---

## 📞 Support & Resources

### **Getting Help**
- 📚 **Documentation**: Comprehensive guides in [`docs/`](docs/) directory
- 🔧 **API Docs**: Interactive documentation at http://localhost:8000/docs
- 🧪 **Testing Guide**: Detailed testing instructions in [`tests/DOCKER_TESTING_GUIDE.md`](tests/DOCKER_TESTING_GUIDE.md)
- 🚀 **Deployment Guide**: Kubernetes and AWS deployment instructions

### **Quick Reference Commands**
```bash
# System health check
make health-check

# View all available commands
make help

# Complete system cleanup and rebuild
make clean-all

# Performance monitoring
make monitor

# Backup system data
make backup
```

### **Performance Reports**
- 📈 **Optimization Report**: [`reports/OPTIMIZATION_REPORT.md`](reports/OPTIMIZATION_REPORT.md)
- ✅ **Deployment Verification**: [`reports/DEPLOYMENT_SUCCESS_REPORT.md`](reports/DEPLOYMENT_SUCCESS_REPORT.md)
- 🧪 **API Testing Results**: [`reports/API_TEST_REPORT.md`](reports/API_TEST_REPORT.md)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 Ready to Deploy!

**LexiOps** is production-ready and includes everything needed for enterprise deployment:

✅ **Scalable Architecture** - Microservices with Kubernetes support  
✅ **AI Integration** - OpenAI GPT with RAG pipeline  
✅ **Real-time Communication** - WebSocket-powered chat interface  
✅ **Comprehensive Testing** - Full test coverage with automated CI/CD  
✅ **Enterprise Security** - Authentication, authorization, and data protection  
✅ **Performance Optimized** - Sub-second response times with caching  
✅ **DevOps Ready** - Docker, Kubernetes, Terraform, and monitoring  

---

**LexiOps - Transforming Legal Information Access with AI** 🏛️🤖

*Built with ❤️ using FastAPI, React, OpenAI, Docker, and modern DevOps practices*
---

✅ **Ready to deploy your AI-powered Legal Retrieval System!** 🚀

*Built with ❤️ using FastAPI, React, OpenAI, Docker, and modern DevOps practices*