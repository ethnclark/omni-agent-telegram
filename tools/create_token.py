import requests
import logging
import json
from typing import Annotated, Literal, Optional
from langchain_core.tools import tool

# Set up logging
logger = logging.getLogger(__name__)

@tool
def create_token(
    name: Annotated[str, "The name of the token"],
    symbol: Annotated[str, "The symbol of the token (e.g., BTC, ETH)"],
    description: Annotated[str, "A description of the token and its purpose"],
    image_url: Annotated[str, "URL to the token's image or logo"],
    init_supply: Annotated[int, "The initial supply of the token"],
    network: Annotated[Literal["mainnet", "testnet", "devnet"], "The network to create the token on"],
    user_id: Annotated[str, "Telegram user ID of the token creator"],
    twitter: Annotated[Optional[str], "Twitter handle or URL for the token"] = "",
    telegram: Annotated[Optional[str], "Telegram group/channel URL for the token"] = "",
    website: Annotated[Optional[str], "Official website URL for the token"] = "",
    uri: Annotated[Optional[str], "Additional URI for token metadata"] = ""
) -> str:
    """
    Create a new token on the Sui blockchain
    
    Args:
        name (str): The name of the token
        symbol (str): The symbol of the token
        description (str): A description of the token
        image_url (str): URL to the token's image
        init_supply (int): The initial supply of the token
        network (str): The network to create the token on (mainnet/testnet/devnet)
        user_id (str): Telegram user ID of the token creator
        twitter (str, optional): Twitter handle or URL for the token
        telegram (str, optional): Telegram group/channel URL for the token
        website (str, optional): Official website URL for the token
        uri (str, optional): Additional URI for token metadata
        
    Returns:
        str: The response from the API
    """
    try:
        api_url = "http://localhost:7777/api/sui/token"
        payload = {
            "name": name,
            "symbol": symbol,
            "description": description,
            "image_url": image_url,
            "init_supply": init_supply,
            "network": network,
            "twitter": twitter,
            "telegram": telegram,
            "website": website,
            "uri": uri,
            "user_id": user_id
        }
        
        logger.info(f"Creating token on {network} with payload: {payload}")
        
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Token creation response: {result}")
        
        return str(result)
        
    except requests.RequestException as e:
        error_msg = f"Failed to create token on {network}: {str(e)}"
        logger.error(error_msg)
        return error_msg
