# utils/prediction.py

from typing import List, Dict, Any
import pandas as pd
from prophet import Prophet
import logging
from datetime import timedelta
from utils.news_fetcher import fetch_news
from utils.sentiment_analysis import get_overall_sentiment

logger = logging.getLogger(__name__)

# Original predict_stock_price function
def predict_stock_price(full_year_data: List[Dict[str, Any]], forecast_period: str) -> Dict[str, Any]:
    """
    Generate future stock price predictions using Prophet.

    :param full_year_data: List of dictionaries containing 1 year of historical stock data
    :param forecast_period: String indicating the forecast period (e.g., '1d', '1w', '1m', '3m', '6m')
    :return: Dictionary containing forecasted data
    """
    logger.info(f"Starting prediction with {len(full_year_data)} historical data points for period: {forecast_period}")
    try:
        # Prepare data for Prophet
        df = pd.DataFrame(full_year_data)
        df['ds'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
        df['y'] = df['Close'].astype(float)
        
        # Initialize and fit the Prophet model
        model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=True)
        model.fit(df)
        
        # Determine forecast parameters based on the period
        if forecast_period == '1d':
            periods = 288  # 5-minute intervals for 1 day (288 * 5 minutes = 24 hours)
            freq = '5min'
        elif forecast_period == '1w':
            periods = 672  # 15-minute intervals for 1 week (672 * 15 minutes = 7 days)
            freq = '15min'
        elif forecast_period == '1m':
            periods = 720  # 1-hour intervals for 1 month (720 * 1 hour ≈ 30 days)
            freq = 'H'
        elif forecast_period == '3m':
            periods = 90  # Daily intervals for 3 months
            freq = 'D'
        elif forecast_period == '6m':
            periods = 180  # Daily intervals for 6 months
            freq = 'D'
        else:
            raise ValueError(f"Unsupported forecast period: {forecast_period}")

        # Create future dates for forecasting
        future = model.make_future_dataframe(periods=periods, freq=freq)
        
        # Make predictions
        forecast = model.predict(future)
        
        # Prepare the forecast data (only for the future dates)
        last_historical_date = df['ds'].max()
        forecast_data = forecast[forecast['ds'] > last_historical_date][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records')
        
        # Prepare data for Plotly
        plotly_data = []
        for i, row in enumerate(forecast_data):
            plotly_data.append({
                'Date': row['ds'].isoformat(),
                'Open': forecast_data[max(0, i-1)]['yhat'],  # Use previous prediction as Open
                'High': row['yhat_upper'],
                'Low': row['yhat_lower'],
                'Close': row['yhat'],
                'Volume': None  # Prophet doesn't predict volume
            })
        
        logger.info(f"Generated forecast: {len(plotly_data)} data points")
        
        return {
            "forecast_data": plotly_data
        }
    except Exception as e:
        logger.error(f"Error in predict_stock_price: {str(e)}")
        return None

# New function for sentiment-adjusted predictions
def predict_stock_price_with_sentiment(full_year_data: List[Dict[str, Any]], forecast_period: str, symbol: str, company_name: str, sentiment_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate future stock price predictions using Prophet and adjust based on sentiment analysis.

    :param full_year_data: List of dictionaries containing 1 year of historical stock data
    :param forecast_period: String indicating the forecast period (e.g., '1d', '1w', '1m', '3m', '6m')
    :param symbol: Stock symbol
    :param company_name: Company name
    :param sentiment_result: Sentiment analysis result
    :return: Dictionary containing forecasted data and sentiment information
    """
    # First, get the base prediction
    prediction_data = predict_stock_price(full_year_data, forecast_period)
    
    if sentiment_result:
        # Adjust predictions based on sentiment
        adjustment_factor = 1 + (sentiment_result['score'] * 0.01)  # 1% adjustment per sentiment unit
        
        adjusted_forecast = []
        for data in prediction_data['forecast_data']:
            adjusted_data = data.copy()
            adjusted_data['Close'] *= adjustment_factor
            adjusted_data['High'] *= adjustment_factor
            adjusted_data['Low'] *= adjustment_factor
            adjusted_data['Open'] *= adjustment_factor
            adjusted_forecast.append(adjusted_data)
        
        prediction_data['forecast_data'] = adjusted_forecast
        prediction_data['sentiment_result'] = sentiment_result
    
    return prediction_data
