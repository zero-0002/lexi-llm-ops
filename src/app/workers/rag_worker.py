# app/workers/rag_worker.py
"""
Specialized RAG Worker - chỉ xử lý rag_queue tasks
"""
from app.celery_config import celery_app

# Chỉ import tasks liên quan đến RAG
from app.tasks.legal_rag_tasks import *

if __name__ == "__main__":
    celery_app.start()
