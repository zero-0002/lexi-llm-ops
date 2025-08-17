"""
Simplified logging utility - Production optimized
No file-based thread logging, pure JSON stdout/stderr for K8s
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar

# Context variables for request tracking
request_id_ctx: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_ctx: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
task_id_ctx: ContextVar[Optional[str]] = ContextVar('task_id', default=None)

class ProductionFormatter(logging.Formatter):
    """Production JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        
        # Base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add context if available
        if request_id := request_id_ctx.get():
            log_entry["request_id"] = request_id
        if user_id := user_id_ctx.get():
            log_entry["user_id"] = user_id
        if task_id := task_id_ctx.get():
            log_entry["task_id"] = task_id
            
        # Add extra fields from record
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
            
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_production_logging(log_level: str = "INFO") -> None:
    """
    Setup production logging - stdout only, JSON format
    Perfect for Docker/K8s environments
    """
    
    # Remove all existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ProductionFormatter())
    
    # Configure root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate logs
    root_logger.propagate = False
    
    logging.info("Production logging initialized", extra={
        'extra_fields': {
            'log_level': log_level,
            'format': 'json',
            'output': 'stdout'
        }
    })

def get_logger(name: str) -> logging.Logger:
    """Get logger instance with consistent configuration"""
    return logging.getLogger(name)

def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs
) -> None:
    """Log with additional context fields"""
    
    extra_fields = {}
    
    # Add performance metrics if provided
    if 'duration' in kwargs:
        extra_fields['duration_ms'] = kwargs['duration']
    if 'status_code' in kwargs:
        extra_fields['status_code'] = kwargs['status_code']
    if 'operation' in kwargs:
        extra_fields['operation'] = kwargs['operation']
        
    # Add business context
    if 'query' in kwargs:
        extra_fields['query_length'] = len(kwargs['query'])
    if 'document_count' in kwargs:
        extra_fields['document_count'] = kwargs['document_count']
        
    # Log with structured data
    getattr(logger, level.lower())(
        message,
        extra={'extra_fields': extra_fields}
    )

# Legacy compatibility functions - simplified versions
def schedule_log_consolidation(delay_seconds: int = 15) -> str:
    """
    Legacy compatibility - returns dummy task ID
    In production, log aggregation handles this automatically
    """
    logger = get_logger(__name__)
    logger.info("Log consolidation not needed in production", extra={
        'extra_fields': {
            'reason': 'stdout_logging_with_aggregation',
            'delay_seconds': delay_seconds
        }
    })
    return f"no_consolidation_needed_{int(datetime.utcnow().timestamp())}"

def consolidate_extraction_logs() -> None:
    """
    Legacy compatibility - no-op in production
    Structured JSON logging to stdout eliminates need for file consolidation
    """
    logger = get_logger(__name__)
    logger.debug("Log consolidation skipped", extra={
        'extra_fields': {
            'reason': 'json_structured_logging_active'
        }
    })
