import sys
import os
import time
sys.path.append(r'D:\Data\Legal-Retrieval')
from app.web_search.web_search_tool import get_links_from_serper
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import logging
# from tasks_embedding import process_and_embed_url
from app.web_search.extraction_service import ExtractionService
extraction_service = ExtractionService()

# Simplified logging imports for production
from app.utils.logging_simplified import get_logger, log_with_context, task_id_ctx, schedule_log_consolidation, consolidate_extraction_logs

# Use centralized logging instead of basicConfig
logger = get_logger(__name__)
import json
from urllib.parse import urlparse

# def trigger_log_consolidation(delay_seconds: int = 10):
#     """
#     Trigger log consolidation với delay để đảm bảo tất cả tasks đã hoàn thành
#     """
#     print(f"🕒 Scheduling log consolidation in {delay_seconds} seconds...")
    
#     # Schedule log consolidator task
#     task_result = log_consolidator.apply_async(countdown=delay_seconds)
    
#     print(f"✅ Log consolidation task scheduled: {task_result.id}")
#     return task_result.id


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

def extract_from_links(query: str, max_links: int = 3, max_workers: int = 3) -> List[Dict[str, Any]]:
    """
    Extract text from search results and send chunks to Redis for embedding
    """
    logger.info(f"🔍 Starting web search extraction for query: '{query}'")
    
    # 1. Get URLs from search (SERPER or test links)
    # Load search results from Serper API
    data_links = get_links_from_serper(query)[:max_links]
    # data_links = get_links_from_serper(query, num_results=15)
    
    name_to_skip = [
        # Pháp luật (đã có)
        "thuvienphapluat", "luatvietnam", "danluat",

        # Video 
        "youtube", 
        
        # Thương mại điện tử
        "shopee", "lazada", "tiki", "amazon", "aliexpress",
        # Chia sẻ tài liệu
        "slideshare", "scribd", "academia.edu", "researchgate",
    ]

    # Các đuôi file không phải là trang web có thể đọc được
    file_extensions_to_skip = (
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
        '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar'
    )


    data_links_new = []
    for link in data_links:
        url = link["url"]
        
        # **Cải tiến 1: Chỉ kiểm tra tên miền (domain) thay vì cả URL**
        # Điều này giúp tránh bỏ sót sai, ví dụ một bài viết có từ "youtube" trong tiêu đề
        try:
            domain = urlparse(url).netloc.lower()
        except Exception:
            # logger.warning(f"URL không hợp lệ, bỏ qua: {url}")
            continue

        # **Cải tiến 2: Kiểm tra đuôi file**
        if url.lower().endswith(file_extensions_to_skip):
            # logger.info(f"Bỏ qua vì là file: {url}")
            continue

        # Kiểm tra xem tên miền có chứa từ khóa cần bỏ qua không
        if any(name in domain for name in name_to_skip):
            # Tìm chính xác tên miền đã khớp để log ra
            matched_name = next((name for name in name_to_skip if name in domain), "không xác định")
            # logger.info(f"Bỏ qua '{url}' vì chứa tên miền không mong muốn: '{matched_name}'")
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
                logger.info(f"{status} {data_link['url']} | {method} | {text_len} chars | {extraction_time}")
                
            except Exception as exc:
                logger.error(f"💥 Thread exception cho {data_link['url']}: {exc}")
                results.append({'success': False, 'error': str(exc), 'url': data_link['url']})
    total_time = time.time() - start_time
    # 3. Gộp extraction logs từ các threads
    consolidate_extraction_logs()
    
    # 4. Trigger Celery log consolidation (KHÔNG block main process)
    # consolidation_task_id = trigger_log_consolidation(delay_seconds=20)
    consolidation_task_id = schedule_log_consolidation(delay_seconds=15)
    logger.info(f"🗂️ Celery log consolidation scheduled: {consolidation_task_id}")
    
    # 5. Summary (KHÔNG đợi consolidation)
    
    successful = sum(1 for r in results if r['success'])
    
    logger.info(f"🎯 Extraction completed in {total_time:.2f}s | "
                f"Documents sent: {documents_sent}/{len(data_links)}")
    
    summary = {
        'query': query,
        'urls_processed': len(data_links),
        'successful_extractions': successful,
        'total_documents_sent': documents_sent,
        'log_consolidation_task': consolidation_task_id,
        'results': results
    }
    
    return summary


if __name__ == "__main__":
    query = "thông tin về luật nghĩa vụ quân sự"
    extract_from_links(query)
    # final_results = extract_from_links(query)
    
    # for i, res in enumerate(final_results, 1):
    #     print(f"\n📝 Result {i}:")
    #     print(f"URL: {res.get('url')}")
    #     print(f"Title: {res.get('title')}")
    #     print(f"Method: {res.get('method')}")
    #     print(f"Success: {res.get('success')}")
    #     print(f"Text length: {len(res.get('text', ''))}")
    #     print(f"Text snippet: {res.get('text')[:300]}...\n")
        # break
