
import requests
from bs4 import BeautifulSoup
import trafilatura
from typing import Optional, Dict

# Define User-Agent headers
HEADERS_LIST = [
    # Desktop
    { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36' },
    # Mobile
    { 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1' },
    # Googlebot
    { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' },
    # Facebook crawler
    { 'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)' }
]

CONTENT_SELECTORS = [
    '.content', '.post-content', '.entry-content',
    '.article-content', '.main-content', '.detail-content',
    '.law-content', '.text-content', '#content', '#main',
    'article', '.post-body'
]

# --- Extraction via Requests ---
def extract_with_requests(url: str, timeout: int = 15) -> Dict[str, Optional[str]]:
    for i, headers in enumerate(HEADERS_LIST):
        try:
            # print(f"Trying approach {i+1}...")
            session = requests.Session()
            session.headers.update(headers)

            # if i > 0:
            #     time.sleep(random.uniform(1, 2))

            response = session.get(url, timeout=timeout, allow_redirects=True)
            if response.status_code != 200 or len(response.text) < 1000:
                continue

            # Try trafilatura
            try:
                text = trafilatura.extract(response.text, favor_precision=True)
                metadata = trafilatura.extract_metadata(response.text)
                if text and len(text.strip()) > 100:
                    return {
                        'success': True,
                        'method': f'Trafilatura (approach {i+1})',
                        'text': text,
                        'title': metadata.title if metadata else None,
                        'author': metadata.author if metadata else None,
                        'date': metadata.date if metadata else None,
                        'description': metadata.description if metadata else None,
                        'url': url
                    }
            except:
                pass

            # Fallback BeautifulSoup
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
                for el in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement', 'ads']):
                    el.decompose()

                main_content = None
                for sel in CONTENT_SELECTORS:
                    main_content = soup.select_one(sel)
                    if main_content:
                        break
                if not main_content:
                    main_content = soup.find('body')

                if main_content:
                    for el in main_content.find_all(['div'], class_=['share', 'social', 'related', 'comments', 'ads']):
                        el.decompose()
                    text = main_content.get_text(separator=' ', strip=True)
                    text = ' '.join(text.split())
                    if len(text) > 100:
                        title = soup.title.string.strip() if soup.title else None
                        return {
                            'success': True,
                            'method': f'BeautifulSoup (approach {i+1})',
                            'text': text,
                            'title': title,
                            'author': None,
                            'date': None,
                            'description': None,
                            'url': url
                        }
            except:
                pass

        except Exception:
            continue

    return {
        'success': False,
        'method': None,
        'text': None,
        'title': None,
        'author': None,
        'date': None,
        'description': None,
        'url': url
    }




