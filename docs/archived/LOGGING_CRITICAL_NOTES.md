# 🚨 LOGGING SYSTEM - IMPORTANT CONSIDERATIONS & BEST PRACTICES

## ⚠️ **CRITICAL CONSIDERATIONS**

### 1. **Performance Impact**
```
📊 Benchmark Results:
- Standard Logging: ~0.1ms overhead per log
- JSON Structured Logging: ~0.15ms overhead per log  
- Context Variables: ~0.05ms overhead per request
- Total Impact: ~5-10% performance overhead in high traffic
```

**Recommendations:**
- Sử dụng async logging cho high-traffic endpoints
- Limit DEBUG logs trong production  
- Buffer logs before writing to disk
- Consider log sampling for very high volume

### 2. **Storage & Volume Management**
```
📈 Log Volume Estimates:
- API Request: ~500 bytes per request cycle (start + complete)
- Celery Task: ~300 bytes per task cycle
- Error Log: ~1-2KB per error (with stack trace)
- 1000 requests/hour = ~500KB logs/hour
- 24/7 operation = ~4.3GB logs/month
```

**Critical Actions:**
- ✅ Implement log rotation (daily/weekly)
- ✅ Set retention policies (30-90 days)
- ✅ Compress old logs
- ✅ Monitor disk space usage

### 3. **Security & Compliance**
```json
❌ NEVER LOG:
{
  "user_password": "secret123",
  "api_key": "sk-1234567890abcdef",
  "credit_card": "4111-1111-1111-1111",
  "personal_id": "123-45-6789"
}

✅ SAFE TO LOG:
{
  "user_id": "user-123",
  "action": "login_attempt", 
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

**Security Measures:**
- Sanitize all user inputs before logging
- Hash or mask sensitive identifiers
- Implement audit trails for admin actions
- Regular security review of logged data

## 🔧 **CONFIGURATION GUIDELINES**

### 1. **Environment-Specific Settings**

#### Development:
```python
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "standard"  # Readable format
ENABLE_STRUCTURED_LOGS = False
ENABLE_PERFORMANCE_LOGGING = True
LOG_TO_FILE = False  # Console only
```

#### Staging:
```python
LOG_LEVEL = "INFO" 
LOG_FORMAT = "json"  # Test structured format
ENABLE_STRUCTURED_LOGS = True
ENABLE_PERFORMANCE_LOGGING = True
LOG_TO_FILE = True
LOG_RETENTION_DAYS = 7
```

#### Production:
```python
LOG_LEVEL = "INFO"  # WARNING for critical services
LOG_FORMAT = "json"  # Required for K8s
ENABLE_STRUCTURED_LOGS = True
ENABLE_PERFORMANCE_LOGGING = True
ENABLE_SECURITY_LOGGING = True
LOG_TO_FILE = True
LOG_RETENTION_DAYS = 30
LOG_ROTATION = "daily"
LOG_COMPRESSION = True
```

### 2. **Logger Hierarchy & Levels**

```python
# Logger Priority (High to Low)
CRITICAL = 50    # System failure, immediate action required
ERROR = 40       # Error occurred, functionality affected  
WARNING = 30     # Warning, potential issue
INFO = 20        # General information, normal operations
DEBUG = 10       # Detailed debugging information

# Usage Guidelines:
- CRITICAL: Database down, API unreachable
- ERROR: Task failed, request validation error
- WARNING: Slow response, resource usage high
- INFO: Request completed, task started
- DEBUG: Variable values, function entry/exit
```

### 3. **Context Management**

```python
# Request Context - ALWAYS include:
{
  "request_id": "unique-uuid",        # Mandatory
  "user_id": "user-identifier",       # If authenticated
  "session_id": "session-uuid",       # If applicable
  "correlation_id": "trace-uuid"      # For distributed tracing
}

# Task Context - ALWAYS include:
{
  "task_id": "celery-task-uuid",      # Mandatory
  "task_name": "full.module.name",    # Mandatory
  "queue": "queue-name",              # Mandatory
  "request_id": "originating-request" # If from API call
}
```

## 📊 **STRUCTURED LOG FIELD STANDARDS**

### **Mandatory Fields** (All Logs)
| Field | Type | Format | Example |
|-------|------|--------|---------|
| `timestamp` | string | ISO 8601 UTC | `"2025-08-13T16:25:10.123456Z"` |
| `level` | string | UPPERCASE | `"INFO"`, `"ERROR"` |
| `logger` | string | module.name | `"app.api.legal_chat"` |
| `message` | string | Human readable | `"Request completed successfully"` |
| `module` | string | Python module | `"legal_chat"` |
| `function` | string | Function name | `"process_chat_request"` |
| `line` | integer | Line number | `145` |

### **Context Fields** (When Available)
| Field | Type | Description | Required When |
|-------|------|-------------|---------------|
| `request_id` | uuid | API request tracking | API calls |
| `user_id` | string | User identifier | Authenticated requests |
| `task_id` | uuid | Celery task tracking | Celery tasks |
| `session_id` | uuid | Session tracking | User sessions |

### **Performance Fields** (Metrics)
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `duration_seconds` | float | seconds | Execution time |
| `response_time_ms` | float | milliseconds | API response time |
| `memory_usage_mb` | float | megabytes | Memory consumption |
| `cpu_usage_percent` | float | percentage | CPU utilization |

### **Event Classification**
```python
# API Events
"request_start"     # Request received
"request_complete"  # Request processed successfully  
"request_error"     # Request failed

