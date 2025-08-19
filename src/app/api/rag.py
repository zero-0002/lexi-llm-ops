from fastapi import APIRouter
from app.models.api_schema import QueryRequest, TaskResponse, HealthResponse
from app.tasks.retrieval_tasks import retrieval_document
from app.tasks.link_extract_tasks import get_links_and_extract_task
from app.tasks.legal_embedding_tasks import embed_query_task, search_legal_documents
from datetime import datetime

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/health")
def rag_health():
    """Health check for RAG service"""
    return HealthResponse(
        success=True,
        message="RAG service is healthy",
        service="rag",
        status="healthy",
        timestamp=datetime.utcnow().isoformat()
    )


@router.post("/retrieve")
def retrieve_docs(request: QueryRequest):
    """Retrieve legal documents"""
    try:
        task = retrieval_document.apply_async(
            args=[request.query],
            queue='retrieval_queue',
        )
        return TaskResponse(
            success=True,
            message="Document retrieval task started successfully",
            task_id=task.id,
            queue='retrieval_queue',
            estimated_time=30,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return TaskResponse(
            success=False,
            message="Failed to start retrieval task",
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )


@router.post("/web_search")  
def web_search(request: QueryRequest):
    """Web search for legal information"""
    try:
        task = get_links_and_extract_task.apply_async(
            args=[request.query, 5],  # max_links = 5
            queue='link_extract_queue',
        )
        return TaskResponse(
            success=True,
            message="Web search task started successfully",
            task_id=task.id,
            queue='link_extract_queue',
            estimated_time=60,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return TaskResponse(
            success=False,
            message="Failed to start web search task",
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )

@router.post("/embed")
def embed_query(request: QueryRequest):
    """Embed query for similarity search"""
    try:
        task = embed_query_task.apply_async(
            args=[request.query],
            queue='embed_queue',
        )
        return TaskResponse(
            success=True,
            message="Embedding task started successfully",
            task_id=task.id,
            queue='embed_queue',
            estimated_time=10,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return TaskResponse(
            success=False,
            message="Failed to start embedding task",
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )

@router.post("/search")
def search_documents(request: QueryRequest):
    """Search legal documents"""
    try:
        task = search_legal_documents.apply_async(
            args=[request.query, 5],  # top_k = 5
            queue='embed_queue',
        )
        return TaskResponse(
            success=True,
            message="Document search task started successfully",
            task_id=task.id,
            queue='embed_queue',
            estimated_time=15,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return TaskResponse(
            success=False,
            message="Failed to start search task",
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )