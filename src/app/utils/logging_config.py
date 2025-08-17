"""
📊 STANDARDIZED LOGGING CONFIGURATION FOR K8S DEPLOYMENT
======================================================
Centralized logging system with structured logs, metrics, and performance tracking
"""

import logging
import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union
from contextvars import ContextVar
from functools import wraps
import traceback
import sys
import os

# Context variables for request tracking
request_id_ctx: ContextVar[str] = ContextVar('request_id', default='')
user_id_ctx: ContextVar[str] = ContextVar('user_id', default='')
task_id_ctx: ContextVar[str] = ContextVar('task_id', default='')

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging in K8s"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Base log structure
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add context information
        if request_id_ctx.get():
            log_entry['request_id'] = request_id_ctx.get()
        if user_id_ctx.get():
            log_entry['user_id'] = user_id_ctx.get()
        if task_id_ctx.get():
            log_entry['task_id'] = task_id_ctx.get()
        
        # Add extra fields from record
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception information
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add performance metrics if available
        if hasattr(record, 'metrics'):
            log_entry['metrics'] = record.metrics
        
        return json.dumps(log_entry, ensure_ascii=False)

class PerformanceLogger:
    """Performance tracking and metrics collection"""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       response_time: float, request_size: int = 0, 
                       response_size: int = 0, **kwargs):
        """Log API request performance metrics"""
        metrics = {
            'type': 'api_request',
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time_ms': round(response_time * 1000, 2),
            'request_size_bytes': request_size,
            'response_size_bytes': response_size,
            **kwargs
        }
        
        self.logger.info(
            f"API {method} {endpoint} - {status_code} ({response_time*1000:.2f}ms)",
            extra={'metrics': metrics}
        )
    
    def log_task_performance(self, task_name: str, execution_time: float, 
                           status: str, **kwargs):
        """Log Celery task performance metrics"""
        metrics = {
            'type': 'celery_task',
            'task_name': task_name,
            'execution_time_ms': round(execution_time * 1000, 2),
            'status': status,
            **kwargs
        }
        
        self.logger.info(
            f"Task {task_name} completed in {execution_time*1000:.2f}ms - {status}",
            extra={'metrics': metrics}
        )
    
    def log_database_operation(self, operation: str, collection: str, 
                             execution_time: float, record_count: int = 0, **kwargs):
        """Log database operation performance"""
        metrics = {
            'type': 'database_operation',
            'operation': operation,
            'collection': collection,
            'execution_time_ms': round(execution_time * 1000, 2),
            'record_count': record_count,
            **kwargs
        }
        
        self.logger.info(
            f"DB {operation} on {collection} - {record_count} records ({execution_time*1000:.2f}ms)",
            extra={'metrics': metrics}
        )
    def info(self, msg, *args, **kwargs):
        return self.logger.info(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        return self.logger.log(level, msg, *args, **kwargs)
class ApplicationLogger:
    """Main application logger with business logic tracking"""
    
    def __init__(self, logger_name: str = "application"):
        self.logger = logging.getLogger(logger_name)
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log info message"""
        self.logger.info(message, extra=extra or {})
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log warning message"""
        self.logger.warning(message, extra=extra or {})
    
    def error(self, message: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        """Log error message"""
        self.logger.error(message, extra=extra or {}, exc_info=exc_info)
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        """Log debug message"""
        self.logger.debug(message, extra=extra or {})
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """Log user actions and business events"""
        extra_fields = {
            'type': 'user_action',
            'action': action,
            'details': details or {}
        }
        
        self.logger.info(f"User action: {action}", extra={'extra_fields': extra_fields})
    
    def log_system_event(self, event: str, severity: str = "info", details: Dict[str, Any] = None):
        """Log system events and state changes"""
        extra_fields = {
            'type': 'system_event',
            'event': event,
            'severity': severity,
            'details': details or {}
        }
        
        level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(level, f"System event: {event}", extra={'extra_fields': extra_fields})

class SecurityLogger:
    """Security and audit logging"""
    
    def __init__(self, logger_name: str = "security"):
        self.logger = logging.getLogger(logger_name)
    
    def log_auth_event(self, event: str, user_id: str = None, ip_address: str = None, 
                      success: bool = True, details: Dict[str, Any] = None):
        """Log authentication and authorization events"""
        extra_fields = {
            'type': 'auth_event',
            'event': event,
            'user_id': user_id,
            'ip_address': ip_address,
            'success': success,
            'details': details or {}
        }
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, f"Auth event: {event}", extra={'extra_fields': extra_fields})
    
    def log_security_incident(self, incident: str, severity: str = "high", 
                            details: Dict[str, Any] = None):
        """Log security incidents and threats"""
        extra_fields = {
            'type': 'security_incident',
            'incident': incident,
            'severity': severity,
            'details': details or {}
        }
        
        self.logger.error(f"Security incident: {incident}", extra={'extra_fields': extra_fields})

def setup_logging(
    level: str = "INFO",
    format_type: str = "structured",  # "structured" or "console"
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """Setup centralized logging configuration"""
    
    # Determine log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatters
    if format_type == "structured":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    loggers_config = {
        'uvicorn.access': logging.WARNING,
        'uvicorn.error': logging.INFO,
        'celery': logging.INFO,
        'celery.task': logging.INFO,
        'celery.worker': logging.INFO,
    }
    
    for logger_name, logger_level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_level)

# Decorators for automatic logging
def log_performance(logger_name: str = "performance"):
    """Decorator to automatically log function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            perf_logger = PerformanceLogger(logger_name)
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                perf_logger.log_task_performance(
                    task_name=f"{func.__module__}.{func.__name__}",
                    execution_time=execution_time,
                    status="success"
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                perf_logger.log_task_performance(
                    task_name=f"{func.__module__}.{func.__name__}",
                    execution_time=execution_time,
                    status="error",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator

def log_api_call(logger_name: str = "api"):
    """Decorator to automatically log API calls"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # ✅ Fix: Handle FastAPI request injection
            from fastapi import Request
            
            # Extract request from args if available
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            start_time = time.time()
            
            # Generate or extract request ID
            if request:
                request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
                user_id = request.headers.get('user-id', 'anonymous')
            else:
                request_id = str(uuid.uuid4())
                user_id = 'system'
            
            request_id_ctx.set(request_id)
            user_id_ctx.set(user_id)
            
            logger = logging.getLogger(logger_name)
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log with proper metrics
                metrics = {
                    'type': 'api_call',
                    'function': func.__name__,
                    'execution_time_ms': round(execution_time * 1000, 2),
                    'status': 'success'
                }
                
                logger.info(
                    f"API call {func.__name__} completed successfully",
                    extra={'metrics': metrics}
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                metrics = {
                    'type': 'api_call',
                    'function': func.__name__,
                    'execution_time_ms': round(execution_time * 1000, 2),
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
                
                logger.error(
                    f"API call {func.__name__} failed: {str(e)}",
                    extra={'metrics': metrics}
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            request_id = str(uuid.uuid4())
            request_id_ctx.set(request_id)
            
            logger = logging.getLogger(logger_name)
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    f"Function {func.__name__} completed successfully",
                    extra={
                        'extra_fields': {
                            'type': 'function_call',
                            'function': func.__name__,
                            'execution_time_ms': round(execution_time * 1000, 2),
                            'status': 'success'
                        }
                    }
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(
                    f"Function {func.__name__} failed: {str(e)}",
                    extra={
                        'extra_fields': {
                            'type': 'function_call',
                            'function': func.__name__,
                            'execution_time_ms': round(execution_time * 1000, 2),
                            'status': 'error',
                            'error_type': type(e).__name__,
                            'error_message': str(e)
                        }
                    }
                )
                raise
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

# Factory functions for logger instances
def get_application_logger(name: str = None) -> ApplicationLogger:
    """Get application logger instance"""
    logger_name = name or "application"
    return ApplicationLogger(logger_name)

def get_performance_logger(name: str = None) -> PerformanceLogger:
    """Get performance logger instance"""
    logger_name = name or "performance"
    return PerformanceLogger(logger_name)

def get_security_logger(name: str = None) -> SecurityLogger:
    """Get security logger instance"""
    logger_name = name or "security"
    return SecurityLogger(logger_name)

# Global logger instances
perf_logger = PerformanceLogger()
app_logger = ApplicationLogger()
security_logger = SecurityLogger()

# Initialize logging on module import
def init_logging():
    """Initialize logging based on environment"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", "structured")
    log_file = os.getenv("LOG_FILE")
    
    setup_logging(
        level=log_level,
        format_type=log_format,
        log_file=log_file,
        enable_console=True
    )

# Auto-initialize if not in test environment
if not os.getenv("TESTING"):
    init_logging()
