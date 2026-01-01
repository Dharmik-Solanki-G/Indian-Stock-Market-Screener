# My Python Trading Project

This project is designed to implement and test various trading strategies using historical stock data. It provides a user interface for executing strategies and analyzing their performance.

## Project Structure

- **app.py**: Contains all the logic and user interface for the application, including data processing and strategy execution.
- **strategies/**: Directory holding JSON files that define various trading strategies, including parameters and rules for implementation.
- **ohlcv_cache/**: Directory for storing cached OHLCV (Open, High, Low, Close, Volume) data for each stock to optimize data retrieval and processing.
- **data/stocks.csv**: A CSV file containing a list of NSE (National Stock Exchange) symbols used to identify stocks for strategy application.
- **requirements.txt**: Lists the Python dependencies required for the project, facilitating package installation using pip.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd my-python-project
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have the necessary data files in the `data/` directory, particularly `stocks.csv`.

## Usage

To run the application, execute the following command:
```
python app.py
```

Follow the on-screen instructions to select and execute trading strategies.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.