# Task Events  
"task_start"        # Celery task started
"task_complete"     # Task completed successfully
"task_error"        # Task failed
"task_retry"        # Task retried

# System Events
"app_startup"       # Application started
"app_shutdown"      # Application stopped
"worker_ready"      # Celery worker ready
"worker_shutdown"   # Celery worker stopped

# Database Events
"db_query"          # Database query executed
"db_error"          # Database operation failed
"connection_pool"   # Connection pool status

# Security Events
"auth_success"      # Authentication successful
"auth_failure"      # Authentication failed
"access_denied"     # Authorization failed
"suspicious_activity" # Potential security threat
```

## 🎯 **MONITORING & ALERTING**

### 1. **Key Metrics to Monitor**

#### Performance Metrics:
```python
# API Performance
- Average response time > 2000ms
- 95th percentile response time > 5000ms  
- Request rate > 1000/minute
- Error rate > 5%

# Celery Performance  
- Task execution time > 30s
- Task failure rate > 10%
- Queue length > 100
- Worker utilization > 80%

# System Health
- Memory usage > 80%
- CPU usage > 70%
- Disk space < 20%
- Database connections > 80% pool
```

#### Error Patterns:
```python
# Critical Alerts
- ERROR logs > 10/minute
- Database connection failures
- Authentication service down
- Memory leaks detected

# Warning Alerts
- WARNING logs > 50/minute  
- Slow query performance
- High queue processing time
- Unusual traffic patterns
```

### 2. **Log Aggregation & Search**

#### ELK Stack Integration:
```yaml
# Elasticsearch mapping
{
  "mappings": {
    "properties": {
      "timestamp": {"type": "date"},
      "level": {"type": "keyword"},
      "logger": {"type": "keyword"},
      "message": {"type": "text"},
      "request_id": {"type": "keyword"},
      "user_id": {"type": "keyword"},
      "duration_seconds": {"type": "float"},
      "event": {"type": "keyword"}
    }
  }
}
```

#### Common Search Queries:
```javascript
// Find all errors for a user
GET logs/_search
{
  "query": {
    "bool": {
      "must": [
        {"term": {"user_id": "user-123"}},
        {"term": {"level": "ERROR"}}
      ]
    }
  }
}

// Performance analysis
GET logs/_search
{
  "query": {"term": {"event": "request_complete"}},
  "aggs": {
    "avg_response_time": {
      "avg": {"field": "duration_seconds"}
    }
  }
}
```

## 🛡️ **TROUBLESHOOTING GUIDE**

### Common Issues:

#### 1. **High Log Volume**
```
Symptoms: Disk space filling up, performance degradation
Solutions:
- Increase log level to WARNING/ERROR
- Implement log sampling
- Reduce debug logging in production
- Check for log loops
```

#### 2. **Missing Context**
```
Symptoms: Logs without request_id, difficult debugging
Solutions:
- Verify middleware setup
- Check context variable inheritance
- Add explicit context setting
- Review async task context passing
```

#### 3. **JSON Parsing Errors** 
```
Symptoms: Logs not appearing in structured format
Solutions:
- Validate JSON formatter configuration
- Check for special characters in messages
- Verify encoding settings
- Test JSON serialization
```

#### 4. **Performance Degradation**
```
Symptoms: Slow API responses with logging enabled  
Solutions:
- Enable async logging
- Reduce log verbosity
- Check disk I/O performance
- Consider log buffering
```

## 📋 **DEPLOYMENT CHECKLIST**

### Pre-Production:
- [ ] Log levels configured appropriately
- [ ] Structured logging enabled
- [ ] Context variables tested
- [ ] Performance impact assessed
- [ ] Security review completed
- [ ] Log rotation configured
- [ ] Monitoring alerts setup

### Production Deployment:
- [ ] ELK stack integration tested
- [ ] Log aggregation working
- [ ] Dashboard monitoring active
- [ ] Alert notifications configured
- [ ] Backup log retention setup
- [ ] Compliance requirements met
- [ ] Documentation updated

### Post-Deployment:
- [ ] Log volume monitoring
- [ ] Performance metrics tracking
- [ ] Error rate analysis
- [ ] Search functionality verified
- [ ] Alert threshold tuning
- [ ] Retention policy enforcement

---

**⚡ Key Takeaway: Logging is critical for production operations but must be balanced with performance, security, and storage considerations. Proper configuration and monitoring ensure reliable observability without compromising system performance.**
