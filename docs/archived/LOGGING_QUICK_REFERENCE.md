# 📚 LOGGING QUICK REFERENCE GUIDE

## 🚀 **QUICK START**

### 1. Basic Usage in Your Code:

```python
# Import standardized loggers
from app.utils.logging_config import get_application_logger, get_performance_logger

# Get logger for your module
logger = get_application_logger(__name__)

# Basic logging
logger.info("Processing user request", extra={"user_id": "user-123"})
logger.error("Database connection failed", extra={"error_code": "DB_001"})

# Performance logging (automatic timing)
@log_performance
def process_legal_query(query: str):
    # Your function logic here
    return results
```

### 2. Add Request Context:

```python
# In FastAPI endpoints
from app.utils.logging_config import request_id_ctx, user_id_ctx

@app.post("/api/legal-chat")
async def legal_chat(request: ChatRequest):
    # Context automatically set by middleware
    logger = get_application_logger(__name__)
    logger.info("Chat request received", extra={
        "query_length": len(request.query),
        "user_type": request.user_type
    })
```

### 3. Celery Task Logging:

```python
# In celery tasks
from app.utils.logging_config import get_application_logger, task_id_ctx

@celery_app.task
def process_document_embedding(doc_id: str):
    logger = get_application_logger(__name__)
    
    # Task context automatically set by signals
    logger.info("Starting document processing", extra={
        "document_id": doc_id,
        "document_size": get_doc_size(doc_id)
    })
    
    try:
        # Process document
        result = embed_document(doc_id)
        logger.info("Document processed successfully", extra={
            "embedding_dimensions": len(result.vector)
        })
        return result
    except Exception as e:
        logger.error("Document processing failed", extra={
            "error": str(e),
            "document_id": doc_id
        })
        raise
```

## 🎯 **LOG LEVEL GUIDE**

| Level | When to Use | Example |
|-------|-------------|---------|
| `DEBUG` | Development debugging only | `logger.debug("Variable X = %s", x)` |
| `INFO` | Normal operations, important events | `logger.info("User logged in successfully")` |
| `WARNING` | Potential issues, degraded performance | `logger.warning("API response time > 2s")` |
| `ERROR` | Errors that affect functionality | `logger.error("Failed to save user data")` |
| `CRITICAL` | System failures requiring immediate attention | `logger.critical("Database connection lost")` |

## 🔍 **SEARCH PATTERNS**

### Common Kibana/Elasticsearch Queries:

```javascript
// Find all errors for specific user
level:ERROR AND user_id:"user-123"

// API performance analysis
event:"request_complete" AND duration_seconds:>2.0

// Failed Celery tasks
logger:"app.celery*" AND level:ERROR

// Security events
event:"auth_failure" OR event:"access_denied"

// High-traffic endpoints
message:"legal_chat" AND timestamp:[now-1h TO now]
```

## 📊 **STANDARD EXTRA FIELDS**

### API Requests:
```python
logger.info("Request processed", extra={
    "endpoint": "/api/legal-chat",
    "method": "POST", 
    "status_code": 200,
    "user_agent": request.headers.get("user-agent"),
    "response_size_bytes": len(response_data)
})
```

### Database Operations:
```python
logger.info("Query executed", extra={
    "table": "legal_documents",
    "operation": "SELECT",
    "rows_affected": cursor.rowcount,
    "query_time_ms": execution_time * 1000
})
```

### File Operations:
```python
logger.info("File processed", extra={
    "file_path": file_path,
    "file_size_bytes": os.path.getsize(file_path),
    "operation": "upload",
    "mime_type": file.content_type
})
```

### Business Logic:
```python
logger.info("Legal analysis completed", extra={
    "document_type": "contract",
    "analysis_type": "risk_assessment", 
    "confidence_score": 0.87,
    "identified_issues": 3
})
```

## ⚡ **PERFORMANCE MONITORING**

### Automatic Performance Decorators:

```python
# API endpoints - tracks response time
@log_api_call
@app.post("/api/search")
async def search_documents(query: str):
    return search_results

# Background tasks - tracks execution time  
@log_performance
def heavy_computation():
    return results

# Database operations - tracks query time
@log_performance  
def complex_database_query():
    return db_results
```

### Manual Performance Logging:

```python
import time
start_time = time.time()

# Your operation here
result = process_data()

duration = time.time() - start_time
logger.info("Operation completed", extra={
    "operation": "data_processing",
    "duration_seconds": duration,
    "records_processed": len(result)
})
```

## 🐛 **ERROR HANDLING PATTERNS**

### Standard Error Logging:

```python
try:
    result = risky_operation()
except ValidationError as e:
    logger.warning("Input validation failed", extra={
        "error_type": "validation",
        "field": e.field,
        "invalid_value": e.value
    })
    raise HTTPException(status_code=400, detail=str(e))
    
except DatabaseError as e:
    logger.error("Database operation failed", extra={
        "error_type": "database",
        "operation": "INSERT",
        "table": "documents", 
        "error_code": e.code
    })
    raise HTTPException(status_code=500, detail="Internal server error")
    
except Exception as e:
    logger.critical("Unexpected error occurred", extra={
        "error_type": "unexpected",
        "error_class": e.__class__.__name__,
        "stack_trace": traceback.format_exc()
    })
    raise
```

### Celery Error Handling:

```python
@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def process_document(self, doc_id: str):
    logger = get_application_logger(__name__)
    
    try:
        return do_processing(doc_id)
    except RetryableError as e:
        logger.warning("Task will be retried", extra={
            "retry_count": self.request.retries,
            "max_retries": self.max_retries,
            "error": str(e)
        })
        raise self.retry(countdown=60)
    except FatalError as e:
        logger.error("Task failed permanently", extra={
            "document_id": doc_id,
            "error": str(e),
            "final_attempt": True
        })
        raise
```

## 🔧 **CONFIGURATION SNIPPETS**

### Environment Variables:
```bash
# .env file
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_STRUCTURED_LOGS=true
ENABLE_PERFORMANCE_LOGGING=true
LOG_FILE_PATH=/app/logs/application.log
LOG_RETENTION_DAYS=30
```

### Kubernetes ConfigMap:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: logging-config
data:
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
  ENABLE_STRUCTURED_LOGS: "true"
  ENABLE_PERFORMANCE_LOGGING: "true"
```

### Docker Compose:
```yaml
services:
  legal-chatbot:
    environment:
      - LOG_LEVEL=INFO
      - LOG_FORMAT=json
      - ENABLE_STRUCTURED_LOGS=true
    volumes:
      - ./logs:/app/logs
```

## 📈 **MONITORING DASHBOARD QUERIES**

### Response Time Trends:
```javascript
// Average API response time over time
GET logs/_search
{
  "query": {"term": {"event": "request_complete"}},
  "aggs": {
    "response_time_over_time": {
      "date_histogram": {
        "field": "timestamp",
        "interval": "5m"
      },
      "aggs": {
        "avg_response_time": {
          "avg": {"field": "duration_seconds"}
        }
      }
    }
  }
}
```

### Error Rate Analysis:
```javascript
// Error rate by endpoint
GET logs/_search
{
  "query": {"term": {"level": "ERROR"}},
  "aggs": {
    "errors_by_endpoint": {
      "terms": {"field": "endpoint.keyword"}
    }
  }
}
```

### User Activity:
```javascript
// Active users over time
GET logs/_search
{
  "query": {"exists": {"field": "user_id"}},
  "aggs": {
    "unique_users": {
      "cardinality": {"field": "user_id.keyword"}
    }
  }
}
```

## 🚨 **TROUBLESHOOTING CHECKLIST**

### "Logs not appearing":
1. ✅ Check LOG_LEVEL setting
2. ✅ Verify logger name matches module
3. ✅ Confirm structured logging enabled
4. ✅ Check file permissions
5. ✅ Validate JSON format

### "Missing context information":
1. ✅ Verify middleware enabled
2. ✅ Check context variable setup
3. ✅ Confirm async context inheritance
4. ✅ Validate request_id generation

### "Performance issues":
1. ✅ Check log volume
2. ✅ Verify log level (avoid DEBUG in prod)
3. ✅ Monitor disk I/O
4. ✅ Consider async logging
5. ✅ Check log rotation

### "Search not working":
1. ✅ Verify JSON format
2. ✅ Check Elasticsearch mapping
3. ✅ Confirm field names match
4. ✅ Validate timestamp format
5. ✅ Test with simple queries

---

**🎯 Remember: Good logging is about finding the right balance between too much noise and too little information. Log what you need to debug issues and monitor performance, but avoid logging sensitive data or creating excessive volume.**
