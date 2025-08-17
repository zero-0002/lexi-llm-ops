from fastapi import APIRouter
from app.models.api_schema import QueryWebSearch, QueryRequest
from app.tasks.link_extract_tasks import get_links_and_extract_task
from app.services.web_search_service import WebSearchService
router = APIRouter(prefix="/web-search", tags=["web_search"])

web_search_service = WebSearchService()


@router.get("/health")
def web_search_health():
    """Health check for web search service"""
    return {"status": "healthy", "service": "web_search"}


# @router.post("/web_search")
# def web_search(request: QueryRequest):
#     return web_search_service.search(request.query)


@router.post("/web_search")
def get_links_and_extract(data: QueryWebSearch):
    """
    Triggers the link extraction task with the specified parameters.
    """
    try:
        id_task = get_links_and_extract_task.apply_async(args=[data.query, data.max_links, data.max_workers], queue='link_extract_queue')
        return {"task_id": id_task.id, "message": "Link extraction task started successfully."}
    except Exception as e:
        return {"error": str(e)}

