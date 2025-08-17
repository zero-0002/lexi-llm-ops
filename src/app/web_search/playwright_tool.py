import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
import trafilatura
from bs4 import BeautifulSoup
import random
import time
import logging
from datetime import datetime
from typing import Optional, Dict, List

# Use centralized logging instead of basicConfig
logger = logging.getLogger(__name__)

playwright_context = None
browser_instance = None

def log_time(message: str, start: float, enable_log: bool = True):
    if not enable_log:
        return
    elapsed = time.time() - start
    # print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message} - {elapsed:.2f}s")
    logging.info(f"{message} - {elapsed:.2f}s")


def get_browser_page(stealth_mode: bool = True):
    """
    Quản lý và tái sử dụng trình duyệt cho mỗi worker process.
    Hàm này sẽ khởi tạo trình duyệt với các tùy chọn stealth chỉ một lần.
    """
    global playwright_context, browser_instance
    
    if browser_instance is None or not browser_instance.is_connected():
        logging.info("[PLAYWRIGHT-WORKER] Khởi tạo instance Playwright và trình duyệt mới...")
        playwright_context = sync_playwright().start()
        
        browser_args = [
            '--no-sandbox', '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage', '--disable-extensions', '--disable-plugins',
            '--disable-default-apps', '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding'
        ]
        if stealth_mode:
            browser_args.extend(['--disable-web-security', '--disable-features=VizDisplayCompositor'])
        
        browser_instance = playwright_context.chromium.launch(headless=True, args=browser_args)
    
    # Tạo một context mới cho mỗi page để đảm bảo sự cô lập (cookies, storage)
    context = browser_instance.new_context(
        viewport={'width': 1366, 'height': 768},
        locale='vi-VN',
        timezone_id='Asia/Ho_Chi_Minh',
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    if stealth_mode:
        # Thêm các stealth script vào context
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['vi-VN', 'vi', 'en-US', 'en'] });
        """)
    
    return context.new_page()

def extract_text_task( url: str) -> str:
    """
    Công đoạn 1: Bóc tách text từ URL bằng Playwright (phiên bản sync).
    Sử dụng logic từ hàm async cũ của bạn.
    """
    logging.info(f"[PLAYWRIGHT-WORKER] Bắt đầu bóc tách: {url}")
    page = None

    start_total = time.time()
    try:
        page = get_browser_page(stealth_mode=True)
        
        # Navigate
        page.goto(url, timeout=45000, wait_until="domcontentloaded")
        
        # Chờ thêm một chút cho các nội dung động
        page.wait_for_timeout(1000)
        
        html_content = page.content()
        
        # --- Logic bóc tách đa tầng ---
        extracted_text = None
        method_used = None

        # 1. Thử Trafilatura
        try:
            text = trafilatura.extract(html_content, include_comments=False, include_tables=True, favor_precision=True)
            if text and len(text.strip()) > 100:
                extracted_text = ' '.join(text.split())
                method_used = "Trafilatura"
        except Exception:
            pass
        
        # 2. Thử BeautifulSoup (nếu Trafilatura thất bại)
        if not extracted_text:
            try:
                soup = BeautifulSoup(html_content, 'lxml')
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    element.decompose()
                body_text = soup.body.get_text(separator=' ', strip=True)
                if body_text and len(body_text.strip()) > 100:
                    extracted_text = ' '.join(body_text.split())
                    method_used = "BeautifulSoup"
            except Exception:
                pass

        if not extracted_text:
            raise ValueError("Không thể bóc tách được nội dung đáng kể từ trang web.")

        log_time(f"Bóc tách thành công bằng {method_used}", start_total)
        return extracted_text

    except Exception as e:
        log_time(f"Lỗi khi bóc tách {url}", start_total)
        logging.exception(f"[PLAYWRIGHT-WORKER] Lỗi chi tiết: {e}")
        return ""
    finally:
        if page:
            # Đóng cả context của page để dọn dẹp triệt để
            context = page.context
            page.close()
            context.close()


async def extract_text_with_playwright_async(
    url: str, 
    timeout: int = 30000,  # milliseconds
    wait_for_content: bool = True,
    stealth_mode: bool = True,
    log_time_enable: bool = True
) -> Dict[str, Optional[str]]:
    start_total = time.time()
    log_time("Start extraction", start_total, log_time_enable)

    async with async_playwright() as p:
        try:
            start_browser = time.time()
            # Launch browser with stealth options
            browser_args = [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-default-apps',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
            
            if stealth_mode:
                browser_args.extend([
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ])
            
            browser = await p.chromium.launch(
                headless=True,
                args=browser_args
            )
            log_time("Browser launched", start_browser, log_time_enable)

            start_context = time.time()
            # Create context with Vietnamese locale and realistic viewport
            context = await browser.new_context(
                viewport={'width': 1366, 'height': 768},
                locale='vi-VN',
                timezone_id='Asia/Ho_Chi_Minh',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            log_time("Context created", start_context, log_time_enable)

            if stealth_mode:
                start_stealth = time.time()
                # Add extra headers if stealth mode
                await context.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"'
                })
                
                # Add stealth scripts
                await context.add_init_script("""
                    // Remove webdriver property
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Mock chrome object
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                    
                    // Mock plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    
                    // Mock languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['vi-VN', 'vi', 'en-US', 'en'],
                    });
                """)
                log_time("Stealth headers/scripts added", start_stealth, log_time_enable)

            start_page = time.time()
            page = await context.new_page()
            log_time("New page created", start_page, log_time_enable)

            # Random delay to seem more human
            if stealth_mode:
                await asyncio.sleep(random.uniform(0, 0.3))

            start_nav = time.time()
            # Navigate to page
            response = await page.goto(url, timeout=timeout, wait_until='domcontentloaded')
            log_time("Page navigation", start_nav, log_time_enable)

            if not response:
                raise Exception("Failed to load page")
            
            if response.status >= 400:
                raise Exception(f"HTTP {response.status}: {response.status_text}")

            # Wait for content to load
            if wait_for_content:
                start_wait_content = time.time()
                try:
                    # Wait for common content selectors
                    await page.wait_for_selector('body', timeout=5000)
                    try:
                        await page.wait_for_function("""
                            (selectors) => selectors.some(sel => document.querySelector(sel))
                        """, arg=content_selectors, timeout=5000)
                    except:
                        pass
                    # Additional wait for dynamic content
                    
                    await asyncio.sleep(0.3)

                except PlaywrightTimeoutError:
                    pass  # Continue anyway
                log_time("Wait for content", start_wait_content, log_time_enable)

            # Get page content
            html_content = await page.content()

            # Extract title
            title = await page.title()

            # Extraction methods timing
            start_extract = time.time()
            extracted_text = None
            method_used = None
            
            # Method 1: Try trafilatura first
            try:
                text = trafilatura.extract(
                    html_content,
                    include_comments=False,
                    include_tables=True,
                    include_formatting=False,
                    favor_precision=True
                )
                if text and len(text.strip()) > 100:
                    extracted_text = text
                    method_used = "Trafilatura"
            except:
                pass
            log_time("Trafilatura extraction", start_extract, log_time_enable)

            # Method 2: Custom JavaScript extraction
            if not extracted_text:
                start_js = time.time()
                try:
                    js_text = await page.evaluate("""
                        () => {
                            // Remove unwanted elements
                            const unwanted = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement', 'ads', 'sidebar', 'menu'];
                            unwanted.forEach(tag => {
                                document.querySelectorAll(tag).forEach(el => el.remove());
                            });
                            
                            // Try to find main content
                            const contentSelectors = [
                                '.content', '.post-content', '.entry-content', 
                                '.article-content', '.main-content', '.detail-content',
                                '.law-content', '.text-content', 'article', '.post-body'
                            ];
                            
                            let mainContent = null;
                            for (const selector of contentSelectors) {
                                mainContent = document.querySelector(selector);
                                if (mainContent) break;
                            }
                            
                            if (!mainContent) {
                                mainContent = document.body;
                            }
                            
                            // Clean up and extract text
                            if (mainContent) {
                                // Remove more unwanted elements within content
                                mainContent.querySelectorAll('.share, .social, .related, .comments, .ads').forEach(el => el.remove());
                                return mainContent.innerText || mainContent.textContent || '';
                            }
                            
                            return document.body.innerText || document.body.textContent || '';
                        }
                    """)
                    
                    if js_text and len(js_text.strip()) > 100:
                        extracted_text = ' '.join(js_text.split())
                        method_used = "JavaScript extraction"
                except:
                    pass
                log_time("JavaScript extraction", start_js, log_time_enable)
            # Method 3: BeautifulSoup fallback
            if not extracted_text:
                start_bs = time.time()
                try:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                                       'aside', 'advertisement', 'ads', 'sidebar', 'menu']):
                        element.decompose()
                    
                    # Find main content
                    content_selectors = [
                        '.content', '.post-content', '.entry-content',
                        '.article-content', '.main-content', '.detail-content',
                        '.law-content', '.text-content', 'article', '.post-body'
                    ]
                    
                    main_content = None
                    for selector in content_selectors:
                        main_content = soup.select_one(selector)
                        if main_content:
                            break
                    
                    if not main_content:
                        main_content = soup.find('body')
                    
                    if main_content:
                        text = main_content.get_text(separator=' ', strip=True)
                        text = ' '.join(text.split())
                        if len(text.strip()) > 100:
                            extracted_text = text
                            method_used = "BeautifulSoup"
                except:
                    pass
                log_time("BeautifulSoup extraction", start_bs, log_time_enable)

            start_meta = time.time()
            # Extract metadata
            metadata = {}
            try:
                metadata = trafilatura.extract_metadata(html_content)
            except:
                pass
            log_time("Metadata extraction", start_meta, log_time_enable)

            await browser.close()

            log_time("Total extraction finished", start_total, log_time_enable)

            if extracted_text:
                return {
                    'success': True,
                    'error': None,
                    'method': method_used,
                    'title': title,
                    'text': extracted_text,
                    'author': metadata.author if metadata and hasattr(metadata, 'author') else None,
                    'date': metadata.date if metadata and hasattr(metadata, 'date') else None,
                    'url': url,
                    'description': metadata.description if metadata and hasattr(metadata, 'description') else None,
                    'status_code': response.status
                }
            else:
                return {
                    'success': False,
                    'error': 'No substantial content found',
                    'method': None,
                    'title': title,
                    'text': None,
                    'author': None,
                    'date': None,
                    'url': url,
                    'status_code': response.status
                }
                
        except Exception as e:
            try:
                await browser.close()
            except:
                pass
            
            log_time("Exception occurred", start_total, log_time_enable)
            return {
                'success': False,
                'error': str(e),
                'method': None,
                'title': None,
                'text': None,
                'author': None,
                'date': None,
                'url': url
            }

# def extract_text_with_playwright_sync(
#     url: str, 
#     timeout: int = 30000,
#     wait_for_content: bool = True,
#     stealth_mode: bool = True,
#     log_time_enable: bool = True
# ) -> Dict[str, Optional[str]]:
#     """
#     Synchronous wrapper for Playwright extraction
#     """
#     return asyncio.run(extract_text_with_playwright_async(url, timeout, wait_for_content, stealth_mode, log_time_enable))

