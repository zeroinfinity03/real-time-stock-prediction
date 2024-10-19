# utils/sentiment_analysis.py

import httpx
import os
import logging
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Initialize FinBERT model and tokenizer globally to avoid re-loading on each call
MODEL_NAME = "yiyanghkust/finbert-tone"
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    logger.info(f"FinBERT model and tokenizer loaded successfully from {MODEL_NAME}.")
except Exception as e:
    logger.error(f"Error loading FinBERT model/tokenizer: {e}")
    tokenizer = None
    model = None

async def fetch_news_headlines(symbol: str) -> List[str]:
    """
    Fetch news headlines related to the stock symbol using NewsAPI asynchronously.

    :param symbol: Stock symbol (e.g., 'AAPL')
    :return: List of news headlines
    """
    logger.info(f"Fetching news headlines for symbol: {symbol}")
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        logger.error("NEWSAPI_KEY not found in environment variables.")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": symbol,
        "apiKey": api_key,
        "language": "en",
        "pageSize": 10,  # Number of articles to fetch
        "sortBy": "publishedAt"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "ok":
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
            articles = data.get("articles", [])
            headlines = [article["title"] for article in articles if article.get("title")]
            logger.info(f"Fetched {len(headlines)} headlines for symbol: {symbol}")
            return headlines
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error while fetching news: {exc.response.status_code} - {exc.response.text}")
        except httpx.RequestError as exc:
            logger.error(f"Request error while fetching news: {exc}")
        except Exception as e:
            logger.error(f"Unexpected error while fetching news: {e}")
    return []

def preprocess_text(text: str) -> str:
    """Preprocess the input text."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    logger.debug(f"Preprocessed text: {text[:50]}...")  # Log first 50 characters
    return text

def analyze_sentiment(texts: List[str]) -> List[Dict[str, float]]:
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt", max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
    labels = ['neutral', 'positive', 'negative']
    
    results = []
    for score in scores:
        sentiment_scores = {label: score[i].item() for i, label in enumerate(labels)}
        results.append(sentiment_scores)
    
    return results

def get_overall_sentiment(articles: List[Dict[str, str]]) -> Dict[str, Any]:
    logger.info(f"Calculating overall sentiment for {len(articles)} articles")
    if not articles:
        logger.warning("No articles provided for sentiment analysis")
        return {
            "score": 0.0,
            "label": "Neutral",
            "confidence": 0.0,
            "details": {
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0
            }
        }
    
    texts = [f"{article.get('title', '')} {article.get('description', '')}".strip() for article in articles]
    logger.debug(f"First article text: {texts[0][:100]}...")  # Log first 100 characters of the first article
    
    sentiments = analyze_sentiment(texts)
    
    weighted_scores = []
    for sentiment in sentiments:
        score = sentiment['positive'] - sentiment['negative']
        confidence = max(sentiment.values())
        weighted_scores.append(score * confidence)
    
    overall_score = sum(weighted_scores) / len(weighted_scores)
    
    if overall_score > 0.1:
        label = "Positive"
    elif overall_score < -0.1:
        label = "Negative"
    else:
        label = "Neutral"
    
    avg_positive = sum(s['positive'] for s in sentiments) / len(sentiments)
    avg_negative = sum(s['negative'] for s in sentiments) / len(sentiments)
    avg_neutral = sum(s['neutral'] for s in sentiments) / len(sentiments)
    
    result = {
        "score": float(overall_score),
        "label": label,
        "confidence": float(max(avg_positive, avg_negative, avg_neutral)),
        "details": {
            "positive": float(avg_positive),
            "negative": float(avg_negative),
            "neutral": float(avg_neutral)
        }
    }
    
    logger.info(f"Overall sentiment result: {result}")
    return result

async def get_stock_sentiment(symbol: str) -> float:
    """
    Perform sentiment analysis on news related to the stock symbol using FinBERT.

    :param symbol: Stock symbol (e.g., 'AAPL')
    :return: Aggregated sentiment score (float between -1 and 1)
    """
    logger.info(f"Performing sentiment analysis for symbol: {symbol}")
    try:
        # Fetch news headlines related to the stock symbol
        news_headlines = await fetch_news_headlines(symbol)

        if not news_headlines:
            logger.warning(f"No news headlines found for symbol: {symbol}")
            return 0.0  # Neutral sentiment if no news

        # Analyze sentiment for each headline
        sentiments = []
        for headline in news_headlines:
            sentiment = analyze_sentiment([headline])[0]
            sentiments.append(sentiment)

        if not sentiments:
            logger.warning(f"No sentiments calculated for symbol: {symbol}")
            return 0.0

        # Aggregate sentiment scores
        average_sentiment = sum(sentiment['positive'] for sentiment in sentiments) / len(sentiments)
        logger.info(f"Aggregated sentiment score for {symbol}: {average_sentiment}")
        return average_sentiment
    except Exception as e:
        logger.error(f"Error performing sentiment analysis for {symbol}: {e}")
        return 0.0
