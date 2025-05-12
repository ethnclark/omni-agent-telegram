import os
import requests
import logging
from typing import Annotated, Literal
from dotenv import load_dotenv
from langchain_core.tools import tool

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

@tool
def create_nft(
    name: Annotated[str, "The name of the NFT"],
    description: Annotated[str, "A description of the NFT"],
    url: Annotated[str, "URL to the NFT's image or media"],
    network: Annotated[Literal["mainnet", "testnet", "devnet"], "The network to create the NFT on"],
    user_id: Annotated[str, "The Telegram user ID of the NFT creator"]
) -> str:
    """
    Create a new NFT on the Sui blockchain
    
    Args:
        name (str): The name of the NFT
        description (str): A description of the NFT
        url (str): URL to the NFT's image or media
        network (str): The network to create the NFT on (mainnet/testnet/devnet)
        user_id (str): The Telegram user ID of the NFT creator
        
    Returns:
        str: The response from the API
    """
    try:
        if not network:
            return "Network parameter is required. Please specify 'mainnet', 'testnet', or 'devnet'."

        if network not in ["mainnet", "testnet", "devnet"]:
            return "Invalid network. Please choose 'mainnet', 'testnet', or 'devnet'."

        api_url = f"{os.getenv('API_RELAYER_URL')}/api/sui/nft"
        payload = {
            "name": name,
            "description": description,
            "url": url,
            "network": network,
            "user_id": user_id
        }
        
        logger.info(f"Creating NFT on {network} with payload: {payload}")
        
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"NFT creation response: {result}")
        
        return str(result)
        
    except requests.RequestException as e:
        error_msg = f"Failed to create NFT on {network}: {str(e)}"
        logger.error(error_msg)
        return error_msg 