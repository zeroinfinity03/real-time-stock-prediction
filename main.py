# main.py
from fastapi import FastAPI, Request, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
import asyncio
import time
from cachetools import TTLCache

from utils.data_fetcher import fetch_stock_data, fetch_year_data_for_prediction
from utils.prediction import predict_stock_price, predict_stock_price_with_sentiment
# from utils.sentiment_analysis import get_stock_sentiment  # Not implemented yet
from utils.plotter import generate_chart, generate_prediction_chart
from utils.symbols import get_sp500_symbols, is_valid_symbol
from utils.news_fetcher import fetch_news
from utils.sentiment_analysis import get_overall_sentiment

from utils.schemas import StockDataRequest, StockResponse, SymbolResponse

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/symbols", response_model=SymbolResponse)
async def get_symbols(request: Request):
    symbols = await get_sp500_symbols()
    if not symbols:
        raise HTTPException(status_code=500, detail="Unable to fetch stock symbols.")
    return SymbolResponse(symbols=symbols)

# Create a cache for sentiment results (1-hour TTL)
sentiment_cache = TTLCache(maxsize=100, ttl=3600)

@app.post("/api/get_stock_data", response_model=StockResponse)
async def get_stock_data(
    request: Request,
    payload: StockDataRequest,
    background_tasks: BackgroundTasks,
    include_prediction: bool = Query(False, description="Include prediction data"),
    include_sentiment: bool = Query(False, description="Include sentiment analysis")
):
    try:
        symbol = payload.symbol.upper()
        duration = payload.duration
        chart_style = payload.chart_style
        
        logger.info(f"Requested stock symbol: {symbol}, period: {duration}, include_prediction: {include_prediction}, include_sentiment: {include_sentiment}")

        if not is_valid_symbol(symbol):
            raise HTTPException(status_code=400, detail="Invalid stock symbol.")

        loop = asyncio.get_event_loop()
        stock_data = await loop.run_in_executor(None, fetch_stock_data, symbol, duration)
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock data not found for symbol: {symbol}")

        main_chart = generate_chart(stock_data, chart_style, duration)

        # Start sentiment analysis in the background if not already cached
        if symbol not in sentiment_cache:
            background_tasks.add_task(update_sentiment, symbol, stock_data['company_name'])

        prediction_chart = None
        forecast = None
        sentiment_result = None
        if include_prediction:
            year_data = await loop.run_in_executor(None, fetch_year_data_for_prediction, symbol)
            
            if include_sentiment:
                # Wait for sentiment analysis to complete if it's still running
                sentiment_result = await wait_for_sentiment(symbol)
                prediction_data = predict_stock_price_with_sentiment(year_data, duration, symbol, stock_data['company_name'], sentiment_result)
            else:
                prediction_data = predict_stock_price(year_data, duration)
            
            if prediction_data:
                prediction_chart = generate_prediction_chart(prediction_data, chart_style)
                forecast = prediction_data['forecast_data']

        response = StockResponse(
            stock_data=stock_data,
            charts={
                "main": main_chart,
                "prediction": prediction_chart
            },
            forecast=forecast,
            sentiment_result=sentiment_result if include_sentiment else None
        )

        return response
    except Exception as e:
        logger.error(f"Unexpected error in get_stock_data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

async def update_sentiment(symbol: str, company_name: str):
    articles = fetch_news(symbol, company_name)
    sentiment_result = get_overall_sentiment(articles) if articles else None
    if sentiment_result:
        sentiment_cache[symbol] = sentiment_result

async def wait_for_sentiment(symbol: str, timeout: int = 10):
    start_time = time.time()
    while symbol not in sentiment_cache:
        if time.time() - start_time > timeout:
            logger.warning(f"Sentiment analysis timeout for {symbol}")
            return None
        await asyncio.sleep(0.5)
    return sentiment_cache[symbol]

def get_forecast_period(duration: str) -> int:
    duration_map = {
        "1d": 1,
        "1w": 7,
        "1m": 30,
        "3m": 90,
        "6m": 180
    }
    return duration_map.get(duration, 30)
