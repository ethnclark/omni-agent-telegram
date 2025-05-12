import os
import requests
import logging
from typing import Annotated, Literal, Optional
from dotenv import load_dotenv
from langchain_core.tools import tool

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

@tool
def get_account(
    user_id: Annotated[str, "The user ID to get account for"],
    privatekey: Annotated[Optional[bool], "Whether to include private key in response"] = None,
    network: Annotated[Optional[Literal["mainnet", "testnet", "devnet"]], "The network to get account from"] = None
) -> str:
    """
    Get user's Sui wallet account information
    
    Args:
        user_id (str): The Telegram user_id of the user
        privatekey (bool, optional): Whether to include private key in response
        network (str, optional): The network to get account from (mainnet/testnet/devnet)
        
    Returns:
        str: The response from the API containing account information
    """
    try:
        api_url = f"{os.getenv('API_RELAYER_URL')}/api/sui/account/by-user"
        params = {"user_id": user_id}
        if privatekey:
            params["privatekey"] = privatekey
        if network:
            if network not in ["mainnet", "testnet", "devnet"]:
                return "Invalid network. Please choose 'mainnet', 'testnet', or 'devnet'."
            params["network"] = network
        
        logger.info(f"Fetching Sui account for user: {user_id}, network: {network or 'mainnet'}")
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Get account response: {result}")
        return str(result)
    except requests.RequestException as e:
        error_msg = f"Failed to get account: {str(e)}"
        logger.error(error_msg)
        return error_msg

def format_balance(balance, decimals):
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

@tool
def get_account_detail(
    address: Annotated[str, "The Sui wallet address to fetch details for"],
    network: Annotated[Optional[Literal["mainnet", "testnet", "devnet"]], "The network to get account from"] = None
) -> str:
    """
    Get detailed Sui account info such as balance, tokens, NFTs, and on-chain objects by wallet address
    
    Args:
        address (str): The Sui wallet address
        network (str, optional): The network to get account from (mainnet/testnet/devnet)
        
    Returns:
        str: The response from the API containing account details with formatted balances
    """
    try:
        api_base_url = os.getenv('API_RELAYER_URL')
        url = f"{api_base_url}/api/sui/account/{address}"
        params = {}
        if network:
            if network not in ["mainnet", "testnet", "devnet"]:
                return "Invalid network. Please choose 'mainnet', 'testnet', or 'devnet'."
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
                    balance_info["totalBalance"] = format_balance(balance_info["totalBalance"], 9) + " SUI"
            
            # Format token balances
            if "tokens" in data and isinstance(data["tokens"], list):
                # Limit to 5 items
                data["tokens"] = data["tokens"][:5]
                for token in data["tokens"]:
                    if "balance" in token and "decimals" in token:
                        decimals = int(token.get("decimals", 0))
                        formatted = format_balance(token["balance"], decimals)
                        token["formatted_balance"] = f"{formatted} {token.get('symbol', '')}".strip()
        
        logger.info(f"Account detail response: {result}")
        return str(result)
    except requests.RequestException as e:
        error_msg = f"Failed to get account detail: {str(e)}"
        logger.error(error_msg)
        return error_msg
