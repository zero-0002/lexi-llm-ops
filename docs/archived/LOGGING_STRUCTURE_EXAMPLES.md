# 📊 STANDARDIZED LOGGING SYSTEM - STRUCTURE & EXAMPLES

## 🏗️ Cấu trúc Log System

### 1. **Hai Loại Log Format**

#### A. **Standard Format** (Legacy/Compatibility)
```
2025-08-13 23:15:02,288 - app.celery_config - INFO - 🔄 Celery configured with broker: redis://localhost:6379/0
```

**Cấu trúc**: `TIMESTAMP - LOGGER_NAME - LEVEL - MESSAGE`

#### B. **Structured JSON Format** (Production/K8s)
```json
{
  "timestamp": "2025-08-13T16:15:14.277622Z",
  "level": "INFO",
  "logger": "application",
  "message": "FastAPI application started",
  "module": "logging_config",
  "function": "info",
  "line": 132
}
```

## 📋 **Log Entry Fields**

### **Core Fields** (Required)
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | ISO 8601 UTC timestamp | `"2025-08-13T16:15:14.277622Z"` |
| `level` | string | Log level | `"INFO"`, `"ERROR"`, `"WARNING"`, `"DEBUG"` |
| `logger` | string | Logger name/component | `"application"`, `"app.celery_config"` |
| `message` | string | Log message | `"FastAPI application started"` |
| `module` | string | Python module name | `"main"`, `"celery_config"` |
| `function` | string | Function name | `"startup"`, `"log_task_start"` |
| `line` | integer | Line number | `132` |

### **Context Fields** (Conditional)
| Field | Type | Description | When Added |
|-------|------|-------------|------------|
| `request_id` | string | Unique request identifier | During API calls |
| `user_id` | string | User identifier | When user context available |
| `task_id` | string | Celery task identifier | During Celery task execution |

### **Performance Fields** (Metrics)
| Field | Type | Description | Usage |
|-------|------|-------------|-------|
| `metrics` | object | Performance data | API calls, task execution |
| `duration_seconds` | float | Execution time | Performance tracking |
| `status_code` | integer | HTTP status | API responses |
| `queue` | string | Celery queue name | Task routing |

### **Error Fields** (Errors/Exceptions)
| Field | Type | Description | Usage |
|-------|------|-------------|-------|
| `exception` | object | Exception details | Error handling |
| `exception.type` | string | Exception class name | Error classification |
| `exception.message` | string | Error message | Debugging |
| `exception.traceback` | string | Stack trace | Detailed debugging |

## 🎯 **Log Examples by Category**

### 1. **Application Startup Logs**

#### Standard Format:
```
2025-08-13 23:15:02,288 - app.celery_config - INFO - 🔄 Celery configured with broker: redis://localhost:6379/0
2025-08-13 23:15:03,061 - app.config.database - INFO - Connecting to MongoDB: mongodb://localhost:27017
```

#### JSON Format:
```json
{
  "timestamp": "2025-08-13T16:15:14.277622Z",
  "level": "INFO",
  "logger": "application",
  "message": "FastAPI application started",
  "module": "logging_config",
  "function": "info",
  "line": 132,
  "event": "app_startup",
  "app_name": "Legal Chatbot API",
  "version": "2.0.0",
  "host": "0.0.0.0",
  "port": 8001
}
```

### 2. **API Request Logs**

#### Request Start:
```json
{
  "timestamp": "2025-08-13T16:20:15.123456Z",
  "level": "INFO",
  "logger": "application",
  "message": "Request started",
  "module": "main",
  "function": "logging_middleware",
  "line": 65,
  "request_id": "req-550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "method": "POST",
  "url": "http://localhost:8001/api/v1/legal-chat",
  "path": "/api/v1/legal-chat",
  "query_params": {},
  "client_host": "127.0.0.1",
  "user_agent": "Mozilla/5.0...",
  "event": "request_start"
}
```

#### Request Complete:
```json
{
  "timestamp": "2025-08-13T16:20:16.234567Z",
  "level": "INFO",
  "logger": "perf",
  "message": "Request completed",
  "module": "main",
  "function": "logging_middleware",
  "line": 89,
  "request_id": "req-550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "method": "POST",
  "path": "/api/v1/legal-chat",
  "status_code": 200,
  "duration_seconds": 1.111,
  "response_size": "1024",
  "event": "request_complete"
}
```

### 3. **Celery Task Logs**

#### Task Start:
```json
{
  "timestamp": "2025-08-13T16:20:16.345678Z",
  "level": "INFO",
  "logger": "perf",
  "message": "Task started",
  "module": "celery_config",
  "function": "log_task_start",
  "line": 156,
  "task_id": "task-660f9511-f39c-52e5-b827-557766551111",
  "task_name": "app.tasks.legal_rag_tasks.process_legal_query",
  "queue": "rag_queue",
  "args_count": 2,
  "kwargs_keys": ["max_tokens", "temperature"],
  "event": "task_start"
}
```

#### Task Complete:
```json
{
  "timestamp": "2025-08-13T16:20:18.456789Z",
  "level": "INFO",
  "logger": "perf",
  "message": "Task completed",
  "module": "celery_config",
  "function": "log_task_completion",
  "line": 178,
  "task_id": "task-660f9511-f39c-52e5-b827-557766551111",
  "task_name": "app.tasks.legal_rag_tasks.process_legal_query",
  "duration_seconds": 2.111,
  "state": "SUCCESS",
  "queue": "rag_queue",
  "has_result": true,
  "event": "task_complete"
}
```

