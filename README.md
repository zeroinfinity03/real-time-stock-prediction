
# Real-Time Stock Analysis and Prediction Platform (RTSP)

![Project Logo](https://via.placeholder.com/150) <!-- Replace with your project logo if available -->

## Table of Contents

- [Project Summary](#project-summary)
- [Project Objectives](#project-objectives)
- [Key Features](#key-features)
- [Technical Stack](#technical-stack)
- [Project Structure](#project-structure)
- [Implementation Workflow](#implementation-workflow)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Error Handling](#error-handling)
- [Requirements](#requirements)
- [Additional Notes](#additional-notes)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## Project Summary

The **Real-Time Stock Analysis and Prediction Platform (RTSP)** is a sophisticated web application designed to empower investors and financial enthusiasts with up-to-the-minute stock information, predictive analytics, and sentiment-driven trend adjustments. By seamlessly integrating real-time financial data, historical performance analysis, and the latest news sentiment, RTSP provides users with a holistic toolkit for informed decision-making. Leveraging **FastAPI** for backend efficiency and **Jinja2** for dynamic frontend rendering, the platform ensures a responsive, secure, and user-centric experience.

## Project Objectives

1. **Real-Time Data Monitoring**: Provide live stock prices and updates for user-selected stocks.
2. **Predictive Analytics**: Utilize historical data and advanced forecasting models to predict short-term stock trends.
3. **Sentiment Analysis**: Incorporate real-time news sentiment analysis to enhance and refine predictive models.
4. **Data Visualization**: Present data through interactive and intuitive visualizations for effortless interpretation.
5. **Security Enhancements**: Implement robust security measures to protect against API abuse and ensure data integrity.

## Key Features

### 1. Interactive Stock Selection
- **Dropdown and Search Functionality**: Users can select stocks via a dropdown menu or by typing the stock symbol. The dropdown dynamically filters to display matching stocks as users input text.
- **Accurate Symbol Retrieval**: Stock symbols are fetched and cached from reliable sources (S&P 500 list from Wikipedia) using `httpx`, ensuring accuracy and minimizing redundant requests.

### 2. Real-Time Data Visualization
- **Dynamic Plotly Graphs**: Upon stock selection, the application displays live stock data using Plotly graphs.
- **Customizable Graph Types**: Users can choose between various graph types (e.g., candlestick, line) to view data in their preferred format.
- **Adjustable Time Frames**: Users can customize the time frame for data visualization (e.g., 1 day, 1 week, 1 month, 3 months, 6 months), enabling tailored analysis.

### 3. Historical Data Analysis
- **Comprehensive Data Retrieval**: The application fetches and analyzes historical stock data using `yfinance`, providing insights into past performance.
- **Trend and Pattern Identification**: Utilizes historical data to identify trends, seasonality, and other patterns crucial for accurate predictions.

### 4. Predictive Analytics
- **Forecast Generation**: A dedicated "Show Predictions" button triggers the display of a prediction chart.
- **Prophet Integration with CmdStanPy**: Predictions are generated using Facebook's Prophet model with the `cmdstanpy` backend, known for its efficiency and compatibility.
- **Visualization of Predictions**: The prediction chart appears below the actual data chart for easy comparison, with options to select different graph types and time frames.

### 5. Sentiment Analysis Integration
- **Real-Time News Fetching**: The application retrieves recent news articles related to the selected stock using the NewsData.io API.
- **FinBERT Analysis**: Sentiment analysis is performed on these articles using FinBERT via Hugging Face models.
- **Sentiment-Driven Insights**: Sentiment scores are utilized to adjust or contextualize the predictions made by Prophet, offering a nuanced understanding of market trends.
- **Background Processing**: Sentiment analysis tasks are handled asynchronously in the background to ensure a smooth user experience without blocking main operations.

### 6. User-Friendly Interface
- **Intuitive Design**: A clean and responsive design ensures seamless navigation and data interpretation.
- **Interactive Elements**: Dropdown menus, search bars, and customizable options enhance user interaction and engagement.
- **Responsive Layout**: Compatibility across various devices and screen sizes ensures accessibility and convenience.

### 7. Security Measures
- **Secure API Key Management**: Utilizes environment variables managed by `python-dotenv` to securely store API keys, preventing unauthorized access.
- **Input Validation**: Implements robust input validation mechanisms using Pydantic models in `schemas.py` to ensure that only valid stock symbols and parameters are processed, mitigating potential security vulnerabilities.
- **Caching Mechanisms**: Employs in-memory caching using `cachetools.TTLCache` to store frequently accessed data (e.g., stock symbols, stock data, sentiment results), enhancing performance while reducing the risk of API abuse.

## Technical Stack

- **Backend Framework**: FastAPI
- **Frontend Framework**: Jinja2 Templates
- **Data Sources**:
  - **Financial Data**: yfinance
  - **News Data**: NewsData.io API
- **Prediction Models**:
  - **Time-Series Forecasting**: Prophet with cmdstanpy backend
  - **Sentiment Analysis**: FinBERT (via Hugging Face)
- **Data Visualization**: Plotly
- **Utilities**:
  - **Environment Management**: python-dotenv
  - **Concurrency**: asyncio and httpx
  - **Data Scraping**: pandas
  - **Caching**: cachetools.TTLCache (in-memory caching)
  - **Version Control**: Git

## Project Structure

Maintain a clean and modular codebase by organizing your project directory (`RTSP/`) as follows:

```
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
```

> **Note**: The `data/` folder is not used for caching in this implementation. All caching is handled in-memory using `cachetools.TTLCache`.

## Implementation Workflow

### 1. Project Initialization and Environment Setup
- **Version Control**: Initialize a Git repository to manage the project’s codebase and track changes.
  ```bash
  git init
  ```
- **Virtual Environment**: Create and activate a virtual environment using `venv` to isolate project dependencies.
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```
- **Dependency Management**: Populate `requirements.txt` with all necessary packages and install them using pip.
  ```bash
  pip install -r requirements.txt
  ```
- **Environment Variables**: Configure environment variables securely using a `.env` file managed by `python-dotenv`.
  ```env
  # .env
  NEWSAPI_API_KEY=your_newsapi_key
  # Add other necessary environment variables
  ```

### 2. Stock Symbol Management
- **Fetching Symbols**: Utilize `pandas` to scrape the list of S&P 500 companies from Wikipedia.
  - Use `pandas.read_html` to extract the table of S&P 500 companies.
  - Extract the 'Symbol' column and clean the symbols by replacing periods with dashes to match yfinance formatting (e.g., BRK.B to BRK-B).
- **Caching Mechanism**: Implement in-memory caching using `cachetools.TTLCache` to store fetched symbols for 24 hours, reducing redundant web scraping and enhancing performance.
- **Utility Development**: Develop `symbols.py` within the `utils/` directory to handle the retrieval and caching logic for stock symbols using `httpx` for asynchronous requests.

### 3. Backend API Development with FastAPI
- **Application Setup**: Initialize the FastAPI application instance in `main.py` and configure routing for various endpoints.
- **Endpoint Creation**:
  - **`/` (GET)**: Serves the main dashboard page (`index.html`) using Jinja2 templates.
  - **`/api/symbols` (GET)**: Provides a list of valid stock symbols for frontend consumption.
  - **`/api/get_stock_data` (POST)**: Fetches live and historical stock data, generates predictions and sentiment analysis, and serves Plotly visualizations.
- **Concurrency Management**: Employ `asyncio` and `httpx` to handle I/O-bound tasks efficiently, ensuring the application remains responsive.
- **Chart Generation**: Utilize `plotter.py` within the `utils/` directory to generate Plotly charts, which are serialized into JSON and sent to the frontend for rendering.

### 4. Predictive Analytics and Sentiment Analysis
- **Forecast Generation**: Utilize the Prophet model with the `cmdstanpy` backend to generate future stock price predictions based on historical data.
- **Sentiment Analysis Integration**: Perform sentiment analysis on recent news articles related to the selected stock using FinBERT via Hugging Face models. Sentiment scores are used to adjust the predictions, providing a more comprehensive market trend analysis.
- **Background Processing**: Implement background tasks using FastAPI's `BackgroundTasks` to handle sentiment analysis asynchronously, ensuring that the main application flow remains unaffected.

### 5. Data Visualization
- **Main Chart**: Display live stock data using interactive Plotly charts, allowing users to choose between candlestick and line graph types.
- **Prediction Chart**: Present forecasted stock trends alongside actual data for easy comparison, with options to customize graph types and time frames.

### 6. User Interface Development
- **Responsive Design**: Utilize Tailwind CSS to create a responsive and aesthetically pleasing user interface that adapts seamlessly across various devices and screen sizes.
- **Interactive Elements**: Incorporate search bars, dropdown menus, and buttons to enhance user interaction and engagement.
- **Dynamic Content Rendering**: Use JavaScript (`app.js`) to handle frontend interactivity, including fetching data from the backend, rendering charts, and displaying sentiment analysis results.

### 7. Security Enhancements
- **Secure API Key Management**: Store API keys and sensitive information in environment variables managed by `python-dotenv`, preventing exposure of credentials in the codebase.
- **Input Validation**: Implement robust input validation using Pydantic models defined in `schemas.py` to ensure that only valid stock symbols and parameters are processed, safeguarding against potential security vulnerabilities.
- **Caching and Rate Limiting**: Utilize `cachetools.TTLCache` to cache frequently accessed data (e.g., stock symbols, stock data, sentiment results), reducing the number of external API calls and minimizing the risk of exceeding rate limits.

### 8. Running the Application
- **Start the Server**: Launch the FastAPI application using Uvicorn.
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ```
- **Access the Dashboard**: Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser to interact with the RTSP dashboard.

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/RTSP.git
   cd RTSP
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   - Create a `.env` file in the root directory.
   - Add your API keys and other necessary environment variables.
     ```env
     NEWSAPI_API_KEY=your_newsapi_key
     # Add other necessary environment variables
     ```

## Running the Application

1. **Start the Server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the Dashboard**
   - Open your web browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Usage

1. **Search for a Stock**
   - Type a stock symbol into the search input. As you type, the company list filters based on your input.

2. **Select a Stock**
   - Click on a stock symbol from the list. This triggers the `fetchStockData` function in `app.js`, which sends a POST request to the backend.

3. **View Data and Charts**
   - The stock information populates in the `stockDetails` section, and Plotly charts render in their respective `<div>` elements (`chart` and `predictionChart`).

4. **Show Predictions**
   - Click the "Show Predictions" button to display the predicted stock trends below the actual data charts, with options to select different time frames and graph types.

5. **Combine Sentiment Analysis**
   - Click the "Combine Sentiment Analysis" button to integrate sentiment data with your predictions, offering a more nuanced view of market trends. This action fetches recent news articles, analyzes their sentiment, and adjusts the predictions accordingly.

## Error Handling

- **Invalid Symbol**
  - If an invalid symbol is submitted (though unlikely due to UI constraints), an error alert notifies the user.

- **Sentiment Analysis Timeout**
  - If sentiment analysis does not complete within the specified timeout, a warning is logged, and the application proceeds without adjusting predictions based on sentiment.

- **API Failures**
  - Robust error handling mechanisms are in place to manage failures in external API calls, ensuring the application remains stable and provides informative feedback to the user.

## Requirements

Ensure your `requirements.txt` includes all necessary dependencies. Notably, it excludes SlowAPI and any rate-limiting packages.

```plaintext
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
```

> **Note**: You may need to run `pip install uvicorn` again after installing other packages. Additionally, ensure that `prophet` dependencies are correctly installed, including `cmdstanpy` and `aiohttp` if using asynchronous requests.

## Additional Notes

- **In-Memory Caching**: The application employs in-memory caching using `cachetools.TTLCache` for stock symbols (24-hour TTL), general stock data (5-minute TTL), and sentiment results (1-hour TTL). This approach optimizes performance by reducing redundant API calls and computations. However, cached data is not persisted across application restarts.

  - **Stock Data Cache**: Cached for 5 minutes to provide up-to-date stock information without frequent API requests.
  - **1-Year Historical Data Cache**: Cached for 1 hour to facilitate efficient predictive analytics.
  - **Sentiment Analysis Cache**: Cached for 1 hour to maintain recent sentiment insights without continuous processing.

- **Background Tasks**: Sentiment analysis is performed as a background task to prevent blocking the main application flow, ensuring a smooth user experience even when processing large amounts of data.

- **Logging**: Comprehensive logging is implemented across all modules to facilitate debugging and monitoring of application behavior.

- **Scalability**: The modular project structure and efficient use of asynchronous programming paradigms position RTSP for scalability and easy maintenance.

## Future Enhancements

- **Persistent Caching**: To retain cached data across restarts, consider implementing a persistent caching mechanism using databases like Redis or file-based caches.

- **Enhanced Security**: Integrate additional security measures such as authentication, authorization, and rate limiting to further protect the application.

- **Expanded Data Sources**: Incorporate more diverse data sources to enrich the analysis and prediction capabilities of the platform.

- **User Accounts**: Allow users to create accounts to save their favorite stocks and preferences.

- **Advanced Analytics**: Implement more sophisticated analytics features, such as portfolio tracking and risk assessment tools.

## License

[MIT License](LICENSE)



## for uv:-

<!-- uv add fastapi python-dotenv jinja2 uvicorn plotly prophet cmdstanpy transformers torch requests yfinance cachetools pandas httpx lxml -->

<!-- uv run uvicorn main:app --reload -->


---

*This project is open-source and available under the [MIT License](LICENSE). Feel free to contribute, report issues, or suggest enhancements!*

