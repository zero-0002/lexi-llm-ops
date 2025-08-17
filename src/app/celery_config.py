"""
📊 ENHANCED CELERY CONFIGURATION
===================================================
Production-ready Celery setup with structured logging, monitoring, and K8s support
"""
import os
import redis
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure, worker_ready, worker_shutdown
from kombu import Queue
from app.config.settings import settings, get_redis_url, get_celery_broker_url, get_celery_result_backend_url
from app.utils.logging_config import perf_logger, app_logger, task_id_ctx
import logging
import time
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

def get_celery_broker_url():
    """Get Celery broker URL using environment variables"""
    from app.config.settings import get_celery_broker_url as _get_celery_broker_url
    broker_url = _get_celery_broker_url()
    logger.info(f"🔄 Using Celery broker from environment: {broker_url}")
    return broker_url

def get_celery_result_backend_url():
    """Get Celery result backend URL using environment variables"""
    from app.config.settings import get_celery_result_backend_url as _get_celery_result_backend_url
    result_backend = _get_celery_result_backend_url()
    logger.info(f"📊 Using Celery result backend from environment: {result_backend}")
    return result_backend

# Determine which tasks to include based on worker type
WORKER_TYPE = os.getenv('WORKER_TYPE', 'all')

task_includes = {
    'all': [
        "app.tasks.legal_embedding_tasks",
        "app.tasks.legal_rag_tasks", 
        "app.tasks.retrieval_tasks",
        "app.tasks.link_extract_tasks"
    ],
    'rag': ["app.tasks.legal_rag_tasks"],
    'embed': ["app.tasks.legal_embedding_tasks"],
    'retrieval': ["app.tasks.retrieval_tasks"],
    'link': ["app.tasks.link_extract_tasks"]
}

# Create Celery app with enhanced configuration
celery_app = Celery(
    "legal_chatbot_tasks",
    broker=get_celery_broker_url(),
    backend=get_celery_result_backend_url(),
    include=task_includes.get(WORKER_TYPE, task_includes['all'])
)

# Enhanced Celery configuration for Docker networking
celery_app.conf.update(
    # Connection settings with retries for Docker networking
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=20,
    broker_connection_timeout=30,
    
    # Redis connection pool settings
    broker_pool_limit=10,
    redis_socket_timeout=30,
    redis_socket_connect_timeout=30,
    redis_retry_on_timeout=True,
    redis_health_check_interval=30,
    
    # Additional Redis settings for stability
    redis_max_connections=20,
    redis_retry_on_error=[redis.exceptions.ConnectionError, redis.exceptions.TimeoutError],
)

# Enhanced Celery configuration for K8s
celery_app.conf.update(
    # Task execution
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Performance optimizations
    task_compression='gzip',
    result_compression='gzip',
    
    # Reliability
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Monitoring
    task_track_started=True,
    task_send_sent_event=True,
    worker_send_task_events=True,
    
    # Timeouts
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    
    # Retries
    task_retry_backoff=True,
    task_retry_backoff_max=700,
    task_retry_jitter=False,
    
    # Results
    result_expires=3600,  # 1 hour
    
    # Worker configuration
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)

# Queue configuration based on worker type
queue_config = {
    'all': (
        Queue('rag_queue', routing_key='rag.#'),
        Queue('embed_queue', routing_key='embed.#'),
        Queue('retrieval_queue', routing_key='retrieval.#'),
        Queue('link_extract_queue', routing_key='link_extract.#'),
    ),
    'rag': (Queue('rag_queue', routing_key='rag.#'),),
    'embed': (Queue('embed_queue', routing_key='embed.#'),),
    'retrieval': (Queue('retrieval_queue', routing_key='retrieval.#'),),
    'link': (Queue('link_extract_queue', routing_key='link_extract.#'),)
}

