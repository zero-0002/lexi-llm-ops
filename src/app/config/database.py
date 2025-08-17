"""
Database connection manager with proper connection pooling and monitoring
Supports both development and production K8s environments
"""
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import redis
from qdrant_client import QdrantClient
import logging
from typing import Optional
from .settings import get_mongo_url, get_qdrant_url, get_redis_url, settings

# Get settings instance

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Centralized database connection management"""
    
    def __init__(self):
        self._mongo_client: Optional[MongoClient] = None
        self._mongo_client_async: Optional[AsyncIOMotorClient] = None
        self._redis_clients: dict = {}
        self._qdrant_client: Optional[QdrantClient] = None
    
    @property
    def mongo_client(self) -> MongoClient:
        """Get synchronous MongoDB client"""
        if self._mongo_client is None:
            mongo_url = get_mongo_url()
            logger.info(f"Connecting to MongoDB: {mongo_url}")
            self._mongo_client = MongoClient(
                mongo_url,
                connectTimeoutMS=10000,
                serverSelectionTimeoutMS=10000,
                maxPoolSize=50,
                minPoolSize=5
            )
        return self._mongo_client
    
    @property
    def mongo_client_async(self) -> AsyncIOMotorClient:
        """Get asynchronous MongoDB client"""
        if self._mongo_client_async is None:
            mongo_url = get_mongo_url()
            logger.info(f"Connecting to async MongoDB: {mongo_url}")
            self._mongo_client_async = AsyncIOMotorClient(
                mongo_url,
                maxPoolSize=50,
                minPoolSize=5
            )
        return self._mongo_client_async
    
    def get_redis_client(self, db: int = 0) -> redis.Redis:
        """Get Redis client for specific database"""
        if db not in self._redis_clients:
            redis_url = get_redis_url(db)
            logger.info(f"Connecting to Redis DB {db}: {redis_url}")
            self._redis_clients[db] = redis.from_url(
                redis_url,
                decode_responses=True,
                max_connections=20,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
        return self._redis_clients[db]
    
    @property
    def qdrant_client(self) -> QdrantClient:
        """Get Qdrant vector database client"""
        if self._qdrant_client is None:
            qdrant_url = get_qdrant_url()
            logger.info(f"Connecting to Qdrant: {qdrant_url}")
            self._qdrant_client = QdrantClient(
                url=qdrant_url,
                api_key=settings.QDRANT_API_KEY,
                timeout=30.0
            )
        return self._qdrant_client
    
    def close_connections(self):
        """Close all database connections"""
        if self._mongo_client:
            self._mongo_client.close()
        if self._mongo_client_async:
            self._mongo_client_async.close()
        for redis_client in self._redis_clients.values():
            redis_client.close()
        if self._qdrant_client:
            self._qdrant_client.close()

# Database manager instance (singleton pattern)
_db_manager_instance = None

def get_database_manager() -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance

# Global database manager instance
db_manager = get_database_manager()

# Legacy compatibility - gradually migrate to db_manager
mongo_client = db_manager.mongo_client
mongo_client_async = db_manager.mongo_client_async

# Database and collections
db = mongo_client[settings.MONGO_DB_NAME]
db_async = mongo_client_async[settings.MONGO_DB_NAME]

conversations_col = db["conversations"]
messages_col = db["messages"]
analysis_results_col = db["analysis_results"]

conversations_col_async = db_async["conversations"]
messages_col_async = db_async["messages"]
analysis_results_col_async = db_async["analysis_results"]

# Redis clients for different use cases
redis_cache = db_manager.get_redis_client(0)      # General cache
redis_sessions = db_manager.get_redis_client(1)   # Session storage
redis_embed_cache = db_manager.get_redis_client(2) # Embedding cache
redis_celery_broker = db_manager.get_redis_client(3) # Celery broker
redis_celery_result = db_manager.get_redis_client(4) # Celery results

# Legacy aliases for backward compatibility
redis_client_web = redis_sessions                  # Web search cache (DB 1)
redis_client_retrieval = redis_embed_cache         # Retrieval cache (DB 2)
redis_client_streaming = redis_celery_result       # Streaming cache (DB 4)

# Qdrant vector database
qdrant_client = db_manager.qdrant_client
