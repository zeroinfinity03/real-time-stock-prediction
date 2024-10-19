# utils/plotter.py

import plotly.graph_objects as go
import plotly.utils
import pandas as pd
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

def generate_chart(stock_data: Dict[str, Any], chart_type: str = 'candlestick', period: str = '1mo') -> str:
    # Convert historical_data to DataFrame
    df = pd.DataFrame(stock_data['historical_data'])
    df['Date'] = pd.to_datetime(df['Date'], utc=True)
    df.set_index('Date', inplace=True)
    
    fig = go.Figure()

    if chart_type == 'candlestick':
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ))
    elif chart_type == 'line':
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue')
        ))

    # Add volume bar chart
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        yaxis='y2',
        marker_color='rgba(0, 0, 255, 0.3)'
    ))

    # Update layout
    fig.update_layout(
        title=f"{stock_data['company_name']} ({stock_data['symbol']}) Stock Price",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        height=600,
        xaxis_title="Date",
        yaxis=dict(
            title="Price",
            side="left",
            showgrid=False
        ),
        showlegend=True,
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified'
    )

    # Update y-axes to not share the same position
    fig.update_layout(yaxis=dict(domain=[0.3, 1]), yaxis2=dict(domain=[0, 0.2]))

    # Add current price line
    fig.add_hline(
        y=stock_data['current_price'],
        line_color="red",
        line_dash="dash",
        annotation_text=f"Current Price: ${stock_data['current_price']:.2f}",
        annotation_position="bottom right"
    )

    # Convert the figure to JSON string
    chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_json

def generate_prediction_chart(prediction_data: Dict[str, Any], chart_type: str = 'line') -> str:
    logger.info(f"Generating prediction chart with {len(prediction_data['forecast_data'])} data points")
    
    df = pd.DataFrame(prediction_data['forecast_data'])
    df['Date'] = pd.to_datetime(df['Date'], utc=True)
    df.set_index('Date', inplace=True)
    
    fig = go.Figure()

    hover_template = (
        "<b>Date:</b> %{x}<br>"
        "<b>Predicted Price:</b> $%{y:.2f}<br>"
        "<b>Upper Bound:</b> $%{customdata[0]:.2f}<br>"
        "<b>Lower Bound:</b> $%{customdata[1]:.2f}<br>"
        "<b>Note:</b> Volume data not available for predictions"
    )

    if chart_type == 'line':
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Predicted Price',
            line=dict(color='blue'),
            hovertemplate=hover_template,
            customdata=df[['High', 'Low']].values
        ))

    # Add prediction interval
    fig.add_trace(go.Scatter(
        x=df.index.tolist() + df.index.tolist()[::-1],
        y=df['High'].tolist() + df['Low'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Prediction Interval',
        hoverinfo='skip'
    ))

    # Add last known price line if available
    if 'last_known_price' in prediction_data:
        fig.add_hline(
            y=prediction_data['last_known_price'],
            line_color="red",
            line_dash="dash",
            annotation_text=f"Last Known Price: ${prediction_data['last_known_price']:.2f}",
            annotation_position="bottom right"
        )

    fig.update_layout(
        title='Stock Price Forecast',
        yaxis_title='Price',
        xaxis_title='Date',
        height=600,
        xaxis_rangeslider_visible=False,
        yaxis=dict(
            title='Price',
            side='left',
            showgrid=False
        ),
        showlegend=True,
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified'
    )

    chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    logger.info("Prediction chart generated successfully")
    return chart_json
