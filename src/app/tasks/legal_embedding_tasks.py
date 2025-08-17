"""
Refactored embedding tasks with environment-based configuration
"""
import logging
from app.celery_config import celery_app
from app.config.database import redis_client_web, db_manager
from app.config.settings import cfg_settings
import redis
import time
import json
from typing import List, Dict, Any
from app.services.embeddings import EmbeddingHandler
import numpy as np

logger = logging.getLogger(__name__)
# Initialize embedding model
embedding_model = EmbeddingHandler(provider=cfg_settings.PROVIDER, model_name=cfg_settings.EMBEDDING_MODEL)


def embed_query_sync(query: str):
    """Embed a legal query synchronously (for use within other tasks)"""
    logger.info(f"Embedding query synchronously: {query}")
    embedding_result = embedding_model.encode(query)
    logger.info(f"Query embedding completed synchronously")
    
    # Check if result is in new format with dense_vecs
    if isinstance(embedding_result, dict) and "dense_vecs" in embedding_result:
        embedding = embedding_result["dense_vecs"][0]  # Extract first vector
        logger.info(f"Extracted vector from dense_vecs: {type(embedding)}, length: {len(embedding) if isinstance(embedding, list) else 'N/A'}")
    else:
        embedding = embedding_result
        
    return {"query": query, "embedding": embedding}


@celery_app.task(name="app.tasks.legal_embedding_tasks.embed_query", queue="embed_queue")
def embed_query_task(query: str):
    """Embed a legal query"""
    return embed_query_sync(query)


@celery_app.task(name="app.tasks.legal_embedding_tasks.process_legal_document_embedding", queue="embed_queue")
def process_legal_document_embedding(document_chunks: List[Dict[str, Any]], batch_size: int = 32):
    """Process legal document embeddings in batches"""
    logger.info(f"Processing {len(document_chunks)} legal document chunks for embedding")
    
    try:
        processed_chunks = []
        
        for i in range(0, len(document_chunks), batch_size):
            batch = document_chunks[i:i + batch_size]
            
            # Split oversized texts
            batch_texts = []
            for chunk in batch:
                text = chunk.get('text', '')
                # Split text if too long (approx 8000 tokens = ~6000 chars)
                if len(text) > 6000:
                    # Split into smaller chunks
                    text_parts = [text[j:j+6000] for j in range(0, len(text), 6000)]
                    batch_texts.extend(text_parts)
                    # Mark original chunk for splitting
                    chunk['_split'] = True
                    chunk['_parts'] = len(text_parts)
                else:
                    batch_texts.append(text)
                    chunk['_split'] = False
            
            # Generate embeddings
            batch_embeddings = embedding_model.encode(
                batch_texts, 
                return_dense=True, 
                return_sparse=False
            )
            
            # Process each chunk in batch
            embedding_idx = 0
            for j, chunk in enumerate(batch):
                if chunk.get('_split'):
                    # Handle split chunks - use first part embedding
                    embedding = batch_embeddings['dense_vecs'][embedding_idx]
                    embedding_idx += chunk['_parts']
                else:
                    embedding = batch_embeddings['dense_vecs'][embedding_idx]
                    embedding_idx += 1
                
                # Handle embedding - convert to list properly
                if hasattr(embedding, 'tolist'):
                    # NumPy array - convert to list
                    chunk['embedding'] = embedding.tolist()
                elif isinstance(embedding, list):
                    # Already a list - use as is
                    chunk['embedding'] = embedding
                else:
                    # Convert to list for other types
                    chunk['embedding'] = list(embedding)
                chunk['embedding_model'] = cfg_settings.EMBEDDING_MODEL
                chunk['processed_at'] = time.time()
                processed_chunks.append(chunk)
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(document_chunks) + batch_size - 1)//batch_size}")
        
        # Store embeddings in vector database
        store_legal_embeddings(processed_chunks)
        
        logger.info(f"Successfully processed {len(processed_chunks)} legal document embeddings")
        return {"status": "success", "processed_count": len(processed_chunks)}
        
    except Exception as e:
        logger.error(f"Error processing legal document embeddings: {str(e)}")
        return {"status": "error", "error": str(e)}

