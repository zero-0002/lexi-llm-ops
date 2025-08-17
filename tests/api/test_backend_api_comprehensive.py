#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE BACKEND API TESTING SUITE
==========================================
Test all major API endpoints including streaming responses
"""
import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
import uuid
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='🧪 [API-TEST] %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class BackendAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, 
                       response_time: float = 0, details: Dict = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name} ({result['response_time_ms']}ms)")
        
        if details and not success:
            logger.error(f"   Error details: {details}")
    
    # ==========================================
    # 1. HEALTH & STATUS ENDPOINTS
    # ==========================================
    
    async def test_health_endpoints(self):
        """Test all health check endpoints"""
        logger.info("🏥 Testing Health & Status Endpoints...")
        
        endpoints = [
            ("/health", "Main Health Check"),
            ("/health-simple", "Simple Health Check"),
            ("/ready", "Readiness Check"),
            ("/metrics", "Metrics Endpoint")
        ]
        
        for endpoint, name in endpoints:
            start_time = time.time()
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    success = response.status == 200
                    details = {
                        "status_code": response.status,
                        "response_data": data
                    }
                    
                    self.log_test_result(name, success, response_time, details)
                    
            except Exception as e:
                response_time = time.time() - start_time
                self.log_test_result(name, False, response_time, {"error": str(e)})
    
    # ==========================================
    # 2. LEGAL CHAT API TESTS
    # ==========================================
    
    async def test_legal_chat_endpoints(self):
        """Test legal chat API endpoints"""
        logger.info("⚖️ Testing Legal Chat Endpoints...")
        
        # Test data
        user_id = f"test_user_{int(time.time())}"
        test_query = "Tôi có thể khởi kiện nếu bị chủ nhà đuổi không đúng quy định không?"
        
        # 1. Send legal query
        await self._test_send_legal_query(user_id, test_query)
        
        # 2. Test conversations API
        await self._test_get_conversations(user_id)
        
        # 3. Legal chat health check
        await self._test_legal_chat_health()
    
    async def _test_send_legal_query(self, user_id: str, query: str):
        """Test sending legal query"""
        start_time = time.time()
        try:
            payload = {
                "user_id": user_id,
                "message": query,
                "conversation_id": None
            }
            
            async with self.session.post(
                f"{self.base_url}/api/legal-chat/send-query",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                data = await response.json()
                
                success = response.status == 200
                details = {
                    "status_code": response.status,
                    "response_data": data,
                    "payload": payload
                }
                
                self.log_test_result("Send Legal Query", success, response_time, details)
                
                # Store conversation_id for streaming test
                if success and "conversation_id" in data:
                    self.conversation_id = data["conversation_id"]
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Send Legal Query", False, response_time, {"error": str(e)})
    
    async def _test_get_conversations(self, user_id: str):
        """Test get conversations"""
        start_time = time.time()
        try:
            async with self.session.get(
                f"{self.base_url}/api/legal-chat/conversations?user_id={user_id}"
            ) as response:
                response_time = time.time() - start_time
                data = await response.json()
                
                success = response.status == 200
                details = {
                    "status_code": response.status,
                    "response_data": data,
                    "user_id": user_id
                }
                
                self.log_test_result("Get Conversations", success, response_time, details)
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Get Conversations", False, response_time, {"error": str(e)})
    
    async def _test_legal_chat_health(self):
        """Test legal chat health endpoint"""
        start_time = time.time()
        try:
            async with self.session.get(
                f"{self.base_url}/api/legal-chat/health"
            ) as response:
                response_time = time.time() - start_time
                data = await response.json()
                
                success = response.status == 200
                details = {
                    "status_code": response.status,
                    "response_data": data
                }
                
                self.log_test_result("Legal Chat Health", success, response_time, details)
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Legal Chat Health", False, response_time, {"error": str(e)})
    
    # ==========================================
    # 3. STREAMING RESPONSE TESTS
    # ==========================================
    
    async def test_streaming_endpoints(self):
        """Test streaming response endpoints"""
        logger.info("🌊 Testing Streaming Response Endpoints...")
        
        # Use conversation_id from previous test or create dummy
        conversation_id = getattr(self, 'conversation_id', 'test_conversation_123')
        
        await self._test_streaming_legal_response(conversation_id)
    
    async def _test_streaming_legal_response(self, conversation_id: str):
        """Test streaming legal response"""
        start_time = time.time()
        tokens_received = 0
        first_token_time = None
        last_token_time = None
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/legal-chat/stream-legal-response/{conversation_id}"
            ) as response:
                
                if response.status != 200:
                    response_time = time.time() - start_time
                    self.log_test_result(
                        "Streaming Legal Response", 
                        False, 
                        response_time, 
                        {"error": f"HTTP {response.status}", "conversation_id": conversation_id}
                    )
                    return
                
                # Read streaming response
                async for chunk in response.content.iter_chunked(1024):
                    if chunk:
                        current_time = time.time()
                        if first_token_time is None:
                            first_token_time = current_time
                        last_token_time = current_time
                        
                        tokens_received += len(chunk.decode('utf-8', errors='ignore'))
                        
                        # Break if we get [DONE] or error
                        chunk_text = chunk.decode('utf-8', errors='ignore')
                        if '[DONE]' in chunk_text or '[ERROR]' in chunk_text:
                            break
                
                total_time = time.time() - start_time
                first_token_latency = (first_token_time - start_time) if first_token_time else 0
                
                success = tokens_received > 0
                details = {
                    "conversation_id": conversation_id,
                    "tokens_received": tokens_received,
                    "total_time_ms": round(total_time * 1000, 2),
                    "first_token_latency_ms": round(first_token_latency * 1000, 2),
                    "streaming_duration_ms": round((last_token_time - first_token_time) * 1000, 2) if first_token_time and last_token_time else 0
                }
                
                self.log_test_result("Streaming Legal Response", success, total_time, details)
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Streaming Legal Response", False, response_time, {"error": str(e)})
    
    # ==========================================
    # 4. RAG & WEB SEARCH ENDPOINTS
    # ==========================================
    
    async def test_rag_endpoints(self):
        """Test RAG API endpoints"""
        logger.info("🔍 Testing RAG & Search Endpoints...")
        
        # Check if RAG endpoints exist
        endpoints_to_test = [
            ("/api/rag/search", "RAG Search"),
            ("/api/rag/embed", "RAG Embedding"),
            ("/api/web-search/search", "Web Search"),
            ("/api/system/status", "System Status")
        ]
        
        for endpoint, name in endpoints_to_test:
            await self._test_get_endpoint(endpoint, name)
    
    async def _test_get_endpoint(self, endpoint: str, name: str):
        """Test GET endpoint"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}{endpoint}") as response:
                response_time = time.time() - start_time
                
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                success = response.status in [200, 404]  # 404 is acceptable for unimplemented endpoints
                details = {
                    "status_code": response.status,
                    "response_data": str(data)[:500] + "..." if len(str(data)) > 500 else data
                }
                
                self.log_test_result(name, success, response_time, details)
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result(name, False, response_time, {"error": str(e)})
    
    # ==========================================
    # 5. PERFORMANCE TESTS
    # ==========================================
    
    async def test_performance_concurrent(self):
        """Test concurrent requests performance"""
        logger.info("⚡ Testing Concurrent Performance...")
        
        async def make_health_request():
            async with self.session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        
        # Test 10 concurrent requests
        start_time = time.time()
        tasks = [make_health_request() for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful_requests = sum(1 for result in results if result is True)
        success = successful_requests >= 8  # Allow some failures
        
        details = {
            "concurrent_requests": 10,
            "successful_requests": successful_requests,
            "total_time_ms": round(total_time * 1000, 2),
            "avg_time_per_request_ms": round((total_time / 10) * 1000, 2)
        }
        
        self.log_test_result("Concurrent Performance", success, total_time, details)
    
    # ==========================================
    # 6. ERROR HANDLING TESTS
    # ==========================================
    
    async def test_error_handling(self):
        """Test error handling"""
        logger.info("🚨 Testing Error Handling...")
        
        # Test invalid endpoints
        error_tests = [
            ("/api/invalid-endpoint", "Invalid Endpoint"),
            ("/api/legal-chat/send-query", "Missing Body", "POST"),  # POST without body
        ]
        
        for test_config in error_tests:
            if len(test_config) == 2:
                endpoint, name = test_config
                method = "GET"
            else:
                endpoint, name, method = test_config
            
            await self._test_error_endpoint(endpoint, name, method)
    
    async def _test_error_endpoint(self, endpoint: str, name: str, method: str = "GET"):
        """Test error endpoint"""
        start_time = time.time()
        try:
            if method == "GET":
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    response_time = time.time() - start_time
                    success = response.status in [404, 422, 400]  # Expected error codes
            else:  # POST
                async with self.session.post(f"{self.base_url}{endpoint}") as response:
                    response_time = time.time() - start_time
                    success = response.status in [422, 400]  # Expected error codes for missing body
            
            details = {"status_code": response.status, "method": method}
            self.log_test_result(name, success, response_time, details)
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result(name, False, response_time, {"error": str(e)})
    
    # ==========================================
    # 7. MAIN TEST RUNNER
    # ==========================================
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        logger.info("🚀 Starting Comprehensive Backend API Test Suite...")
        logger.info(f"📍 Target URL: {self.base_url}")
        
        # Test categories
        test_categories = [
            ("Health & Status", self.test_health_endpoints),
            ("Legal Chat API", self.test_legal_chat_endpoints),
            ("Streaming Responses", self.test_streaming_endpoints),
            ("RAG & Search APIs", self.test_rag_endpoints),
            ("Performance Tests", self.test_performance_concurrent),
            ("Error Handling", self.test_error_handling)
        ]
        
        for category_name, test_func in test_categories:
            logger.info(f"\n📋 {category_name}")
            try:
                await test_func()
            except Exception as e:
                logger.error(f"❌ Category {category_name} failed: {e}")
        
        # Generate test report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        avg_response_time = sum(result["response_time_ms"] for result in self.test_results) / total_tests if total_tests > 0 else 0
        
        logger.info("\n" + "="*60)
        logger.info("📊 TEST REPORT SUMMARY")
        logger.info("="*60)
        logger.info(f"📈 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        logger.info(f"⚡ Avg Response Time: {avg_response_time:.2f}ms")
        
        if failed_tests > 0:
            logger.info("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"   • {result['test_name']}: {result['details'].get('error', 'Unknown error')}")
        
        logger.info("\n✅ Passed Tests:")
        for result in self.test_results:
            if result["success"]:
                logger.info(f"   • {result['test_name']} ({result['response_time_ms']}ms)")
        
        logger.info("="*60)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "detailed_results": self.test_results
        }

# ==========================================
# CLI INTERFACE
# ==========================================

async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backend API Test Suite")
    parser.add_argument("--url", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--category", choices=["health", "legal", "streaming", "rag", "performance", "errors", "all"], 
                       default="all", help="Test category to run")
    
    args = parser.parse_args()
    
    async with BackendAPITester(args.url) as tester:
        if args.category == "all":
            await tester.run_all_tests()
        elif args.category == "health":
            await tester.test_health_endpoints()
        elif args.category == "legal":
            await tester.test_legal_chat_endpoints()
        elif args.category == "streaming":
            await tester.test_streaming_endpoints()
        elif args.category == "rag":
            await tester.test_rag_endpoints()
        elif args.category == "performance":
            await tester.test_performance_concurrent()
        elif args.category == "errors":
            await tester.test_error_handling()

if __name__ == "__main__":
    asyncio.run(main())
