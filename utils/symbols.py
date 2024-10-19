# utils/symbols.py

import httpx
import pandas as pd
from cachetools import TTLCache
import logging
from typing import List
from io import StringIO
import asyncio

logger = logging.getLogger(__name__)

# Create a cache for symbols with a TTL of 24 hours (86400 seconds)
symbol_cache = TTLCache(maxsize=1, ttl=86400)

async def fetch_sp500_symbols() -> List[str]:
    """
    Fetch the list of S&P 500 stock symbols from Wikipedia.

    :return: List of stock symbols
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    logger.info("Fetching S&P 500 symbols from Wikipedia.")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            html_content = StringIO(response.text)
            tables = pd.read_html(html_content)
            df = tables[0]  # The first table typically contains the symbols
            symbols = df['Symbol'].tolist()
            # Clean symbols by replacing '.' with '-' to match yfinance formatting
            symbols = [symbol.replace('.', '-') for symbol in symbols]
            logger.info(f"Fetched and cleaned {len(symbols)} symbols.")
            return symbols
        except Exception as e:
            logger.error(f"Error fetching S&P 500 symbols: {e}")
            return []

async def get_sp500_symbols() -> List[str]:
    """
    Get and cache the list of S&P 500 stock symbols.

    :return: List of stock symbols
    """
    if 'symbols' not in symbol_cache:
        symbols = await fetch_sp500_symbols()
        symbol_cache['symbols'] = symbols
    return symbol_cache['symbols']

def is_valid_symbol(symbol: str) -> bool:
    """
    Validate if the provided symbol exists in the S&P 500 symbols list.

    :param symbol: Stock symbol to validate
    :return: True if valid, False otherwise
    """
    symbols = symbol_cache.get('symbols')
    if not symbols:
        # If cache miss, return True to allow the symbol (we'll validate it later)
        logger.warning("Symbol cache is empty. Cannot validate symbols accurately.")
        return True
    return symbol in symbols
