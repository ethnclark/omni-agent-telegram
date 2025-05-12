import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.tools import tool

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

def format_date(timestamp):
    """
    Format timestamp to readable date
    """
    try:
        date = datetime.fromtimestamp(timestamp / 1000)
        return date.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ""

@tool
def get_news() -> str:
    """
    Get latest news about SUI cryptocurrency
    
    Returns:
        str: The response containing news information with title, description, and url
    """
    try:
        api_url = "https://api.cryptorank.io/v0/news"
        params = {
            "lang": "en",
            "coinKeys": "sui",
            "withFullContent": "true"
        }
        
        logger.info("Fetching SUI news")
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        result = response.json()
        
        # Format the news items with only required fields and limit to 5 items
        formatted_news = []
        if "data" in result:
            for news in result["data"][:5]:  # Limit to 5 items
                formatted_news.append({
                    "title": news.get("title", ""),
                    "description": news.get("description", ""),
                    "url": news.get("url", "")
                })
                
        return str({
            "status": "success",
            "data": formatted_news
        })
        
    except requests.RequestException as e:
        error_msg = f"Failed to fetch news: {str(e)}"
        logger.error(error_msg)
        return error_msg 