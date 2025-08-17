"""
Refactored chat service with environment-based configuration and better naming
"""
from app.utils.utils_essential import generate_id, current_time
from app.models.api_schema import MessageInput, GenerateInput
from app.tasks.legal_rag_tasks import generate_legal_response
from app.brain import analyze_user_query
from app.config.database import conversations_col, messages_col, db_async
from app.config.settings import cfg_settings
import logging
from fastapi import HTTPException

# Use centralized logging instead of basicConfig
logger = logging.getLogger(__name__)

class LegalChatService:
    """Enhanced chat service for legal consultations with improved naming"""
    
    def __init__(self):
        self.app_name = cfg_settings.APP_NAME
        self.similarity_threshold = cfg_settings.SIMILARITY_THRESHOLD
    
    def handle_legal_message(self, data: MessageInput):
        """Handle incoming legal consultation message"""
        conversation_id = data.conversation_id or generate_id()
        
        # Create new conversation if needed
        if not data.conversation_id:
            self._create_new_legal_conversation(conversation_id, data.user_id, data.message)
        else:
            self._update_conversation_stats(conversation_id)

        # Save user message
        self._save_user_message(conversation_id, data.user_id, data.message)
        
        # Check for reused answer (currently disabled for legal queries)
        # reused_answer = self._check_legal_reuse(data.message)
        reused_answer = None
        if reused_answer:
            self._save_reused_legal_response(conversation_id, data.user_id, data.message, reused_answer)
            return {
                "conversation_id": conversation_id,
                "status": "reused",
                "answer": reused_answer,
                "response_type": "legal_reuse"
            }
        
        return {
            "conversation_id": conversation_id,
            "status": "processing",
            "message": "Đang phân tích câu hỏi pháp luật của bạn..."
        }
    
    def _create_new_legal_conversation(self, conversation_id: str, user_id: str, message: str):
        """Create new legal conversation with proper metadata"""
        try:
            conversations_col.insert_one({
                "conversation_id": conversation_id,
                "user_id": user_id,
                "title": self.smart_title_generation(message),
                "conversation_type": "legal_consultation",
                "created_at": current_time(),
                "updated_at": current_time(),
                "message_count": 1,
                "deleted": False,
                "tags": ["legal", "consultation"]
            })
            logger.info(f"Created new legal conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Error creating legal conversation: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create conversation")
    
    def _update_conversation_stats(self, conversation_id: str):
        """Update conversation statistics"""
        try:
            conversations_col.update_one(
                {"conversation_id": conversation_id},
                {
                    "$inc": {"message_count": 1}, 
                    "$set": {"updated_at": current_time()}
                }
            )
        except Exception as e:
            logger.error(f"Error updating conversation stats: {str(e)}")
    
    def _save_user_message(self, conversation_id: str, user_id: str, message: str):
        """Save user message with legal context"""
        try:
            messages_col.insert_one({
                "conversation_id": conversation_id,
                "user_id": user_id,
                "role": "user",
                "text": message,
                "message_type": "legal_query",
                "is_reused": False,
                "created_at": current_time(),
                "metadata": {
                    "character_count": len(message),
                    "word_count": len(message.split())
                }
            })
            logger.info(f"Saved user legal query for conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Error saving user message: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save message")
    
    def _save_reused_legal_response(self, conversation_id: str, user_id: str, question: str, response: str):
        """Save reused legal response"""
        try:
            messages_col.insert_one({
                "conversation_id": conversation_id,
                "user_id": user_id,
                "role": "assistant",
                "text": response,
                "question": question,
                "message_type": "legal_response",
                "is_reused": True,
                "created_at": current_time()
            })
        except Exception as e:
            logger.error(f"Error saving reused legal response: {str(e)}")
    
    def _check_legal_reuse(self, message: str) -> str:
        """Check if legal query can be reused (currently disabled)"""
        # TODO: Implement legal-specific similarity checking
        # For now, always return False to ensure fresh legal analysis
        return None
    
    async def generate_conversation_title(self, conversation_id: str) -> str:
        """Generate a meaningful title from the first user message"""
        try:
            # Get first user message
            first_message = await db_async.messages.find_one(
                {
                    "conversation_id": conversation_id,
                    "role": "user"
                },
                sort=[("created_at", 1)]
            )
            
            if first_message and first_message.get("text"):
                # Truncate and clean the message for title
                title = first_message["text"].strip()

                title = self.smart_title_generation(title)
                # logger.info(f"Generated title for {conversation_id}: {title}")
                return title if title else f"Cuộc trò chuyện {conversation_id[:8]}"
            
            return f"Cuộc trò chuyện {conversation_id[:8]}"
        
        except Exception as e:
            logger.error(f"Error generating title for {conversation_id}: {e}")
            return f"Cuộc trò chuyện {conversation_id[:8]}"
        
    def smart_title_generation(self, content: str) -> str:
        """Smart title generation from message content"""
        # Remove common prefixes
        prefixes_to_remove = [
            "tôi muốn hỏi", "cho tôi biết", "xin hỏi", "hỏi về",
            "giúp tôi", "tư vấn về", "tư vấn", "hỏi"
        ]
        
        title = content.lower()
        for prefix in prefixes_to_remove:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        
        # Capitalize first letter
        title = title.capitalize()
        
        # Remove question marks and periods
        title = title.replace("?", "").replace(".", "").strip()
        
        # Truncate if too long
        if len(title) > 50:
            # Try to break at word boundary
            words = title[:50].split()
            if len(words) > 1:
                title = " ".join(words[:-1]) + "..."
            else:
                title = title[:47] + "..."
        
        return title
    
    
    async def analyze_legal_query(self, conversation_id: str, user_id: str, query: str):
        """Analyze legal query with enhanced processing"""
        logger.info(f"Analyzing legal query for conversation: {conversation_id}")
        
        try:
            # Use enhanced brain analysis for legal queries
            analysis_result = await analyze_user_query(
                conversation_id=conversation_id,
                user_id=user_id,
                query=query,
                model= cfg_settings.DEFAULT_LLM_MODEL
            )
            
            logger.info(f"Legal query analysis completed for: {conversation_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing legal query: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to analyze legal query")
    
    def generate_legal_consultation_response(self, data: GenerateInput):
        """Generate comprehensive legal consultation response"""
        logger.info(f"Generating legal consultation for conversation: {data.conversation_id}")
        
        try:
            # Trigger legal response generation task
            task_result = generate_legal_response.delay(
                conversation_id=data.conversation_id,
                user_id=data.user_id,
                user_message=data.rewrite_query or "Legal consultation request",
                using_web_search=data.use_web_search,
                using_retrieval=data.use_retrieval
            )
            
            logger.info(f"Legal consultation task queued: {task_result.id}")
            return {
                "status": "queued",
                "task_id": task_result.id,
                "message": "Đang tạo phản hồi tư vấn pháp luật..."
            }
            
        except Exception as e:
            logger.error(f"Error generating legal consultation: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate legal consultation")
    
    async def get_conversations(self,user_id: str = "tinh123"):
        """Get all conversations for a user with titles"""
        try:
            conversations = []
            cursor = db_async.conversations.find({"user_id": user_id, "deleted": False}).sort("created_at", -1)
            
            async for conv in cursor:
                # Generate title from first message or use default
                if not conv.get("custom_title"):
                    title = await self.generate_conversation_title(conv["conversation_id"])
                else:
                    title = conv.get("custom_title")
                conversations.append({
                    "conversation_id": conv["conversation_id"],
                    "title": title,
                    "created_at": conv.get("created_at"),
                    "updated_at": conv.get("updated_at"),
                    "message_count": await self.get_message_count(conv["conversation_id"])
                })
            
            logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting conversations: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_message_count(self, conversation_id: str) -> int:
        """Get total message count for a conversation"""
        try:
            count = await db_async.messages.count_documents({"conversation_id": conversation_id})
            return count
        except Exception as e:
            logger.error(f"Error counting messages for {conversation_id}: {e}")
            return 0  
        
        
    def get_legal_conversation_history(self, conversation_id: str, limit: int = 20):
        """Get legal conversation history with enhanced metadata"""
        try:
            messages = list(messages_col.find(
                {"conversation_id": conversation_id},
                {"_id": 0}
            ).sort("created_at", 1).limit(limit))
            
            # Add legal-specific metadata
            for message in messages:
                if message.get("role") == "assistant":
                    message["consultation_type"] = "legal_advice"
                    message["disclaimer"] = "Thông tin này chỉ mang tính tham khảo"
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting legal conversation history: {str(e)}")
            return []

    # def get_messages(self, conversation_id: str):
    #     messages = list(
    #         messages_col.find({"conversation_id": conversation_id})
    #         .sort("created_at", 1)
    #     )
    #     return [
    #         {
    #             "role": m["role"],
    #             "text": m["text"],
    #             "created_at": m["created_at"],
    #         }
    #         for m in messages
    #     ]

    async def get_legal_conversation_summary(self, conversation_id: str):
        """Get legal conversation summary with key insights"""
        try:
            # Get conversation metadata
            conversation = conversations_col.find_one({"conversation_id": conversation_id})
            
            if not conversation:
                return None
            
            # Get message statistics
            message_count = messages_col.count_documents({"conversation_id": conversation_id})
            user_queries = messages_col.count_documents({
                "conversation_id": conversation_id,
                "role": "user"
            })
            
            return {
                "conversation_id": conversation_id,
                "title": conversation.get("title", ""),
                "conversation_type": conversation.get("conversation_type", ""),
                "created_at": conversation.get("created_at", ""),
                "updated_at": conversation.get("updated_at", ""),
                "total_messages": message_count,
                "user_queries": user_queries,
                "legal_responses": message_count - user_queries,
                "tags": conversation.get("tags", [])
            }
            
        except Exception as e:
            logger.error(f"Error getting legal conversation summary: {str(e)}")
            return None
