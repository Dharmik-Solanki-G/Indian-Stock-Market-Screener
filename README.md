# Indian Stock Market Screener

A powerful, interactive Streamlit-based application for screening Indian stocks (NSE) using advanced technical indicators and customizable trading strategies. This tool helps traders and investors identify potential trading opportunities by applying complex multi-timeframe analysis to historical stock data.

## 🚀 Features

- **Comprehensive Stock Screening**: Screen thousands of NSE-listed stocks with customizable parameters
- **Advanced Technical Indicators**: Supports RSI, EMA, WMA, MACD, and many more indicators across daily, weekly, and monthly timeframes
- **Customizable Strategies**: Create, edit, and manage trading strategies using a user-friendly JSON-based system
- **Multi-Timeframe Analysis**: Analyze stocks across different timeframes (daily, weekly, monthly) simultaneously
- **Real-Time Data Fetching**: Fetch live market data using Yahoo Finance API
- **Data Caching**: Intelligent caching system to optimize performance and reduce API calls
- **Interactive Web UI**: Modern, responsive interface built with Streamlit
- **Strategy Editor**: Built-in editor for creating and modifying screening strategies
- **Performance Metrics**: View detailed results with buy/sell signals and stock performance data

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for data fetching
- Git (for cloning the repository)

## 🛠 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Dharmik-Solanki-G/Indian-Stock-Market-Screener.git
   cd Indian-Stock-Market-Screener
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure data files are present:**
   - The `data/stocks.csv` file should contain NSE stock symbols
   - The application will automatically create necessary directories

## 🚀 Usage

1. **Run the application:**
   ```bash
   streamlit run app.py
   ```

2. **Access the app:**
   - Open your browser and navigate to `http://localhost:8501`
   - The app will load NSE stock data and available strategies

3. **Using the Screener:**
   - Select a strategy from the sidebar dropdown
   - Adjust the maximum number of stocks to screen (default: 200)
   - Click "Run Screening" to apply the strategy
   - View results in the interactive table with buy/sell signals

4. **Strategy Management:**
   - Use the "Strategy Editor" section to create new strategies
   - Edit existing strategies by selecting and modifying parameters
   - Delete strategies you no longer need

## 📁 Project Structure

```
Indian-Stock-Market-Screener/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── data/
│   └── stocks.csv                  # NSE stock symbols list
├── strategies/                     # JSON strategy files
│   ├── momentum_gain.json
│   ├── multitimeframe_momentum_accelerator.json
│   └── swing_booster_new.json
├── ohlcv_cache/                    # Cached OHLCV data (auto-generated)
│   ├── RELIANCE.csv
│   ├── TCS.csv
│   └── ... (other stocks)
└── .venv/                          # Virtual environment (created during setup)
```

### Key Files Explanation

- **app.py**: The core application containing all logic, UI components, data processing, and strategy execution
- **strategies/*.json**: JSON files defining trading strategies with conditions, operands, and parameters
- **ohlcv_cache/*.csv**: Cached historical price data for each stock to improve performance
- **data/stocks.csv**: List of NSE stock symbols to screen

## 📊 Understanding Strategies

Strategies are defined in JSON format and consist of conditions that must be met for a stock to pass the screen. Each condition includes:

- **Operands**: Indicators like RSI, EMA, Close price, Volume, etc.
- **Operators**: Comparison operators (>, <, >=, <=, ==)
- **Timeframes**: Daily, Weekly, Monthly
- **Offsets**: Look back periods (e.g., 4 days ago)

Example strategy structure:
```json
{
  "name": "Momentum Gain",
  "conditions": [
    {
      "lhs": {"type": "indicator", "name": "rsi", "params": {"period": 14}, "timeframe": "daily"},
      "operator": ">",
      "rhs": {"type": "value", "value": 60}
    }
  ]
}
```

## 🔧 Configuration

The application uses several configuration constants defined in `app.py`:

- `CACHE_DIR`: Directory for cached data
- `STRATEGIES_DIR`: Directory for strategy files
- `DATA_DIR`: Directory for stock lists
- `STOCKS_FILE`: Path to the stocks CSV file

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Test strategies with various market conditions
- Update README for any new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is for educational and informational purposes only. It is not financial advice. Always do your own research and consult with financial professionals before making investment decisions. Past performance does not guarantee future results.

## 🆘 Support

If you encounter issues:

1. Check the terminal output for error messages
2. Ensure all dependencies are installed correctly
3. Verify your internet connection for data fetching
4. Check that `data/stocks.csv` contains valid NSE symbols

For bugs or feature requests, please open an issue on GitHub.