# Task routing configuration based on worker type
routing_config = {
    'all': {
        'app.tasks.legal_rag_tasks.*': {
            'queue': 'rag_queue',
            'routing_key': 'rag.task'
        },
        'app.tasks.legal_embedding_tasks.*': {
            'queue': 'embed_queue',
            'routing_key': 'embed.task'
        },
        'app.tasks.retrieval_tasks.*': {
            'queue': 'retrieval_queue',
            'routing_key': 'retrieval.task'
        },
        'app.tasks.link_extract_tasks.*': {
            'queue': 'link_extract_queue',
            'routing_key': 'link_extract.task'
        }
    },
    'rag': {
        'app.tasks.legal_rag_tasks.*': {
            'queue': 'rag_queue',
            'routing_key': 'rag.task'
        }
    },
    'embed': {
        'app.tasks.legal_embedding_tasks.*': {
            'queue': 'embed_queue',
            'routing_key': 'embed.task'
        }
    },
    'retrieval': {
        'app.tasks.retrieval_tasks.*': {
            'queue': 'retrieval_queue',
            'routing_key': 'retrieval.task'
        }
    },
    'link': {
        'app.tasks.link_extract_tasks.*': {
            'queue': 'link_extract_queue',
            'routing_key': 'link_extract.task'
        }
    }
}

# Apply configurations based on worker type
celery_app.conf.task_queues = queue_config.get(WORKER_TYPE, queue_config['all'])
celery_app.conf.task_routes = routing_config.get(WORKER_TYPE, routing_config['all'])

# Logging configuration
logger.info(f"🔄 Celery configured with broker: {get_celery_broker_url()}")
logger.info(f"📊 Task queues: {[q.name for q in celery_app.conf.task_queues]}")

# Task state tracking
task_performance = {}

@task_prerun.connect
def log_task_start(task_id, task, *args, **kwargs):
    """Log task start with performance tracking"""
    task_start_time = time.time()
    task_performance[task_id] = {
        'start_time': task_start_time,
        'task_name': task.name,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    token = task_id_ctx.set(task_id)
    try:
        perf_logger.info(
            "Task started",
            extra={
                'task_name': task.name,
                'task_id': task_id,
                'queue': getattr(task, 'queue', 'default'),
                'args_count': len(args) if args else 0,
                'kwargs_keys': list(kwargs.keys()) if kwargs else [],
                'event': 'task_start'
            }
        )
    finally:
        task_id_ctx.reset(token)

@task_postrun.connect
def log_task_completion(task_id, task, retval, state, *args, **kwargs):
    """Log task completion with performance metrics"""
    if task_id in task_performance:
        start_time = task_performance[task_id]['start_time']
        duration = time.time() - start_time
        
        token = task_id_ctx.set(task_id)
        try:
            perf_logger.info(
                "Task completed",
                extra={
                    'task_name': task.name,
                    'task_id': task_id,
                    'duration': duration,
                    'state': state,
                    'success': state == 'SUCCESS',
                    'event': 'task_complete'
                }
            )
        finally:
            task_id_ctx.reset(token)
        
        # Clean up tracking
        del task_performance[task_id]

@task_failure.connect
def log_task_failure(task_id, exception, einfo, *args, **kwargs):
    """Log task failures with error details"""
    token = task_id_ctx.set(task_id)
    try:
        app_logger.error(
            f"Task failed: {exception}",
            extra={
                'task_id': task_id,
                'exception': str(exception),
                'traceback': str(einfo),
                'event': 'task_failure'
            }
        )
    finally:
        task_id_ctx.reset(token)

@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Log when worker is ready"""
    app_logger.info(f"🟢 Celery worker {sender.hostname} is ready")

@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Log when worker shuts down"""
    app_logger.info(f"🔴 Celery worker {sender.hostname} is shutting down")

# Health check utility
def get_celery_status():
    """Get Celery worker status for health checks"""
    try:
        # Check active workers
        active_workers = celery_app.control.inspect().active()
        registered_tasks = celery_app.control.inspect().registered()
        stats = celery_app.control.inspect().stats()
        
        status = {
            'workers_active': len(active_workers) if active_workers else 0,
            'workers': list(active_workers.keys()) if active_workers else [],
            'registered_tasks': registered_tasks,
            'stats': stats,
            'broker_url': celery_app.conf.broker_url,
            'backend_url': celery_app.conf.result_backend
        }
        
        app_logger.info(
            "Celery status check",
            extra={
                'event': 'celery_status',
                'workers_count': status['workers_active'],
                'workers': status['workers']
            }
        )
        
        return status
    except Exception as e:
        app_logger.error(
            "Failed to get Celery status",
            extra={
                'event': 'celery_status_error',
                'error': str(e)
            },
            exc_info=True
        )
        return {'error': str(e), 'workers_active': 0}

# Health check task for monitoring
@celery_app.task(name="health_check")
def health_check():
    """Health check task for monitoring"""
    return {"status": "healthy", "worker": "active"}

# Export for use in other modules
__all__ = ['celery_app', 'get_celery_status']
