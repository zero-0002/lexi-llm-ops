import redis
import json
from typing import Optional
from app.config.database import redis_client_cache

class ExtractionCache:
    def __init__(self):
        self.redis_client = redis_client_cache
        self.ttl = 24 * 60 * 60  # 24 hours
    
    def get(self, url: str) -> Optional[dict]:
        cached = self.redis_client.get(f"extract:{url}")
        return json.loads(cached) if cached else None
    
    def set(self, url: str, result: dict):
        self.redis_client.setex(f"extract:{url}", self.ttl, json.dumps(result))
