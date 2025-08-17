import asyncio
import logging
import time
import json
import redis
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import uuid
# from web_search.playwright_tool import extract_text_with_playwright_async  # COMMENTED FOR DOCKER OPTIMIZATION
# from .playwright_tool_simple import extract_with_requests  # Simple fallback
from .requests_tool import extract_with_requests 
from app.utils.logging_simplified import get_logger, consolidate_extraction_logs
# from app.tasks.embedding_tasks import process_document_and_select_chunks  # REMOVED: File deleted in cleanup
from app.tasks.legal_embedding_tasks import process_legal_document_embedding  # Updated import
from app.config.database import get_database_manager

logger = logging.getLogger(__name__)

@dataclass
class ExtractedDocument:
    """Document với text nguyên bản để gửi qua Redis"""
    doc_id: str
    url: str
    title: str
    text: str
    method: str
    metadata: Dict[str, Any]
    extracted_at: float

class ExtractionService:
    """Service extract text và gửi documents nguyên qua Redis"""

    def __init__(self):
        self.db_manager = get_database_manager()
        self.redis_client = self.db_manager.get_redis_client(1)  # Web search cache
        self.document_queue = "extracted_documents"  # ✅ Queue mới cho documents

    def _extract_with_requests(self, url: str) -> Dict[str, Optional[str]]:
        """Extract using requests method"""
        return extract_with_requests(url)

    def _extract_with_playwright(self, url: str) -> Dict[str, Optional[str]]:
        """Extract using simple requests (Playwright disabled for Docker optimization)"""
        return extract_with_requests(url)
        # try:
        #     # Try direct asyncio.run first
        #     return asyncio.run(extract_text_with_playwright_async(
        #         url=url
        #     ))
        # except RuntimeError as e:
        #     if "asyncio.run() cannot be called from a running event loop" in str(e):
        #         # Handle nested event loop case
        #         logger.info("   🔄 Creating new event loop for Playwright...")
        #         loop = asyncio.new_event_loop()
        #         asyncio.set_event_loop(loop)
        #         result = loop.run_until_complete(extract_text_with_playwright_async(
        #             url=url
        #         ))
        #         return result
        #     else:
        #         raise

    def extract_and_send_document(self, query: str, data_link: str, thread_id: str = None) -> Dict[str, Any]:
        """Extract text và gửi document nguyên qua Redis với simplified logging"""
        
        # Use simplified logger - no more thread-specific files
        thread_logger = get_logger(f"extraction.{thread_id}" if thread_id else "extraction")
            
        url = data_link['url']
        title = data_link['title']
        snippet = data_link['snippet']

        thread_logger.info(f"🔍 Bắt đầu extract document từ: {url}")
        thread_logger.info(f"📋 Title: {title}")
        thread_logger.info(f"📝 Snippet: {snippet}")

        start_time = time.time()
        methods_to_try = [
                ("requests", self._extract_with_requests),
                # ("playwright", self._extract_with_playwright)
            ]
        try:
            for method_name, extract_func in methods_to_try:
                try:
                    method_start = time.time()
                    thread_logger.info(f"🔧 Thử method: {method_name}")
                    
                    result = extract_func(url)
                    method_time = time.time() - method_start
                    
                    if result.get("success") and result.get("text") and len(result["text"].strip()) > 100:
                        result["extraction_time"] = time.time() - start_time
                        result["method_time"] = method_time
                        result["fallback_method"] = method_name
                        
                        thread_logger.info(f"   ✅ {method_name} thành công | "
                                f"Length: {len(result['text'])} chars | "
                                f"Time: {method_time:.2f}s")
                        break
                    else:
                        error_msg = result.get("error", "No substantial content")
                        thread_logger.warning(f"   ⚠️ {method_name} thất bại: {error_msg}")
                        
                except Exception as e:
                    thread_logger.error(f"   ❌ {method_name} exception: {e}")
                    continue
                
            total_time = time.time() - start_time
            thread_logger.info(f"📊 So sánh titles - Links: '{title}' vs Extract: '{result.get('title', '')}'")
            thread_logger.info(f"📄 Snippet: {snippet}")

            # Create document object
            document = ExtractedDocument(
                doc_id=str(uuid.uuid4()),
                url=url,
                title=result.get('title', ''),
                text=result['text'],
                method=result.get('fallback_method', 'unknown'),
                metadata={
                    'status_code': result.get('status_code'),
                    'extraction_time': result.get('extraction_time', 0),
                    'text_length': len(result['text'])
                },
                extracted_at=time.time()
            )
            
            thread_logger.info(f"📦 Tạo document object với ID: {document.doc_id}")
            
            # ✅ Send document to Redis (not chunks)
            document_sent = self.send_document_to_redis(query, document, thread_logger)

            total_time = time.time() - start_time
            thread_logger.info(f"✅ Hoàn thành extract {url}")
            thread_logger.info(f"   📊 Method: {result.get('fallback_method')}")
            thread_logger.info(f"   📏 Length: {len(result['text'])} chars")
            thread_logger.info(f"   📤 Sent to Redis: {document_sent}")
            thread_logger.info(f"   ⏱️ Total time: {total_time:.2f}s")
            
            # Cleanup thread logger khi kết thúc
            # Simplified logging - no cleanup needed for JSON stdout logging
            thread_logger.info(f"✅ Thread {thread_id} completed extraction")

            return {
                'url': url,
                'success': True,
                'document_sent': document_sent,
                'text_length': len(result['text']),
                'method': result.get('fallback_method'),
                'extraction_time': total_time,
                'doc_id': document.doc_id
            }
        except Exception as e:
            # Simplified logging - no cleanup needed
            thread_logger.error(f"💥 Lỗi khi extract {url}: {e}")

            return {
                'url': url,
                'success': False,
                'error': str(e),
                'document_sent': False,
                'method': 'unknown',
                'extraction_time': time.time() - start_time
            }

    def send_document_to_redis(self,query, document: ExtractedDocument, thread_logger: logging.Logger = None) -> bool:
        """Send document to Redis queue for Celery processing"""
        if not thread_logger:
            thread_logger = logger
            
        try:
            thread_logger.info(f"📤 Đang gửi document {document.doc_id} lên Redis...")
            
            document_data = asdict(document)
            self.redis_client.delete(self.document_queue)  # Xóa nếu đã tồn tại
            self.redis_client.lpush(self.document_queue, json.dumps(document_data))

            # Updated to use legal embedding task
            task_result = process_legal_document_embedding.delay([document_data], 32)
            
            thread_logger.info(f"✅ Document {document.doc_id} đã gửi lên Redis")
            thread_logger.info(f"🚀 Celery task được trigger: {task_result.id}")
            
            return True
        except Exception as e:
            thread_logger.error(f"❌ Thất bại gửi document {document.doc_id}: {e}")
            return False

# # Global service instance
# extraction_service = ExtractionService()
