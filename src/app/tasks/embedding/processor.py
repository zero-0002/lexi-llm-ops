"""
Document processing service
"""
import logging
import json
import redis
import time
import threading
import traceback
from typing import Dict, Any, Optional, List
from dataclasses import asdict

from .models import TextChunk
from .chunker import TextChunker
from .ranker import ChunkRanker

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service xử lý documents - Balanced logging"""
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        # STDOUT: Log khởi tạo chính
        logger.info("Initializing DocumentProcessor...")
        
        try:
            from app.config.database import redis_client_web
            self.redis_client = redis_client_web
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
        
        self.document_queue = "extracted_documents"
        self.processed_queue = "web_search_chunks"
        self.chunker = TextChunker()
        self.ranker = ChunkRanker()
        
        logger.info(f"Queues configured: {self.document_queue} -> {self.processed_queue}")
    
    def get_document_from_redis(self, task_logger=None) -> Optional[Dict[str, Any]]:
        """Get document from Redis - main result to stdout"""
        try:
            # Check queue length first
            queue_length = self.redis_client.llen(self.document_queue)
            
            if queue_length == 0:
                logger.info("Queue is empty")
                return None
            
            # STDOUT: Log chính
            logger.info(f"Getting document from Redis (queue: {queue_length})")
            
            result = self.redis_client.brpop(self.document_queue, timeout=5)
            
            if result:
                queue_name, json_data = result
                document = json.loads(json_data.decode('utf-8'))
                doc_id = document.get('doc_id', 'unknown')
                
                # STDOUT: Kết quả chính
                logger.info(f"Document retrieved: {doc_id}")
                
                # TASK_LOGGER: Chi tiết
                if task_logger:
                    task_logger.info(f"✅ Document retrieved successfully:")
                    task_logger.info(f"   Doc ID: {doc_id}")
                    task_logger.info(f"   Keys: {list(document.keys())}")
                    task_logger.info(f"   Data size: {len(json_data)} bytes")
                
                return document
            else:
                logger.info("No documents available")
                return None
                
        except Exception as e:
            logger.error(f"Error getting document from Redis: {e}")
            if task_logger:
                task_logger.error(f"   Traceback: {traceback.format_exc()}")
            return None
    
    def save_chunks_to_redis(self, chunks: List[TextChunk], task_logger=None) -> int:
        """Save chunks - main result to stdout"""
        if not chunks:
            logger.warning("No chunks to save")
            return 0
        
        # STDOUT: Log chính
        logger.info(f"Saving {len(chunks)} chunks to Redis...")
        
        saved_count = 0
        
        for i, chunk in enumerate(chunks):
            try:
                chunk.processed_at = time.time()
                chunk_data = asdict(chunk)
                
                self.redis_client.lpush(self.processed_queue, json.dumps(chunk_data))
                saved_count += 1
                
                # TASK_LOGGER: Chi tiết từng chunk
                if task_logger:
                    task_logger.debug(f"✅ Saved chunk {i}: {chunk.chunk_id}")
                
            except Exception as e:
                logger.error(f"Error saving chunk {i}: {e}")
                if task_logger:
                    task_logger.error(f"   Chunk ID: {getattr(chunk, 'chunk_id', 'unknown')}")
                    task_logger.error(f"   Error: {traceback.format_exc()}")
        
        # STDOUT: Kết quả chính
        logger.info(f"Saved {saved_count}/{len(chunks)} chunks to Redis")
        
        return saved_count
    
    def process_document(self, document: Dict[str, Any], query: str, top_k: int, task_logger=None) -> Dict[str, Any]:
        """Process a single document - orchestrate the workflow"""
        doc_id = document.get('doc_id', 'unknown')
        url = document.get('url', 'unknown')
        title = document.get('title', '')
        
        # STDOUT: Progress chính
        logger.info(f"Processing document: {doc_id}")
        
        # TASK_LOGGER: Chi tiết
        if task_logger:
            task_logger.info(f"📄 Starting document processing:")
            task_logger.info(f"   Doc ID: {doc_id}")
            task_logger.info(f"   URL: {url}")
            task_logger.info(f"   Title: {title}")
            task_logger.info(f"   Query: {query}")
            task_logger.info(f"   Top K: {top_k}")
        
        # Step 1: Chunk document
        chunks = self.chunker.chunk_document(document, task_logger)
        
        if not chunks:
            logger.warning(f"No chunks created for document: {doc_id}")
            return {
                'success': False,
                'message': 'No chunks created from document',
                'document_id': doc_id,
                'url': url,
                'title': title
            }
        
        # STDOUT: Progress
        logger.info(f"Created {len(chunks)} chunks for document: {doc_id}")
        
        # Step 2: Rank chunks
        search_results = self.ranker.rank_chunks(chunks, query, top_k, task_logger)
        
        # Step 3: Filter results
        filtered_results = self.ranker.filter_by_threshold(search_results, task_logger=task_logger, threshold=0.05)
        
        # STDOUT: Progress
        logger.info(f"Selected {len(filtered_results)} chunks for document: {doc_id}")
        
        # Step 4: Save chunks
        saved_count = 0
        if filtered_results:
            filtered_chunks = [result.chunk for result in filtered_results]
            # Update similarity scores
            for i, result in enumerate(filtered_results):
                filtered_chunks[i].similarity_score = result.final_score
            
            saved_count = self.save_chunks_to_redis(filtered_chunks, task_logger)
        else:
            logger.warning(f"No chunks to save for document: {doc_id}")
        
        # Calculate metrics
        avg_score = sum(r.final_score for r in filtered_results) / len(filtered_results) if filtered_results else 0
        
        # STDOUT: Kết quả chính
        logger.info(f"Document processed: {doc_id} | "
                   f"chunks={len(chunks)}→{len(filtered_results)}→{saved_count} | "
                   f"score={avg_score:.3f}")
        
        # TASK_LOGGER: Chi tiết đầy đủ
        if task_logger:
            task_logger.info(f"✅ Document processing completed:")
            task_logger.info(f"   Total chunks: {len(chunks)}")
            task_logger.info(f"   Ranked chunks: {len(search_results)}")
            task_logger.info(f"   Selected chunks: {len(filtered_results)}")
            task_logger.info(f"   Saved chunks: {saved_count}")
            task_logger.info(f"   Average score: {avg_score:.3f}")
        
        return {
            'success': True,
            'document_id': doc_id,
            'url': url,
            'title': title,
            'total_chunks': len(chunks),
            'ranked_chunks': len(search_results),
            'selected_chunks': len(filtered_results),
            'saved_chunks': saved_count,
            'average_score': avg_score,
            'method': document.get('method', 'unknown')
        }