import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BRAVE_SEARCH_API_KEY = os.getenv('BRAVE_SEARCH_API_KEY')
if not BRAVE_SEARCH_API_KEY:
    logger.error("BRAVE_SEARCH_API_KEY not found in environment variables")

class WebSearchTool:
    """Tool for searching the web using Brave Search API."""
    
    def __init__(self):
        self.api_key = BRAVE_SEARCH_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
    
    def search(self, query: str, count: int = 5) -> Dict[str, Any]:
        """
        Search the web using Brave Search API.
        
        Args:
            query (str): The search query
            count (int, optional): Number of results to return. Defaults to 5.
            
        Returns:
            Dict[str, Any]: The search results
        """
        try:
            params = {
                "q": query,
                "count": count
            }
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code != 200:
                logger.error(f"Error in Brave Search API: {response.status_code} - {response.text}")
                return {"error": f"Search API returned status code {response.status_code}"}
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return {"error": str(e)}
    
    def get_function_schema(self) -> Dict[str, Any]:
        """
        Return the function schema for the OpenAI function calling API.
        
        Returns:
            Dict[str, Any]: The function schema
        """
        return {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web for information using Brave Search API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of results to return (max 10)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    def execute(self, query: str, count: int = 5) -> str:
        """
        Execute the web search and format results for the agent.
        
        Args:
            query (str): The search query
            count (int, optional): Number of results to return. Defaults to 5.
            
        Returns:
            str: Formatted search results
        """
        raw_results = self.search(query, count)
        
        if "error" in raw_results:
            return f"Error searching the web: {raw_results['error']}"
        
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