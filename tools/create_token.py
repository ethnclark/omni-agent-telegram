import requests
import logging
import json

# Set up logging
logger = logging.getLogger(__name__)

class CreateTokenTool:
    def __init__(self):
        self.api_url = "http://localhost:7777/api/sui/token"
    
    def get_function_schema(self):
        """
        Return the schema for the create token function in the format required by OpenAI's function calling
        """
        return {
            "type": "function",
            "function": {
                "name": "create_token",
                "description": "Create a new token on the Sui blockchain",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the token"
                        },
                        "symbol": {
                            "type": "string",
                            "description": "The symbol of the token (e.g., BTC, ETH)"
                        },
                        "description": {
                            "type": "string",
                            "description": "A description of the token and its purpose"
                        },
                        "image_url": {
                            "type": "string",
                            "description": "URL to the token's image or logo"
                        },
                        "init_supply": {
                            "type": "integer",
                            "description": "The initial supply of the token"
                        },
                        "wallet_address": {
                            "type": "string",
                            "description": "The Sui wallet address of the token creator"
                        },
                        "network": {
                            "type": "string",
                            "description": "The network to create the token on (mainnet/testnet/devnet)",
                            "enum": ["mainnet", "testnet", "devnet"]
                        }
                    },
                    "required": ["name", "symbol", "init_supply", "wallet_address", "network"]
                }
            }
        }
    
    def execute(self, name, symbol, description="", image_url="", init_supply=0, wallet_address="", network="mainnet"):
        """
        Execute the token creation by calling the API
        
        Args:
            name (str): The name of the token
            symbol (str): The symbol of the token
            description (str): A description of the token (optional)
            image_url (str): URL to the token's image (optional)
            init_supply (int): The initial supply of the token
            wallet_address (str): The Sui wallet address of the token creator
            network (str): The network to create the token on (mainnet/testnet/devnet)
            
        Returns:
            dict: The response from the API
        """
        try:
            payload = {
                "name": name,
                "symbol": symbol,
                "description": description,
                "image_url": image_url,
                "init_supply": init_supply,
                "wallet_address": wallet_address,
                "network": network
            }
            
            logger.info(f"Creating token on {network} with payload: {payload}")
            
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Token creation response: {result}")
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error creating token on {network}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create token on {network}: {str(e)}"
            }
