from pydantic import BaseModel
from typing import Optional, Dict, Any

# ======================================
# STANDARDIZED API RESPONSE SCHEMAS
# ======================================

class APIResponse(BaseModel):
    """Standardized API response format for all endpoints"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None

class TaskResponse(APIResponse):
    """Response format for async task endpoints"""
    task_id: str
    queue: Optional[str] = None
    estimated_time: Optional[int] = None

class HealthResponse(APIResponse):
    """Response format for health check endpoints"""
    service: str
    status: str
    details: Optional[Dict[str, Any]] = None

# ======================================
# REQUEST SCHEMAS
# ======================================

class QueryRequest(BaseModel):
    query: str
    
class AnalyzeResponse(BaseModel):
    conversation_id: str
    user_id: str
    query: str
    

class QueryWebSearch(BaseModel):
    query: str
    max_links: int = 3
    max_workers: int = 3

class TitleUpdate(BaseModel):
    title: str

class QueryInput(BaseModel):
    rewrite_query: str
    use_web_search: bool
    rephrased_query: str
    direct_answer: str | None = None

class GenerateInput(BaseModel):
    conversation_id: str
    user_id: str
    rewrite_query: str
    use_web_search: bool = True
    use_retrieval: bool = True

class MessageInput(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None
    
class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None
    
class TriggerToolsRequest(BaseModel):
    query: str
    use_retrieval: bool = True
    use_web_search: bool = True