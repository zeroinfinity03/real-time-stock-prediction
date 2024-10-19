# utils/schemas.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any


class StockDataRequest(BaseModel):
    symbol: str
    duration: str = Field(..., description="Duration of historical data", example="1mo")
    chart_style: str = Field(..., description="Chart style", example="candlestick")

    @validator('duration')
    def validate_duration(cls, v):
        allowed_durations = ['1d', '1w', '1m', '3m', '6m', '1y']
        if v not in allowed_durations:
            raise ValueError(f"Invalid duration. Must be one of {allowed_durations}")
        return v

    @validator('chart_style')
    def validate_chart_style(cls, v):
        allowed_styles = ['candlestick', 'line']
        if v not in allowed_styles:
            raise ValueError(f"Invalid chart style. Must be one of {allowed_styles}")
        return v


class StockData(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    change: Optional[float] = None
    change_percent: Optional[float] = None
    previous_close: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    historical_data: List[Dict[str, Any]]


class ForecastData(BaseModel):
    ds: str  # Date in ISO format, e.g., '2023-10-15'
    yhat: float  # Forecasted value
    yhat_lower: float  # Lower bound of the forecast
    yhat_upper: float  # Upper bound of the forecast


class Charts(BaseModel):
    main: str  # JSON string of the main chart
    prediction: Optional[str]  # JSON string of the prediction chart


class StockResponse(BaseModel):
    stock_data: Dict[str, Any]
    charts: Charts
    forecast: Optional[List[Dict[str, Any]]] = None
    sentiment_result: Optional[Dict[str, Any]] = None


class SymbolResponse(BaseModel):
    symbols: List[str]
