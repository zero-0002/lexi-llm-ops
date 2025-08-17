"""
📊 ENHANCED FASTAPI WITH STANDARDIZED LOGGING
===========================================
Production-ready FastAPI with structured logging, monitoring, and K8s support
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import cfg_settings
from app.api import rag, web_search, system
from app.api.legal_chat import legal_chat_router
from app.utils.logging_config import (
    setup_logging, app_logger, perf_logger, security_logger,
    log_api_call, log_performance, request_id_ctx, user_id_ctx
)
from app.celery_config import get_celery_status
import logging
import time
import uuid
from datetime import datetime

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title=cfg_settings.APP_NAME,
    version=cfg_settings.APP_VERSION,
    debug=cfg_settings.DEBUG,
    docs_url="/docs" if cfg_settings.DEBUG else None,
    redoc_url="/redoc" if cfg_settings.DEBUG else None,
)

# CORS configuration
BACKEND_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📊 REQUEST LOGGING MIDDLEWARE
# ============================
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    request_id_ctx.set(request_id)
    
    # Set user context
    user_id = request.headers.get("user-id", "anonymous")
    user_id_ctx.set(user_id)
    
    app_logger.info("Request started")
    
    # Calculate request size safely - check content-length header instead of reading body
    request_size = int(request.headers.get("content-length", 0))
    
    try:
        response = await call_next(request)
        execution_time = time.time() - start_time
        
        # Calculate response size from headers
        response_size = 0
        if hasattr(response, 'headers') and 'content-length' in response.headers:
            response_size = int(response.headers['content-length'])
        
        # Use perf_logger.log_api_request with proper parameters
        perf_logger.log_api_request(
            method=request.method,
            endpoint=str(request.url.path),
            status_code=response.status_code,
            response_time=execution_time,
            request_size=request_size,
            response_size=response_size
        )
        
        # Add request ID to response headers
        if hasattr(response, 'headers'):
            response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Log error with performance metrics
        perf_logger.log_api_request(
            method=request.method,
            endpoint=str(request.url.path),
            status_code=500,
            response_time=execution_time,
            request_size=request_size,
            response_size=0,
            error=str(e)
        )
        
        app_logger.error(f"Request failed: {str(e)}", exc_info=True)
        
        # Return proper error response
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"X-Request-ID": request_id}
        )

        
# 🏥 ENHANCED HEALTH CHECK ENDPOINTS
# ===================================

@app.get("/health-simple")
async def health_check_simple():
    """Simple health check without decorators"""
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
# @log_api_call  # Tạm thời tắt để test
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    app_logger.info("Health check requested", extra={'event': 'health_check'})
    return {
        "status": "healthy", 
        "version": cfg_settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ready")
# @log_api_call  # Tạm thời tắt để test
async def readiness_check():
    """Readiness check endpoint for Kubernetes"""
    try:
        # Check Celery status
        celery_status = get_celery_status()
        
        status = {
            "status": "ready",
            "version": cfg_settings.APP_VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "celery": {
                "workers_active": celery_status.get('workers_active', 0),
                "workers": celery_status.get('workers', [])
            }
        }
        
        app_logger.info(
            "Readiness check completed",
            extra={
                'event': 'readiness_check',
                'celery_workers': celery_status.get('workers_active', 0)
            }
        )
        
        return status
        
    except Exception as e:
        app_logger.error(
            "Readiness check failed",
            extra={
                'event': 'readiness_error',
                'error': str(e)
            },
            exc_info=True
        )
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/metrics")
# @log_api_call  # Tạm thời tắt để test
async def metrics():
    """Metrics endpoint for monitoring"""
    try:
        celery_status = get_celery_status()
        
        metrics_data = {
            "app": {
                "name": cfg_settings.APP_NAME,
                "version": cfg_settings.APP_VERSION,
                "uptime": "N/A",  # Can be calculated from start time
            },
            "celery": {
                "workers_active": celery_status.get('workers_active', 0),
                "workers": celery_status.get('workers', []),
                "queues": ["rag_queue", "embed_queue", "retrieval_queue", "link_extract_queue"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return metrics_data
        
    except Exception as e:
        app_logger.error(
            "Metrics collection failed",
            extra={
                'event': 'metrics_error',
                'error': str(e)
            },
            exc_info=True
        )
        return {"error": "Metrics collection failed", "timestamp": datetime.utcnow().isoformat()}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for K8s probes"""
    try:
        # Quick database connection check
        from app.config.database import db_manager
        redis_status = "ok"
        mongo_status = "ok"
        qdrant_status = "ok"
        
        try:
            # Test Redis
            redis_client = db_manager.get_redis_client(0)
            redis_client.ping()
        except:
            redis_status = "error"
            
        try:
            # Test MongoDB 
            mongo_client = db_manager.mongo_client
            mongo_client.admin.command('ismaster')
        except:
            mongo_status = "error"
            
        try:
            # Test Qdrant
            qdrant_client = db_manager.qdrant_client
            qdrant_client.get_collections()
        except:
            qdrant_status = "error"
            
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "redis": redis_status,
                "mongodb": mongo_status,
                "qdrant": qdrant_status
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Include API routers with logging
app.include_router(legal_chat_router, prefix=cfg_settings.API_V1_STR)
app.include_router(rag.router, prefix=cfg_settings.API_V1_STR)
app.include_router(web_search.router, prefix=cfg_settings.API_V1_STR)
app.include_router(system.router, prefix=cfg_settings.API_V1_STR)

# Startup logging
app_logger.info(
    "FastAPI application started",
    extra={
        'event': 'app_startup',
        'app_name': cfg_settings.APP_NAME,
        'version': cfg_settings.APP_VERSION,
        'host': cfg_settings.HOST,
        'port': cfg_settings.PORT,
        'debug': cfg_settings.DEBUG,
        'cors_origins': BACKEND_CORS_ORIGINS
    }
)

if __name__ == "__main__":
    import uvicorn
    
    app_logger.info(
        "Starting uvicorn server",
        extra={
            'event': 'server_start',
            'host': cfg_settings.HOST,
            'port': cfg_settings.PORT,
            'workers': cfg_settings.WORKERS,
            'reload': cfg_settings.DEBUG
        }
    )
    
    uvicorn.run(
        "app.main:app",
        host=cfg_settings.HOST,
        port=cfg_settings.PORT,
        workers=cfg_settings.WORKERS,
        reload=cfg_settings.DEBUG,
        log_config=None  # Use our custom logging
    )
