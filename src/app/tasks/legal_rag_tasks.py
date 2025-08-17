"""
Refactored RAG tasks with environment-based configuration and proper naming
"""
import logging
from app.celery_config import celery_app
from app.config.database import messages_col, redis_client_web, redis_client_retrieval, redis_client_streaming
from app.config.settings import cfg_settings
from app.utils.utils_essential import current_time
import requests
# import google.generativeai as genai  # Commented out for lightweight deployment
from typing import List, Dict
from uuid import uuid5, NAMESPACE_DNS
import os
import json
import openai
import time
from openai import OpenAI
import redis
import redis.asyncio as redis_async
import traceback

# Configure Google AI with environment variable
# genai.configure(api_key=cfg_settings.GEMINI_API_KEY)  # Commented out for lightweight deployment

# Initialize OpenAI client
openai_client = OpenAI(api_key=cfg_settings.OPENAI_API_KEY)

# Initialize Gemini model
# gemini_model = genai.GenerativeModel("gemini-1.5-flash")  # Commented out for lightweight deployment

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ========== Core Task ==========
@celery_app.task(name="app.tasks.legal_rag_tasks.generate_legal_response", queue="rag_queue")
def generate_legal_response(
    conversation_id: str, 
    user_id: str, 
    user_message: str, 
    using_web_search: bool = False, 
    using_retrieval: bool = False
):
    """Generate response for legal queries with environment-based configuration"""
    logger.info(f"[LEGAL_RAG] Processing query from user={user_id} in conversation={conversation_id}")
    
    try:
        # Fetch conversation history
        chat_history = fetch_conversation_history(conversation_id, n=3)
        if not chat_history:
            logger.info("No conversation history found.")
        else:
            logger.info("Retrieved conversation history:\n" + "\n".join([
                f"{msg['role']}: {msg['text']}" for msg in chat_history
            ]))

        # Step 1: Legal document retrieval
        legal_documents = []
        if using_retrieval:
            retrieval_start_time = time.time()
            logger.info("🔍 Legal retrieval enabled, fetching documents from Redis...")
            legal_documents = wait_for_legal_chunks(redis_client_retrieval, key="retrieval_chunks", timeout=10)
            logger.info(f"Retrieved {len(legal_documents)} legal documents in {time.time() - retrieval_start_time:.2f}s")
            if legal_documents:
                logger.info(f"Sample legal document: {legal_documents[0]['text'][:300]}")

        # Step 2: Web search results
        web_results = []
        if using_web_search:
            web_search_start_time = time.time()
            logger.info("🌐 Web search enabled, fetching results from Redis...")
            web_results = wait_for_web_chunks(redis_client_web, key="web_search_chunks", timeout=10)
            logger.info(f"Retrieved {len(web_results)} web results in {time.time() - web_search_start_time:.2f}s")
            if web_results:
                logger.info(f"Sample web result: {web_results[0]['text'][:300]}")

        # Step 3: Generate response
        final_response = generate_comprehensive_legal_response_stream(
            conversation_id=conversation_id,
            user_message=user_message,
            conversation_history=chat_history,
            legal_documents=legal_documents,
            web_results=web_results,
            redis_client=redis_client_streaming
        )

        # Step 4: Save response to database
        save_legal_response(conversation_id, user_id, user_message, final_response)
        redis_client_web.delete("web_search_chunks")
        redis_client_retrieval.delete("retrieval_chunks")


        logger.info(f"[LEGAL_RAG] Successfully processed query: {user_message[:100]}...")
        return {"status": "success", "response_length": len(final_response)}

    except Exception as e:
        logger.error(f"[LEGAL_RAG] Error processing query: {str(e)}" + traceback.format_exc())
        error_response = f"Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi pháp luật của bạn: {str(e)}"
        save_legal_response(conversation_id, user_id, user_message, error_response)
        # publish_legal_response(conversation_id, error_response)
        return {"status": "error", "error": str(e)}

def fetch_conversation_history(conversation_id: str, n: int = 6) -> List[Dict]:
    """Fetch last N messages from conversation history"""
    try:
        messages = list(messages_col.find(
            {"conversation_id": conversation_id},
            {"_id": 0, "role": 1, "text": 1, "created_at": 1}
        ).sort("created_at", -1).limit(n))
        return list(reversed(messages))
    except Exception as e:
        logger.error(f"Error fetching conversation history: {str(e)}")
        return []

def wait_for_legal_chunks(redis_client: redis.Redis, key: str, timeout: int = 10) -> List[Dict]:
    """Wait for legal document chunks from Redis list"""
    try:
        for _ in range(timeout):
            # Kiểm tra số phần tử trong list
            length = redis_client.llen(key)
            if length > 0:
                # Lấy toàn bộ phần tử
                chunks_data = redis_client.lrange(key, 0, -1)
                # Giải mã từng item từ bytes → string → json
                chunks = [json.loads(item) for item in chunks_data]
                return chunks
            time.sleep(1)

        logger.warning(f"Timeout waiting for legal chunks with key: {key}")
        return []
    except Exception as e:
        logger.error(f"Error waiting for legal chunks: {str(e)}")
        return []

