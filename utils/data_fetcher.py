# utils/data_fetcher.py

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
import logging
from cachetools import TTLCache, cached
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache for general stock data (5 minutes TTL)
stock_data_cache = TTLCache(maxsize=100, ttl=300)

# Cache for 1-year historical data (1 hour TTL)
year_data_cache = TTLCache(maxsize=100, ttl=3600)

def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

@cached(stock_data_cache)
def fetch_stock_data(symbol: str, period: str = "1d") -> Optional[Dict[str, Any]]:
    logger.info(f"Fetching stock data for symbol: {symbol}, period: {period}")
    try:
        stock = yf.Ticker(symbol)
        end_date = datetime.now()

        # Adjust interval and start date based on period
        if period == "1d":
            start_date = end_date - timedelta(days=1)
            interval = "5m"
        elif period == "1w":
            start_date = end_date - timedelta(weeks=1)
            interval = "15m"
        elif period == "1m":
            start_date = end_date - timedelta(days=30)
            interval = "1h"
        elif period == "3m":
            start_date = end_date - timedelta(days=90)
            interval = "1d"
        elif period == "6m":
            start_date = end_date - timedelta(days=180)
            interval = "1d"
        else:  # Default to 1d
            start_date = end_date - timedelta(days=1)
            interval = "5m"

        # Fetch historical data
        hist = stock.history(start=start_date, end=end_date, interval=interval)
        
        logger.info(f"Fetched data shape: {hist.shape}")
        logger.info(f"Date range: from {hist.index.min()} to {hist.index.max()}")
        logger.info(f"Number of unique dates: {hist.index.nunique()}")
        logger.info(f"Data points: {len(hist)}")
        logger.info(f"Columns: {hist.columns}")
        logger.info(f"First few rows:\n{hist.head()}")
        logger.info(f"Last few rows:\n{hist.tail()}")
        
        info = stock.info

        historical_data = []
        for date, row in hist.iterrows():
            historical_data.append({
                "Date": date.isoformat(),
                "Open": convert_numpy_types(row['Open']),
                "High": convert_numpy_types(row['High']),
                "Low": convert_numpy_types(row['Low']),
                "Close": convert_numpy_types(row['Close']),
                "Volume": convert_numpy_types(row['Volume'])
            })

        previous_close = convert_numpy_types(hist['Close'].iloc[-2] if len(hist) > 1 else None)
        current_price = convert_numpy_types(hist['Close'].iloc[-1])
        change = convert_numpy_types(current_price - previous_close if previous_close is not None else None)
        change_percent = convert_numpy_types((change / previous_close * 100) if previous_close is not None and previous_close != 0 else None)

        # Fetch 1-year data separately and cache it
        full_year_data = fetch_year_data(symbol)
        
        data = {
            "symbol": symbol,
            "company_name": info.get('longName', 'N/A'),
            "current_price": current_price,
            "change": change,
            "change_percent": change_percent,
            "previous_close": previous_close,
            "open": convert_numpy_types(hist['Open'].iloc[-1]),
            "high": convert_numpy_types(hist['High'].iloc[-1]),
            "low": convert_numpy_types(hist['Low'].iloc[-1]),
            "volume": convert_numpy_types(hist['Volume'].iloc[-1]),
            "market_cap": convert_numpy_types(info.get('marketCap', 'N/A')),
            "pe_ratio": convert_numpy_types(info.get('trailingPE', 'N/A')),
            "dividend_yield": convert_numpy_types(info.get('dividendYield', 'N/A')),
            "fifty_two_week_high": convert_numpy_types(info.get('fiftyTwoWeekHigh', 'N/A')),
            "fifty_two_week_low": convert_numpy_types(info.get('fiftyTwoWeekLow', 'N/A')),
            "historical_data": historical_data,
            "full_year_data": full_year_data
        }
        
        logger.info(f"Successfully fetched data for symbol: {symbol}")
        return data
    except Exception as e:
        logger.error(f"Error fetching data for symbol {symbol}: {e}")
        return None

@cached(year_data_cache)
def fetch_year_data(symbol: str) -> List[Dict[str, Any]]:
    logger.info(f"Fetching 1-year data for symbol: {symbol}")
    try:
        stock = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        hist = stock.history(start=start_date, end=end_date, interval="1d")
        
        return [
            {
                "Date": date.isoformat(),
                "Open": convert_numpy_types(row['Open']),
                "High": convert_numpy_types(row['High']),
                "Low": convert_numpy_types(row['Low']),
                "Close": convert_numpy_types(row['Close']),
                "Volume": convert_numpy_types(row['Volume'])
            }
            for date, row in hist.iterrows()
        ]
    except Exception as e:
        logger.error(f"Error fetching 1-year data for symbol {symbol}: {e}")
        return []

@cached(year_data_cache)
def fetch_year_data_for_prediction(symbol: str) -> List[Dict[str, Any]]:
    logger.info(f"Fetching 1-year data for prediction, symbol: {symbol}")
    try:
        stock = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        hist = stock.history(start=start_date, end=end_date, interval="1d")
        
        return [
            {
                "Date": date.isoformat(),
                "Close": convert_numpy_types(row['Close'])
            }
            for date, row in hist.iterrows()
        ]
    except Exception as e:
        logger.error(f"Error fetching 1-year data for symbol {symbol}: {e}")
        return []
