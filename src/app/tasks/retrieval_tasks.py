import logging
import time
import json
import redis
from app.celery_config import celery_app
from app.services.rag_service import LegalRAGService
from typing import List

rag_service = LegalRAGService()
from app.config.database import redis_client_retrieval
logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.retrieval_tasks.retrieval_document", queue="retrieval_queue")
def retrieval_document(query: str):
    logger.info(f"Retrieving chunks for query: {query}")
    start_time = time.time()
    chunks = rag_service.search("legal_documents_collection", query)
    duration = time.time() - start_time
    logger.info(f"Retrieval completed in {duration:.2f} seconds")
    saved_count = save_chunks_to_redis(chunks)
    logger.info(f"Saved {saved_count} chunks to Redis")
    return chunks

def save_chunks_to_redis(chunks: List) -> int:
    if not chunks:
        logger.warning("No chunks to save")
        return 0
    try:
        # Xóa list cũ trước khi lưu
        redis_client_retrieval.delete("retrieval_chunks")
        # Lưu từng chunk dưới dạng JSON string
        count = 0
        for chunk in chunks:
            redis_client_retrieval.lpush("retrieval_chunks", json.dumps(chunk))
            count += 1
    except Exception as e:
        logger.error(f"Error saving chunks: {e}")
        return 0
    return count
