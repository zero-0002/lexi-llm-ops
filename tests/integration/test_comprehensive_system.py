#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE BACKEND & STREAMING TEST SUITE
==============================================
Test suite to verify all backend APIs and streaming functionality after Redis IP resolution fixes
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

class BackendStreamingTester:
    """Comprehensive tester for backend APIs and streaming"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
        
    async def test_health_endpoints(self, session: aiohttp.ClientSession):
        """Test all health endpoints"""
        print("🏥 Testing Health Endpoints...")
        
        endpoints = [
            "/health",
            "/health-simple", 
            "/ready",
            "/api/legal-chat/health",
            "/api/rag/health",
            "/api/web-search/health",
            "/api/system/health"
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                    response_time = time.time() - start_time
                    status = response.status
                    data = await response.text()
                    
                    result = {
                        "test": f"Health - {endpoint}",
                        "status": "✅ PASS" if status == 200 else "❌ FAIL",
                        "status_code": status,
                        "response_time": f"{response_time:.2f}s",
                        "endpoint": endpoint
                    }
                    
                    if status == 200:
                        try:
                            json_data = json.loads(data)
                            result["response"] = json_data.get("status", "unknown")
                        except:
                            result["response"] = "non-json"
                    else:
                        result["error"] = data[:100]
                        
                    self.results.append(result)
                    print(f"  {result['status']} {endpoint} - {status} ({response_time:.2f}s)")
                    
            except Exception as e:
                result = {
                    "test": f"Health - {endpoint}",
                    "status": "❌ ERROR",
                    "error": str(e)[:100],
                    "endpoint": endpoint
                }
                self.results.append(result)
                print(f"  ❌ ERROR {endpoint} - {str(e)[:50]}")
                
    async def test_legal_chat_endpoints(self, session: aiohttp.ClientSession):
        """Test legal chat endpoints"""
        print("\n💬 Testing Legal Chat Endpoints...")
        
        # Test data
        test_conversations = [
            {
                "user_id": "test_user_001",
                "conversation_id": f"test_conv_{uuid.uuid4().hex[:8]}",
                "message": "Luật về bảo vệ quyền lợi người tiêu dùng như thế nào?"
            },
            {
                "user_id": "test_user_002", 
                "conversation_id": f"test_conv_{uuid.uuid4().hex[:8]}",
                "message": "Quy định về hợp đồng lao động?"
            }
        ]
        
        for test_data in test_conversations:
            # Test send-query endpoint
            try:
                start_time = time.time()
                async with session.post(
                    f"{self.base_url}/api/legal-chat/send-query",
                    json=test_data,
                    timeout=30
                ) as response:
                    response_time = time.time() - start_time
                    status = response.status
                    data = await response.text()
                    
                    result = {
                        "test": f"Legal Chat - send-query",
                        "status": "✅ PASS" if status == 200 else "❌ FAIL",
                        "status_code": status,
                        "response_time": f"{response_time:.2f}s",
                        "conversation_id": test_data["conversation_id"]
                    }
                    
                    if status == 200:
                        try:
                            json_data = json.loads(data)
                            result["task_id"] = json_data.get("task_id", "unknown")
                            result["response"] = "Task created successfully"
                        except:
                            result["response"] = "non-json"
                    else:
                        result["error"] = data[:100]
                        
                    self.results.append(result)
                    print(f"  {result['status']} send-query - {status} ({response_time:.2f}s) - {test_data['conversation_id']}")
                    
            except Exception as e:
                result = {
                    "test": f"Legal Chat - send-query",
                    "status": "❌ ERROR",
                    "error": str(e)[:100],
                    "conversation_id": test_data["conversation_id"]
                }
                self.results.append(result)
                print(f"  ❌ ERROR send-query - {str(e)[:50]} - {test_data['conversation_id']}")
                
    async def test_streaming_endpoints(self, session: aiohttp.ClientSession):
        """Test streaming response endpoints"""
        print("\n🌊 Testing Streaming Endpoints...")
        
        # Create test conversations for streaming
        test_conversations = [
            f"stream_test_{uuid.uuid4().hex[:8]}",
            f"stream_test_{uuid.uuid4().hex[:8]}"
        ]
        
        for conversation_id in test_conversations:
            try:
                start_time = time.time()
                
                # First send a query to create task
                query_data = {
                    "user_id": "stream_tester",
                    "conversation_id": conversation_id,
                    "message": "Quy định về thuế thu nhập cá nhân như thế nào?"
                }
                
                async with session.post(
                    f"{self.base_url}/api/legal-chat/send-query",
                    json=query_data,
                    timeout=15
                ) as response:
                    if response.status != 200:
                        print(f"  ❌ Failed to create query for {conversation_id}")
                        continue
                        
                # Wait a bit for task to start
                await asyncio.sleep(2)
                
                # Now test streaming endpoint
                stream_start_time = time.time()
                content_received = ""
                
                async with session.get(
                    f"{self.base_url}/api/legal-chat/stream-legal-response/{conversation_id}",
                    timeout=60
                ) as response:
                    stream_response_time = time.time() - stream_start_time
                    status = response.status
                    
                    if status == 200:
                        chunks_received = 0
                        async for chunk in response.content.iter_chunked(1024):
                            if chunk:
                                content_received += chunk.decode('utf-8', errors='ignore')
                                chunks_received += 1
                                
                                # Stop after receiving some content or timeout
                                if chunks_received > 10 or time.time() - stream_start_time > 30:
                                    break
                                    
                        result = {
                            "test": f"Streaming - {conversation_id}",
                            "status": "✅ PASS" if chunks_received > 0 else "⚠️ NO_CONTENT",
                            "status_code": status,
                            "response_time": f"{stream_response_time:.2f}s",
                            "chunks_received": chunks_received,
                            "content_preview": content_received[:100] if content_received else "No content",
                            "conversation_id": conversation_id
                        }
                    else:
                        error_data = await response.text()
                        result = {
                            "test": f"Streaming - {conversation_id}",
                            "status": "❌ FAIL",
                            "status_code": status,
                            "error": error_data[:100],
                            "conversation_id": conversation_id
                        }
                        
                    self.results.append(result)
                    print(f"  {result['status']} stream-{conversation_id} - {status} - {result.get('chunks_received', 0)} chunks")
                    
            except Exception as e:
                result = {
                    "test": f"Streaming - {conversation_id}",
                    "status": "❌ ERROR", 
                    "error": str(e)[:100],
                    "conversation_id": conversation_id
                }
                self.results.append(result)
                print(f"  ❌ ERROR stream-{conversation_id} - {str(e)[:50]}")
                
    async def test_celery_workers(self, session: aiohttp.ClientSession):
        """Test Celery worker status via metrics"""
        print("\n🔧 Testing Celery Workers...")
        
        try:
            async with session.get(f"{self.base_url}/metrics", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    celery_info = data.get("celery", {})
                    
                    result = {
                        "test": "Celery Workers Status",
                        "status": "✅ PASS" if celery_info.get("active_workers", 0) > 0 else "⚠️ NO_WORKERS",
                        "active_workers": celery_info.get("active_workers", 0),
                        "total_workers": len(celery_info.get("workers", [])),
                        "worker_names": celery_info.get("workers", [])  # workers is already a list of strings
                    }
                    
                    self.results.append(result)
                    print(f"  {result['status']} Workers: {result['active_workers']} active, {result['total_workers']} total")
                    
                    for worker in result['worker_names']:
                        print(f"    - {worker}")
                        
                else:
                    result = {
                        "test": "Celery Workers Status",
                        "status": "❌ FAIL",
                        "status_code": response.status,
                        "error": await response.text()
                    }
                    self.results.append(result)
                    print(f"  ❌ FAIL - Status {response.status}")
                    
        except Exception as e:
            result = {
                "test": "Celery Workers Status",
                "status": "❌ ERROR",
                "error": str(e)[:100]
            }
            self.results.append(result)
            print(f"  ❌ ERROR - {str(e)[:50]}")
            
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"].startswith("✅")])
        failed_tests = len([r for r in self.results if r["status"].startswith("❌")])
        warning_tests = len([r for r in self.results if r["status"].startswith("⚠️")])
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        for result in self.results:
            status_icon = result["status"][:2]
            test_name = result["test"]
            
            if "response_time" in result:
                print(f"{status_icon} {test_name:<40} {result.get('status_code', 'N/A'):<4} {result['response_time']:<8}")
            else:
                print(f"{status_icon} {test_name:<40} {result.get('status_code', 'N/A'):<4}")
                
            if "error" in result:
                print(f"   ⚠️ Error: {result['error']}")
                
            if "chunks_received" in result:
                print(f"   📦 Chunks: {result['chunks_received']}, Content: {result.get('content_preview', 'N/A')[:50]}...")
                
        print("\n" + "="*80)
        
        # Streaming analysis
        streaming_tests = [r for r in self.results if "Streaming" in r["test"]]
        if streaming_tests:
            print("🌊 STREAMING ANALYSIS:")
            successful_streams = len([r for r in streaming_tests if r["status"].startswith("✅")])
            print(f"   Streaming Success Rate: {(successful_streams/len(streaming_tests)*100):.1f}%")
            
            for stream in streaming_tests:
                if stream["status"].startswith("✅"):
                    print(f"   ✅ {stream['conversation_id']}: {stream.get('chunks_received', 0)} chunks received")
                else:
                    print(f"   ❌ {stream['conversation_id']}: {stream.get('error', 'Unknown error')[:50]}")
                    
        print("="*80)

async def run_comprehensive_test():
    """Run all tests"""
    print("🚀 STARTING COMPREHENSIVE BACKEND & STREAMING TEST SUITE")
    print("="*80)
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: http://localhost:8000")
    print("="*80)
    
    tester = BackendStreamingTester()
    
    timeout = aiohttp.ClientTimeout(total=120)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Run all test suites
        await tester.test_health_endpoints(session)
        await tester.test_legal_chat_endpoints(session)
        await tester.test_streaming_endpoints(session)
        await tester.test_celery_workers(session)
        
    # Print comprehensive summary
    tester.print_summary()
    
    print(f"\n⏰ Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 COMPREHENSIVE TEST SUITE COMPLETED!")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