def store_legal_embeddings(processed_chunks: List[Dict[str, Any]]):
    """Store legal document embeddings in Qdrant"""
    try:
        vector_client = db_manager.qdrant_client
        collection_name = "legal_documents_collection"
        
        # Ensure collection exists - use collection_exists method
        collection_exists = False
        try:
            collection_exists = vector_client.collection_exists(collection_name)
            if collection_exists:
                logger.info(f"Collection {collection_name} already exists")
            else:
                logger.info(f"Collection {collection_name} does not exist, will create")
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            # Try creating collection anyway
            pass
        
        if not collection_exists:
            try:
                from qdrant_client.models import VectorParams, Distance
                vector_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)  # OpenAI embedding size
                )
                logger.info(f"Created new collection {collection_name}")
            except Exception as create_error:
                if "already exists" in str(create_error):
                    logger.info(f"Collection {collection_name} already exists (race condition)")
                else:
                    logger.error(f"Error creating collection: {create_error}")
                    raise
        
        # Prepare points for upsert
        import uuid
        points = []
        for i, chunk in enumerate(processed_chunks):
            # Use unique ID from document_id and chunk_index, or generate UUID
            point_id = chunk.get('doc_id') or f"{chunk.get('document_id', str(uuid.uuid4()))}_{chunk.get('chunk_index', i)}"
            points.append({
                "id": point_id,
                "vector": chunk['embedding'],
                "payload": {
                    "text": chunk.get('text', ''),
                    "source": chunk.get('source', ''),
                    "document_id": chunk.get('document_id', ''),
                    "chunk_index": chunk.get('chunk_index', 0),
                    "processed_at": chunk.get('processed_at'),
                    "doc_id": chunk.get('doc_id', '')
                }
            })
        
        # Batch upsert
        vector_client.upsert(collection_name=collection_name, points=points)
        logger.info(f"Stored {len(points)} legal document embeddings in Qdrant")
        
    except Exception as e:
        logger.error(f"Error storing legal embeddings: {str(e)}")
        raise

@celery_app.task(name="app.tasks.legal_embedding_tasks.search_legal_documents", queue="embed_queue")
def search_legal_documents(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search similar legal documents based on query embedding"""
    logger.info(f"Searching legal documents for query: {query[:100]}...")
    
    try:
        # Generate query embedding
        query_embedding = embedding_model.encode([query], return_dense=True)['dense_vecs'][0]
        
        # Convert embedding to list properly
        if hasattr(query_embedding, 'tolist'):
            # NumPy array - convert to list
            query_vector = query_embedding.tolist()
        elif isinstance(query_embedding, list):
            # Already a list - use as is
            query_vector = query_embedding
        else:
            # Convert to list for other types
            query_vector = list(query_embedding)
        
        # Search in vector database
        vector_client = db_manager.qdrant_client
        collection_name = "legal_documents_collection"
        
        search_results = vector_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=cfg_settings.SIMILARITY_THRESHOLD
        )
        
        # Format results
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "text": result.payload.get("text", ""),
                "source": result.payload.get("source", ""),
                "score": result.score,
                "document_id": result.payload.get("document_id", ""),
                "chunk_index": result.payload.get("chunk_index", 0)
            })
        
        logger.info(f"Found {len(formatted_results)} relevant legal documents")
        
        # Cache results in Redis
        cache_key = f"legal_search:{hash(query)}"
        redis_client_web.setex(
            cache_key, 
            3600,  # 1 hour cache
            json.dumps(formatted_results)
        )
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error searching legal documents: {str(e)}")
        return []

@celery_app.task(name="app.tasks.legal_embedding_tasks.update_legal_index", queue="embed_queue")
def update_legal_index(new_documents: List[Dict[str, Any]]):
    """Update legal document index with new documents"""
    logger.info(f"Updating legal index with {len(new_documents)} new documents")
    
    try:
        # Process embeddings for new documents
        result = process_legal_document_embedding(new_documents)
        
        if result["status"] == "success":
            # Update index metadata
            update_metadata = {
                "last_updated": time.time(),
                "document_count": result["processed_count"],
                "model_version": cfg_settings.EMBEDDING_MODEL
            }
            
            redis_client_web.setex(
                "legal_index_metadata",
                86400,  # 24 hours
                json.dumps(update_metadata)
            )
            
            logger.info("Legal index updated successfully")
            return {"status": "success", "updated_count": result["processed_count"]}
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error updating legal index: {str(e)}")
        return {"status": "error", "error": str(e)}

@celery_app.task(name="app.tasks.legal_embedding_tasks.legal_embedding_health_check")
def legal_embedding_health_check():
    """Health check for legal embedding system"""
    try:
        # Test embedding model
        test_embedding = embedding_model.encode(["test query"], return_dense=True)
        
        # Test vector database
        vector_client = db_manager.qdrant_client
        collections = vector_client.get_collections()
        
        # Test Redis cache
        redis_client_web.ping()
        
        return {
            "status": "healthy",
            "embedding_model": cfg_settings.EMBEDDING_MODEL,
            "vector_collections": len(collections.collections),
            "redis_cache": "connected",
            "test_embedding_shape": len(test_embedding['dense_vecs'][0])
        }
        
    except Exception as e:
        logger.error(f"Legal embedding health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
