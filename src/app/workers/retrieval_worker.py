# app/workers/retrieval_worker.py
"""
Specialized Retrieval Worker - chỉ xử lý retrieval_queue tasks
"""
from app.celery_config import celery_app

# Chỉ import tasks liên quan đến Retrieval
from app.tasks.retrieval_tasks import *

if __name__ == "__main__":
    celery_app.start()
