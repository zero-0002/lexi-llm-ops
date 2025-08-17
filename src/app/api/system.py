from fastapi import APIRouter
from app.celery_config import celery_app, get_celery_status
from app.models.api_schema import HealthResponse
from datetime import datetime

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
def system_health():
    """Health check for system service"""
    return HealthResponse(
        success=True,
        message="System service is healthy",
        service="system",
        status="healthy",
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/worker")
def check_worker_status():
    """Enhanced worker status check with better timeout and error handling"""
    try:
        # Use the comprehensive status function
        celery_status = get_celery_status()
        
        if 'error' in celery_status:
            return {
                "status": "error", 
                "detail": f"Celery error: {celery_status['error']}",
                "workers_active": 0
            }
        
        workers_active = celery_status.get('workers_active', 0)
        
        if workers_active == 0:
            return {
                "status": "down", 
                "detail": "No active Celery workers detected",
                "workers_active": 0,
                "broker_url": celery_status.get('broker_url', 'unknown'),
                "backend_url": celery_status.get('backend_url', 'unknown')
            }
        
        return {
            "status": "up", 
            "workers_active": workers_active,
            "workers": celery_status.get('workers', []),
            "broker_url": celery_status.get('broker_url'),
            "backend_url": celery_status.get('backend_url')
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "detail": f"Exception: {str(e)}",
            "workers_active": 0
        }