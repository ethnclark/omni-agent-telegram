import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Annotated
from dotenv import load_dotenv
from langchain_core.tools import tool

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BRAVE_SEARCH_API_KEY = os.getenv('BRAVE_SEARCH_API_KEY')
if not BRAVE_SEARCH_API_KEY:
    logger.error("BRAVE_SEARCH_API_KEY not found in environment variables")

@tool
def search_web(query: str, count: int = 5) -> str:
    """
    Search the web for information using Brave Search API.
    
    Args:
        query: The search query
        count: Number of results to return (max 10)
        
    Returns:
        Formatted search results
    """
    try:
        base_url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": BRAVE_SEARCH_API_KEY
        }
        
        params = {
            "q": query,
            "count": count
        }
        
        response = requests.get(
            base_url,
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            logger.error(f"Error in Brave Search API: {response.status_code} - {response.text}")
            return f"Error searching the web: Search API returned status code {response.status_code}"
        
        raw_results = response.json()
        formatted_results = "Web Search Results:\n\n"
        
        if "web" in raw_results and "results" in raw_results["web"]:
            results = raw_results["web"]["results"]
            
            for i, result in enumerate(results, 1):
                title = result.get("title", "No title")
                url = result.get("url", "No URL")
                description = result.get("description", "No description")
                
                formatted_results += f"{i}. {title}\n"
                formatted_results += f"   URL: {url}\n"
                formatted_results += f"   {description}\n\n"
        else:
            formatted_results += "No results found."
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error in web search: {e}")
        return f"Error searching the web: {str(e)}" 