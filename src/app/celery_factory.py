"""
Celery App Factory - Tạo celery app với các task modules khác nhau
"""
import os
from celery import Celery
from app.config.settings import get_celery_broker_url, get_celery_result_backend_url

def create_celery_app(name: str, task_modules: list, default_queue: str = 'celery'):
    """
    Tạo Celery app với task modules cụ thể
    
    Args:
        name: Tên của celery app
        task_modules: List các modules chứa tasks
        default_queue: Queue mặc định
    """
    broker_url = get_celery_broker_url()
    backend_url = get_celery_result_backend_url()
    
    celery_app = Celery(
        name,
        broker=broker_url,
        backend=backend_url,
        include=task_modules
    )
    
    # Enhanced Celery configuration
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_concurrency=2,
        worker_max_tasks_per_child=1000,
        task_default_queue=default_queue,
        task_default_exchange='celery',
        task_default_exchange_type='direct',
        task_default_routing_key=default_queue,
        
        # Worker pool configuration
        worker_pool='prefork',  # Force prefork pool for task isolation
        
        # Queue configuration
        task_routes={},  # Will be set by individual workers
        
        # Monitoring and logging
        worker_send_task_events=True,
        task_send_sent_event=True,
        
        # Performance tuning
        worker_disable_rate_limits=True,
        task_ignore_result=False,
        result_expires=3600,  # 1 hour
        
        # Error handling
        task_reject_on_worker_lost=True,
        task_acks_on_failure_or_timeout=True,
    )
    
    return celery_app
