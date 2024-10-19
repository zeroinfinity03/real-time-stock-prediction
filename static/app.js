// static/app.js

document.addEventListener('DOMContentLoaded', () => {
    const stockList = document.getElementById('stockList');
    const searchInput = document.getElementById('searchInput');
    const durationSelect = document.getElementById('durationSelect');
    const chartStyleSelect = document.getElementById('chartStyleSelect');
    const displayArea = document.getElementById('displayArea');
    const showLiveBtn = document.getElementById('showLiveBtn');
    const showPredictBtn = document.getElementById('showPredictBtn');
    const combineSentimentBtn = document.getElementById('combineSentimentBtn');

    let allSymbols = [];
    let currentSymbol = '';
    let predictionData = null;  // Store prediction data

    // Fetch and populate stock symbols on page load
    fetch('/api/symbols')
        .then(response => response.json())
        .then(data => {
            allSymbols = data.symbols.sort(); // Sort symbols alphabetically
            populateStockList(allSymbols);
            setDefaultValues();
            fetchStockData(currentSymbol);  // Fetch data with default values
        })
        .catch(error => {
            displayError('Failed to load stock symbols.');
            console.error('Error fetching symbols:', error);
        });

    // Populate the stock list
    function populateStockList(symbols) {
        stockList.innerHTML = '';
        symbols.forEach(symbol => {
            const option = document.createElement('option');
            option.value = symbol;
            option.textContent = symbol;
            stockList.appendChild(option);
        });
    }

    // Set default values
    function setDefaultValues() {
        if (allSymbols.length > 0) {
            currentSymbol = allSymbols[0];
            stockList.value = currentSymbol;
            searchInput.value = currentSymbol;
        }
        // Set default duration to 1 day and chart style to candlestick
        durationSelect.value = '1d';
        chartStyleSelect.value = 'candlestick';
        console.log("Default values set:", {
            symbol: currentSymbol,
            duration: durationSelect.value,
            chartStyle: chartStyleSelect.value
        });
    }

    // Filter stock list based on search input
    searchInput.addEventListener('input', () => {
        const searchTerm = searchInput.value.toUpperCase();
        const filteredSymbols = allSymbols.filter(symbol => symbol.includes(searchTerm));
        populateStockList(filteredSymbols);
    });

    // Handle stock selection
    stockList.addEventListener('change', () => {
        currentSymbol = stockList.value;
        searchInput.value = currentSymbol;
        fetchStockData(currentSymbol);
    });

    // Fetch stock data
    function fetchStockData(symbol, includePrediction = false, includeSentiment = false) {
        const duration = durationSelect.value;
        const chartStyle = chartStyleSelect.value;
        const queryParams = new URLSearchParams({ 
            include_prediction: includePrediction,
            include_sentiment: includeSentiment
        });
        const url = `/api/get_stock_data?${queryParams.toString()}`;

        fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ symbol, duration, chart_style: chartStyle })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data);
            displayStockData(data.stock_data);
            
            if (data.sentiment_result) {
                displaySentimentScore(data.sentiment_result);
            } else {
                document.getElementById('sentimentDetails').innerHTML = '';
            }

            if (includePrediction) {
                if (data.charts.prediction) {
                    console.log("Prediction chart data:", data.charts.prediction);
                    renderChart(data.charts.prediction, 'predictionChart');
                    document.getElementById('predictionChart').style.display = 'block';
                    document.getElementById('chart').style.display = 'none';
                } else {
                    console.error("Prediction data is missing");
                    displayError("Failed to generate prediction data.");
                }
            } else {
                renderChart(data.charts.main, 'chart');
                document.getElementById('predictionChart').style.display = 'none';
                document.getElementById('chart').style.display = 'block';
            }
            resizePlotly();
        })
        .catch(error => {
            console.error('Error:', error);
            displayError('Error fetching stock data: ' + error.message);
        });
    }

    function pollPredictionData(symbol) {
        const pollInterval = setInterval(() => {
            fetch(`/api/get_prediction/${symbol}`)
                .then(response => response.json())
                .then(data => {
                    if (data.prediction_chart) {
                        clearInterval(pollInterval);
                        renderChart(data.prediction_chart, 'predictionChart');
                        document.getElementById('predictionChart').style.display = 'block';
                    }
                })
                .catch(error => console.error('Error polling prediction data:', error));
        }, 5000); // Poll every 5 seconds
    }

    // Display stock data
    function displayStockData(stockData) {
        const formatNumber = (num) => num != null ? Number(num).toFixed(2) : 'N/A';
        const formatLargeNumber = (num) => num != null ? (num / 1e6).toFixed(2) + 'M' : 'N/A';

        const stockDetails = document.getElementById('stockDetails');
        stockDetails.innerHTML = `
            <h3 class="text-xl font-bold mb-2">${stockData.company_name} (${stockData.symbol})</h3>
            <p><strong>Price:</strong> $${formatNumber(stockData.current_price)}</p>
            <p><strong>Change:</strong> ${formatNumber(stockData.change)} (${formatNumber(stockData.change_percent)}%)</p>
            <p><strong>Open:</strong> $${formatNumber(stockData.open)}</p>
            <p><strong>High:</strong> $${formatNumber(stockData.high)}</p>
            <p><strong>Low:</strong> $${formatNumber(stockData.low)}</p>
            <p><strong>Volume:</strong> ${formatLargeNumber(stockData.volume)}</p>
            <p><strong>Market Cap:</strong> $${formatLargeNumber(stockData.market_cap)}</p>
        `;
    }

    // Render chart
    function renderChart(chartData, chartId) {
        const chartDiv = document.getElementById(chartId);
        if (!chartData) {
            console.error('No chart data provided for', chartId);
            return;
        }
        try {
            const parsedData = JSON.parse(chartData);
            if (!parsedData.data || !parsedData.layout) {
                console.error('Invalid chart data structure:', parsedData);
                return;
            }
            Plotly.newPlot(chartDiv, parsedData.data, parsedData.layout, {
                responsive: true,
                useResizeHandler: true,
                autosize: true,
            }).then(() => {
                console.log('Chart rendered successfully');
            }).catch((err) => {
                console.error('Error rendering chart:', err);
            });
        } catch (error) {
            console.error('Error parsing chart data:', error);
            displayError(`Failed to render chart: ${error.message}`);
        }
    }

    // Display error
    function displayError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mt-4';
        errorDiv.role = 'alert';
        errorDiv.innerHTML = `<span class="block sm:inline">${message}</span>`;
        
        const mainDiv = document.getElementById('main');
        mainDiv.insertBefore(errorDiv, mainDiv.firstChild);

        // Clear the charts
        const chartDiv = document.getElementById('chart');
        const predictionChartDiv = document.getElementById('predictionChart');
        if (chartDiv) {
            Plotly.purge(chartDiv);
            chartDiv.style.display = 'none';
        }
        if (predictionChartDiv) {
            Plotly.purge(predictionChartDiv);
            predictionChartDiv.style.display = 'none';
        }

        // Remove the error message after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Event listeners for duration and chart style changes
    durationSelect.addEventListener('change', () => {
        if (currentSymbol) {
            fetchStockData(currentSymbol);
        }
    });

    chartStyleSelect.addEventListener('change', () => {
        if (currentSymbol) {
            fetchStockData(currentSymbol);
        }
    });

    // Event listener for Show Live button
    showLiveBtn.addEventListener('click', () => {
        if (currentSymbol) {
            fetchStockData(currentSymbol, false, false);
        }
    });

    // Event listener for Show Predictions button
    showPredictBtn.addEventListener('click', () => {
        if (currentSymbol) {
            const chartStyle = chartStyleSelect.value;
            if (chartStyle === 'candlestick') {
                displayError('For predictions, please select line chart.');
            } else {
                fetchStockData(currentSymbol, true, false);
            }
        } else {
            displayError('Please select a stock first.');
        }
    });

    // Event listener for Combine Sentiment Analysis button
    combineSentimentBtn.addEventListener('click', () => {
        if (currentSymbol) {
            const chartStyle = chartStyleSelect.value;
            if (chartStyle === 'candlestick') {
                displayError('For predictions with sentiment analysis, please select line chart.');
            } else {
                fetchStockData(currentSymbol, true, true);
            }
        } else {
            displayError('Please select a stock first.');
        }
    });

    function displaySentimentScore(sentimentResult) {
        if (!sentimentResult || typeof sentimentResult.score !== 'number') {
            console.error('Invalid sentiment result:', sentimentResult);
            return;
        }

        const formatNumber = (num) => (typeof num === 'number' && !isNaN(num)) ? num.toFixed(2) : 'N/A';

        const sentimentDiv = document.getElementById('sentimentDetails');
        sentimentDiv.innerHTML = `
            <h3 class="text-xl font-bold mb-2">Sentiment Analysis</h3>
            <p><strong>Score:</strong> ${formatNumber(sentimentResult.score)}</p>
            <p><strong>Label:</strong> ${sentimentResult.label ?? 'N/A'}</p>
            <p><strong>Confidence:</strong> ${formatNumber(sentimentResult.confidence)}</p>
            <p><strong>Positive:</strong> ${formatNumber(sentimentResult.details.positive)}</p>
            <p><strong>Negative:</strong> ${formatNumber(sentimentResult.details.negative)}</p>
            <p><strong>Neutral:</strong> ${formatNumber(sentimentResult.details.neutral)}</p>
        `;
    }
});

// Sidebar toggle functions
function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
}

// Add this function at the end of the file
function resizePlotly() {
    const chartDiv = document.getElementById('chart');
    const predictionChartDiv = document.getElementById('predictionChart');
    if (chartDiv && chartDiv.style.display !== 'none') {
        Plotly.Plots.resize(chartDiv);
    }
    if (predictionChartDiv && predictionChartDiv.style.display !== 'none') {
        Plotly.Plots.resize(predictionChartDiv);
    }
}

// Add this event listener at the end of the DOMContentLoaded event
window.addEventListener('resize', resizePlotly);