### 4. **Error Logs**

#### API Error:
```json
{
  "timestamp": "2025-08-13T16:20:19.567890Z",
  "level": "ERROR",
  "logger": "application",
  "message": "Request failed",
  "module": "main",
  "function": "logging_middleware",
  "line": 110,
  "request_id": "req-770f0622-f4ad-63f6-c938-668877552222",
  "user_id": "user-456",
  "method": "POST",
  "path": "/api/v1/rag/query",
  "duration_seconds": 0.045,
  "error_type": "ValidationError",
  "error_message": "Invalid query format",
  "event": "request_error",
  "exception": {
    "type": "ValidationError",
    "message": "Query parameter is required",
    "traceback": "Traceback (most recent call last):\\n  File..."
  }
}
```

#### Celery Task Error:
```json
{
  "timestamp": "2025-08-13T16:20:20.678901Z",
  "level": "ERROR",
  "logger": "application",
  "message": "Task failed",
  "module": "celery_config",
  "function": "log_task_failure",
  "line": 201,
  "task_id": "task-880g1733-g5be-74g7-d049-779988663333",
  "task_name": "app.tasks.embedding_tasks.embed_documents",
  "duration_seconds": 5.234,
  "exception_type": "ConnectionError",
  "exception_message": "Failed to connect to vector database",
  "traceback": "Traceback (most recent call last):\\n...",
  "event": "task_error"
}
```

### 5. **Performance Metrics Logs**

#### Database Operation:
```json
{
  "timestamp": "2025-08-13T16:20:21.789012Z",
  "level": "INFO",
  "logger": "perf",
  "message": "DB query on legal_documents - 15 records (234.56ms)",
  "module": "database",
  "function": "log_database_operation",
  "line": 115,
  "request_id": "req-990h2844-h6cf-85h8-e15a-88aa99774444",
  "metrics": {
    "type": "database_operation",
    "operation": "find",
    "collection": "legal_documents", 
    "execution_time_ms": 234.56,
    "record_count": 15,
    "index_used": "title_text_index"
  }
}
```

#### Memory Usage:
```json
{
  "timestamp": "2025-08-13T16:20:22.890123Z",
  "level": "INFO",
  "logger": "system",
  "message": "Memory usage check",
  "module": "monitoring",
  "function": "log_system_metrics",
  "line": 78,
  "metrics": {
    "type": "system_metrics",
    "memory_usage_mb": 1024.5,
    "cpu_usage_percent": 45.2,
    "active_connections": 12,
    "celery_workers_active": 4
  }
}
```

### 6. **Security/Audit Logs**

#### User Authentication:
```json
{
  "timestamp": "2025-08-13T16:20:23.901234Z",
  "level": "WARNING",
  "logger": "security",
  "message": "Failed login attempt",
  "module": "auth",
  "function": "log_security_event",
  "line": 45,
  "user_id": "unknown",
  "client_ip": "192.168.1.100",
  "user_agent": "curl/7.68.0",
  "event": "auth_failure",
  "reason": "invalid_credentials",
  "attempt_count": 3
}
```

## ⚙️ **Logger Categories**

### 1. **Application Logger** (`application`)
- Request/response lifecycle
- Business logic events
- General application flow

### 2. **Performance Logger** (`perf`)
- API response times
- Task execution durations
- Database operation metrics
- System resource usage

### 3. **Security Logger** (`security`)
- Authentication events
- Authorization failures
- Suspicious activities
- Audit trails

### 4. **Celery Logger** (`celery`)
- Task lifecycle events
- Worker status changes
- Queue monitoring
- Task routing

## 🔧 **Logging Configuration**

### Environment Variables:
```bash
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json                   # json, standard
ENABLE_STRUCTURED_LOGS=true       # Enable JSON format
ENABLE_PERFORMANCE_LOGGING=true   # Enable performance metrics
ENABLE_SECURITY_LOGGING=true      # Enable security events
```

### Context Variables Usage:
```python
from app.utils.logging_config import request_id_ctx, user_id_ctx
from app.utils.logging_config import app_logger

# Set context
with request_id_ctx.set("req-123"), user_id_ctx.set("user-456"):
    app_logger.info("Processing user request")
```

## 📈 **Benefits for K8s Deployment**

1. **Centralized Logging**: JSON format tương thích với ELK stack
2. **Distributed Tracing**: Request IDs track across microservices
3. **Performance Monitoring**: Real-time metrics cho auto-scaling
4. **Error Tracking**: Structured error context cho debugging
5. **Security Auditing**: Comprehensive audit trails
6. **Operational Insights**: System health và performance analytics

## 🚨 **Important Notes**

### Log Volume Management:
- **DEBUG**: Chỉ trong development
- **INFO**: Normal operations, performance metrics
- **WARNING**: Potential issues cần attention
- **ERROR**: Critical failures cần immediate action

### Performance Impact:
- JSON formatting adds ~5-10% overhead
- Context variables are thread-safe
- Async logging recommended cho high traffic

### Security Considerations:
- Never log sensitive data (passwords, tokens)
- Sanitize user inputs before logging
- Use structured fields cho searchability
- Implement log retention policies

---

*Hệ thống logging này cung cấp comprehensive observability cho production deployment với full K8s integration.*
