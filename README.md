# Indian Stock Market Screener

A powerful, interactive Streamlit-based application for screening Indian stocks (NSE) using advanced technical indicators and customizable trading strategies. This tool helps traders and investors identify potential trading opportunities by applying complex multi-timeframe analysis to historical stock data.

## 🚀 Features

### Core Screening Features
- **Comprehensive Stock Screening**: Screen thousands of NSE-listed stocks with customizable parameters
- **Advanced Technical Indicators**: Supports RSI, EMA, WMA, SMA, MACD, ADX, ATR, Bollinger Bands, and more across daily, weekly, and monthly timeframes
- **Multi-Timeframe Analysis**: Analyze stocks across different timeframes simultaneously
- **Real-Time Data Fetching**: Fetch live market data using Yahoo Finance API with intelligent cache fallback
- **Data Caching**: Smart caching system with 2500+ pre-cached stocks for offline screening

### 🤖 NEW: AI Strategy Builder
- **Natural Language to Strategy**: Convert plain English descriptions into executable trading strategies using local LLMs (Ollama)
- **Document Upload**: Upload PDF, TXT, or DOCX strategy documents for automatic conversion
- **AI Explanations**: Get plain English explanations of what each strategy does
- **Live JSON Preview**: View and edit the generated strategy JSON before saving
- **One-Click Execution**: Save and run AI-generated strategies immediately

### Strategy Management
- **Visual Strategy Editor**: Create and modify strategies through an intuitive UI
- **JSON-Based Strategies**: Full control with JSON-based strategy definitions
- **Strategy History**: Track AI-generated strategies with metadata

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for data fetching (or use cached data)
- Git (for cloning the repository)
- **For AI Features**: [Ollama](https://ollama.ai/) installed locally

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

4. **For AI Strategy Builder (Optional):**
   ```bash
   # Install Ollama from https://ollama.ai/
   # Then pull a model:
   ollama pull mistral
   # Start Ollama server:
   ollama serve
   ```

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
   - Adjust the maximum number of stocks to screen
   - Set your price range filter
   - Click "🚀 Run Screener" to execute

4. **Using AI Strategy Builder:**
   - Navigate to the "🤖 AI Strategy Builder" tab
   - Connect to Ollama and select your model
   - Click "🔥 Load Model" to pre-load the model (recommended)
   - Enter your strategy in plain English, e.g.:
     - *"Find stocks with RSI below 30 and price above 50"*
     - *"Stocks trading above 200 EMA with ADX greater than 25"*
   - Click "Generate Strategy" and review the result
   - Save and run your strategy!

## 📁 Project Structure

```
Indian-Stock-Market-Screener/
├── app.py                          # Main Streamlit application
├── ollama_client.py                # Ollama LLM integration module
├── strategy_validator.py           # JSON strategy validation
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── data/
│   └── stocks.csv                  # NSE stock symbols list
├── strategies/                     # JSON strategy files
│   ├── momentum_gain.json
│   ├── multitimeframe_momentum_accelerator.json
│   └── ... (user-created strategies)
├── prompts/
│   └── strategy_conversion_prompt.txt  # AI system prompt
├── ohlcv_cache/                    # Cached OHLCV data (2500+ stocks)
│   ├── RELIANCE.csv
│   ├── TCS.csv
│   └── ... (other stocks)
└── .venv/                          # Virtual environment
```

### Key Files

| File | Description |
|------|-------------|
| `app.py` | Main application with UI, screener logic, and AI builder |
| `ollama_client.py` | Handles Ollama LLM communication and strategy parsing |
| `strategy_validator.py` | Validates and sanitizes AI-generated strategies |
| `prompts/strategy_conversion_prompt.txt` | Detailed prompt for LLM strategy conversion |

## 📊 Strategy Format

Strategies are defined in JSON with conditions that must all be met:

```json
{
  "name": "Oversold Bounce",
  "description": "Find oversold stocks with volume surge",
  "conditions": [
    {
      "lhs": {"type": "indicator", "name": "rsi", "params": {"period": 14}, "timeframe": "daily", "offset": 0},
      "operator": "<",
      "rhs": {"type": "value", "value": 30}
    },
    {
      "lhs": {"type": "indicator", "name": "volume", "params": {}, "timeframe": "daily", "offset": 0},
      "operator": ">",
      "rhs": {"type": "indicator", "name": "volume_sma", "params": {"period": 20}, "timeframe": "daily", "offset": 0}
    }
  ]
}
```

### Available Indicators

| Indicator | Parameters | Description |
|-----------|------------|-------------|
| `close`, `open`, `high`, `low` | - | Price data |
| `volume` | - | Trading volume |
| `sma`, `ema`, `wma` | `period` | Moving averages |
| `rsi` | `period` | Relative Strength Index |
| `macd`, `macd_signal` | `period_fast`, `period_slow`, `period_signal` | MACD |
| `adx` | `period` | Average Directional Index |
| `atr` | `period` | Average True Range |
| `bb_high`, `bb_low`, `bb_mid` | `period` | Bollinger Bands |
| `volume_sma` | `period` | Volume SMA |

## 🤝 Contributing

Contributions are welcome! 

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit: `git commit -am 'Add new feature'`
5. Push: `git push origin feature-name`
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is for educational and informational purposes only. It is not financial advice. Always do your own research and consult with financial professionals before making investment decisions. Past performance does not guarantee future results.

## 🆘 Support

If you encounter issues:

1. Check the terminal output for error messages
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. For AI features, ensure Ollama is running: `ollama serve`
4. The app uses cached data if Yahoo Finance is unavailable

For bugs or feature requests, please open an issue on GitHub.

---

**Made with ❤️ for Indian Stock Market Traders**