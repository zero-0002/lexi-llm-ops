# app/workers/link_worker.py
"""
Specialized Link Extract Worker - chỉ xử lý link_extract_queue tasks
"""
from app.celery_config import celery_app

# Chỉ import tasks liên quan đến Link Extract
from app.tasks.link_extract_tasks import *

if __name__ == "__main__":
    celery_app.start()
