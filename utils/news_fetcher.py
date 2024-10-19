import requests
import os
from typing import List, Dict
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get the API key
NEWSDATA_API_KEY = os.getenv('NEWSDATA_API_KEY')

def fetch_news(symbol: str, company_name: str) -> List[Dict]:
    """
    Fetch news articles related to the given company name.

    :param symbol: Stock symbol (e.g., 'AAPL') - used for logging purposes
    :param company_name: Company name (e.g., 'Apple Inc.')
    :return: List of dictionaries containing news articles
    """
    if not NEWSDATA_API_KEY:
        logger.error("NEWSDATA_API_KEY is not set in the environment variables")
        return []

    url = "https://newsdata.io/api/1/news"
    
    params = {
        'apikey': NEWSDATA_API_KEY,
        'q': f'"{company_name}"',  # Use only company name in quotes for exact matching
        'language': 'en',
        'category': 'business',
        'size': 10
    }
    
    logger.info(f"Fetching news for company: {company_name} (symbol: {symbol})")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        news_data = response.json()
        
        articles = news_data.get('results', [])
        logger.info(f"Fetched {len(articles)} news articles for {company_name}")
        
        # Ensure all required fields are present
        processed_articles = []
        for article in articles:
            if article.get('title') and article.get('description'):
                processed_articles.append({
                    'title': article['title'],
                    'description': article['description']
                })
            else:
                logger.warning(f"Skipping article due to missing title or description: {article}")
        
        return processed_articles
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching news for {company_name}: {e}")
        logger.error(f"Response content: {e.response.content}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching news for {company_name}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching news for {company_name}: {str(e)}")
        return []
