"""
Database Tests for Legal Retrieval System
========================================
Tests MongoDB, Redis, and Qdrant integration
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TestMongoDB:
    """Test MongoDB database operations."""
    
    @pytest.mark.database
    async def test_mongodb_connection(self, mongo_client):
        """Test MongoDB connection."""
        # Test ping
        result = mongo_client.admin.command('ping')
        assert result['ok'] == 1
        
        logger.info("✅ MongoDB connection successful")

    @pytest.mark.database
    async def test_database_collections(self, test_database):
        """Test database collections exist."""
        collections = test_database.list_collection_names()
        
        expected_collections = ["users", "conversations", "messages", "documents"]
        for collection in expected_collections:
            assert collection in collections
        
        logger.info(f"✅ Found {len(collections)} collections")

    @pytest.mark.database
    async def test_user_operations(self, test_database, sample_user_data):
        """Test user CRUD operations."""
        users = test_database.users
        
        # Create user
        result = users.insert_one(sample_user_data)
        assert result.inserted_id is not None
        
        # Read user
        user = users.find_one({"user_id": sample_user_data["user_id"]})
        assert user is not None
        assert user["username"] == sample_user_data["username"]
        
        # Update user
        update_result = users.update_one(
            {"user_id": sample_user_data["user_id"]},
            {"$set": {"email": "updated@test.com"}}
        )
        assert update_result.modified_count == 1
        
        # Verify update
        updated_user = users.find_one({"user_id": sample_user_data["user_id"]})
        assert updated_user["email"] == "updated@test.com"
        
        # Delete user
        delete_result = users.delete_one({"user_id": sample_user_data["user_id"]})
        assert delete_result.deleted_count == 1
        
        logger.info("✅ User CRUD operations successful")

    @pytest.mark.database
    async def test_conversation_operations(self, test_database, sample_conversation_data):
        """Test conversation CRUD operations."""
        conversations = test_database.conversations
        
        # Add required fields
        conversation_data = {
            **sample_conversation_data,
            "conversation_id": f"test_conv_{datetime.now().timestamp()}",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status": "active"
        }
        
        # Create conversation
        result = conversations.insert_one(conversation_data)
        assert result.inserted_id is not None
        
        # Read conversation
        conversation = conversations.find_one({"conversation_id": conversation_data["conversation_id"]})
        assert conversation is not None
        assert conversation["title"] == conversation_data["title"]
        
        # Update conversation
        update_result = conversations.update_one(
            {"conversation_id": conversation_data["conversation_id"]},
            {"$set": {"title": "Updated Title", "updated_at": datetime.now()}}
        )
        assert update_result.modified_count == 1
        
        # Delete conversation
        delete_result = conversations.delete_one({"conversation_id": conversation_data["conversation_id"]})
        assert delete_result.deleted_count == 1
        
        logger.info("✅ Conversation CRUD operations successful")

    @pytest.mark.database
    async def test_message_operations(self, test_database, sample_message_data):
        """Test message CRUD operations."""
        messages = test_database.messages
        
        # Add required fields
        message_data = {
            **sample_message_data,
            "message_id": f"test_msg_{datetime.now().timestamp()}",
            "conversation_id": "test_conversation",
            "timestamp": datetime.now()
        }
        
        # Create message
        result = messages.insert_one(message_data)
        assert result.inserted_id is not None
        
        # Read message
        message = messages.find_one({"message_id": message_data["message_id"]})
        assert message is not None
        assert message["content"] == message_data["content"]
        
        # Update message
        update_result = messages.update_one(
            {"message_id": message_data["message_id"]},
            {"$set": {"content": "Updated content"}}
        )
        assert update_result.modified_count == 1
        
        # Delete message
        delete_result = messages.delete_one({"message_id": message_data["message_id"]})
        assert delete_result.deleted_count == 1
        
        logger.info("✅ Message CRUD operations successful")

    @pytest.mark.database
    async def test_document_search(self, test_database):
        """Test document text search."""
        documents = test_database.documents
        
        # Search for documents
        search_results = list(documents.find({"$text": {"$search": "luật doanh nghiệp"}}))
        
        # Should find at least one test document
        assert len(search_results) > 0
        
        # Verify search result structure
        doc = search_results[0]
        assert "document_id" in doc
        assert "title" in doc
        assert "content" in doc
        
        logger.info(f"✅ Found {len(search_results)} documents in text search")

    @pytest.mark.database
    async def test_aggregation_queries(self, test_database):
        """Test MongoDB aggregation queries."""
        conversations = test_database.conversations
        
        # Aggregate conversations by user
        pipeline = [
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        results = list(conversations.aggregate(pipeline))
        assert isinstance(results, list)
        
        if results:
            result = results[0]
            assert "_id" in result
            assert "count" in result
            assert isinstance(result["count"], int)
        
        logger.info("✅ Aggregation queries successful")


class TestRedis:
    """Test Redis cache and session operations."""
    
    @pytest.mark.database
    async def test_redis_connection(self, redis_client):
        """Test Redis connection."""
        result = redis_client.ping()
        assert result is True
        
        logger.info("✅ Redis connection successful")

    @pytest.mark.database
    async def test_redis_basic_operations(self, redis_client):
        """Test basic Redis operations."""
        # Set value
        result = redis_client.set("test_key", "test_value")
        assert result is True
        
        # Get value
        value = redis_client.get("test_key")
        assert value.decode() == "test_value"
        
        # Delete value
        result = redis_client.delete("test_key")
        assert result == 1
        
        # Verify deletion
        value = redis_client.get("test_key")
        assert value is None
        
        logger.info("✅ Redis basic operations successful")

    @pytest.mark.database
    async def test_redis_expiration(self, redis_client):
        """Test Redis key expiration."""
        # Set value with expiration
        result = redis_client.setex("temp_key", 2, "temp_value")
        assert result is True
        
        # Verify value exists
        value = redis_client.get("temp_key")
        assert value.decode() == "temp_value"
        
        # Wait for expiration
        await asyncio.sleep(3)
        
        # Verify value expired
        value = redis_client.get("temp_key")
        assert value is None
        
        logger.info("✅ Redis expiration test successful")

    @pytest.mark.database
    async def test_redis_hash_operations(self, redis_client):
        """Test Redis hash operations."""
        hash_key = "test_hash"
        
        # Set hash fields
        redis_client.hset(hash_key, "field1", "value1")
        redis_client.hset(hash_key, "field2", "value2")
        
        # Get hash field
        value = redis_client.hget(hash_key, "field1")
        assert value.decode() == "value1"
        
        # Get all hash fields
        hash_data = redis_client.hgetall(hash_key)
        assert b"field1" in hash_data
        assert b"field2" in hash_data
        
        # Delete hash
        result = redis_client.delete(hash_key)
        assert result == 1
        
        logger.info("✅ Redis hash operations successful")

    @pytest.mark.database
    async def test_redis_list_operations(self, redis_client):
        """Test Redis list operations."""
        list_key = "test_list"
        
        # Push values to list
        redis_client.lpush(list_key, "item1", "item2", "item3")
        
        # Get list length
        length = redis_client.llen(list_key)
        assert length == 3
        
        # Pop value from list
        value = redis_client.rpop(list_key)
        assert value.decode() == "item1"
        
        # Get list range
        items = redis_client.lrange(list_key, 0, -1)
        assert len(items) == 2
        
        # Clean up
        redis_client.delete(list_key)
        
        logger.info("✅ Redis list operations successful")


class TestQdrant:
    """Test Qdrant vector database operations."""
    
    @pytest.mark.database
    async def test_qdrant_connection(self, qdrant_client):
        """Test Qdrant connection."""
        collections = qdrant_client.get_collections()
        assert hasattr(collections, 'collections')
        
        logger.info("✅ Qdrant connection successful")

    @pytest.mark.database
    async def test_qdrant_collection_operations(self, qdrant_client):
        """Test Qdrant collection operations."""
        collection_name = "test_collection"
        
        try:
            # Create collection
            from qdrant_client.models import Distance, VectorParams
            
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            
            # Verify collection exists
            collections = qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            assert collection_name in collection_names
            
            # Get collection info
            info = qdrant_client.get_collection(collection_name)
            assert info.config.params.vectors.size == 384
            
            logger.info("✅ Qdrant collection operations successful")
            
        finally:
            # Clean up
            try:
                qdrant_client.delete_collection(collection_name)
            except Exception:
                pass

    @pytest.mark.database
    async def test_qdrant_vector_operations(self, qdrant_client):
        """Test Qdrant vector operations."""
        collection_name = "test_vectors"
        
        try:
            # Create collection
            from qdrant_client.models import Distance, VectorParams, PointStruct
            
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=3, distance=Distance.COSINE)
            )
            
            # Insert vectors
            points = [
                PointStruct(
                    id=1,
                    vector=[1.0, 0.0, 0.0],
                    payload={"text": "first document"}
                ),
                PointStruct(
                    id=2,
                    vector=[0.0, 1.0, 0.0],
                    payload={"text": "second document"}
                )
            ]
            
            result = qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )
            assert result.status == "completed"
            
            # Search vectors
            search_results = qdrant_client.search(
                collection_name=collection_name,
                query_vector=[1.0, 0.0, 0.0],
                limit=2
            )
            
            assert len(search_results) > 0
            assert search_results[0].id == 1
            assert search_results[0].score > 0.9  # Should be very similar
            
            logger.info("✅ Qdrant vector operations successful")
            
        finally:
            # Clean up
            try:
                qdrant_client.delete_collection(collection_name)
            except Exception:
                pass

    @pytest.mark.database
    async def test_qdrant_search_with_filter(self, qdrant_client):
        """Test Qdrant search with metadata filtering."""
        collection_name = "test_search_filter"
        
        try:
            # Create collection
            from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
            
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=3, distance=Distance.COSINE)
            )
            
            # Insert vectors with metadata
            points = [
                PointStruct(
                    id=1,
                    vector=[1.0, 0.0, 0.0],
                    payload={"category": "legal", "year": 2020}
                ),
                PointStruct(
                    id=2,
                    vector=[0.0, 1.0, 0.0],
                    payload={"category": "legal", "year": 2021}
                ),
                PointStruct(
                    id=3,
                    vector=[0.0, 0.0, 1.0],
                    payload={"category": "other", "year": 2020}
                )
            ]
            
            qdrant_client.upsert(collection_name=collection_name, points=points)
            
            # Search with filter
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(value="legal")
                    )
                ]
            )
            
            search_results = qdrant_client.search(
                collection_name=collection_name,
                query_vector=[1.0, 0.0, 0.0],
                query_filter=search_filter,
                limit=10
            )
            
            # Should only return legal documents
            assert len(search_results) == 2
            for result in search_results:
                assert result.payload["category"] == "legal"
            
            logger.info("✅ Qdrant filtered search successful")
            
        finally:
            # Clean up
            try:
                qdrant_client.delete_collection(collection_name)
            except Exception:
                pass


class TestDatabaseIntegration:
    """Test database integration scenarios."""
    
    @pytest.mark.database
    @pytest.mark.integration
    async def test_cross_database_consistency(self, test_database, redis_client, sample_conversation_data):
        """Test consistency across MongoDB and Redis."""
        # Create conversation in MongoDB
        conversation_data = {
            **sample_conversation_data,
            "conversation_id": f"consistency_test_{datetime.now().timestamp()}",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status": "active"
        }
        
        conversations = test_database.conversations
        result = conversations.insert_one(conversation_data)
        assert result.inserted_id is not None
        
        # Cache conversation in Redis
        import json
        cache_key = f"conversation:{conversation_data['conversation_id']}"
        cache_data = {
            "conversation_id": conversation_data["conversation_id"],
            "title": conversation_data["title"],
            "user_id": conversation_data["user_id"]
        }
        
        redis_client.setex(cache_key, 3600, json.dumps(cache_data))
        
        # Verify data in both databases
        # MongoDB
        mongo_conversation = conversations.find_one({"conversation_id": conversation_data["conversation_id"]})
        assert mongo_conversation is not None
        
        # Redis
        cached_conversation = redis_client.get(cache_key)
        assert cached_conversation is not None
        cached_data = json.loads(cached_conversation.decode())
        assert cached_data["conversation_id"] == conversation_data["conversation_id"]
        
        # Clean up
        conversations.delete_one({"conversation_id": conversation_data["conversation_id"]})
        redis_client.delete(cache_key)
        
        logger.info("✅ Cross-database consistency test successful")

    @pytest.mark.database
    @pytest.mark.integration
    async def test_database_transaction_simulation(self, test_database, redis_client):
        """Test transaction-like behavior across databases."""
        user_id = f"transaction_test_{datetime.now().timestamp()}"
        conversation_id = f"conv_{user_id}"
        
        try:
            # Step 1: Create user
            user_data = {
                "user_id": user_id,
                "username": f"user_{user_id}",
                "email": f"{user_id}@test.com",
                "created_at": datetime.now()
            }
            
            users = test_database.users
            user_result = users.insert_one(user_data)
            assert user_result.inserted_id is not None
            
            # Step 2: Create conversation
            conversation_data = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "title": "Transaction Test Conversation",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "status": "active"
            }
            
            conversations = test_database.conversations
            conv_result = conversations.insert_one(conversation_data)
            assert conv_result.inserted_id is not None
            
            # Step 3: Cache in Redis
            import json
            cache_key = f"user_conversations:{user_id}"
            redis_client.sadd(cache_key, conversation_id)
            redis_client.expire(cache_key, 3600)
            
            # Verify all operations succeeded
            # MongoDB user
            user = users.find_one({"user_id": user_id})
            assert user is not None
            
            # MongoDB conversation
            conversation = conversations.find_one({"conversation_id": conversation_id})
            assert conversation is not None
            
            # Redis cache
            cached_conversations = redis_client.smembers(cache_key)
            assert conversation_id.encode() in cached_conversations
            
            logger.info("✅ Database transaction simulation successful")
            
        finally:
            # Clean up (simulating transaction rollback)
            test_database.users.delete_one({"user_id": user_id})
            test_database.conversations.delete_one({"conversation_id": conversation_id})
            redis_client.delete(f"user_conversations:{user_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
