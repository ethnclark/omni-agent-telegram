import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class TokenPriceTool:
    def __init__(self):
        self.base_url = os.getenv("API_URL")
        
    def get_function_schema(self):
        """Return the function schema for the OpenAI function calling"""
        return {
            "type": "function",
            "function": {
                "name": "get_token_price",
                "description": "Get the current price of a specified cryptocurrency token",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "token": {
                            "type": "string",
                            "description": "The cryptocurrency token symbol (e.g., 'btc', 'eth', 'sui')"
                        }
                    },
                    "required": ["token"]
                }
            }
        }
        
    def execute(self, token):
        """
        Get the current price information for a cryptocurrency token
        
        Args:
            token (str): The cryptocurrency token symbol (e.g., 'btc', 'eth', 'sui')
            
        Returns:
            str: JSON string with token price information
        """
        try:
            print(f"Fetching price for token: {token}")
            # Normalize token symbol to lowercase
            token = token.lower()
            
            # Make the API request
            response = requests.get(self.base_url+'/api/token/price?token='+token)
            response.raise_for_status()
            
            data = response.json()

            # Check if data was returned
            if not data.get("data") or len(data["data"]) == 0:
                return f"No price information found for token '{token}'"
            
            # Extract relevant information from the response
            token_data = data["data"]['data'][0]
            token_info = {
                "symbol": token_data.get("fromCoin", {}).get("symbol", ""),
                "name": token_data.get("fromCoin", {}).get("name", ""),
                "price_usd": token_data.get("usdLast", 0),
                "price": token_data.get("last", 0),
                "quote_currency": token_data.get("toCoin", {}).get("symbol", "USDT"),
                "change_24h_percent": token_data.get("changePercent", 0),
                "high_24h": token_data.get("high", 0),
                "low_24h": token_data.get("low", 0),
                "exchange": token_data.get("exchangeName", ""),
                "url": token_data.get("url", "")
            }
            
            return token_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching token price: {e}")
            return f"Error fetching price information: {str(e)}"
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing token price data: {e}")
            return f"Error processing price information: {str(e)}"
