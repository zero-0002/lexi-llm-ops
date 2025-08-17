# app/workers/embed_worker.py
"""
Specialized Embedding Worker - chỉ xử lý embed_queue tasks
"""
from app.celery_config import celery_app

# Chỉ import tasks liên quan đến Embedding
from app.tasks.legal_embedding_tasks import *

if __name__ == "__main__":
    celery_app.start()
