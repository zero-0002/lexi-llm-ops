"""
Simplified utilities - Production ready
Only essential functions, no complex logging management
"""
import uuid
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

def generate_id() -> str:
    """Generate unique ID"""
    return str(uuid.uuid4())

def current_time():
    """Get current time in Vietnam timezone"""
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

# ==================== QDRANT INTEGRATION ====================
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
    from app.config.database import get_database_manager

    def get_qdrant_client():
        """Get Qdrant client from database manager"""
        db_manager = get_database_manager()
        return db_manager.qdrant_client

    def qdrant_insert_point(vector, payload, point_id):
        """Insert point vào Qdrant collection"""
        try:
            qdrant_client = get_qdrant_client()
            qdrant_client.upsert(
                collection_name="chat_questions",
                points=[
                    PointStruct(id=point_id, vector=vector, payload=payload)
                ]
            )
            return True
        except Exception as e:
            logger.error(f"Error inserting point to Qdrant: {e}")
            return False

except ImportError:
    logger.warning("Qdrant client not available")
    
    def get_qdrant_client():
        logger.error("Qdrant client not available")
        return None
    
    def qdrant_insert_point(vector, payload, point_id):
        logger.error("Qdrant client not available")
        return False
