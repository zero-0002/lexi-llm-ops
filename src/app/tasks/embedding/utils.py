"""
Utility functions for embedding tasks
"""
import logging
import redis
from typing import Dict, Any

logger = logging.getLogger(__name__)


from app.config.database import redis_client_web

def get_queue_status() -> Dict[str, Any]:
    """Get queue status - minimal logging"""
    try:
        return {
            'documents_pending': redis_client_web.llen("extracted_documents"),
            'chunks_processed': redis_client_web.llen("web_search_chunks"),
            'redis_status': 'connected'
        }
    except Exception as e:
        logger.error(f"Queue status error: {e}")
        return {
            'documents_pending': -1,
            'chunks_processed': -1,
            'redis_status': f'error: {str(e)}'
        }


def clear_queues() -> bool:
    """Clear all Redis queues"""
    try:
        doc_cleared = redis_client_web.delete("extracted_documents")
        chunk_cleared = redis_client_web.delete("web_search_chunks")
        
        logger.info(f"Cleared queues - Documents: {doc_cleared}, Chunks: {chunk_cleared}")
        return True
    except Exception as e:
        logger.error(f"Error clearing queues: {e}")
        return False


def validate_task_input(query: str, top_k: int) -> Dict[str, Any]:
    """Validate task input parameters"""
    errors = []
    
    if not isinstance(query, str) or not query.strip():
        errors.append(f"Invalid query: {type(query)}")
    
    if not isinstance(top_k, int) or top_k <= 0:
        errors.append(f"Invalid top_k: {top_k}")
    
    if top_k > 100:
        errors.append(f"top_k too large: {top_k} (max: 100)")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }