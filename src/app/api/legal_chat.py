"""
Enhanced API routes for legal chat with improved naming and structure
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from app.models.api_schema import MessageInput, AnalyzeResponse, GenerateInput
from app.services.legal_chat_service import LegalChatService
from app.config.database import redis_client_web,db_async
from app.config.settings import cfg_settings
from app.utils.utils_essential import current_time    
from fastapi import Body,Path, Query
from fastapi.responses import StreamingResponse, JSONResponse
import logging
from typing import Optional
import json
import asyncio
import redis.asyncio as redis_async
import time
import os
import socket

logger = logging.getLogger(__name__)

def get_redis_url(db: int = 3) -> str:
    """Get Redis URL with proper IP resolution for streaming (using dedicated streaming DB)"""
    try:
        # Try to get resolved IP from environment (set by resolve-redis-ip.py)
        redis_ip = os.environ.get('REDIS_IP')
        if redis_ip:
            redis_url = f"redis://{redis_ip}:6379/{db}"
            logger.info(f"🔗 Using resolved Redis IP: {redis_url}")
            return redis_url
    except Exception:
        pass
    
    try:
        # Fallback: resolve hostname manually
        redis_host = os.environ.get('REDIS_HOST', 'redis')
        redis_ip = socket.gethostbyname(redis_host)
        redis_url = f"redis://{redis_ip}:6379/{db}"
        logger.info(f"🔗 Resolved Redis hostname {redis_host} -> {redis_url}")
        return redis_url
    except Exception as e:
        logger.warning(f"⚠️ Redis resolution failed: {e}, using localhost fallback")
        return f"redis://localhost:6379/{db}"

# Create router with enhanced configuration
legal_chat_router = APIRouter(
    prefix="/legal-chat", 
    tags=["legal-consultation"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Initialize legal chat service
legal_chat_service = LegalChatService()

@legal_chat_router.post("/send-query")
async def send_legal_query(data: MessageInput):
    """
    Send legal consultation query
    Enhanced endpoint for legal-specific message handling
    """
    try:
        logger.info(f"Received legal query from user: {data.user_id}")
        
        result = legal_chat_service.handle_legal_message(data)
        
        if result["status"] == "reused":
            logger.info(f"Returning reused legal advice for conversation: {result['conversation_id']}")
            return {
                "conversation_id": result["conversation_id"],
                "status": "completed",
                "response_type": "reused_legal_advice",
                "answer": result["answer"]
            }
        
        # Return processing status for FE to call analyze-legal-query next
        return {
            "conversation_id": result["conversation_id"],
            "status": "processing",
            "message": "Đang phân tích câu hỏi pháp luật của bạn...",
            "estimated_time": "30-60 giây"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_legal_query: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi xử lý câu hỏi pháp luật")


@legal_chat_router.post("/analyze-legal-query")
async def analyze_legal_query_endpoint(data: AnalyzeResponse):
    """
    Analyze legal query with enhanced legal context processing
    Let LLM decide which tools to trigger based on query analysis
    """
    try:
        logger.info(f"Analyzing legal query for conversation: {data.conversation_id}")
        
        # Phân tích query và để LLM tự quyết định trigger tools
        analysis_result = await legal_chat_service.analyze_legal_query(
            conversation_id=data.conversation_id,
            user_id=data.user_id,
            query=data.query
        )
        
        logger.info(f"✅ Legal query analysis completed for: {data.conversation_id}")
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing legal query: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi phân tích câu hỏi pháp luật")

@legal_chat_router.post("/generate-legal-response")
async def generate_legal_response_endpoint(data: GenerateInput):
    """
    Generate comprehensive legal consultation response
    """
    try:
        logger.info(f"Generating legal response for conversation: {data.conversation_id}")
        
        result = legal_chat_service.generate_legal_consultation_response(data)
        
        return {
            "status": result["status"],
            "task_id": result.get("task_id"),
            "message": result["message"],
            "conversation_id": data.conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating legal response: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi tạo phản hồi tư vấn pháp luật")

@legal_chat_router.get("/conversations")
async def get_conversations(user_id: str = Query(...)):
    return await legal_chat_service.get_conversations(user_id)


@legal_chat_router.put("/conversations/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str = Path(..., description="Conversation ID"),
    title: str = Body(..., embed=True, description="New conversation title"),
    user_id: str = Query(..., description="User ID for ownership verification")
):
    

    # 1️⃣ Kiểm tra quyền sở hữu conversation
    conversation = await db_async["conversations"].find_one({
        "conversation_id": conversation_id,
        "user_id": user_id,
        "deleted": False
    })

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found or access denied")

    # 2️⃣ Thêm trường custom_title và update updated_at
    result = await db_async["conversations"].update_one(
        {"conversation_id": conversation_id},
        {"$set": {
            "custom_title": title,
            "updated_at": current_time()
        }}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes made")

    return {
        "conversation_id": conversation_id,
        "custom_title": title,
        "updated_at": current_time()
    }


@legal_chat_router.get("/conversation-history/{conversation_id}")
async def get_legal_conversation_history(
    conversation_id: str,
    limit: int = Query(default=20, ge=1, le=100, description="Number of messages to retrieve")
):
    """
    Get legal conversation history with enhanced metadata
    """
    try:
        messages = legal_chat_service.get_legal_conversation_history(conversation_id, limit)
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "total_retrieved": len(messages),
            "conversation_type": "legal_consultation"
        }
        
    except Exception as e:
        logger.error(f"Error getting legal conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi lấy lịch sử tư vấn pháp luật")

@legal_chat_router.get("/conversation-summary/{conversation_id}")
async def get_legal_conversation_summary(conversation_id: str):
    """
    Get legal conversation summary with key insights
    """
    try:
        summary = await legal_chat_service.get_legal_conversation_summary(conversation_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Không tìm thấy cuộc hội thoại")
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting legal conversation summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi lấy tóm tắt cuộc hội thoại")


@legal_chat_router.get("/stream-legal-response")
async def stream_legal_response(conversation_id: str = Query(..., description="Conversation ID to stream responses for")):
    async def legal_response_generator():
        redis_client = None
        pubsub = None
        all_tokens = []  # ✅ Lưu token để debug

        try:
            redis_url = get_redis_url(db=4)  # Use DB 4 for streaming as per database.py config
            redis_client = redis_async.from_url(
                redis_url, decode_responses=True
            )
            pubsub = redis_client.pubsub()
            channel = f"legal_response:{conversation_id}"
            await pubsub.subscribe(channel)
            logger.info(f"Subscribed to: {channel} via {redis_url}")

            first_msg_received = False
            start_time = time.monotonic()
            last_msg_time = start_time

            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=0.1
                )
                now = time.monotonic()

                if message:
                    if message.get("type") == "message":
                        content = message["data"]

                        if isinstance(content, bytes):
                            content = content.decode("utf-8")

                        all_tokens.append(content)  # ✅ Lưu token

                        yield content  # Yield token đơn giản

                        last_msg_time = now
                        first_msg_received = True

                        if content == "[DONE]":
                            break
                else:
                    if not first_msg_received and now - start_time >= 45:
                        logger.info("Timeout 45s trước message đầu tiên → completed")
                        break
                    if first_msg_received and now - last_msg_time >= 10:
                        logger.info("Timeout 10s sau message cuối → completed")
                        break

                await asyncio.sleep(0.01)

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"[ERROR] {str(e)}"

        finally:
            if pubsub:
                await pubsub.unsubscribe(channel)
                await pubsub.close()
            if redis_client:
                await redis_client.close()

    return StreamingResponse(legal_response_generator(), media_type="text/plain")


@legal_chat_router.get("/health")
async def legal_chat_health_check():
    """
    Health check endpoint for legal chat service
    """
    try:
        # Test Redis connection
        redis_client_web.ping()
        
        # Test service initialization
        service_status = {
            "legal_chat_service": "healthy",
            "redis_connection": "connected",
            "app_version": cfg_settings.APP_VERSION,
            "timestamp": current_time()
        }
        
        return {
            "status": "healthy",
            "service": "legal-chat",
            "details": service_status
        }
        
    except Exception as e:
        logger.error(f"Legal chat health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "legal-chat",
            "error": str(e),
            "timestamp": current_time()
        }

# Export router for main app
router = legal_chat_router
