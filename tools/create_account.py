import requests
import logging
import os
from typing import Annotated, Literal, Optional
from dotenv import load_dotenv
from langchain_core.tools import tool

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

@tool
def create_account(
    network: Annotated[Literal["mainnet", "testnet", "devnet"], "The network to create account on"],
    scheme: Annotated[Literal["secp256k1", "ed25519"], "The cryptographic scheme to use"] = "secp256k1",
    user_id: Annotated[Optional[int], "The Telegram user_id of the user creating the account"] = None
) -> str:
    """
    Create a new wallet account on the Sui blockchain
    
    Args:
        network (str): The network to create account on (mainnet/testnet/devnet)
        scheme (str): The cryptographic scheme to use (default: secp256k1)
        user_id (int, optional): The Telegram user_id of the user
        
    Returns:
        str: The response from the API containing wallet information
    """
    try:
        if not network:
            return "Network parameter is required. Please specify 'mainnet', 'testnet', or 'devnet'."

        if network not in ["mainnet", "testnet", "devnet"]:
            return "Invalid network. Please choose 'mainnet', 'testnet', or 'devnet'."

        api_url = f"{os.getenv('API_RELAYER_URL')}/api/sui/account"
        payload = {
            "scheme": scheme,
            "network": network
        }
        if user_id:
            payload["user_id"] = user_id
        
        logger.info(f"Creating Sui account with scheme: {scheme}, network: {network}, user_id: {user_id}")
        
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Account creation successful: {result['status']}")
        
        return str(result)
        
    except requests.RequestException as e:
        error_msg = f"Failed to create wallet account: {str(e)}"
        logger.error(error_msg)
        return error_msg 