"""
Test Configuration and Fixtures for Legal Retrieval API Testing
=============================================================
"""

import asyncio
import os
import pytest
import httpx
import redis
from pymongo import MongoClient
from qdrant_client import QdrantClient
from typing import Generator, AsyncGenerator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test Configuration
TEST_CONFIG = {
    "api_base_url": os.getenv("API_BASE_URL", "http://backend-api-test:8000"),
    "api_test_url": os.getenv("API_TEST_URL", "http://backend-api-test:8000/api"),
    "ws_test_url": os.getenv("WS_TEST_URL", "ws://backend-api-test:8000/ws"),
    "mongo_test_url": os.getenv("MONGO_TEST_URL", "mongodb://admin:testpass123@mongodb-test:27017/legaldb_test?authSource=admin"),
    "redis_test_url": os.getenv("REDIS_TEST_URL", "redis://redis-test:6379"),
    "qdrant_test_url": os.getenv("QDRANT_TEST_URL", "http://qdrant-test:6333"),
    "test_timeout": int(os.getenv("TEST_TIMEOUT", "300")),
    "max_retries": int(os.getenv("MAX_RETRIES", "3")),
}

# Test Data
TEST_USER_DATA = {
    "user_id": "api_test_user",
    "username": "apitester",
    "email": "apitest@example.com"
}

TEST_CONVERSATION_DATA = {
    "title": "Test Conversation for API",
    "user_id": "api_test_user"
}

TEST_MESSAGE_DATA = {
    "role": "user",
    "content": "Test message for API testing"
}

TEST_QUERY_DATA = {
    "query": "Luật doanh nghiệp",
    "max_results": 5,
    "user_id": "api_test_user"
}

# Pytest Fixtures
# ===============

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def api_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client for API testing."""
    async with httpx.AsyncClient(
        base_url=TEST_CONFIG["api_base_url"],
        timeout=httpx.Timeout(TEST_CONFIG["test_timeout"])
    ) as client:
        # Wait for API to be ready
        for attempt in range(TEST_CONFIG["max_retries"]):
            try:
                response = await client.get("/health")
                if response.status_code == 200:
                    logger.info("API is ready for testing")
                    break
            except Exception as e:
                logger.warning(f"API not ready, attempt {attempt + 1}: {e}")
                await asyncio.sleep(5)
        else:
            pytest.fail("API failed to become ready for testing")
        
        yield client

@pytest.fixture(scope="session")
def sync_api_client() -> Generator[httpx.Client, None, None]:
    """Synchronous HTTP client for API testing."""
    with httpx.Client(
        base_url=TEST_CONFIG["api_base_url"],
        timeout=httpx.Timeout(TEST_CONFIG["test_timeout"])
    ) as client:
        # Wait for API to be ready
        for attempt in range(TEST_CONFIG["max_retries"]):
            try:
                response = client.get("/health")
                if response.status_code == 200:
                    logger.info("API is ready for testing (sync)")
                    break
            except Exception as e:
                logger.warning(f"API not ready (sync), attempt {attempt + 1}: {e}")
                import time
                time.sleep(5)
        else:
            pytest.fail("API failed to become ready for testing (sync)")
        
        yield client

@pytest.fixture(scope="session")
def mongo_client() -> Generator[MongoClient, None, None]:
    """MongoDB client for database testing."""
    client = MongoClient(TEST_CONFIG["mongo_test_url"])
    try:
        # Test connection
        client.admin.command('ping')
        logger.info("MongoDB connection established")
        yield client
    except Exception as e:
        pytest.fail(f"Failed to connect to MongoDB: {e}")
    finally:
        client.close()

@pytest.fixture(scope="session")
def redis_client() -> Generator[redis.Redis, None, None]:
    """Redis client for cache testing."""
    client = redis.Redis.from_url(TEST_CONFIG["redis_test_url"])
    try:
        # Test connection
        client.ping()
        logger.info("Redis connection established")
        yield client
    except Exception as e:
        pytest.fail(f"Failed to connect to Redis: {e}")
    finally:
        client.close()

@pytest.fixture(scope="session")
def qdrant_client() -> Generator[QdrantClient, None, None]:
    """Qdrant client for vector database testing."""
    client = QdrantClient(url=TEST_CONFIG["qdrant_test_url"])
    try:
        # Test connection
        client.get_collections()
        logger.info("Qdrant connection established")
        yield client
    except Exception as e:
        pytest.fail(f"Failed to connect to Qdrant: {e}")
    finally:
        client.close()

@pytest.fixture(scope="function")
def test_database(mongo_client):
    """Get test database instance."""
    db = mongo_client.legaldb_test
    yield db
    # Cleanup after test if needed
    # Note: We don't clear the entire database to keep test data

@pytest.fixture(scope="function")
def clean_collections(test_database):
    """Clean specific collections before test."""
    collections_to_clean = ["test_conversations", "test_messages"]
    for collection_name in collections_to_clean:
        if collection_name in test_database.list_collection_names():
            test_database[collection_name].delete_many({})
    yield
    # Cleanup after test
    for collection_name in collections_to_clean:
        if collection_name in test_database.list_collection_names():
            test_database[collection_name].delete_many({})

@pytest.fixture(scope="function")
def test_user_id():
    """Generate unique test user ID."""
    import uuid
    return f"test_user_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="function")
def test_conversation_id():
    """Generate unique test conversation ID."""
    import uuid
    return f"test_conv_{uuid.uuid4().hex[:8]}"

# Test Data Fixtures
# ==================

@pytest.fixture
def sample_user_data(test_user_id):
    """Sample user data for testing."""
    return {
        "user_id": test_user_id,
        "username": f"testuser_{test_user_id}",
        "email": f"{test_user_id}@test.com"
    }

@pytest.fixture
def sample_conversation_data(test_user_id):
    """Sample conversation data for testing."""
    return {
        "title": "Test Conversation",
        "user_id": test_user_id
    }

@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "role": "user",
        "content": "This is a test message for API testing"
    }

@pytest.fixture
def sample_query_data():
    """Sample query data for RAG testing."""
    return {
        "query": "Luật doanh nghiệp Việt Nam",
        "max_results": 5,
        "include_metadata": True
    }

# Utility Fixtures
# ================

@pytest.fixture(scope="session")
def test_config():
    """Test configuration dictionary."""
    return TEST_CONFIG

@pytest.fixture
def api_headers():
    """Standard API headers for testing."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

@pytest.fixture
def websocket_headers():
    """WebSocket headers for testing."""
    return {
        "Authorization": "Bearer test-token"
    }

# Async Fixtures
# ==============

@pytest.fixture
async def async_test_database(mongo_client):
    """Async database fixture."""
    import motor.motor_asyncio
    
    async_client = motor.motor_asyncio.AsyncIOMotorClient(TEST_CONFIG["mongo_test_url"])
    db = async_client.legaldb_test
    yield db
    async_client.close()

# Session Cleanup
# ===============

def pytest_sessionfinish(session, exitstatus):
    """Cleanup after all tests are finished."""
    logger.info("Test session finished, performing cleanup...")
    
    # Additional cleanup if needed
    # Note: We keep test data for debugging, but could add cleanup here
    
    logger.info("Test cleanup completed")
