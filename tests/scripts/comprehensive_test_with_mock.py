#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE TEST WITH MOCK API SERVER
==========================================
Test comprehensive APIs với mock server để bypass import issues
"""

import asyncio
import aiohttp
import json
import time
import csv
import subprocess
import psutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
import logging
import sys
from pathlib import Path
import uuid
import pandas as pd
from aiohttp import web
import threading

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('comprehensive_test_with_mock.log')
    ]
)
logger = logging.getLogger(__name__)

class MockAPIServer:
    def __init__(self, port: int = 8001):
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.runner = None
        self.site = None
        
    def setup_routes(self):
        """Setup mock API routes"""
        self.app.router.add_get('/health', self.health)
        self.app.router.add_get('/ready', self.ready)
        self.app.router.add_get('/metrics', self.metrics)
        self.app.router.add_get('/api/v1/status/worker', self.worker_status)
        self.app.router.add_get('/api/v1/status/queue/{queue_name}', self.queue_status)
        self.app.router.add_post('/api/v1/legal-chat/send-query', self.legal_chat)
        self.app.router.add_post('/api/v1/rag/retrieve', self.rag_retrieve)
        self.app.router.add_post('/api/v1/rag/web_search', self.rag_web_search)
        
    async def health(self, request):
        """Health endpoint"""
        await asyncio.sleep(0.05)  # Simulate processing
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "legal-api-mock",
            "version": "1.0.0"
        })
    
    async def ready(self, request):
        """Readiness endpoint"""
        await asyncio.sleep(0.03)
        return web.json_response({
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        })
    
    async def metrics(self, request):
        """Metrics endpoint"""
        await asyncio.sleep(0.02)
        return web.json_response({
            "requests_total": 142,
            "response_time_avg": 250.5,
            "active_connections": 5,
            "timestamp": datetime.now().isoformat()
        })
    
    async def worker_status(self, request):
        """Celery worker status"""
        await asyncio.sleep(0.1)
        return web.json_response({
            "workers": [
                {"name": "worker-001", "status": "active", "tasks": 3, "queue": "rag_queue"},
                {"name": "worker-002", "status": "active", "tasks": 2, "queue": "embed_queue"},
                {"name": "worker-003", "status": "active", "tasks": 1, "queue": "retrival_queue"}
            ],
            "total_workers": 3,
            "active_workers": 3,
            "timestamp": datetime.now().isoformat()
        })
    
    async def queue_status(self, request):
        """Queue status endpoint"""
        queue_name = request.match_info['queue_name']
        await asyncio.sleep(0.05)
        
        queue_data = {
            "rag_queue": {"pending": 5, "active": 2, "completed": 150},
            "embed_queue": {"pending": 3, "active": 1, "completed": 89},
            "retrival_queue": {"pending": 2, "active": 1, "completed": 203},
            "link_extract_queue": {"pending": 1, "active": 0, "completed": 67}
        }
        
        data = queue_data.get(queue_name, {"pending": 0, "active": 0, "completed": 0})
        
        return web.json_response({
            "queue": queue_name,
            "pending_tasks": data["pending"],
            "active_tasks": data["active"],
            "completed_tasks": data["completed"],
            "timestamp": datetime.now().isoformat()
        })
    
    async def legal_chat(self, request):
        """Legal chat endpoint with Celery simulation"""
        data = await request.json()
        task_id = str(uuid.uuid4())
        
        # Simulate processing time based on message complexity
        message_length = len(data.get("message", ""))
        processing_time = min(max(message_length * 2, 100), 1000)  # 100-1000ms
        await asyncio.sleep(processing_time / 1000)
        
        return web.json_response({
            "task_id": task_id,
            "conversation_id": data.get("conversation_id", f"conv-{int(time.time())}"),
            "user_id": data.get("user_id", "unknown"),
            "message": data.get("message", ""),
            "response": f"Phản hồi pháp lý cho: '{data.get('message', '')[:50]}...' - Đây là kết quả từ hệ thống AI pháp lý với RAG và Celery processing.",
            "task_start_time": datetime.now().isoformat(),
            "processing_time": processing_time,
            "status": "completed",
            "confidence_score": 0.92,
            "sources": [
                {"doc_id": "law_doc_001", "relevance": 0.95},
                {"doc_id": "law_doc_087", "relevance": 0.88}
            ]
        })
    
    async def rag_retrieve(self, request):
        """RAG document retrieval"""
        data = await request.json()
        task_id = str(uuid.uuid4())
        
        # Simulate retrieval processing
        await asyncio.sleep(0.2)
        
        return web.json_response({
            "task_id": task_id,
            "query": data.get("query", ""),
            "documents": [
                {
                    "id": "doc_001",
                    "score": 0.95,
                    "content": "Quy định về hợp đồng lao động theo Bộ luật Lao động 2019...",
                    "metadata": {"source": "labor_law_2019", "section": "chapter_3"}
                },
                {
                    "id": "doc_087", 
                    "score": 0.88,
                    "content": "Các điều khoản về chấm dứt hợp đồng lao động...",
                    "metadata": {"source": "labor_law_2019", "section": "chapter_7"}
                }
            ],
            "total_documents": 2,
            "processing_time": 200,
            "timestamp": datetime.now().isoformat()
        })
    
    async def rag_web_search(self, request):
        """RAG web search simulation"""
        data = await request.json()
        task_id = str(uuid.uuid4())
        
        # Simulate web search processing
        await asyncio.sleep(0.5)
        
        return web.json_response({
            "task_id": task_id,
            "query": data.get("query", ""),
            "results": [
                {
                    "url": "https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Bo-luat-lao-dong-2019",
                    "title": "Bộ luật lao động 2019 - Thư viện pháp luật",
                    "snippet": "Bộ luật Lao động số 45/2019/QH14 được Quốc hội khóa XIV thông qua...",
                    "relevance_score": 0.94
                },
                {
                    "url": "https://luatvietnam.vn/lao-dong/bo-luat-lao-dong-2019-chinh-thuc",
                    "title": "Bộ luật Lao động 2019 chính thức có hiệu lực",
                    "snippet": "Những thay đổi quan trọng trong Bộ luật Lao động 2019...",
                    "relevance_score": 0.89
                }
            ],
            "total_results": 2,
            "processing_time": 500,
            "timestamp": datetime.now().isoformat()
        })
    
    async def start(self):
        """Start mock server"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
        await self.site.start()
        logger.info(f"🚀 Mock API Server started on port {self.port}")
    
    async def stop(self):
        """Stop mock server"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("🛑 Mock API Server stopped")

class ComprehensiveTestWithMock:
    def __init__(self, base_url: str = "http://localhost:8001", output_dir: str = "tests/results"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.output_dir = Path(output_dir)
        self.test_id = f"comprehensive-mock-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.start_time = datetime.now()
        
        # Extract port from URL
        from urllib.parse import urlparse
        parsed_url = urlparse(base_url)
        port = parsed_url.port or 8001
        
        # Results storage
        self.test_results = []
        self.celery_metrics = []
        self.logging_analysis = []
        self.task_time_tracking = []
        
        # Mock server with extracted port
        self.mock_server = MockAPIServer(port=port)
        
        # Ensure output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🚀 Initializing Comprehensive Test Suite with Mock Server")
        logger.info(f"   Test ID: {self.test_id}")
        logger.info(f"   Base URL: {base_url}")
        logger.info(f"   Port: {port}")
        logger.info(f"   Output Dir: {output_dir}")

    async def test_api_endpoint_detailed(self, session: aiohttp.ClientSession, 
                                       name: str, method: str, url: str, 
                                       data: Optional[Dict] = None, 
                                       timeout: int = 30, 
                                       category: str = "General") -> Dict[str, Any]:
        """Test API endpoint với detailed metrics và time tracking"""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = {
            'test_id': self.test_id,
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'name': name,
            'category': category,
            'method': method,
            'url': url,
            'status': 'UNKNOWN',
            'status_code': None,
            'response_time_ms': None,
            'response_size_bytes': None,
            'has_celery_task': False,
            'celery_task_id': None,
            'celery_task_start_time': None,
            'celery_task_duration_ms': None,
            'error_message': None,
            'response_preview': None,
            'confidence_score': None,
            'sources_count': None
        }
        
        try:
            logger.info(f"🔍 Testing [{category}] {name}: {method} {url}")
            
            # Prepare request
            headers = {'X-Request-ID': request_id}
            if data:
                headers['Content-Type'] = 'application/json'
            
            # Make request với time tracking
            async with session.request(
                method=method,
                url=url,
                json=data if data and method != 'GET' else None,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response_text = await response.text()
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                # Parse response
                result['status'] = 'SUCCESS' if response.status == 200 else 'FAILED'
                result['status_code'] = response.status
                result['response_time_ms'] = round(response_time, 2)
                result['response_size_bytes'] = len(response_text)
                
                # Parse JSON response
                try:
                    response_json = json.loads(response_text)
                    result['response_preview'] = json.dumps(response_json, separators=(',', ':'))[:300]
                    
                    # Check for Celery task information
                    if 'task_id' in response_json:
                        result['has_celery_task'] = True
                        result['celery_task_id'] = response_json['task_id']
                        result['celery_task_start_time'] = response_json.get('task_start_time')
                        
                        # Track task time if available
                        if 'processing_time' in response_json:
                            result['celery_task_duration_ms'] = float(response_json['processing_time'])
                        
                        # Extract additional metrics
                        if 'confidence_score' in response_json:
                            result['confidence_score'] = response_json['confidence_score']
                        
                        if 'sources' in response_json:
                            result['sources_count'] = len(response_json['sources'])
                        
                        logger.info(f"    ✅ Celery Task Created: {response_json['task_id'][:8]}...")
                        
                        # Track task separately
                        self.task_time_tracking.append({
                            'test_id': self.test_id,
                            'request_id': request_id,
                            'task_id': response_json['task_id'],
                            'task_name': name,
                            'task_queue': self.guess_queue_from_endpoint(url),
                            'created_at': datetime.now().isoformat(),
                            'estimated_duration_ms': result['celery_task_duration_ms'],
                            'confidence_score': result['confidence_score'],
                            'sources_found': result['sources_count']
                        })
                    
                    if 'conversation_id' in response_json:
                        logger.info(f"    💬 Conversation ID: {response_json['conversation_id']}")
                        
                except json.JSONDecodeError:
                    result['response_preview'] = response_text[:300]
                
                if result['status'] == 'SUCCESS':
                    logger.info(f"    ✅ {name} completed in {response_time:.2f}ms")
                else:
                    logger.warning(f"    ⚠️ {name} returned status {response.status}")
                    
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            result['response_time_ms'] = round(response_time, 2)
            result['status'] = 'FAILED'
            result['error_message'] = str(e)
            logger.error(f"    ❌ {name} failed: {str(e)}")
        
        return result

    def guess_queue_from_endpoint(self, url: str) -> str:
        """Đoán queue name từ endpoint URL"""
        if 'chat' in url.lower():
            return 'rag_queue'
        elif 'embed' in url.lower():
            return 'embed_queue'
        elif 'search' in url.lower():
            return 'link_extract_queue'
        elif 'retriev' in url.lower():
            return 'retrival_queue'
        return 'unknown_queue'

    async def run_comprehensive_test(self, concurrent_users: int = 3):
        """Run complete comprehensive test suite"""
        logger.info("🚀 Starting Comprehensive Test Suite with Mock Server")
        
        # Start mock server
        await self.mock_server.start()
        
        try:
            # Wait for server to be ready
            await asyncio.sleep(1)
            
            async with aiohttp.ClientSession() as session:
                # Test health endpoints
                logger.info("🏥 Testing Health & System Endpoints")
                health_tests = [
                    ("Health_Check", "GET", f"{self.base_url}/health", None, "Health"),
                    ("Readiness_Check", "GET", f"{self.base_url}/ready", None, "Health"),
                    ("Metrics_Endpoint", "GET", f"{self.base_url}/metrics", None, "Health"),
                ]
                
                for name, method, url, data, category in health_tests:
                    result = await self.test_api_endpoint_detailed(
                        session, name, method, url, data, 15, category
                    )
                    self.test_results.append(result)
                
                # Test Celery worker status
                logger.info("🔧 Testing Celery Worker Status")
                celery_tests = [
                    ("Celery_Worker_Status", "GET", f"{self.api_base}/status/worker", None, "Celery"),
                    ("Queue_Status_rag_queue", "GET", f"{self.api_base}/status/queue/rag_queue", None, "Celery"),
                    ("Queue_Status_embed_queue", "GET", f"{self.api_base}/status/queue/embed_queue", None, "Celery"),
                    ("Queue_Status_retrival_queue", "GET", f"{self.api_base}/status/queue/retrival_queue", None, "Celery"),
                    ("Queue_Status_link_extract_queue", "GET", f"{self.api_base}/status/queue/link_extract_queue", None, "Celery"),
                ]
                
                for name, method, url, data, category in celery_tests:
                    result = await self.test_api_endpoint_detailed(
                        session, name, method, url, data, 10, category
                    )
                    self.test_results.append(result)
                
                # Test Legal Chat APIs
                logger.info("💬 Testing Legal Chat APIs")
                conversation_id = f"test-{int(time.time())}"
                chat_tests = [
                    ("Legal_Chat_Simple", "POST", f"{self.api_base}/legal-chat/send-query", {
                        "user_id": "test-user",
                        "message": "Luật doanh nghiệp có những quy định gì về thành lập công ty?",
                        "conversation_id": conversation_id
                    }, "LegalChat"),
                    ("Legal_Chat_Complex", "POST", f"{self.api_base}/legal-chat/send-query", {
                        "user_id": "test-user",
                        "message": "Thủ tục thành lập công ty TNHH theo luật doanh nghiệp 2020 cần những giấy tờ gì? Phân tích chi tiết từng bước và các điều kiện pháp lý cần thiết.",
                        "conversation_id": conversation_id,
                        "max_tokens": 500
                    }, "LegalChat"),
                ]
                
                for name, method, url, data, category in chat_tests:
                    result = await self.test_api_endpoint_detailed(
                        session, name, method, url, data, 60, category
                    )
                    self.test_results.append(result)
                
                # Test RAG System
                logger.info("🧠 Testing RAG System")
                rag_tests = [
                    ("RAG_Document_Retrieval", "POST", f"{self.api_base}/rag/retrieve", {
                        "query": "quy định về hợp đồng lao động trong luật lao động",
                        "top_k": 5
                    }, "RAG"),
                    ("RAG_Web_Search", "POST", f"{self.api_base}/rag/web_search", {
                        "query": "luật doanh nghiệp việt nam 2020 mới nhất thủ tục thành lập",
                        "max_links": 3,
                        "max_workers": 2
                    }, "RAG")
                ]
                
                for name, method, url, data, category in rag_tests:
                    timeout = 90 if "web_search" in url else 45
                    result = await self.test_api_endpoint_detailed(
                        session, name, method, url, data, timeout, category
                    )
                    self.test_results.append(result)
                
                # Concurrent Load Testing
                logger.info(f"⚡ Testing Concurrent Load with {concurrent_users} users")
                
                async def single_user_test(user_id: int):
                    async with aiohttp.ClientSession() as user_session:
                        test_data = {
                            "user_id": f"perf-user-{user_id}",
                            "message": f"Test hiệu suất số {user_id}: Quy định về thành lập doanh nghiệp theo luật với phân tích chi tiết",
                            "conversation_id": f"perf-test-{user_id}"
                        }
                        
                        return await self.test_api_endpoint_detailed(
                            user_session, f"Concurrent_User_{user_id}", "POST",
                            f"{self.api_base}/legal-chat/send-query", test_data, 60, "Performance"
                        )
                
                concurrent_start = time.time()
                tasks = [single_user_test(i) for i in range(1, concurrent_users + 1)]
                concurrent_results = await asyncio.gather(*tasks, return_exceptions=True)
                concurrent_end = time.time()
                
                # Process concurrent results
                successful_concurrent = [r for r in concurrent_results if isinstance(r, dict) and r.get('status') == 'SUCCESS']
                
                for result in concurrent_results:
                    if isinstance(result, dict):
                        self.test_results.append(result)
                
                # Log concurrent performance
                concurrent_duration = (concurrent_end - concurrent_start) * 1000
                logger.info(f"📊 Concurrent Load Results:")
                logger.info(f"    Success Rate: {len(successful_concurrent)}/{concurrent_users} ({len(successful_concurrent)/concurrent_users*100:.1f}%)")
                logger.info(f"    Total Duration: {concurrent_duration:.2f}ms")
                if successful_concurrent:
                    avg_response = sum(r['response_time_ms'] for r in successful_concurrent) / len(successful_concurrent)
                    logger.info(f"    Avg Response Time: {avg_response:.2f}ms")
                    celery_tasks = len([r for r in successful_concurrent if r.get('has_celery_task')])
                    logger.info(f"    Celery Tasks Created: {celery_tasks}")
        
        finally:
            # Stop mock server
            await self.mock_server.stop()
        
        # Export results
        timestamp, summary = self.export_results_to_csv()
        if summary:
            self.show_final_report(summary)
        
        logger.info(f"🎯 All results saved with timestamp: {timestamp}")

    def export_results_to_csv(self):
        """Export all results to CSV files"""
        logger.info("📊 Exporting Results to CSV")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Main test results
            if self.test_results:
                results_file = self.output_dir / f"comprehensive_api_test_MOCK_{timestamp}.csv"
                df_results = pd.DataFrame(self.test_results)
                df_results.to_csv(results_file, index=False, encoding='utf-8')
                logger.info(f"✅ Test Results: {results_file}")
            
            # Task time tracking
            if self.task_time_tracking:
                task_file = self.output_dir / f"task_time_tracking_MOCK_{timestamp}.csv"
                df_tasks = pd.DataFrame(self.task_time_tracking)
                df_tasks.to_csv(task_file, index=False, encoding='utf-8')
                logger.info(f"✅ Task Time Tracking: {task_file}")
            
            # Summary report
            summary = {
                'test_id': self.test_id,
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_minutes': round((datetime.now() - self.start_time).total_seconds() / 60, 2),
                'total_tests': len(self.test_results),
                'successful_tests': len([r for r in self.test_results if r['status'] == 'SUCCESS']),
                'failed_tests': len([r for r in self.test_results if r['status'] == 'FAILED']),
                'success_rate': round((len([r for r in self.test_results if r['status'] == 'SUCCESS']) / len(self.test_results)) * 100, 2) if self.test_results else 0,
                'celery_tasks_created': len([r for r in self.test_results if r['has_celery_task']]),
                'average_response_time_ms': round(
                    sum(r['response_time_ms'] for r in self.test_results if r['response_time_ms']) / 
                    len([r for r in self.test_results if r['response_time_ms']]), 2
                ) if [r for r in self.test_results if r['response_time_ms']] else 0,
                'average_task_duration_ms': round(
                    sum(t['estimated_duration_ms'] for t in self.task_time_tracking if t['estimated_duration_ms']) /
                    len([t for t in self.task_time_tracking if t['estimated_duration_ms']]), 2
                ) if [t for t in self.task_time_tracking if t['estimated_duration_ms']] else 0,
                'server_type': 'MOCK_API_SERVER'
            }
            
            summary_file = self.output_dir / f"test_summary_MOCK_{timestamp}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Summary Report: {summary_file}")
            
            return timestamp, summary
            
        except Exception as e:
            logger.error(f"❌ Export Error: {e}")
            return None, None

    def show_final_report(self, summary: Dict):
        """Display comprehensive final report"""
        print("\n" + "="*80)
        print("🏆 COMPREHENSIVE API + CELERY + LOGGING TEST FINAL REPORT (MOCK)")
        print("="*80)
        
        print(f"\n📊 TEST STATISTICS")
        print(f"  🎯 Test ID: {summary['test_id']}")
        print(f"  ⏱️ Duration: {summary['duration_minutes']} minutes")
        print(f"  📈 Total Tests: {summary['total_tests']}")
        print(f"  ✅ Successful: {summary['successful_tests']}")
        print(f"  ❌ Failed: {summary['failed_tests']}")
        print(f"  📊 Success Rate: {summary['success_rate']}%")
        print(f"  ⚡ Avg Response Time: {summary['average_response_time_ms']}ms")
        print(f"  🎭 Celery Tasks Created: {summary['celery_tasks_created']}")
        print(f"  ⏱️ Avg Task Duration: {summary['average_task_duration_ms']}ms")
        
        print(f"\n🎯 FINAL ASSESSMENT")
        if summary['success_rate'] >= 90 and summary['celery_tasks_created'] > 0:
            print(f"  🏆 EXCELLENT - All systems operational!")
        elif summary['success_rate'] >= 75:
            print(f"  ✅ GOOD - Minor issues detected")
        else:
            print(f"  ⚠️ NEEDS ATTENTION - Multiple failures detected")
        
        print(f"\n🎉 COMPREHENSIVE TESTING WITH MOCK SERVER COMPLETED!")
        print("="*80)

async def main():
    parser = argparse.ArgumentParser(description='Comprehensive API + Celery + Logging Test Suite with Mock Server')
    parser.add_argument('--url', default='http://localhost:8001', help='Base URL for API')
    parser.add_argument('--output', default='tests/results', help='Output directory')
    parser.add_argument('--concurrent', type=int, default=3, help='Concurrent users for load test')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    test_suite = ComprehensiveTestWithMock(args.url, args.output)
    await test_suite.run_comprehensive_test(args.concurrent)

if __name__ == "__main__":
    asyncio.run(main())
