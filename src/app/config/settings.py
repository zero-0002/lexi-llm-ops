"""
Production-ready configuration management for Legal Chatbot RAG System
Handles environment variables, validation, and service discovery for K8s deployment
"""
import os
import logging
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator 
from dotenv import load_dotenv
import json

load_dotenv()

# Setup logger for settings
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application configuration with environment variable support"""
    
    # Application Settings
    APP_NAME: str = "Legal Chatbot RAG"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "6379")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # MongoDB Configuration
    MONGO_HOST: str = os.getenv("MONGO_HOST", "mongodb")
    MONGO_PORT: str = os.getenv("MONGO_PORT", "27017")
    MONGO_USER: str = os.getenv("MONGO_USER", "admin")
    MONGO_PASSWORD: str = os.getenv("MONGO_PASSWORD", "password123")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "chat_db")
    MONGO_AUTH_SOURCE: str = os.getenv("MONGO_AUTH_SOURCE", "admin")
    
    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "qdrant")
    QDRANT_PORT: str = os.getenv("QDRANT_PORT", "6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    
    # API and External Services
    INTERNAL_API_BASE: str = "http://localhost:8000"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Model Configuration
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"
    PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    SIMILARITY_THRESHOLD: float = 0.95
    
    # Task Configuration
    TASK_TIMEOUT: int = 300  # 5 minutes
    MAX_RETRIES: int = 3
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra environment variables

# Global settings instance
settings = Settings()

# Database URL builders using environment variables
def get_redis_url(db: int = 0) -> str:
    """Get Redis URL using environment variables"""
    redis_host = settings.REDIS_HOST
    redis_port = settings.REDIS_PORT
    
    if settings.REDIS_PASSWORD:
        return f"redis://:{settings.REDIS_PASSWORD}@{redis_host}:{redis_port}/{db}"
    else:
        return f"redis://{redis_host}:{redis_port}/{db}"

def get_mongo_url() -> str:
    """Get MongoDB URL using environment variables"""
    mongo_host = settings.MONGO_HOST
    mongo_port = settings.MONGO_PORT
    mongo_user = settings.MONGO_USER
    mongo_password = settings.MONGO_PASSWORD
    mongo_db = settings.MONGO_DB_NAME
    mongo_auth_source = settings.MONGO_AUTH_SOURCE
    
    return f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}?authSource={mongo_auth_source}"

def get_qdrant_url() -> str:
    """Get Qdrant URL using environment variables"""
    qdrant_host = settings.QDRANT_HOST
    qdrant_port = settings.QDRANT_PORT
    
    return f"http://{qdrant_host}:{qdrant_port}"

# Celery configuration using Redis with DNS fallback
def get_celery_broker_url() -> str:
    """Get Celery broker URL - prefer environment variable, fallback to Redis DB 3 with DNS fallback"""
    broker_url = os.getenv('CELERY_BROKER_URL')
    if broker_url:
        logger.info(f"🔄 Using CELERY_BROKER_URL from environment: {broker_url}")
        return broker_url
    
    # Use fallback mechanism with DNS -> IP fallback
    fallback_url = get_redis_url_with_fallback(3)
    logger.info(f"🔄 Generated Celery broker URL with fallback: {fallback_url}")
    return fallback_url

def get_celery_result_backend_url() -> str:
    """Get Celery result backend URL - prefer environment variable, fallback to Redis DB 4 with DNS fallback"""
    result_backend = os.getenv('CELERY_RESULT_BACKEND')
    if result_backend:
        logger.info(f"📊 Using CELERY_RESULT_BACKEND from environment: {result_backend}")
        return result_backend
    
    # Use fallback mechanism with DNS -> IP fallback
    fallback_url = get_redis_url_with_fallback(4)
    logger.info(f"📊 Generated Celery result backend URL with fallback: {fallback_url}")
    return fallback_url

def get_redis_url_with_fallback(db: int = 0) -> str:
    """
    Get Redis URL with DNS-first approach, fallback to IP for K8s environments
    
    Strategy:
    1. Try DNS hostname first (preferred for service discovery)
    2. If DNS resolution fails, fallback to direct IP resolution
    3. Enhanced error logging for troubleshooting
    """
    redis_host = settings.REDIS_HOST
    redis_port = settings.REDIS_PORT
    
    # Build URLs for both approaches
    def build_url(host: str) -> str:
        if settings.REDIS_PASSWORD:
            return f"redis://:{settings.REDIS_PASSWORD}@{host}:{redis_port}/{db}"
        else:
            return f"redis://{host}:{redis_port}/{db}"
    
    # Try DNS resolution first
    try:
        import socket
        logger.info(f"🔍 Attempting DNS resolution for Redis host: {redis_host}")
        resolved_ip = socket.gethostbyname(redis_host)
        
        hostname_url = build_url(redis_host)
        ip_url = build_url(resolved_ip)
        
        logger.info(f"✅ DNS resolution successful: {redis_host} -> {resolved_ip}")
        logger.info(f"🏷️  Hostname URL: {hostname_url}")
        logger.info(f"🔢 IP URL: {ip_url}")
        
        # Return hostname URL (DNS-first approach)
        # IP URL is available for manual fallback if needed
        return hostname_url
        
    except socket.gaierror as e:
        logger.warning(f"⚠️  DNS resolution failed for {redis_host}: {e}")
        logger.info(f"🔄 Falling back to hostname-based URL without resolution")
    except Exception as e:
        logger.error(f"❌ Unexpected error during DNS resolution: {e}")
        logger.info(f"🔄 Falling back to hostname-based URL")
    
    # Fallback: return URL with original hostname
    fallback_url = build_url(redis_host)
    logger.info(f"🔄 Using fallback Redis URL: {fallback_url}")
    return fallback_url

# Service discovery for Kubernetes
def get_service_url(service_name: str, port: int = 80, namespace: str = "default") -> str:
    """
    Generate Kubernetes service URL
    In K8s: http://service-name.namespace.svc.cluster.local:port
    """
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return f"http://{service_name}.{namespace}.svc.cluster.local:{port}"
    return settings.INTERNAL_API_BASE

# Legacy compatibility - will be deprecated
cfg_settings = settings
