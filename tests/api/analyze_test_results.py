#!/usr/bin/env python3
"""
BACKEND TEST RESULTS ANALYZER
============================
Quick analysis tool for backend test results
"""

import pandas as pd
import json
import glob
from datetime import datetime
import sys
from pathlib import Path

def analyze_latest_test_results(results_dir: str = "tests/results"):
    """Analyze the latest test results"""
    print("[CHART] BACKEND TEST RESULTS ANALYSIS")
    print("=" * 50)
    
    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"[ERROR] Results directory not found: {results_dir}")
        return
    
    # Find latest result files
    api_files = list(results_path.glob("api_test_results_*.csv"))
    summary_files = list(results_path.glob("test_summary_*.json"))
    log_files = list(results_path.glob("log_analysis_*.csv"))
    
    if not api_files:
        print("[ERROR] No test result files found!")
        print("Please run the backend test suite first:")
        print("  python tests/api/comprehensive_backend_test.py")
        return
    
    # Load latest files
    latest_api_file = max(api_files, key=lambda f: f.stat().st_mtime)
    latest_summary_file = max(summary_files, key=lambda f: f.stat().st_mtime) if summary_files else None
    latest_log_file = max(log_files, key=lambda f: f.stat().st_mtime) if log_files else None
    
    print(f"[FILE] Latest API Results: {latest_api_file.name}")
    print(f"[FILE] Latest Summary: {latest_summary_file.name if latest_summary_file else 'N/A'}")
    print(f"[FILE] Latest Log Analysis: {latest_log_file.name if latest_log_file else 'N/A'}")
    
    # Load and analyze API results
    df_api = pd.read_csv(latest_api_file)
    
    print(f"\n[SEARCH] API TEST RESULTS OVERVIEW")
    print(f"Total API Tests: {len(df_api)}")
    print(f"Successful Tests: {len(df_api[df_api.status == 'SUCCESS'])}")
    print(f"Failed Tests: {len(df_api[df_api.status == 'FAILED'])}")
    
    success_rate = len(df_api[df_api.status == 'SUCCESS']) / len(df_api) * 100
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Response time analysis
    successful_tests = df_api[df_api.status == 'SUCCESS']
    if len(successful_tests) > 0:
        print(f"Average Response Time: {successful_tests.response_time_ms.mean():.2f}ms")
        print(f"Fastest Response: {successful_tests.response_time_ms.min():.2f}ms")
        print(f"Slowest Response: {successful_tests.response_time_ms.max():.2f}ms")
    
    # Category breakdown
    print(f"\n[CLIPBOARD] RESULTS BY CATEGORY")
    category_stats = df_api.groupby('category').agg({
        'status': lambda x: f"{sum(x=='SUCCESS')}/{len(x)}",
        'response_time_ms': lambda x: f"{x.mean():.1f}ms" if x.notna().any() else "N/A"
    })
    
    for category, stats in category_stats.iterrows():
        success_count = int(stats['status'].split('/')[0])
        total_count = int(stats['status'].split('/')[1])
        success_rate_cat = (success_count / total_count) * 100
        icon = "[CHECK]" if success_rate_cat >= 90 else "[WARNING]" if success_rate_cat >= 70 else "[ERROR]"
        print(f"{icon} {category}: {stats['status']} ({success_rate_cat:.1f}%) - Avg: {stats['response_time_ms']}")
    
    # Task creation analysis
    tasks_created = df_api[df_api.has_task == True]
    print(f"\n[MASK] CELERY TASK ANALYSIS")
    print(f"Total Tasks Created: {len(tasks_created)}")
    if len(tasks_created) > 0:
        print(f"Task Creation Rate: {len(tasks_created)/len(df_api)*100:.1f}%")
    
    # Detailed test results
    print(f"\n[SEARCH] DETAILED TEST RESULTS")
    for _, row in df_api.iterrows():
        status_icon = "[CHECK]" if row.status == 'SUCCESS' else "[ERROR]"
        task_info = f" [MASK]" if row.has_task else ""
        print(f"{status_icon} {row['name']}: {row.response_time_ms:.1f}ms{task_info}")
    
    # Failed tests analysis
    failed_tests = df_api[df_api.status == 'FAILED']
    if len(failed_tests) > 0:
        print(f"\n[ERROR] FAILED TESTS ANALYSIS ({len(failed_tests)} failures)")
        for _, row in failed_tests.iterrows():
            print(f"  - {row['name']}: {row.error_message}")
    
    # Load summary if available
    if latest_summary_file:
        with open(latest_summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        print(f"\n[CHART] EXECUTION SUMMARY")
        print(f"Test ID: {summary['test_id']}")
        print(f"Duration: {summary['execution_time']['duration_minutes']} minutes")
        print(f"Environment: {summary['environment']['conda_env']}")
        print(f"Log Files Analyzed: {summary['system_analysis']['log_files_analyzed']}")
    
    # Log analysis if available
    if latest_log_file:
        df_log = pd.read_csv(latest_log_file)
        print(f"\n[CLIPBOARD] LOG ANALYSIS SUMMARY")
        for _, row in df_log.iterrows():
            quality_icon = "[CHECK]" if row.quality_status == 'EXCELLENT' else "[WARNING]" if row.quality_status == 'GOOD' else "[ERROR]"
            print(f"{quality_icon} {Path(row.log_file).name}: {row.structured_percentage:.1f}% structured, "
                  f"{row.error_percentage:.1f}% errors")
    
    # Stream analysis if available
    stream_tests = df_api[df_api.category == 'Stream']
    if len(stream_tests) > 0:
        print(f"\n[WAVE] STREAMING ANALYSIS")
        for _, row in stream_tests.iterrows():
            if row.status == 'SUCCESS' and 'chunks_received' in df_api.columns:
                print(f"  Stream: {row.get('chunks_received', 0)} chunks, {row.get('total_content_length', 0)} bytes")
    
    # Recommendations
    print(f"\n[TARGET] RECOMMENDATIONS")
    if success_rate >= 95:
        print("[TROPHY] EXCELLENT - Backend system is production ready!")
        print("   • All systems functioning optimally")
        print("   • Ready for deployment")
    elif success_rate >= 85:
        print("[CHECK] GOOD - System functional with minor issues")
        print("   • Address failed tests before production")
        print("   • Monitor performance metrics")
    elif success_rate >= 70:
        print("[WARNING] FAIR - Several components need attention")
        print("   • Review and fix failing endpoints")
        print("   • Check system dependencies")
    else:
        print("[ERROR] POOR - Significant issues need resolution")
        print("   • System not ready for production")
        print("   • Immediate attention required")
    
    print(f"\n[FOLDER] Full results available in: {results_dir}")

if __name__ == "__main__":
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "tests/results"
    analyze_latest_test_results(results_dir)
