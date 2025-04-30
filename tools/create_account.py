import requests
import logging
import os
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

class CreateAccountTool:
    def __init__(self):
        load_dotenv()
        self.api_url = f"{os.getenv('API_RELAYER_URL')}/api/sui/account"
    
    def get_function_schema(self):
        """
        Return the schema for the create account function in the format required by OpenAI's function calling
        """
        return {
            "type": "function",
            "function": {
                "name": "create_account",
                "description": "Create a new wallet account on the Sui blockchain. Network parameter is required (mainnet/testnet/devnet).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scheme": {
                            "type": "string",
                            "description": "The cryptographic scheme to use (default: secp256k1)",
                            "enum": ["secp256k1", "ed25519"]
                        },
                        "user_id": {
                            "type": "number",
                            "description": "The Telegram user_id of the user creating the account"
                        },
                        "network": {
                            "type": "string",
                            "description": "The network to create account on (mainnet/testnet/devnet)",
                            "enum": ["mainnet", "testnet", "devnet"]
                        }
                    },
                    "required": ["network"]
                }
            }
        }
    
    def execute(self, network, scheme="secp256k1", user_id=None):
        """
        Execute the account creation by calling the API
        
        Args:
            network (str): The network to create account on (mainnet/testnet/devnet)
            scheme (str): The cryptographic scheme to use (default: secp256k1)
            user_id (int): The Telegram user_id of the user
            
        Returns:
            dict: The response from the API containing wallet information
        """
        try:
            if not network:
                return {
                    "status": "error",
                    "error": "Network parameter is required. Please specify 'mainnet', 'testnet', or 'devnet'."
                }

            if network not in ["mainnet", "testnet", "devnet"]:
                return {
                    "status": "error",
                    "error": "Invalid network. Please choose 'mainnet', 'testnet', or 'devnet'."
                }

            payload = {
                "scheme": scheme,
                "network": network
            }
            if user_id:
                payload["user_id"] = user_id
            
            logger.info(f"Creating Sui account with scheme: {scheme}, network: {network}, user_id: {user_id}")
            
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Account creation successful: {result['status']}")
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error creating account: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to create wallet account: {str(e)}"
            } 