# Wrapper cho compatibility
def extract_text_with_playwright_sync(url):
    """Wrapper function cho compatibility với code cũ"""
    return extract_text_task(url)


def extract_text_with_playwright_multiple_attempts(
    url: str,
    max_attempts: int = 3,
    base_timeout: int = 30000,
    log_time_enable: bool = True
) -> Dict[str, Optional[str]]:
    """
    Try multiple extraction attempts with different strategies
    """
    strategies = [
        # Strategy 1: Full stealth mode
        {'stealth_mode': True, 'wait_for_content': True, 'timeout': base_timeout, 'log_time_enable': log_time_enable},
        
        # Strategy 2: Faster loading, less waiting
        {'stealth_mode': True, 'wait_for_content': False, 'timeout': base_timeout // 2, 'log_time_enable': log_time_enable},
        
        # Strategy 3: No stealth, just raw extraction
        {'stealth_mode': False, 'wait_for_content': True, 'timeout': base_timeout, 'log_time_enable': log_time_enable}
    ]
    
    for attempt in range(min(max_attempts, len(strategies))):
        try:
            logger.info(f"Playwright attempt {attempt + 1} with strategy: {strategies[attempt]}")
            
            result = extract_text_with_playwright_sync(url, **strategies[attempt])
            
            if result['success'] and result['text'] and len(result['text'].strip()) > 100:
                result['attempt'] = attempt + 1
                return result
            
            # Wait between attempts
            if attempt < max_attempts - 1:
                time.sleep(random.uniform(2, 5))
                
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            continue
    
    return {
        'success': False,
        'error': f'All {max_attempts} attempts failed',
        'method': None,
        'title': None,
        'text': None,
        'author': None,
        'date': None,
        'url': url
    }

# Test function for Vietnamese websites
async def test_vietnamese_website_playwright():
    """
    Test Playwright extraction on Vietnamese website with anti-bot protection
    """
    url = "https://luatvietnam.vn/quoc-phong/luat-nghia-vu-quan-su-2015-so-78-2015-qh13-moi-nhat-96362-d1.html"
    
    logger.info("Testing Playwright extraction...")
    result = await extract_text_with_playwright_async(url)
    
    if result['success']:
        logger.info(f"✅ Success with {result['method']}")
        logger.info(f"Title: {result['title']}")
        logger.info(f"Status Code: {result.get('status_code', 'Unknown')}")
        logger.info(f"Text length: {len(result['text']) if result['text'] else 0} characters")
        logger.info(f"Preview: {result['text'][:300] if result['text'] else 'No text'}...")
    else:
        logger.error(f"❌ Failed: {result['error']}")
        
    return result

def test_vietnamese_website_sync():
    """
    Synchronous test function
    """
    return asyncio.run(test_vietnamese_website_playwright())

# url = "https://luatvietnam.vn/quoc-phong/luat-nghia-vu-quan-su-2015-so-78-2015-qh13-moi-nhat-96362-d1.html"

# result = test_vietnamese_website_sync()
# Installation and usage instructions
"""
Installation:
pip install playwright trafilatura beautifulsoup4

# Install browser
playwright install chromium

Basic usage:
# Async version
result = await extract_text_with_playwright_async("https://example.com")

# Sync version  
result = extract_text_with_playwright_sync("https://example.com")

# Multiple attempts with different strategies
result = extract_text_with_playwright_multiple_attempts("https://protected-site.com")

# Test with Vietnamese website
result = test_vietnamese_website_sync()

Advanced features:
- Real browser automation (handles JavaScript)
- Stealth mode to avoid detection
- Vietnamese locale and timezone
- Multiple extraction strategies
- Custom headers and user agent
- Dynamic content waiting
- Anti-detection scripts

Perfect for:
- JavaScript-heavy websites
- Sites with anti-bot protection
- Dynamic content loading
- Complex Vietnamese websites
"""
