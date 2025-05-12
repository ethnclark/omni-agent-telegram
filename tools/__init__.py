"""
Tools package for the Omni Agent.
This package contains various tools that can be used by the agent.
"""

from .web_search import search_web
from .get_price_token import get_token_price
from .create_token import create_token
from .create_account import create_account
from .get_account import get_account, get_account_detail
from .get_news import get_news
from .switch_account import switch_account
from .create_nft import create_nft

__all__ = [
    'search_web',
    'get_token_price',
    'create_token',
    'create_account',
    'get_account',
    'get_account_detail',
    'get_news',
    'switch_account',
    'create_nft'
] 