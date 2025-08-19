"""
Centralized HTTP client for internal service communication
Handles service discovery, retries, and circuit breaker pattern
"""
import httpx
import asyncio
import logging
from typing import Dict, Any, Optional
from .settings import cfg_settings
import os

logger = logging.getLogger(__name__)

class InternalAPIClient:
    """HTTP client for internal service communication with K8s service discovery"""
    
    def __init__(self):
        self.base_url = self._get_base_url()
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        
    def _get_base_url(self) -> str:
        """Get base URL - brain calls itself via localhost"""
        # Brain should always call itself on localhost since it's in same pod
        return "http://localhost:8000"
    
    async def post(self, endpoint: str, data: Dict[str, Any], retries: int = 1) -> Dict[str, Any]:
        """POST request with retries and error handling"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=data)
                    response.raise_for_status()
                    return response.json()
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code} for {url}: {e.response.text}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                logger.error(f"Connection error for {url}: {str(e)}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
                
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {str(e)}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(1)
    
    async def web_search(self, query: str) -> Dict[str, Any]:
        """Call web search service"""
        return await self.post("/api/rag/web_search", {"query": query})
    
    async def laws_retrieval(self, query: str) -> Dict[str, Any]:
        """Call laws retrieval service"""
        return await self.post("/api/rag/retrieve", {"query": query})
    
    async def generate_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call response generation service"""
        return await self.post("/api/legal-chat/generate-legal-response", payload)

# Global API client instance
api_client = InternalAPIClient()
