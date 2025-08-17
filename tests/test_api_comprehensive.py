"""
Comprehensive API Test Suite for Legal Retrieval System
======================================================
Tests all major API endpoints with Docker Compose setup
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TestAPIEndpoints:
    """Test all API endpoints comprehensively."""
    
    @pytest.mark.smoke
    @pytest.mark.api
    async def test_health_endpoint(self, api_client):
        """Test basic health check endpoint."""
        response = await api_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        
        logger.info("✅ Health endpoint test passed")

    @pytest.mark.smoke
    @pytest.mark.api
    async def test_root_endpoint(self, api_client):
        """Test root endpoint."""
        response = await api_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Legal Retrieval" in data["message"]
        
        logger.info("✅ Root endpoint test passed")

    @pytest.mark.api
    async def test_api_docs_endpoint(self, api_client):
        """Test API documentation endpoint."""
        response = await api_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        logger.info("✅ API docs endpoint test passed")

    @pytest.mark.api
    async def test_openapi_schema(self, api_client):
        """Test OpenAPI schema endpoint."""
        response = await api_client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        logger.info("✅ OpenAPI schema test passed")


class TestConversationAPI:
    """Test conversation-related API endpoints."""
    
    @pytest.mark.api
    async def test_create_conversation(self, api_client, sample_conversation_data):
        """Test creating a new conversation."""
        response = await api_client.post("/api/conversations", json=sample_conversation_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "conversation_id" in data
        assert data["title"] == sample_conversation_data["title"]
        assert data["user_id"] == sample_conversation_data["user_id"]
        assert data["status"] == "active"
        
        # Store conversation_id for other tests
        self.conversation_id = data["conversation_id"]
        logger.info(f"✅ Created conversation: {self.conversation_id}")

    @pytest.mark.api
    async def test_get_conversations(self, api_client, sample_user_data):
        """Test getting user conversations."""
        user_id = sample_user_data["user_id"]
        response = await api_client.get(f"/api/conversations?user_id={user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data["conversations"], list)
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        
        logger.info(f"✅ Retrieved {len(data['conversations'])} conversations")

    @pytest.mark.api
    async def test_get_conversation_detail(self, api_client):
        """Test getting specific conversation details."""
        if not hasattr(self, 'conversation_id'):
            pytest.skip("No conversation created in previous test")
            
        response = await api_client.get(f"/api/conversations/{self.conversation_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["conversation_id"] == self.conversation_id
        assert "title" in data
        assert "created_at" in data
        assert "status" in data
        
        logger.info("✅ Retrieved conversation details")

    @pytest.mark.api
    async def test_update_conversation(self, api_client):
        """Test updating conversation."""
        if not hasattr(self, 'conversation_id'):
            pytest.skip("No conversation created in previous test")
            
        update_data = {"title": "Updated Test Conversation"}
        response = await api_client.put(f"/api/conversations/{self.conversation_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == update_data["title"]
        
        logger.info("✅ Updated conversation successfully")


class TestMessageAPI:
    """Test message-related API endpoints."""
    
    @pytest.mark.api
    async def test_send_message(self, api_client, sample_message_data):
        """Test sending a message."""
        # First create a conversation if not exists
        conv_data = {"title": "Test Conversation for Messages", "user_id": "api_test_user"}
        conv_response = await api_client.post("/api/conversations", json=conv_data)
        conversation_id = conv_response.json()["conversation_id"]
        
        # Send message
        message_data = {**sample_message_data, "conversation_id": conversation_id}
        response = await api_client.post("/api/messages", json=message_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "message_id" in data
        assert data["content"] == sample_message_data["content"]
        assert data["role"] == sample_message_data["role"]
        assert data["conversation_id"] == conversation_id
        
        self.message_id = data["message_id"]
        self.conversation_id = conversation_id
        logger.info(f"✅ Sent message: {self.message_id}")

    @pytest.mark.api
    async def test_get_conversation_messages(self, api_client):
        """Test getting messages for a conversation."""
        if not hasattr(self, 'conversation_id'):
            pytest.skip("No conversation created in previous test")
            
        response = await api_client.get(f"/api/conversations/{self.conversation_id}/messages")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data["messages"], list)
        assert "total" in data
        
        if data["messages"]:
            message = data["messages"][0]
            assert "message_id" in message
            assert "content" in message
            assert "role" in message
            assert "timestamp" in message
        
        logger.info(f"✅ Retrieved {len(data['messages'])} messages")

    @pytest.mark.api
    async def test_get_message_detail(self, api_client):
        """Test getting specific message details."""
        if not hasattr(self, 'message_id'):
            pytest.skip("No message created in previous test")
            
        response = await api_client.get(f"/api/messages/{self.message_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message_id"] == self.message_id
        assert "content" in data
        assert "role" in data
        assert "timestamp" in data
        
        logger.info("✅ Retrieved message details")


class TestRAGAPI:
    """Test RAG (Retrieval Augmented Generation) API endpoints."""
    
    @pytest.mark.api
    @pytest.mark.rag
    async def test_query_endpoint(self, api_client, sample_query_data):
        """Test RAG query endpoint."""
        response = await api_client.post("/api/query", json=sample_query_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "sources" in data
        assert "query_id" in data
        assert isinstance(data["sources"], list)
        
        # Check response quality
        assert len(data["response"]) > 0
        if data["sources"]:
            source = data["sources"][0]
            assert "document_id" in source
            assert "title" in source
            assert "relevance_score" in source
        
        logger.info(f"✅ Query processed: {data['query_id']}")

    @pytest.mark.api
    @pytest.mark.rag
    async def test_search_documents(self, api_client):
        """Test document search endpoint."""
        search_data = {"query": "luật doanh nghiệp", "limit": 10}
        response = await api_client.post("/api/search", json=search_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "documents" in data
        assert "total" in data
        assert isinstance(data["documents"], list)
        
        if data["documents"]:
            doc = data["documents"][0]
            assert "document_id" in doc
            assert "title" in doc
            assert "content" in doc
            assert "score" in doc
        
        logger.info(f"✅ Found {len(data['documents'])} documents")

    @pytest.mark.api
    @pytest.mark.rag
    async def test_get_document_detail(self, api_client):
        """Test getting document details."""
        response = await api_client.get("/api/documents/test_doc_001")
        assert response.status_code == 200
        
        data = response.json()
        assert "document_id" in data
        assert "title" in data
        assert "content" in data
        assert "created_at" in data
        
        logger.info("✅ Retrieved document details")


class TestAsyncAPI:
    """Test asynchronous API endpoints (Celery tasks)."""
    
    @pytest.mark.api
    @pytest.mark.celery
    @pytest.mark.slow
    async def test_async_query_task(self, api_client, sample_query_data):
        """Test asynchronous query processing."""
        # Submit async query
        async_data = {**sample_query_data, "async": True}
        response = await api_client.post("/api/query/async", json=async_data)
        assert response.status_code == 202
        
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "pending"
        
        task_id = data["task_id"]
        
        # Poll for completion
        max_attempts = 30  # 30 seconds timeout
        for attempt in range(max_attempts):
            await asyncio.sleep(1)
            
            status_response = await api_client.get(f"/api/tasks/{task_id}")
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            
            if status_data["status"] == "completed":
                assert "result" in status_data
                assert "response" in status_data["result"]
                logger.info(f"✅ Async query completed: {task_id}")
                return
            elif status_data["status"] == "failed":
                pytest.fail(f"Async query failed: {status_data.get('error', 'Unknown error')}")
        
        pytest.fail(f"Async query timeout after {max_attempts} seconds")

    @pytest.mark.api
    @pytest.mark.celery
    async def test_task_status(self, api_client):
        """Test task status endpoint."""
        # Create a dummy task first
        task_data = {"query": "test query", "async": True}
        response = await api_client.post("/api/query/async", json=task_data)
        task_id = response.json()["task_id"]
        
        # Check status
        status_response = await api_client.get(f"/api/tasks/{task_id}")
        assert status_response.status_code == 200
        
        data = status_response.json()
        assert "task_id" in data
        assert "status" in data
        assert data["status"] in ["pending", "running", "completed", "failed"]
        
        logger.info(f"✅ Task status checked: {task_id}")


class TestErrorHandling:
    """Test API error handling and edge cases."""
    
    @pytest.mark.api
    async def test_invalid_endpoint(self, api_client):
        """Test 404 for invalid endpoints."""
        response = await api_client.get("/api/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        
        logger.info("✅ 404 error handling works")

    @pytest.mark.api
    async def test_invalid_json(self, api_client):
        """Test invalid JSON handling."""
        response = await api_client.post("/api/query", content="invalid json")
        assert response.status_code == 422
        
        logger.info("✅ Invalid JSON error handling works")

    @pytest.mark.api
    async def test_missing_required_fields(self, api_client):
        """Test missing required fields."""
        response = await api_client.post("/api/query", json={})
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data
        
        logger.info("✅ Missing fields validation works")

    @pytest.mark.api
    async def test_invalid_conversation_id(self, api_client):
        """Test invalid conversation ID."""
        response = await api_client.get("/api/conversations/invalid_id")
        assert response.status_code == 404
        
        logger.info("✅ Invalid ID error handling works")


class TestPerformance:
    """Test API performance and load handling."""
    
    @pytest.mark.api
    @pytest.mark.performance
    @pytest.mark.slow
    async def test_concurrent_queries(self, api_client):
        """Test concurrent query processing."""
        query_data = {"query": "test query", "max_results": 3}
        
        # Send multiple concurrent requests
        tasks = []
        for i in range(5):
            task = api_client.post("/api/query", json=query_data)
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all requests succeeded
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
        
        duration = end_time - start_time
        logger.info(f"✅ Processed 5 concurrent queries in {duration:.2f}s")
        
        # Performance check (should handle 5 queries in reasonable time)
        assert duration < 30  # 30 seconds max

    @pytest.mark.api
    @pytest.mark.performance
    async def test_response_time(self, api_client):
        """Test individual response times."""
        query_data = {"query": "luật doanh nghiệp", "max_results": 5}
        
        start_time = time.time()
        response = await api_client.post("/api/query", json=query_data)
        end_time = time.time()
        
        assert response.status_code == 200
        
        duration = end_time - start_time
        logger.info(f"✅ Query response time: {duration:.2f}s")
        
        # Performance check (should respond within reasonable time)
        assert duration < 15  # 15 seconds max for individual query


class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_complete_conversation_flow(self, api_client):
        """Test complete conversation workflow."""
        user_id = "integration_test_user"
        
        # 1. Create conversation
        conv_data = {"title": "Integration Test Conversation", "user_id": user_id}
        conv_response = await api_client.post("/api/conversations", json=conv_data)
        assert conv_response.status_code == 201
        conversation_id = conv_response.json()["conversation_id"]
        
        # 2. Send user message
        message_data = {
            "conversation_id": conversation_id,
            "role": "user",
            "content": "Tôi muốn biết về luật doanh nghiệp"
        }
        msg_response = await api_client.post("/api/messages", json=message_data)
        assert msg_response.status_code == 201
        
        # 3. Query RAG system
        query_data = {
            "query": "luật doanh nghiệp",
            "conversation_id": conversation_id,
            "user_id": user_id
        }
        rag_response = await api_client.post("/api/query", json=query_data)
        assert rag_response.status_code == 200
        rag_data = rag_response.json()
        
        # 4. Send assistant response
        assistant_message = {
            "conversation_id": conversation_id,
            "role": "assistant", 
            "content": rag_data["response"]
        }
        assistant_response = await api_client.post("/api/messages", json=assistant_message)
        assert assistant_response.status_code == 201
        
        # 5. Verify conversation has messages
        messages_response = await api_client.get(f"/api/conversations/{conversation_id}/messages")
        assert messages_response.status_code == 200
        messages_data = messages_response.json()
        assert len(messages_data["messages"]) >= 2
        
        logger.info(f"✅ Complete conversation flow test passed: {conversation_id}")


# Test Summary and Report
# ======================

def pytest_runtest_logreport(report):
    """Log test results for reporting."""
    if report.when == "call":
        if report.outcome == "passed":
            logger.info(f"PASSED: {report.nodeid}")
        elif report.outcome == "failed":
            logger.error(f"FAILED: {report.nodeid} - {report.longrepr}")
        elif report.outcome == "skipped":
            logger.warning(f"SKIPPED: {report.nodeid}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