def wait_for_web_chunks(redis_client: redis.Redis, key: str, timeout: int = 10) -> List[Dict]:
    """Wait for web search results from Redis list"""
    try:
        for _ in range(timeout):
            length = redis_client.llen(key)  # Kiểm tra số phần tử trong list
            if length > 0:
                chunks_data = redis_client.lrange(key, 0, -1)  # Lấy toàn bộ list
                chunks = [json.loads(item) for item in chunks_data]  # Giải mã từng item
                return chunks
            time.sleep(1)

        logger.warning(f"Timeout waiting for web chunks with key: {key}")
        return []
    except Exception as e:
        logger.error(f"Error waiting for web chunks: {str(e)}")
        return []

def generate_comprehensive_legal_response_stream(
    user_message: str,
    conversation_history: List[Dict],
    legal_documents: List[Dict],
    web_results: List[Dict],
    conversation_id: str,
    redis_client
) -> str:
    """Generate legal response with streaming to Redis and return final text"""

    legal_context = build_legal_context(legal_documents)
    web_context = build_web_context(web_results)
    history_context = build_history_context(conversation_history)
    
    legal_prompt = create_legal_prompt(
        user_message, 
        history_context, 
        legal_context, 
        web_context
    )

    channel = f"legal_response:{conversation_id}"
    final_response = ""

    try:
        stream = openai_client.chat.completions.create(
            model=cfg_settings.DEFAULT_LLM_MODEL,
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia tư vấn pháp luật Việt Nam."},
                {"role": "user", "content": legal_prompt}
            ],
            temperature=0.3,
            max_tokens=5000,
            stream=True
        )

        for chunk in stream:
            delta = getattr(chunk.choices[0].delta, "content", None)
            if delta:
                redis_client.publish(channel, delta)
                final_response += delta

        # Gửi thông báo hoàn tất
        redis_client.publish(channel, "[DONE]")

        return final_response.strip()

    except Exception as e:
        logger.error(f"Error generating legal response stream: {str(e)}")
        redis_client.publish(channel, "[ERROR]")
        return "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu."
        

def build_legal_context(legal_documents: List[Dict]) -> str:
    """Build context from legal documents"""
    if not legal_documents:
        return ""
    
    context_parts = []
    for i, doc in enumerate(legal_documents[:5]):  # Limit to top 5
        context_parts.append(f"[Tài liệu {i+1}]: {doc.get('text', '')}")
    
    return "\n\n".join(context_parts)

def build_web_context(web_results: List[Dict]) -> str:
    """Build context from web search results"""
    if not web_results:
        return ""
    
    context_parts = []
    for i, result in enumerate(web_results[:3]):  # Limit to top 3
        context_parts.append(f"[Web {i+1}]: {result.get('text', '')}")
    
    return "\n\n".join(context_parts)

def build_history_context(conversation_history: List[Dict]) -> str:
    """Build context from conversation history"""
    if not conversation_history:
        return ""
    
    history_parts = []
    for msg in conversation_history[-4:]:  # Last 4 messages
        role = "Người dùng" if msg['role'] == 'user' else "Trợ lý"
        history_parts.append(f"{role}: {msg['text']}")
    
    return "\n".join(history_parts)

def create_legal_prompt(
    user_message: str,
    history_context: str,
    legal_context: str,
    web_context: str
) -> str:
    """Create comprehensive legal consultation prompt"""
    
    prompt_parts = [
        f"Câu hỏi pháp luật: {user_message}",
        ""
    ]
    
    if history_context:
        prompt_parts.extend([
            "=== LỊCH SỬ HỘI THOẠI ===",
            history_context,
            ""
        ])
    
    if legal_context:
        prompt_parts.extend([
            "=== TÀI LIỆU PHÁP LUẬT ===",
            legal_context,
            ""
        ])
    
    if web_context:
        prompt_parts.extend([
            "=== THÔNG TIN TỪ WEB ===",
            web_context,
            ""
        ])
    
    prompt_parts.extend([
        "=== YÊU CẦU TƯ VẤN ===",
        "Hãy phân tích và tư vấn pháp luật dựa trên:",
        "1. Các quy định pháp luật hiện hành",
        "2. Thông tin cập nhật từ web (nếu có)",
        "3. Bối cảnh cuộc hội thoại",
        "",
        "Trả lời bằng tiếng Việt, rõ ràng và chính xác."
    ])
    
    return "\n".join(prompt_parts)

def save_legal_response(conversation_id: str, user_id: str, question: str, response: str):
    """Save legal response to database"""
    try:
        messages_col.insert_one({
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": "assistant",
            "text": response,
            "question": question,
            "created_at": current_time(),
            "is_reused": False,
            "response_type": "legal_consultation"
        })
        logger.info(f"Saved legal response for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"Error saving legal response: {str(e)}")

def publish_legal_response(conversation_id: str, response: str):
    """Publish legal response to Redis for real-time streaming"""
    try:
        redis_client_streaming.publish(f"legal_response:{conversation_id}", response)
        logger.info(f"Published legal response for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"Error publishing legal response: {str(e)}")

# Health check task
@celery_app.task(name="app.tasks.legal_rag_tasks.legal_system_health_check")
def legal_system_health_check():
    """Health check for legal RAG system"""
    try:
        # Test database connection
        test_count = messages_col.count_documents({})
        
        # Test Redis connections
        redis_client_web.ping()
        redis_client_retrieval.ping()
        
        return {
            "status": "healthy",
            "timestamp": current_time(),
            "message_count": test_count,
            "redis_web": "connected",
            "redis_retrieval": "connected"
        }
    except Exception as e:
        logger.error(f"Legal system health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": current_time()
        }
