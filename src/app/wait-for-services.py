#!/usr/bin/env python3
"""
Wait for services to be ready before starting application
"""
import os
import sys
import time
import socket
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def wait_for_tcp_service(host: str, port: int, timeout: int = 60) -> bool:
    """Wait for TCP service to be available"""
    logger.info(f"⏳ Waiting for {host}:{port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                logger.info(f"✅ {host}:{port} is ready!")
                return True
        except Exception as e:
            logger.debug(f"Connection attempt failed: {e}")
        
        time.sleep(2)
    
    logger.error(f"❌ Timeout waiting for {host}:{port}")
    return False

def parse_redis_url(url: str) -> tuple:
    """Parse Redis URL to get host and port"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 6379
        return host, port
    except Exception:
        return 'localhost', 6379

def parse_mongo_url(url: str) -> tuple:
    """Parse MongoDB URL to get host and port"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 27017
        return host, port
    except Exception:
        return 'localhost', 27017

def parse_qdrant_url(url: str) -> tuple:
    """Parse Qdrant URL to get host and port"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 6333
        return host, port
    except Exception:
        return 'localhost', 6333

def main():
    """Wait for all required services"""
    logger.info("🔍 Checking service availability...")
    
    services_to_check = []
    
    # Check Redis (prioritize resolved URLs)
    if redis_url := os.getenv('CELERY_BROKER_URL'):
        host, port = parse_redis_url(redis_url)
        services_to_check.append(('Redis (Celery)', host, port))
    elif redis_host := os.getenv('REDIS_HOST'):
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        services_to_check.append(('Redis', redis_host, redis_port))
    
    # Check MongoDB
    if mongo_url := os.getenv('MONGO_URL'):
        host, port = parse_mongo_url(mongo_url)
        services_to_check.append(('MongoDB', host, port))
    elif mongo_host := os.getenv('MONGO_HOST'):
        mongo_port = int(os.getenv('MONGO_PORT', 27017))
        services_to_check.append(('MongoDB', mongo_host, mongo_port))
    
    # Check Qdrant
    if qdrant_url := os.getenv('QDRANT_URL'):
        host, port = parse_qdrant_url(qdrant_url)
        services_to_check.append(('Qdrant', host, port))
    elif qdrant_host := os.getenv('QDRANT_HOST'):
        qdrant_port = int(os.getenv('QDRANT_PORT', 6333))
        services_to_check.append(('Qdrant', qdrant_host, qdrant_port))
    
    # Wait for all services
    all_ready = True
    for service_name, host, port in services_to_check:
        if not wait_for_tcp_service(host, port):
            logger.error(f"❌ {service_name} ({host}:{port}) is not ready")
            all_ready = False
        else:
            logger.info(f"✅ {service_name} ({host}:{port}) is ready")
    
    if not all_ready:
        logger.error("❌ Some services are not ready. Exiting...")
        sys.exit(1)
    
    logger.info("🎉 All services are ready!")

if __name__ == "__main__":
    main()
