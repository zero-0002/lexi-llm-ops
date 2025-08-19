import logging
from typing import Optional, List
from bson.objectid import ObjectId
from qdrant_client.http.models import PointStruct
from qdrant_client.models import VectorParams, Distance
from app.tasks.legal_embedding_tasks import embed_query_task
from app.config.database import db_manager
from app.config.settings import cfg_settings

logger = logging.getLogger(__name__)


class LegalRAGService:
    def __init__(
        self,
        messages_col=None
    ):
        self.vector_client = db_manager.qdrant_client
        self.collection_names = ["chat_questions", "legal_documents_collection"]
        self.messages_col = messages_col
        self.__check_collection_exists(self.collection_names)

    def __check_collection_exists(self, collection_names: List[str]):
        """Kiểm tra hoặc tạo mới collection Qdrant."""
        try:
            for collection_name in collection_names:
                try:
                    # Try to get collection info instead of collection_exists
                    self.vector_client.get_collection(collection_name)
                    logger.info(f"[Qdrant] Collection `{collection_name}` đã tồn tại.")
                except Exception:
                    logger.warning(f"[Qdrant] Collection `{collection_name}` không tồn tại. Tạo mới.")
                    self.vector_client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)  # OpenAI embedding size
                    )
        except Exception as e:
            logger.warning(f"Lỗi khi kiểm tra hoặc tạo collection: {e}")
            logger.warning("Tiếp tục mà không có Qdrant connection...")


    def vector_upsert_question(self, collection_name: str, vector: List[float], payload: dict, point_id: str):
        """Upsert vector vào Qdrant."""
        try:
            self.vector_client.upsert(
                collection_name=collection_name,
                points=[PointStruct(id=point_id, vector=vector, payload=payload)]
            )
        except Exception:
            logger.exception("Lỗi upsert point")
            raise

    def check_reuse(self, query: str, threshold: float = 0.95, top_k: int = 3) -> Optional[str]:
        """Kiểm tra xem câu hỏi đã được hỏi trước chưa."""
        try:
            embedding_task = embed_query_task.delay(query)
            vector = embedding_task.get(timeout=30)
            hits = self.vector_client.search(
                collection_name="chat_questions",
                query_vector=vector,
                limit=top_k,
                with_payload=True,
                score_threshold=threshold
            )

            if not hits or not self.messages_col:
                return None

            for hit in hits:
                message_id = hit.payload.get("message_id")
                if message_id:
                    assistant_msg = self.messages_col.find_one({"_id": ObjectId(message_id)})
                    if assistant_msg and assistant_msg["role"] == "assistant":
                        return assistant_msg["text"]
            return None
        except Exception:
            logger.exception("Lỗi khi check_reuse")
            return None

    def search(self, collection_name: str, query_text: str, limit: int = 20) -> List[dict]:
        """Tìm kiếm trong Qdrant."""
        if not query_text.strip():
            logger.warning("Truy vấn tìm kiếm rỗng hoặc không hợp lệ")
            return []

        try:
            # Import and call embedding function directly to avoid nested task calls
            from app.tasks.legal_embedding_tasks import embed_query_sync
            embedding_result = embed_query_sync(query_text)
            
            # Debug log
            logger.info(f"Embedding result type: {type(embedding_result)}")
            logger.info(f"Embedding result: {embedding_result}")
            
            # Extract vector from embedding result - FIX LOGIC
            if isinstance(embedding_result, dict) and "dense_vecs" in embedding_result:
                # BGE model returns {dense_vecs: [[...]], ...}
                vector = embedding_result["dense_vecs"][0]
                logger.info(f"Extracted vector from dense_vecs: {type(vector)}, length: {len(vector)}")
            elif isinstance(embedding_result, dict) and "embedding" in embedding_result:
                # OpenAI format {embedding: [...], ...}
                vector = embedding_result["embedding"]
                logger.info(f"Extracted vector from embedding: {type(vector)}, length: {len(vector)}")
            elif isinstance(embedding_result, list):
                # Direct list format
                vector = embedding_result
                logger.info(f"Using direct list vector: {type(vector)}, length: {len(vector)}")
            else:
                logger.error(f"Unknown embedding format: {type(embedding_result)}")
                return []
                
            results = self.vector_client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
                with_payload=True
            )
            return [
                {
                    "cid": point.payload.get("cid"),
                    "chunk_index": point.payload.get("chunk_index", 0),
                    "text": point.payload.get("text", ""),
                    "score": point.score
                }
                for point in results  # search returns direct list
            ]
        except Exception:
            logger.exception("Lỗi tìm kiếm trong Qdrant")
            return []