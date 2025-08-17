from threading import Thread
import json
from app.celery_config import celery_app 
from app.web_search.extraction_service import ExtractionService
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils.logging_simplified import schedule_log_consolidation, consolidate_extraction_logs
from app.web_search.web_search_tool import get_links_from_serper

# Use centralized logging instead of basicConfig
logger = logging.getLogger(__name__)

extraction_service = ExtractionService()

@celery_app.task(name="app.tasks.link_extract_tasks.get_links_and_extract_task", queue="link_extract_queue")
def get_links_and_extract_task(query: str, max_links: int, max_workers: int = 3):
    # Get links from SERPER or fallback to mock data
    data_links = get_links_from_serper(query, num_results=15)
    
    # If no results from SERPER (e.g., missing API key), use mock data
    if not data_links or (len(data_links) == 1 and "error" in data_links[0]):
        logger.info("Using mock data for testing")
        data_links = [
            {"title": "Test Legal Document 1", "url": "https://example.com/test1", "snippet": "Test snippet 1"},
            {"title": "Test Legal Document 2", "url": "https://example.com/test2", "snippet": "Test snippet 2"}
        ]

    data_links_new = []
    name_to_skip = ["thuvienphapluat", "luatvietnam", "youtube"]
    for link in data_links:
        # Safety check for link structure
        if not isinstance(link, dict):
            logger.warning(f"⚠️ Invalid link structure (not dict): {link}")
            continue
            
        # Skip error entries from SERPER API
        if "error" in link:
            logger.warning(f"⚠️ Skipping error entry: {link}")
            continue
            
        # Check if required keys exist
        if "url" not in link:
            logger.warning(f"⚠️ Invalid link structure (missing 'url'): {link}")
            continue
            
        if any(name in link["url"] for name in name_to_skip):
            logger.info(f"Skipping {link['url']} as it is from {name_to_skip}")
        else:
            data_links_new.append(link)
    data_links = data_links_new[:max_links]
    
    logger.info(f"📋 Using {len(data_links)} test URLs for extraction")
    
    # 2. ✅ ThreadPoolExecutor logic với thread-specific logging
    logger.info(f"🚀 Starting extraction with {max_workers} workers")
    start_time = time.time()
    
    results = []
    documents_sent = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all extraction tasks với thread_id
        future_to_url = {}
        for i, data_link in enumerate(data_links):
            thread_id = f"{i+1:03d}_{int(time.time())}"
            future = executor.submit(extraction_service.extract_and_send_document, query, data_link, thread_id)
            # future = executor.submit(test_threads)
            future_to_url[future] = data_link
        
        # Collect results as they complete
        for future in as_completed(future_to_url):
            data_link = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                
                # Track documents sent
                if result.get('document_sent'):
                    documents_sent += 1
                
                # Log progress
                status = "✅" if result['success'] else "❌"
                method = result.get('method', 'unknown')
                text_len = result.get('text_length', 0)
                extraction_time = result.get('extraction_time', 0)
                logger.info(f"{status} {data_link['url']} | {method} | {text_len} chars | {extraction_time} s")

            except Exception as exc:
                logger.error(f"💥 Thread exception cho {data_link['url']}: {exc}")
                results.append({'success': False, 'error': str(exc), 'url': data_link['url']})

    total_time = time.time() - start_time
    successful = sum(1 for r in results if r['success'])
    
    logger.info(f"🎯 Extraction completed in {total_time:.2f}s | "
                f"Documents sent: {documents_sent}/{len(data_links)}")
    consolidate_extraction_logs()
    schedule_log_consolidation(delay_seconds=15)
    summary = {
        'query': query,
        'urls_processed': len(data_links),
        'successful_extractions': successful,
        'total_documents_sent': documents_sent,
        'results': results
    } 
    return summary

def test_threads():
    """
    Test function cho việc sử dụng threading trong extraction.
    """
    start = time.time()
    time.sleep(2)
    return {
    'url': "test",
    'success': False,
    'error': "",
    'document_sent': False,
    'method': 'unknown',
    'extraction_time': time.time() - start
}

def load_results_from_txt(filename):
    """
    Đọc file txt chứa kết quả (mỗi dòng là JSON), trả về list[dict]
    """
    results = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            try:
                if "thuvienphapluat" in line:
                    continue
                result = json.loads(line.strip())
                results.append(result)
            except json.JSONDecodeError:
                continue
    return results
