import os
import requests
import logging
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

class GetAccountTool:
    def __init__(self):
        load_dotenv()
        self.api_url = f"{os.getenv('API_RELAYER_URL')}/api/sui/account/by-user"
    
    def get_function_schema(self):
        """
        Return the schema for the get account function in the format required by OpenAI's function calling
        """
        return {
            "type": "function",
            "function": {
                "name": "get_account",
                "description": "Get user's Sui wallet account information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user ID to get account for"
                        },
                        "privatekey": {
                            "type": "boolean",
                            "description": "Whether to include private key in response"
                        },
                        "network": {
                            "type": "string",
                            "description": "The network to get account from (mainnet/testnet/devnet). Optional, defaults to mainnet.",
                            "enum": ["mainnet", "testnet", "devnet"]
                        }
                    },
                    "required": ["user_id"]
                }
            }
        }
    
    def execute(self, user_id, privatekey=None, network=None):
        """
        Get the Sui account by calling the API
        Args:
            user_id (number): The Telegram user_id of the user
            privatekey (str, optional): The private key of the account
            network (str, optional): The network to get account from (mainnet/testnet/devnet)
        Returns:
            dict: The response from the API containing account information
        """
        try:
            params = {"user_id": user_id}
            if privatekey:
                params["privatekey"] = privatekey
            if network:
                if network not in ["mainnet", "testnet", "devnet"]:
                    return {
                        "status": "error",
                        "error": "Invalid network. Please choose 'mainnet', 'testnet', or 'devnet'."
                    }
                params["network"] = network
            
            logger.info(f"Fetching Sui account for user: {user_id}, network: {network or 'mainnet'}")
            response = requests.get(f"{self.api_url}/api/sui/account", params=params)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Get account response: {result}")
            return result
        except requests.RequestException as e:
            logger.error(f"Error getting account: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to get account: {str(e)}"
            }

class GetAccountDetailTool:
    def __init__(self):
        load_dotenv()
        self.api_base_url = os.getenv('API_RELAYER_URL')
    
    def get_function_schema(self):
        """
        Return the schema for the get account detail function in the format required by OpenAI's function calling
        """
        return {
            "type": "function",
            "function": {
                "name": "get_account_detail",
                "description": "Get detailed Sui account info such as balance, tokens, NFTs, and on-chain objects by wallet address.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The Sui wallet address to fetch details for."
                        },
                        "network": {
                            "type": "string",
                            "description": "The network to get account from (mainnet/testnet/devnet). Optional, defaults to mainnet.",
                            "enum": ["mainnet", "testnet", "devnet"]
                        }
                    },
                    "required": ["address"]
                }
            }
        }
    
    def format_balance(self, balance, decimals):
        """
        Format raw balance with proper decimals
        """
        try:
            raw_balance = int(balance)
            formatted = raw_balance / (10 ** decimals)
            return f"{formatted:,.6f}"
        except Exception as e:
            logger.error(f"Error formatting balance: {e}")
            return balance
    
    def execute(self, address, network=None):
        """
        Get detailed Sui account info by address
        Args:
            address (str): The Sui wallet address
            network (str, optional): The network to get account from (mainnet/testnet/devnet)
        Returns:
            dict: The response from the API containing account details with formatted balances
        """
        try:
            url = f"{self.api_base_url}/api/sui/account/{address}"
            params = {}
            if network:
                if network not in ["mainnet", "testnet", "devnet"]:
                    return {
                        "status": "error",
                        "error": "Invalid network. Please choose 'mainnet', 'testnet', or 'devnet'."
                    }
                params["network"] = network
            
            logger.info(f"Fetching Sui account details for address: {address}, network: {network or 'mainnet'}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            # Format balances if present in response
            if isinstance(result, dict) and "data" in result:
                data = result["data"]
                
                # Format total SUI balance
                if "balance" in data and isinstance(data["balance"], dict):
                    balance_info = data["balance"]
                    if "totalBalance" in balance_info:
                        balance_info["totalBalance"] = self.format_balance(balance_info["totalBalance"], 9) + " SUI"
                
                # Format token balances
                if "tokens" in data and isinstance(data["tokens"], list):
                    for token in data["tokens"]:
                        if "balance" in token and "decimals" in token:
                            decimals = int(token.get("decimals", 0))
                            formatted = self.format_balance(token["balance"], decimals)
                            token["formatted_balance"] = f"{formatted} {token.get('symbol', '')}".strip()
            
            logger.info(f"Account detail response: {result}")
            return result
        except requests.RequestException as e:
            logger.error(f"Error fetching account detail: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to get account detail: {str(e)}"
            }
