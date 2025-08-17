#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND API TEST SUITE
====================================
Test toan dien backend API system voi logging analysis
Environment: Production-ready testing
"""

import asyncio
import aiohttp
import json
import time
import csv
import os
import subprocess
import psutil
import requests
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
import logging
import sys
from pathlib import Path
import uuid
import pandas as pd
import glob

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('tests/logs/backend_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class BackendTestSuite:
    def __init__(self, base_url: str = "http://localhost:8000", output_dir: str = "tests/results"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.legal_chat_base = f"{base_url}/api/legal-chat"
        self.rag_base = f"{base_url}/api/rag"
        self.output_dir = Path(output_dir)
        self.test_id = f"backend-test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.start_time = datetime.now()
        
        # Results storage
        self.api_test_results = []
        self.system_health_results = []
        self.celery_metrics = []
        self.log_analysis_results = []
        self.performance_metrics = []
        
        # Ensure output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[ROCKET] Backend Test Suite Initialized")
        logger.info(f"   Test ID: {self.test_id}")
        logger.info(f"   Base URL: {base_url}")
        logger.info(f"   Output: {output_dir}")

    def check_system_prerequisites(self) -> Dict[str, Any]:
        """Kiem tra dieu kien tien quyet cua he thong"""
        logger.info("[SEARCH] Checking System Prerequisites")
        
        prerequisites = {
            'timestamp': datetime.now().isoformat(),
            'server_accessible': False,
            'redis_connected': False,
            'celery_workers': 0,
            'python_version': sys.version.split()[0],
            'platform': sys.platform,
            'conda_env': os.environ.get('CONDA_DEFAULT_ENV', 'unknown')
        }
        
        # Check server accessibility
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                prerequisites['server_accessible'] = True
                prerequisites['server_health'] = response.json()
                logger.info("[CHECK] Server accessible and healthy")
            else:
                logger.warning(f"[WARNING] Server returned status {response.status_code}")
        except Exception as e:
            logger.error(f"[ERROR] Server not accessible: {e}")
        
        # Check Redis connection
        try:
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            redis_client.ping()
            prerequisites['redis_connected'] = True
            logger.info("[CHECK] Redis connection successful")
        except Exception as e:
            logger.error(f"[ERROR] Redis connection failed: {e}")
        
        # Check Celery workers
        celery_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'celery' in cmdline.lower() and 'worker' in cmdline.lower():
                    celery_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline[:100]
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        prerequisites['celery_workers'] = len(celery_processes)
        prerequisites['celery_processes'] = celery_processes
        logger.info(f"[CHART] Found {len(celery_processes)} Celery worker processes")
        
        return prerequisites

    async def test_api_endpoint(self, session: aiohttp.ClientSession, 
                               name: str, method: str, url: str, 
                               data: Optional[Dict] = None, 
                               timeout: int = 30, 
                               category: str = "API") -> Dict[str, Any]:
        """Test individual API endpoint voi detailed tracking"""
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
            'has_task': False,
            'task_id': None,
            'error_message': None,
            'response_data': None
        }
        
        try:
            logger.info(f"[SEARCH] Testing [{category}] {name}: {method} {url}")
            
            headers = {'X-Request-ID': request_id, 'Content-Type': 'application/json'}
            
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
                
                result['status'] = 'SUCCESS' if response.status == 200 else 'FAILED'
                result['status_code'] = response.status
                result['response_time_ms'] = round(response_time, 2)
                result['response_size_bytes'] = len(response_text)
                
                # Parse response
                try:
                    response_json = json.loads(response_text)
                    result['response_data'] = json.dumps(response_json, separators=(',', ':'))[:500]
                    
                    # Check for task creation
                    if 'task_id' in response_json or 'id_task' in response_json:
                        result['has_task'] = True
                        result['task_id'] = response_json.get('task_id') or response_json.get('id_task')
                        logger.info(f"    [MASK] Task created: {result['task_id']}")
                    
                    if 'conversation_id' in response_json:
                        logger.info(f"    [SPEECH] Conversation: {response_json['conversation_id']}")
                        
                except json.JSONDecodeError:
                    result['response_data'] = response_text[:500]
                
                if result['status'] == 'SUCCESS':
                    logger.info(f"    [CHECK] {name} completed in {response_time:.2f}ms")
                else:
                    logger.warning(f"    [WARNING] {name} returned status {response.status}")
                    
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            result['response_time_ms'] = round(response_time, 2)
            result['status'] = 'FAILED'
            result['error_message'] = str(e)
            logger.error(f"    [ERROR] {name} failed: {str(e)}")
        
        return result

    async def test_health_system_endpoints(self, session: aiohttp.ClientSession):
        """Test health va system endpoints"""
        logger.info("[HOSPITAL] Testing Health & System Endpoints")
        
        endpoints = [
            ("Health_Check", "GET", f"{self.base_url}/health", None, "Health"),
            ("Readiness_Check", "GET", f"{self.base_url}/ready", None, "Health"),
            ("API_Documentation", "GET", f"{self.base_url}/docs", None, "System"),
            ("OpenAPI_Schema", "GET", f"{self.base_url}/openapi.json", None, "System"),
        ]
        
        for name, method, url, data, category in endpoints:
            result = await self.test_api_endpoint(session, name, method, url, data, 15, category)
            self.api_test_results.append(result)

    async def test_legal_chat_endpoints(self, session: aiohttp.ClientSession):
        """Test legal chat API endpoints"""
        logger.info("[SPEECH] Testing Legal Chat API Endpoints")
        
        conversation_id = f"test-{int(time.time())}"
        
        endpoints = [
            ("Legal_Chat_Send_Query", "POST", f"{self.legal_chat_base}/send-query", {
                "user_id": "test-user",
                "message": "Luat doanh nghiep Viet Nam co nhung quy dinh gi ve thanh lap cong ty TNHH?",
                "conversation_id": conversation_id
            }, "LegalChat"),
            ("Legal_Chat_Generate_Response", "POST", f"{self.legal_chat_base}/generate-legal-response", {
                "conversation_id": conversation_id,
                "user_id": "test-user",
                "rewrite_query": "thanh lap cong ty TNHH luat doanh nghiep",
                "use_web_search": False,
                "use_retrieval": True
            }, "LegalChat"),
            ("Legal_Chat_History", "GET", f"{self.legal_chat_base}/conversation-history/{conversation_id}", None, "LegalChat"),
        ]
        
        for name, method, url, data, category in endpoints:
            timeout = 60 if method == "POST" else 15
            result = await self.test_api_endpoint(session, name, method, url, data, timeout, category)
            self.api_test_results.append(result)

    async def test_rag_system_endpoints(self, session: aiohttp.ClientSession):
        """Test RAG system endpoints"""
        logger.info("[BRAIN] Testing RAG System Endpoints")
        
        endpoints = [
            ("RAG_Document_Retrieval", "POST", f"{self.rag_base}/retrieve", {
                "query": "quy dinh ve hop dong lao dong trong luat lao dong Viet Nam"
            }, "RAG"),
            ("RAG_Web_Search", "POST", f"{self.rag_base}/web_search", {
                "query": "luat doanh nghiep viet nam 2020 moi nhat thu tuc thanh lap"
            }, "RAG")
        ]
        
        for name, method, url, data, category in endpoints:
            timeout = 90 if "web_search" in url else 45
            result = await self.test_api_endpoint(session, name, method, url, data, timeout, category)
            self.api_test_results.append(result)

    async def test_stream_endpoints(self, session: aiohttp.ClientSession):
        """Test streaming endpoints"""
        logger.info("[WAVE] Testing Streaming Endpoints")
        
        # First create a task
        conversation_id = f"stream-test-{int(time.time())}"
        
        # Generate a legal response first
        generate_result = await self.test_api_endpoint(
            session, "Stream_Preparation", "POST",
            f"{self.legal_chat_base}/generate-legal-response",
            {
                "conversation_id": conversation_id,
                "user_id": "stream-test-user",
                "rewrite_query": "luat hon nhan viet nam quy dinh ve ly hon",
                "use_web_search": False,
                "use_retrieval": True
            }, 60, "Stream"
        )
        
        self.api_test_results.append(generate_result)
        
        # Test streaming if task was created
        if generate_result.get('has_task') and generate_result.get('task_id'):
            await self.test_stream_response(session, conversation_id, generate_result['task_id'])

    async def test_stream_response(self, session: aiohttp.ClientSession, conversation_id: str, task_id: str):
        """Test actual streaming response"""
        logger.info(f"[WAVE] Testing stream for conversation {conversation_id}")
        
        stream_url = f"{self.legal_chat_base}/stream-legal-response/{conversation_id}"
        start_time = time.time()
        
        result = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'name': 'Stream_Legal_Response',
            'category': 'Stream',
            'method': 'GET',
            'url': stream_url,
            'status': 'UNKNOWN',
            'conversation_id': conversation_id,
            'task_id': task_id,
            'chunks_received': 0,
            'total_content_length': 0,
            'time_to_first_chunk': 0,
            'total_stream_time': 0,
            'error_message': None
        }
        
        try:
            async with session.get(stream_url) as response:
                if response.status == 200:
                    first_chunk_time = None
                    
                    async for chunk in response.content.iter_any():
                        if chunk:
                            if first_chunk_time is None:
                                first_chunk_time = time.time()
                                result['time_to_first_chunk'] = (first_chunk_time - start_time)
                            
                            result['chunks_received'] += 1
                            result['total_content_length'] += len(chunk)
                            
                            # Log every 50th chunk
                            if result['chunks_received'] % 50 == 0:
                                logger.info(f"    [WAVE] Received chunk {result['chunks_received']}")
                    
                    result['total_stream_time'] = time.time() - start_time
                    result['status'] = 'SUCCESS'
                    
                    logger.info(f"    [CHECK] Stream completed: {result['chunks_received']} chunks, "
                               f"{result['total_content_length']} bytes, {result['total_stream_time']:.2f}s")
                else:
                    result['status'] = 'FAILED'
                    result['error_message'] = f"HTTP {response.status}"
                    logger.error(f"    [ERROR] Stream failed with status {response.status}")
        
        except Exception as e:
            result['status'] = 'FAILED'
            result['error_message'] = str(e)
            result['total_stream_time'] = time.time() - start_time
            logger.error(f"    [ERROR] Stream exception: {e}")
        
        self.api_test_results.append(result)

    async def test_concurrent_load(self, concurrent_users: int = 3):
        """Test concurrent load performance"""
        logger.info(f"[FLASH] Testing Concurrent Load with {concurrent_users} users")
        
        async def single_user_test(session: aiohttp.ClientSession, user_id: int):
            test_data = {
                "user_id": f"load-test-user-{user_id}",
                "message": f"Test tai concurrent #{user_id}: Quy dinh ve thanh lap doanh nghiep",
                "conversation_id": f"load-test-{user_id}"
            }
            
            return await self.test_api_endpoint(
                session, f"Concurrent_Load_User_{user_id}", "POST",
                f"{self.legal_chat_base}/send-query", test_data, 60, "Performance"
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
                self.api_test_results.append(result)
        
        # Performance metrics
        performance_metric = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'concurrent_users': concurrent_users,
            'successful_requests': len(successful_results),
            'failed_requests': concurrent_users - len(successful_results),
            'success_rate': round((len(successful_results) / concurrent_users) * 100, 2),
            'total_duration_ms': round(total_duration, 2),
            'avg_response_time_ms': round(
                sum(r['response_time_ms'] for r in successful_results) / len(successful_results), 2
            ) if successful_results else 0,
            'tasks_created': len([r for r in successful_results if r.get('has_task')])
        }
        
        self.performance_metrics.append(performance_metric)
        
        logger.info(f"[CHART] Concurrent Load Results:")
        logger.info(f"    Success Rate: {performance_metric['success_rate']}%")
        logger.info(f"    Avg Response: {performance_metric['avg_response_time_ms']}ms")
        logger.info(f"    Tasks Created: {performance_metric['tasks_created']}")

    def analyze_system_logs(self):
        """Analyze system log files for quality and structure"""
        logger.info("[CLIPBOARD] Analyzing System Log Files")
        
        # Find log files
        log_patterns = [
            "*.log",
            "tests/logs/*.log",
            "src/logs/*.log",
            "logs/*.log"
        ]
        
        log_files = []
        for pattern in log_patterns:
            log_files.extend(glob.glob(pattern))
        
        logger.info(f"[FILE] Found {len(log_files)} log files to analyze")
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[-200:]  # Last 200 lines
                
                # Analysis metrics
                analysis = {
                    'test_id': self.test_id,
                    'timestamp': datetime.now().isoformat(),
                    'log_file': log_file,
                    'total_lines': len(lines),
                    'json_structured_lines': 0,
                    'error_lines': 0,
                    'warning_lines': 0,
                    'celery_task_lines': 0,
                    'api_request_lines': 0,
                    'performance_lines': 0
                }
                
                for line in lines:
                    line_lower = line.lower()
                    
                    # Check JSON structured format
                    try:
                        json.loads(line.strip())
                        analysis['json_structured_lines'] += 1
                    except json.JSONDecodeError:
                        pass
                    
                    # Count different log types
                    if any(keyword in line_lower for keyword in ['error', 'exception', 'traceback', 'failed']):
                        analysis['error_lines'] += 1
                    
                    if any(keyword in line_lower for keyword in ['warning', 'warn']):
                        analysis['warning_lines'] += 1
                    
                    if any(keyword in line_lower for keyword in ['celery', 'task', 'worker', 'queue']):
                        analysis['celery_task_lines'] += 1
                    
                    if any(keyword in line_lower for keyword in ['api', 'request', 'response', 'endpoint']):
                        analysis['api_request_lines'] += 1
                    
                    if any(keyword in line_lower for keyword in ['performance', 'duration', 'response_time', 'ms']):
                        analysis['performance_lines'] += 1
                
                # Calculate percentages
                total = analysis['total_lines']
                if total > 0:
                    analysis['structured_percentage'] = round((analysis['json_structured_lines'] / total) * 100, 2)
                    analysis['error_percentage'] = round((analysis['error_lines'] / total) * 100, 2)
                    analysis['celery_percentage'] = round((analysis['celery_task_lines'] / total) * 100, 2)
                else:
                    analysis['structured_percentage'] = 0
                    analysis['error_percentage'] = 0
                    analysis['celery_percentage'] = 0
                
                # Quality assessment
                if analysis['error_percentage'] <= 5 and analysis['structured_percentage'] >= 70:
                    analysis['quality_status'] = 'EXCELLENT'
                elif analysis['error_percentage'] <= 15 and analysis['structured_percentage'] >= 50:
                    analysis['quality_status'] = 'GOOD'
                else:
                    analysis['quality_status'] = 'NEEDS_IMPROVEMENT'
                
                self.log_analysis_results.append(analysis)
                
                logger.info(f"    [FILE] {Path(log_file).name}: {analysis['structured_percentage']}% structured, "
                           f"{analysis['error_percentage']}% errors, Quality: {analysis['quality_status']}")
                
            except Exception as e:
                logger.warning(f"Could not analyze log file {log_file}: {e}")

    def export_results_to_csv(self):
        """Export all test results to CSV files"""
        logger.info("[CHART] Exporting Test Results to CSV")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # API test results
            if self.api_test_results:
                api_file = self.output_dir / f"api_test_results_{timestamp}.csv"
                df_api = pd.DataFrame(self.api_test_results)
                df_api.to_csv(api_file, index=False, encoding='utf-8')
                logger.info(f"[CHECK] API Results: {api_file}")
            
            # System health results
            if self.system_health_results:
                health_file = self.output_dir / f"system_health_{timestamp}.csv"
                df_health = pd.DataFrame(self.system_health_results)
                df_health.to_csv(health_file, index=False, encoding='utf-8')
                logger.info(f"[CHECK] System Health: {health_file}")
            
            # Performance metrics
            if self.performance_metrics:
                perf_file = self.output_dir / f"performance_metrics_{timestamp}.csv"
                df_perf = pd.DataFrame(self.performance_metrics)
                df_perf.to_csv(perf_file, index=False, encoding='utf-8')
                logger.info(f"[CHECK] Performance: {perf_file}")
            
            # Log analysis results
            if self.log_analysis_results:
                log_file = self.output_dir / f"log_analysis_{timestamp}.csv"
                df_log = pd.DataFrame(self.log_analysis_results)
                df_log.to_csv(log_file, index=False, encoding='utf-8')
                logger.info(f"[CHECK] Log Analysis: {log_file}")
            
            # Comprehensive summary
            summary = self.create_test_summary()
            summary_file = self.output_dir / f"test_summary_{timestamp}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"[CHECK] Summary: {summary_file}")
            
            return timestamp, summary
            
        except Exception as e:
            logger.error(f"[ERROR] Export Error: {e}")
            return None, None

    def create_test_summary(self):
        """Create comprehensive test summary"""
        total_api_tests = len(self.api_test_results)
        successful_api_tests = len([r for r in self.api_test_results if r['status'] == 'SUCCESS'])
        
        # Response time analysis
        response_times = [r['response_time_ms'] for r in self.api_test_results if r.get('response_time_ms')]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Category breakdown
        categories = {}
        for result in self.api_test_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'success': 0}
            categories[cat]['total'] += 1
            if result['status'] == 'SUCCESS':
                categories[cat]['success'] += 1
        
        for cat in categories:
            total = categories[cat]['total']
            success = categories[cat]['success']
            categories[cat]['success_rate'] = round((success / total) * 100, 2) if total > 0 else 0
        
        return {
            'test_id': self.test_id,
            'execution_time': {
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_minutes': round((datetime.now() - self.start_time).total_seconds() / 60, 2)
            },
            'api_testing': {
                'total_tests': total_api_tests,
                'successful_tests': successful_api_tests,
                'failed_tests': total_api_tests - successful_api_tests,
                'success_rate': round((successful_api_tests / total_api_tests) * 100, 2) if total_api_tests > 0 else 0,
                'average_response_time_ms': round(avg_response_time, 2),
                'categories': categories
            },
            'system_analysis': {
                'log_files_analyzed': len(self.log_analysis_results),
                'performance_tests': len(self.performance_metrics),
                'celery_tasks_created': len([r for r in self.api_test_results if r.get('has_task')])
            },
            'environment': {
                'base_url': self.base_url,
                'python_version': sys.version.split()[0],
                'platform': sys.platform,
                'conda_env': os.environ.get('CONDA_DEFAULT_ENV', 'unknown')
            }
        }

    def display_final_report(self, summary: Dict):
        """Display comprehensive final test report"""
        logger.info("[TROPHY] BACKEND TEST SUITE COMPLETED")
        
        print("\n" + "="*80)
        print("[TROPHY] COMPREHENSIVE BACKEND API TEST SUITE - FINAL REPORT")
        print("="*80)
        
        print(f"\n[CHART] EXECUTION SUMMARY")
        print(f"  Test ID: {summary['test_id']}")
        print(f"  Base URL: {summary['environment']['base_url']}")
        print(f"  Duration: {summary['execution_time']['duration_minutes']} minutes")
        print(f"  Environment: {summary['environment']['conda_env']}")
        
        api_results = summary['api_testing']
        print(f"\n[SEARCH] API TESTING RESULTS")
        print(f"  Total Tests: {api_results['total_tests']}")
        print(f"  Successful: {api_results['successful_tests']}")
        print(f"  Failed: {api_results['failed_tests']}")
        print(f"  Success Rate: {api_results['success_rate']}%")
        print(f"  Avg Response: {api_results['average_response_time_ms']}ms")
        
        print(f"\n[CLIPBOARD] CATEGORY BREAKDOWN")
        for category, stats in api_results['categories'].items():
            success_icon = "[CHECK]" if stats['success_rate'] >= 90 else "[WARNING]" if stats['success_rate'] >= 70 else "[ERROR]"
            print(f"  {success_icon} {category}: {stats['success']}/{stats['total']} ({stats['success_rate']}%)")
        
        system_analysis = summary['system_analysis']
        print(f"\n[WRENCH] SYSTEM ANALYSIS")
        print(f"  Log Files Analyzed: {system_analysis['log_files_analyzed']}")
        print(f"  Performance Tests: {system_analysis['performance_tests']}")
        print(f"  Celery Tasks Created: {system_analysis['celery_tasks_created']}")
        
        print(f"\n[TARGET] FINAL ASSESSMENT")
        success_rate = api_results['success_rate']
        if success_rate >= 95:
            print(f"  [TROPHY] EXCELLENT - Backend system is production ready!")
        elif success_rate >= 85:
            print(f"  [CHECK] GOOD - System functional with minor issues")
        elif success_rate >= 70:
            print(f"  [WARNING] FAIR - Some components need attention")
        else:
            print(f"  [ERROR] POOR - Significant issues need resolution")
        
        print(f"\n[PARTY] COMPREHENSIVE BACKEND TESTING COMPLETED!")
        print("="*80)

    async def run_comprehensive_test(self, concurrent_users: int = 3):
        """Run complete comprehensive backend test suite"""
        logger.info("[ROCKET] Starting Comprehensive Backend Test Suite")
        
        # System prerequisites check
        self.system_health_results.append(self.check_system_prerequisites())
        
        # Run API tests
        async with aiohttp.ClientSession() as session:
            await self.test_health_system_endpoints(session)
            await self.test_legal_chat_endpoints(session)
            await self.test_rag_system_endpoints(session)
            await self.test_stream_endpoints(session)
        
        # Performance testing
        await self.test_concurrent_load(concurrent_users)
        
        # System analysis
        self.analyze_system_logs()
        
        # Export and report
        timestamp, summary = self.export_results_to_csv()
        if summary:
            self.display_final_report(summary)
        
        logger.info(f"[TARGET] All results exported with timestamp: {timestamp}")

async def main():
    parser = argparse.ArgumentParser(description='Comprehensive Backend API Test Suite')
    parser.add_argument('--url', default='http://localhost:8000', help='Backend API base URL')
    parser.add_argument('--output', default='tests/results', help='Output directory for results')
    parser.add_argument('--concurrent', type=int, default=3, help='Concurrent users for load testing')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("[SEARCH] Starting Comprehensive Backend API Testing...")
    
    test_suite = BackendTestSuite(args.url, args.output)
    await test_suite.run_comprehensive_test(args.concurrent)

if __name__ == "__main__":
    asyncio.run(main())
