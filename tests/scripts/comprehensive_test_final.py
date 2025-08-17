#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE API + CELERY + LOGGING TEST SUITE
================================================
Test toàn diện API endpoints, Celery workers, logging system với time tracking
Môi trường: conda crypto_agent
"""

import asyncio
import aiohttp
import json
import time
import csv
import os
import subprocess
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
import logging
import sys
from pathlib import Path
import uuid
import pandas as pd

# Thiết lập logging cho test script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('comprehensive_test.log')
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveTestSuite:
    def __init__(self, base_url: str = "http://localhost:8001", output_dir: str = "tests/results"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.output_dir = Path(output_dir)
        self.test_id = f"comprehensive-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.start_time = datetime.now()
        
        # Results storage
        self.test_results = []
        self.celery_metrics = []
        self.logging_analysis = []
        self.task_time_tracking = []
        
        # Ensure output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🚀 Initializing Comprehensive Test Suite")
        logger.info(f"   Test ID: {self.test_id}")
        logger.info(f"   Base URL: {base_url}")
        logger.info(f"   Output Dir: {output_dir}")

    def check_conda_environment(self):
        """Kiểm tra môi trường conda crypto_agent"""
        try:
            result = subprocess.run(['conda', 'info', '--envs'], capture_output=True, text=True)
            if 'crypto_agent' in result.stdout:
                logger.info("✅ Conda environment crypto_agent detected")
                return True
            else:
                logger.error("❌ Conda environment crypto_agent not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error checking conda environment: {e}")
            return False

    def check_celery_processes(self):
        """Kiểm tra Celery worker processes"""
        try:
            celery_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'celery' in cmdline.lower() and 'worker' in cmdline.lower():
                        celery_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.info(f"📊 Found {len(celery_processes)} Celery worker processes")
            return celery_processes
        except Exception as e:
            logger.error(f"❌ Error checking Celery processes: {e}")
            return []

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
            'request_headers': {},
            'response_headers': {}
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
                result['response_headers'] = dict(response.headers)
                
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
                        
                        logger.info(f"    ✅ Celery Task Created: {response_json['task_id']}")
                        
                        # Track task separately
                        self.task_time_tracking.append({
                            'test_id': self.test_id,
                            'request_id': request_id,
                            'task_id': response_json['task_id'],
                            'task_name': name,
                            'task_queue': self.guess_queue_from_endpoint(url),
                            'created_at': datetime.now().isoformat(),
                            'estimated_duration_ms': result['celery_task_duration_ms']
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
            return 'embedding_queue'
        elif 'search' in url.lower():
            return 'link_extract_queue'
        elif 'retriev' in url.lower():
            return 'retrival_queue'
        return 'unknown_queue'

    async def test_health_endpoints(self, session: aiohttp.ClientSession):
        """Test health và system endpoints"""
        logger.info("🏥 Testing Health & System Endpoints")
        
        endpoints = [
            ("Health_Check", "GET", f"{self.base_url}/health", None, "Health"),
            ("Readiness_Check", "GET", f"{self.base_url}/ready", None, "Health"),
            ("Metrics_Endpoint", "GET", f"{self.base_url}/metrics", None, "Health"),
        ]
        
        for name, method, url, data, category in endpoints:
            result = await self.test_api_endpoint_detailed(
                session, name, method, url, data, 15, category
            )
            self.test_results.append(result)

    async def test_celery_worker_status(self, session: aiohttp.ClientSession):
        """Test Celery worker status endpoints"""
        logger.info("🔧 Testing Celery Worker Status")
        
        # Test worker status
        result = await self.test_api_endpoint_detailed(
            session, "Celery_Worker_Status", "GET", 
            f"{self.api_base}/status/worker", None, 15, "Celery"
        )
        self.test_results.append(result)
        
        # Test individual queues
        queues = ["rag_queue", "embedding_queue", "retrival_queue", "link_extract_queue"]
        for queue in queues:
            result = await self.test_api_endpoint_detailed(
                session, f"Queue_Status_{queue}", "GET",
                f"{self.api_base}/status/queue/{queue}", None, 10, "Celery"
            )
            self.test_results.append(result)
        
        # Record Celery metrics
        celery_processes = self.check_celery_processes()
        celery_metric = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'worker_processes': len(celery_processes),
            'active_queues': len(queues),
            'status': 'RUNNING' if len(celery_processes) > 0 else 'NOT_RUNNING',
            'process_details': celery_processes
        }
        self.celery_metrics.append(celery_metric)

    async def test_legal_chat_apis(self, session: aiohttp.ClientSession):
        """Test legal chat API với time tracking"""
        logger.info("💬 Testing Legal Chat APIs")
        
        conversation_id = f"test-{int(time.time())}"
        
        tests = [
            ("Legal_Chat_Simple", "POST", f"{self.api_base}/legal-chat/send-query", {
                "user_id": "test-user",
                "message": "Luật doanh nghiệp có những quy định gì về thành lập công ty?",
                "conversation_id": conversation_id
            }, "LegalChat"),
            ("Legal_Chat_Complex", "POST", f"{self.api_base}/legal-chat/send-query", {
                "user_id": "test-user",
                "message": "Thủ tục thành lập công ty TNHH theo luật doanh nghiệp 2020 cần những giấy tờ gì? Phân tích chi tiết từng bước.",
                "conversation_id": conversation_id,
                "max_tokens": 500
            }, "LegalChat"),
        ]
        
        for name, method, url, data, category in tests:
            result = await self.test_api_endpoint_detailed(
                session, name, method, url, data, 60, category
            )
            self.test_results.append(result)

    async def test_rag_system(self, session: aiohttp.ClientSession):
        """Test RAG system endpoints"""
        logger.info("🧠 Testing RAG System")
        
        tests = [
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
        
        for name, method, url, data, category in tests:
            timeout = 90 if "web_search" in url else 45
            result = await self.test_api_endpoint_detailed(
                session, name, method, url, data, timeout, category
            )
            self.test_results.append(result)

    async def test_concurrent_load(self, concurrent_users: int = 3):
        """Test concurrent load với time tracking"""
        logger.info(f"⚡ Testing Concurrent Load with {concurrent_users} users")
        
        async def single_user_test(session: aiohttp.ClientSession, user_id: int):
            test_data = {
                "user_id": f"perf-user-{user_id}",
                "message": f"Test hiệu suất số {user_id}: Quy định về thành lập doanh nghiệp theo luật",
                "conversation_id": f"perf-test-{user_id}"
            }
            
            return await self.test_api_endpoint_detailed(
                session, f"Concurrent_User_{user_id}", "POST",
                f"{self.api_base}/legal-chat/send-query", test_data, 60, "Performance"
            )
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = [single_user_test(session, i) for i in range(1, concurrent_users + 1)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_duration = (end_time - start_time) * 1000
        
        # Process results
        successful_results = [r for r in results if isinstance(r, dict) and r.get('status') == 'SUCCESS']
        
        for result in results:
            if isinstance(result, dict):
                self.test_results.append(result)
        
        # Performance metrics
        performance_metric = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'concurrent_users': concurrent_users,
            'successful_requests': len(successful_results),
            'failed_requests': concurrent_users - len(successful_results),
            'success_rate': round((len(successful_results) / concurrent_users) * 100, 2),
            'total_duration_ms': round(total_duration, 2),
            'requests_per_second': round(concurrent_users / (total_duration / 1000), 2),
            'average_response_time_ms': round(
                sum(r['response_time_ms'] for r in successful_results) / len(successful_results), 2
            ) if successful_results else 0,
            'celery_tasks_created': len([r for r in successful_results if r.get('has_celery_task')])
        }
        
        logger.info(f"📊 Concurrent Load Results:")
        logger.info(f"    Success Rate: {performance_metric['success_rate']}%")
        logger.info(f"    Avg Response Time: {performance_metric['average_response_time_ms']}ms")
        logger.info(f"    Requests/sec: {performance_metric['requests_per_second']}")
        logger.info(f"    Celery Tasks Created: {performance_metric['celery_tasks_created']}")

    def analyze_log_files(self):
        """Analyze log files for structured logging"""
        logger.info("📝 Analyzing Log Files")
        
        log_patterns = ["*.log", "celery_*.log", "app_*.log"]
        log_files = []
        
        for pattern in log_patterns:
            log_files.extend(list(Path(".").glob(pattern)))
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-100:]  # Last 100 lines
                
                json_lines = 0
                total_lines = len(lines)
                
                for line in lines:
                    try:
                        json.loads(line.strip())
                        json_lines += 1
                    except json.JSONDecodeError:
                        pass
                
                structured_percent = round((json_lines / total_lines) * 100, 2) if total_lines > 0 else 0
                
                logging_result = {
                    'test_id': self.test_id,
                    'timestamp': datetime.now().isoformat(),
                    'log_file': log_file.name,
                    'total_lines_analyzed': total_lines,
                    'json_format_lines': json_lines,
                    'structured_percent': structured_percent,
                    'status': 'STRUCTURED' if json_lines > 0 else 'UNSTRUCTURED'
                }
                
                self.logging_analysis.append(logging_result)
                logger.info(f"    📄 {log_file.name}: {structured_percent}% structured")
                
            except Exception as e:
                logger.warning(f"Could not analyze log file {log_file}: {e}")

    def export_results_to_csv(self):
        """Export all results to CSV files"""
        logger.info("📊 Exporting Results to CSV")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Main test results
            if self.test_results:
                results_file = self.output_dir / f"comprehensive_api_test_{timestamp}.csv"
                df_results = pd.DataFrame(self.test_results)
                df_results.to_csv(results_file, index=False, encoding='utf-8')
                logger.info(f"✅ Test Results: {results_file}")
            
            # Celery metrics
            if self.celery_metrics:
                celery_file = self.output_dir / f"celery_metrics_{timestamp}.csv"
                df_celery = pd.DataFrame(self.celery_metrics)
                df_celery.to_csv(celery_file, index=False, encoding='utf-8')
                logger.info(f"✅ Celery Metrics: {celery_file}")
            
            # Task time tracking
            if self.task_time_tracking:
                task_file = self.output_dir / f"task_time_tracking_{timestamp}.csv"
                df_tasks = pd.DataFrame(self.task_time_tracking)
                df_tasks.to_csv(task_file, index=False, encoding='utf-8')
                logger.info(f"✅ Task Time Tracking: {task_file}")
            
            # Logging analysis
            if self.logging_analysis:
                logging_file = self.output_dir / f"logging_analysis_{timestamp}.csv"
                df_logging = pd.DataFrame(self.logging_analysis)
                df_logging.to_csv(logging_file, index=False, encoding='utf-8')
                logger.info(f"✅ Logging Analysis: {logging_file}")
            
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
                'celery_workers_detected': len(self.celery_metrics[0]['process_details']) if self.celery_metrics else 0,
                'log_files_analyzed': len(self.logging_analysis),
                'average_response_time_ms': round(
                    sum(r['response_time_ms'] for r in self.test_results if r['response_time_ms']) / 
                    len([r for r in self.test_results if r['response_time_ms']]), 2
                ) if [r for r in self.test_results if r['response_time_ms']] else 0
            }
            
            summary_file = self.output_dir / f"test_summary_{timestamp}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Summary Report: {summary_file}")
            
            return timestamp, summary
            
        except Exception as e:
            logger.error(f"❌ Export Error: {e}")
            return None, None

    def show_final_report(self, summary: Dict):
        """Display comprehensive final report"""
        logger.info("🏆 COMPREHENSIVE TEST COMPLETED")
        
        print("\n" + "="*80)
        print("🏆 COMPREHENSIVE API + CELERY + LOGGING TEST FINAL REPORT")
        print("="*80)
        
        print(f"\n📊 TEST STATISTICS")
        print(f"  🎯 Test ID: {summary['test_id']}")
        print(f"  ⏱️ Duration: {summary['duration_minutes']} minutes")
        print(f"  📈 Total Tests: {summary['total_tests']}")
        print(f"  ✅ Successful: {summary['successful_tests']}")
        print(f"  ❌ Failed: {summary['failed_tests']}")
        print(f"  📊 Success Rate: {summary['success_rate']}%")
        print(f"  ⚡ Avg Response Time: {summary['average_response_time_ms']}ms")
        
        print(f"\n🔧 CELERY ANALYSIS")
        print(f"  🎭 Tasks Created: {summary['celery_tasks_created']}")
        print(f"  👷 Workers Detected: {summary['celery_workers_detected']}")
        
        print(f"\n📝 LOGGING ANALYSIS")
        print(f"  📄 Log Files Analyzed: {summary['log_files_analyzed']}")
        
        print(f"\n🎯 FINAL ASSESSMENT")
        if summary['success_rate'] >= 90 and summary['celery_tasks_created'] > 0:
            print(f"  🏆 EXCELLENT - System ready for production!")
        elif summary['success_rate'] >= 75:
            print(f"  ✅ GOOD - Minor issues to address")
        else:
            print(f"  ⚠️ NEEDS ATTENTION - Multiple failures detected")
        
        print(f"\n🎉 COMPREHENSIVE TESTING COMPLETED!")
        print("="*80)

    async def run_comprehensive_test(self, concurrent_users: int = 3):
        """Run complete comprehensive test suite"""
        logger.info("🚀 Starting Comprehensive Test Suite")
        
        # Environment checks
        if not self.check_conda_environment():
            logger.error("❌ Conda environment check failed")
            return
        
        async with aiohttp.ClientSession() as session:
            # Test phases
            await self.test_health_endpoints(session)
            await self.test_celery_worker_status(session)
            await self.test_legal_chat_apis(session)
            await self.test_rag_system(session)
        
        # Concurrent testing
        await self.test_concurrent_load(concurrent_users)
        
        # Log analysis
        self.analyze_log_files()
        
        # Export and report
        timestamp, summary = self.export_results_to_csv()
        if summary:
            self.show_final_report(summary)
        
        logger.info(f"🎯 All results saved with timestamp: {timestamp}")

async def main():
    parser = argparse.ArgumentParser(description='Comprehensive API + Celery + Logging Test Suite')
    parser.add_argument('--url', default='http://localhost:8001', help='Base URL for API')
    parser.add_argument('--output', default='tests/results', help='Output directory')
    parser.add_argument('--concurrent', type=int, default=3, help='Concurrent users for load test')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Kiểm tra môi trường conda
    logger.info("🔍 Checking conda environment crypto_agent...")
    
    test_suite = ComprehensiveTestSuite(args.url, args.output)
    await test_suite.run_comprehensive_test(args.concurrent)

if __name__ == "__main__":
    asyncio.run(main())
