import logging
import traceback
from app.web_search.runner import extract_from_links

logger = logging.getLogger(__name__)

class WebSearchService:
    def search(self, query: str):
        """Web search với error handling"""
        try:
            logger.info(f"Received web search query: {query}")
            
            # Extract text from links
            results = extract_from_links(query)
            return {"results": results}
            
        except Exception as e:
            logger.exception("Exception occurred during web search")
            
            # Detailed traceback already logged by logger.exception
            logger.error("Web search error traceback logged above")
            
            return {
                "results": [], 
                "error": f"Web search failed: {type(e).__name__} - {str(e)}"
            }
