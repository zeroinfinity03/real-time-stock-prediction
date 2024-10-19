Real-Time Stock Analysis and Prediction Platform (RTSP)

Project Overview

RTSP is a sophisticated web application designed to empower investors and financial enthusiasts with real-time stock information, predictive analytics and sentiment-driven trend adjustments. This platform seamlessly integrates real-time financial data, historical performance analysis and the latest news sentiment, providing users with a holistic toolkit for informed decision-making.
Project Objectives

Real-Time Data Monitoring: Provide live stock prices and updates for user-selected stocks.
Predictive Analytics: Utilize historical data and advanced forecasting models to predict short-term stock trends.
Sentiment Analysis: Incorporate real-time news sentiment analysis to enhance and refine predictive models.
Data Visualization: Present data through interactive and intuitive visualizations for effortless interpretation.
Security Enhancements: Implement robust security measures to protect against API abuse and ensure data integrity.
Key Features

Interactive Stock Selection:
Dropdown and Search Functionality: Users can select stocks via a dropdown menu or by typing the stock symbol.
Accurate Symbol Retrieval: Stock symbols are fetched and cached from reliable sources (S&P 500 list from Wikipedia) using httpx.
Real-Time Data Visualization:
Dynamic Plotly Graphs: Upon stock selection, the application displays live stock data using Plotly graphs.
Customizable Graph Types: Users can choose between various graph types (e.g., candlestick, line).
Adjustable Time Frames: Users can customize the time frame for data visualization (e.g., 1 day, 1 week, 1 month).
Historical Data Analysis:
Comprehensive Data Retrieval: The application fetches and analyzes historical stock data using yfinance.
Trend and Pattern Identification: Utilizes historical data to identify trends, seasonality and other patterns.
Predictive Analytics:
Forecast Generation: A dedicated "Show Predictions" button triggers the display of a prediction chart.
Prophet Integration with CmdStanPy: Predictions are generated using Facebook's Prophet model with the cmdstanpy backend.
Visualization of Predictions: The prediction chart appears below the actual data chart for easy comparison.
Sentiment Analysis Integration:
Real-Time News Fetching: The application retrieves recent news articles related to the selected stock using the NewsData.io API.
FinBERT Analysis: Sentiment analysis is performed on these articles using FinBERT via Hugging Face models.
Sentiment-Driven Insights: Sentiment scores are utilized to adjust or contextualize the predictions made by Prophet.
User-Friendly Interface:
Intuitive Design: A clean and responsive design ensures seamless navigation and data interpretation.
Interactive Elements: Dropdown menus, search bars and customizable options enhance user interaction and engagement.
Security Measures:
Secure API Key Management: Utilizes environment variables managed by python-dotenv to securely store API keys.
Input Validation: Implements robust input validation mechanisms using Pydantic models.
Caching Mechanisms: Employs in-memory caching using cachetools.TTLCache to store frequently accessed data.
Technical Stack

Backend Framework: FastAPI
Frontend Framework: Jinja2 Templates
Data Sources:
Financial Data: yfinance
News Data: NewsData.io API
Prediction Models:
Time-Series Forecasting: Prophet with cmdstanpy backend
Sentiment Analysis: FinBERT (via Hugging Face)
Data Visualization: Plotly
Utilities:
Environment Management: python-dotenv
Concurrency: asyncio and httpx
Data Scraping: pandas
Caching: cachetools.TTLCache (in-memory caching)
Version Control: Git
Project Structure

RTSP/
│
├── main.py                        # FastAPI app initialization and route definitions
├── .env                           # Environment variables (API keys, etc.)
├── .gitignore                     # Ignore unnecessary files and folders (e.g., .env, venv)
├── requirements.txt               # List of dependencies
│
├── static/
│   └── app.js                     # JavaScript file for frontend interactivity
│
├── templates/
│   └── index.html                 # Main HTML template for displaying stock data
│
└── utils/                         # Utility functions to keep main.py clean
    ├── data_fetcher.py            # Fetches live stock data using yfinance with httpx
    ├── news_fetcher.py            # Retrieves news articles using NewsData.io API
    ├── sentiment_analysis.py      # Performs sentiment analysis with FinBERT and NewsAPI using httpx
    ├── prediction.py              # Time-series forecasting using Prophet
    ├── plotter.py                 # Generates Plotly charts for data visualization
    ├── symbols.py                 # Manages retrieval and caching of stock symbols using httpx
    └── schemas.py                 # Pydantic models for input validation
Implementation Workflow

Project Initialization and Environment Setup:
Initialize a Git repository.
Create and activate a virtual environment using venv.
Populate requirements.txt with necessary packages and install them using pip.
Configure environment variables securely using a .env file.
Stock Symbol Management:
Utilize pandas to scrape the list of S&P 500 companies from Wikipedia.
Implement in-memory caching using cachetools.TTLCache to store fetched symbols.
Backend API Development with FastAPI:
Initialize the FastAPI application instance.
Configure routing for various endpoints.
Employ asyncio and httpx to handle I/O-bound tasks efficiently.
Predictive Analytics and Sentiment Analysis:
Utilize the Prophet model with the cmdstanpy backend to generate future stock price predictions.
Perform sentiment analysis on recent news articles related to the selected stock.
Data Visualization:
Display live stock data using interactive Plotly charts.
Present forecasted stock trends alongside actual data for easy comparison.
User Interface Development:
Utilize Tailwind CSS to create a responsive and aesthetically pleasing user interface.
Incorporate search bars, dropdown menus and buttons to enhance user interaction.
Security Enhancements:
Store API keys and sensitive information in environment variables.
Implement robust input validation using Pydantic models.
Utilize cachetools.TTLCache to cache frequently accessed data.
Usage

Search for a Stock: Type a stock symbol into the search input.
Select a Stock: Click on a stock symbol from the list.
View Data and Charts: The stock information populates in the stockDetails section, and Plotly charts render in their respective <div> elements.
Show Predictions: Click the "Show Predictions" button to display the predicted stock trends.
Combine Sentiment Analysis: Click the "Combine Sentiment Analysis" button to integrate sentiment data with your predictions.
Error Handling

Invalid Symbol: An error alert notifies the user if an invalid symbol is submitted.
Sentiment Analysis Timeout: A warning is logged if sentiment analysis does not complete within the specified timeout.
API Failures: Robust error handling mechanisms are in place to manage failures in external API calls.
Requirements

Ensure your requirements.txt includes all necessary dependencies:
fastapi
python-dotenv
jinja2
uvicorn
plotly
prophet[cmdstanpy]
transformers
torch
requests
yfinance
cachetools
pandas
httpx
Additional Notes

In-Memory Caching: The application employs in-memory caching using cachetools.TTLCache for stock symbols, general stock data and sentiment results.
Background Tasks: Sentiment analysis is performed as a background task to prevent blocking the main application flow.
Logging: Comprehensive logging is implemented across all modules to facilitate debugging and monitoring.
Scalability: The modular project structure and efficient use of asynchronous programming paradigms position RTSP for scalability and easy maintenance.
Future Enhancements

Persistent Caching: Implement a persistent caching mechanism using databases like Redis or file-based caches.
Enhanced Security: Integrate additional security measures such as authentication, authorization and rate limiting.
Expanded Data Sources: Incorporate more diverse data sources to enrich the analysis and prediction capabilities of the platform.
