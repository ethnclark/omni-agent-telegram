import os
import logging
import aiohttp
from typing import Annotated, Literal
from dotenv import load_dotenv
from langchain_core.tools import tool

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

@tool
async def switch_account(
    user_id: Annotated[int, "The Telegram user ID"],
    address: Annotated[str, "The Sui wallet address to switch to"],
    network: Annotated[Literal["mainnet", "testnet", "devnet"], "The network to switch to"]
) -> str:
    """
    Switch the active address for a user
    
    Args:
        user_id (int): The Telegram user ID
        address (str): The Sui wallet address to switch to
        network (str): The network (mainnet, testnet, or devnet)
        
    Returns:
        str: The result of the switch operation
    """
    try:
        # Validate network
        if network not in ["mainnet", "testnet", "devnet"]:
            return "Invalid network. Please use 'mainnet', 'testnet', or 'devnet'."
        
        # Prepare request data
        data = {
            "user_id": user_id,
            "address": address,
            "network": network
        }
        
        api_url = os.getenv('API_RELAYER_URL')
        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{api_url}/api/sui/account/switch", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return str({
                        "status": "success",
                        "message": "Successfully switched active address",
                        "data": result
                    })
                else:
                    error_data = await response.json()
                    return str({
                        "status": "error",
                        "error": error_data.get("error", "Failed to switch active address")
                    })
                    
    except Exception as e:
        error_msg = f"Failed to switch active address: {str(e)}"
        logger.error(error_msg)
        return error_msg 