#!/usr/bin/env python3
"""
🚀 ADVANCED COMPREHENSIVE API + CELERY + LOGGING TEST
====================================================
Advanced testing với async, detailed metrics, và logging analysis
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
import concurrent.futures
import threading
import logging
import sys
from pathlib import Path

class AdvancedTestSuite:
    def __init__(self, base_url: str = "http://localhost:8001", output_dir: str = "tests/results"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.output_dir = Path(output_dir)
        self.test_id = f"advanced-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.start_time = datetime.now()
        
        # Results storage
        self.test_results = []
        self.celery_metrics = []
        self.logging_analysis = []
        self.performance_metrics = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / f"test_execution_{self.test_id}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def test_api_endpoint_async(self, session: aiohttp.ClientSession, name: str, 
                                    method: str, url: str, data: Optional[Dict] = None, 
                                    timeout: int = 30, category: str = "General") -> Dict[str, Any]:
        """Test API endpoint asynchronously with detailed metrics"""
        start_time = time.time()
        result = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'name': name,
            'category': category,
            'method': method,
            'url': url,
            'status': 'UNKNOWN',
            'status_code': None,
            'response_time': None,
            'response_size': None,
            'has_celery_task': False,
            'celery_task_id': None,
            'log_entries': 0,
            'error_message': None,
            'response_preview': None
        }
        
        try:
            self.logger.info(f"🔍 Testing: {name}")
            
            # Make async request
            async with session.request(
                method=method,
                url=url,
                json=data if data and method != 'GET' else None,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response_text = await response.text()
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                result['status'] = 'SUCCESS' if response.status == 200 else 'FAILED'
                result['status_code'] = response.status
                result['response_time'] = round(response_time, 2)
                result['response_size'] = len(response_text)
                
                # Parse JSON response if possible
                try:
                    response_json = json.loads(response_text)
                    result['response_preview'] = json.dumps(response_json, separators=(',', ':'))[:200]
                    
                    # Check for Celery task info
                    if 'task_id' in response_json:
                        result['has_celery_task'] = True
                        result['celery_task_id'] = response_json['task_id']
                        self.logger.info(f"    ✅ Celery Task ID: {response_json['task_id']}")
                    
                    if 'conversation_id' in response_json:
                        self.logger.info(f"    💬 Conversation ID: {response_json['conversation_id']}")
                        
                except json.JSONDecodeError:
                    result['response_preview'] = response_text[:200]
                
                if result['status'] == 'SUCCESS':
                    self.logger.info(f"    ✅ {name} - {response_time:.2f}ms")
                else:
                    self.logger.error(f"    ❌ {name} - HTTP {response.status}")
                    
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            result['response_time'] = round(response_time, 2)
            result['status'] = 'FAILED'
            result['error_message'] = str(e)
            self.logger.error(f"    ❌ {name} - Error: {str(e)}")
        
        return result

    async def test_health_and_system(self, session: aiohttp.ClientSession):
        """Test health and system endpoints"""
        self.logger.info("🏥 Testing Health & System Endpoints")
        
        tests = [
            ("Health_Check", "GET", f"{self.base_url}/health", None, "Health"),
            ("Readiness_Check", "GET", f"{self.base_url}/ready", None, "Health"),
            ("Metrics_Endpoint", "GET", f"{self.base_url}/metrics", None, "Health"),
        ]
        
        for name, method, url, data, category in tests:
            result = await self.test_api_endpoint_async(session, name, method, url, data, 10, category)
            self.test_results.append(result)

    async def test_celery_workers(self, session: aiohttp.ClientSession):
        """Test Celery worker status and queues"""
        self.logger.info("🔧 Testing Celery Workers")
        
        # Test main worker status
        result = await self.test_api_endpoint_async(
            session, "Celery_Worker_Status", "GET", 
            f"{self.api_base}/status/worker", None, 15, "Celery"
        )
        self.test_results.append(result)
        
        # Test individual queues
        queues = ["rag_queue", "embedding_queue", "retrival_queue", "link_extract_queue"]
        for queue in queues:
            result = await self.test_api_endpoint_async(
                session, f"Queue_Status_{queue}", "GET",
                f"{self.api_base}/status/queue/{queue}", None, 10, "Celery"
            )
            self.test_results.append(result)
        
        # Check system processes
        try:
            celery_processes = [p for p in psutil.process_iter(['pid', 'name', 'cmdline']) 
                              if 'celery' in str(p.info.get('cmdline', [])).lower()]
        except:
            celery_processes = []
        
        celery_metric = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'worker_processes': len(celery_processes),
            'active_queues': len(queues),
            'status': 'RUNNING' if len(celery_processes) > 0 else 'NOT_RUNNING'
        }
        self.celery_metrics.append(celery_metric)
        
        self.logger.info(f"📊 Celery Processes: {len(celery_processes)}")

    async def test_legal_chat_apis(self, session: aiohttp.ClientSession):
        """Test legal chat API endpoints"""
        self.logger.info("💬 Testing Legal Chat APIs")
        
        conversation_id = f"test-{int(time.time())}"
        
        tests = [
            ("Legal_Chat_Simple", "POST", f"{self.api_base}/legal-chat/send-query", {
                "user_id": "test-user",
                "message": "Luật doanh nghiệp có những quy định gì?",
                "conversation_id": conversation_id
            }, "LegalChat"),
            ("Legal_Chat_Complex", "POST", f"{self.api_base}/legal-chat/send-query", {
                "user_id": "test-user", 
                "message": "Thủ tục thành lập công ty TNHH theo luật doanh nghiệp 2020 cần những giấy tờ gì?",
                "conversation_id": conversation_id,
                "max_tokens": 500
            }, "LegalChat"),
        ]
        
        for name, method, url, data, category in tests:
            timeout = 45 if method == "POST" else 15
            result = await self.test_api_endpoint_async(session, name, method, url, data, timeout, category)
            self.test_results.append(result)

    async def test_rag_system(self, session: aiohttp.ClientSession):
        """Test RAG system endpoints"""
        self.logger.info("🧠 Testing RAG System")
        
        tests = [
            ("RAG_Document_Retrieval", "POST", f"{self.api_base}/rag/retrieve", {
                "query": "quy định về hợp đồng lao động",
                "top_k": 5
            }, "RAG"),
            ("RAG_Web_Search", "POST", f"{self.api_base}/rag/web_search", {
                "query": "luật doanh nghiệp việt nam 2020 mới nhất",
                "max_links": 3,
                "max_workers": 2
            }, "RAG")
        ]
        
        for name, method, url, data, category in tests:
            timeout = 60 if "web_search" in url else 30
            result = await self.test_api_endpoint_async(session, name, method, url, data, timeout, category)
            self.test_results.append(result)

    async def test_concurrent_load(self, concurrent_users: int = 5):
        """Test concurrent load with multiple users"""
        self.logger.info(f"⚡ Testing Concurrent Load with {concurrent_users} users")
        
        async def single_user_test(session: aiohttp.ClientSession, user_id: int):
            """Single user concurrent test"""
            test_data = {
                "user_id": f"perf-user-{user_id}",
                "message": f"Test hiệu suất số {user_id}: Quy định về thành lập doanh nghiệp",
                "conversation_id": f"perf-test-{user_id}"
            }
            
            return await self.test_api_endpoint_async(
                session, f"Concurrent_User_{user_id}", "POST",
                f"{self.api_base}/legal-chat/send-query", test_data, 45, "Performance"
            )
        
        # Create concurrent requests
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = [single_user_test(session, i) for i in range(1, concurrent_users + 1)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_duration = (end_time - start_time) * 1000
        
        # Process results
        successful_results = [r for r in results if isinstance(r, dict) and r.get('status') == 'SUCCESS']
        failed_results = [r for r in results if not isinstance(r, dict) or r.get('status') != 'SUCCESS']
        
        # Add results to main collection
        for result in results:
            if isinstance(result, dict):
                self.test_results.append(result)
        
        # Calculate performance metrics
        performance_metric = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'concurrent_users': concurrent_users,
            'successful_requests': len(successful_results),
            'failed_requests': len(failed_results),
            'success_rate': round((len(successful_results) / concurrent_users) * 100, 2),
            'total_duration': round(total_duration, 2),
            'requests_per_second': round(concurrent_users / (total_duration / 1000), 2),
            'average_response_time': round(
                sum(r['response_time'] for r in successful_results) / len(successful_results), 2
            ) if successful_results else 0,
            'celery_tasks_created': len([r for r in successful_results if r.get('has_celery_task')])
        }
        
        self.performance_metrics.append(performance_metric)
        
        self.logger.info(f"📊 Performance Results:")
        self.logger.info(f"    ✅ Success Rate: {performance_metric['success_rate']}%")
        self.logger.info(f"    ⚡ Avg Response Time: {performance_metric['average_response_time']}ms")
        self.logger.info(f"    🚀 Requests/sec: {performance_metric['requests_per_second']}")

    def analyze_logging(self):
        """Analyze log files for structured logging"""
        self.logger.info("📝 Analyzing Logging Structure")
        
        log_files = list(Path(".").glob("*.log"))
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-50:]  # Last 50 lines
                
                json_lines = 0
                for line in lines:
                    try:
                        json.loads(line.strip())
                        json_lines += 1
                    except json.JSONDecodeError:
                        pass
                
                structured_percent = round((json_lines / len(lines)) * 100, 2) if lines else 0
                
                logging_result = {
                    'test_id': self.test_id,
                    'timestamp': datetime.now().isoformat(),
                    'log_file': log_file.name,
                    'total_lines': len(lines),
                    'json_format_lines': json_lines,
                    'structured_percent': structured_percent,
                    'status': 'STRUCTURED' if json_lines > 0 else 'UNSTRUCTURED'
                }
                
                self.logging_analysis.append(logging_result)
                
            except Exception as e:
                self.logger.warning(f"Could not analyze log file {log_file}: {str(e)}")

    def export_results(self):
        """Export all test results to CSV files"""
        self.logger.info("📊 Exporting Comprehensive Results")
        
        try:
            # Export main test results
            if self.test_results:
                results_file = self.output_dir / f"advanced_test_{self.test_id}.csv"
                with open(results_file, 'w', newline='', encoding='utf-8') as f:
                    if self.test_results:
                        writer = csv.DictWriter(f, fieldnames=self.test_results[0].keys())
                        writer.writeheader()
                        writer.writerows(self.test_results)
                self.logger.info(f"✅ Test Results: {results_file}")
            
            # Export Celery metrics
            if self.celery_metrics:
                celery_file = self.output_dir / f"advanced_celery_metrics_{self.test_id}.csv"
                with open(celery_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.celery_metrics[0].keys())
                    writer.writeheader()
                    writer.writerows(self.celery_metrics)
                self.logger.info(f"✅ Celery Metrics: {celery_file}")
            
            # Export logging analysis
            if self.logging_analysis:
                logging_file = self.output_dir / f"advanced_logging_analysis_{self.test_id}.csv"
                with open(logging_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.logging_analysis[0].keys())
                    writer.writeheader()
                    writer.writerows(self.logging_analysis)
                self.logger.info(f"✅ Logging Analysis: {logging_file}")
            
            # Export performance metrics
            if self.performance_metrics:
                performance_file = self.output_dir / f"advanced_performance_metrics_{self.test_id}.csv"
                with open(performance_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.performance_metrics[0].keys())
                    writer.writeheader()
                    writer.writerows(self.performance_metrics)
                self.logger.info(f"✅ Performance Metrics: {performance_file}")
            
            # Create comprehensive summary
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
                'log_files_analyzed': len(self.logging_analysis),
                'performance_tests': len(self.performance_metrics)
            }
            
            summary_file = self.output_dir / f"advanced_test_summary_{self.test_id}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Summary Report: {summary_file}")
            
        except Exception as e:
            self.logger.error(f"Export Error: {str(e)}")

    def show_final_report(self):
        """Display comprehensive final report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("🏆 ADVANCED COMPREHENSIVE TEST COMPLETE - FINAL REPORT")
        print("=" * 80)
        
        # Test Statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r['status'] == 'SUCCESS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAILED'])
        success_rate = round((successful_tests / total_tests) * 100, 2) if total_tests > 0 else 0
        
        print(f"📊 TEST STATISTICS")
        print(f"  🎯 Total Tests: {total_tests}")
        print(f"  ✅ Successful: {successful_tests}")
        print(f"  ❌ Failed: {failed_tests}")
        print(f"  📈 Success Rate: {success_rate}%")
        print(f"  ⏱️ Duration: {round(duration.total_seconds() / 60, 2)} minutes")
        
        # Celery Analysis
        celery_tasks = len([r for r in self.test_results if r['has_celery_task']])
        celery_workers = self.celery_metrics[0]['worker_processes'] if self.celery_metrics else 0
        
        print(f"\n🔧 CELERY ANALYSIS")
        print(f"  🎭 Tasks Created: {celery_tasks}")
        print(f"  👷 Worker Processes: {celery_workers}")
        print(f"  📋 Queues Tested: 4")
        
        # Performance Analysis
        if self.performance_metrics:
            perf = self.performance_metrics[0]
            print(f"\n⚡ PERFORMANCE ANALYSIS")
            print(f"  👥 Concurrent Users: {perf['concurrent_users']}")
            print(f"  📈 Success Rate: {perf['success_rate']}%")
            print(f"  ⏱️ Avg Response Time: {perf['average_response_time']}ms")
            print(f"  🚀 Requests/Second: {perf['requests_per_second']}")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT")
        if success_rate >= 90 and celery_tasks > 0:
            print(f"  🏆 EXCELLENT - System ready for production!")
        elif success_rate >= 75:
            print(f"  ✅ GOOD - Minor issues to address")
        else:
            print(f"  ⚠️ NEEDS ATTENTION - Multiple failures detected")
        
        print(f"\n🎉 ADVANCED TESTING COMPLETED!")
        print("=" * 80)

    async def run_comprehensive_test(self, concurrent_users: int = 5):
        """Run the complete comprehensive test suite"""
        self.logger.info("🚀 Starting Advanced Comprehensive Test Suite")
        
        async with aiohttp.ClientSession() as session:
            # Test phases
            await self.test_health_and_system(session)
            await self.test_celery_workers(session)
            await self.test_legal_chat_apis(session)
            await self.test_rag_system(session)
        
        # Concurrent load testing
        await self.test_concurrent_load(concurrent_users)
        
        # Logging analysis
        self.analyze_logging()
        
        # Export and report
        self.export_results()
        self.show_final_report()

async def main():
    parser = argparse.ArgumentParser(description='Advanced Comprehensive API Test Suite')
    parser.add_argument('--url', default='http://localhost:8001', help='Base URL for API')
    parser.add_argument('--output', default='tests/results', help='Output directory')
    parser.add_argument('--concurrent', type=int, default=5, help='Concurrent users for load test')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    test_suite = AdvancedTestSuite(args.url, args.output)
    await test_suite.run_comprehensive_test(args.concurrent)

if __name__ == "__main__":
    asyncio.run(main())
