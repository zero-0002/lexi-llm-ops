"""
Simple Web Search Tool using SERPER API
"""
import requests
import os
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def get_links_from_serper(query: str, num_results: int = 5) -> List[Dict]:
    """
    Simple web search using SERPER API
    """
    if not SERPER_API_KEY:
        return [{"error": "Missing SERPER_API_KEY"}]
    
    try:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": f"{query}",  
            "num": num_results,
            "hl": "en"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        organic_results = data.get("organic", [])
        
        results = []
        for item in organic_results:
            result = {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "position": item.get("position", 0)
            }
            
            if result["url"] and result["title"]:
                results.append(result)
        
        return results
        
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]
