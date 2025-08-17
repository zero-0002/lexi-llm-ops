
import logging
from typing import Optional, Dict
from app.web_search.playwright_tool import extract_text_with_playwright_async
from app.web_search.requests_tool import extract_with_requests
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# --- Main unified function ---
def extract_text_fallback(url: str) -> Dict[str, Optional[str]]:
    result = extract_with_requests(url)
    if result["success"]:
        return result

    logger.info("Fallback to Playwright...")
    try:
        return asyncio.run(extract_text_with_playwright_async(url))
    except RuntimeError:
        # Handle nested event loop case (e.g., inside Jupyter)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(extract_text_with_playwright_async(url))


def extract_multiple_links(urls: list[str], max_workers: int = 5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_text_fallback, url): url for url in urls}
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({'success': False, 'url': futures[future], 'error': str(e)})
    return results

