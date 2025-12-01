Crypto & Stock Volatility Analyzer (Python + yfinance)

This project downloads historical price data for any stock or crypto asset using yfinance, calculates key financial indicators, and visualizes volatility, daily returns, and moving averages.

All results are saved automatically and plotted using matplotlib.

🚀 Features

Download OHLCV data using yfinance

Supports stocks (AAPL, MSFT, TSLA…) and crypto (BTC-USD, ETH-USD…)

Computes:

Daily Returns

20 & 50-Day Moving Averages

20 & 50-Day Annualized Rolling Volatility

Saves processed data as CSV files

Displays 3 charts for each ticker:

Price + Moving Averages

Daily Returns

Volatility Curve (always shown)

Handles invalid tickers & date errors gracefully

📦 Installation

Install required packages:

pip install yfinance pandas numpy matplotlib

▶️ How to Run
python main.py


Then enter:

Ticker symbols (comma-separated)

AAPL,MSFT,GOOGL
BTC-USD,ETH-USD


Start date

2023-01-01


End date

2023-12-31

📊 Output

For each ticker, the script will:

Save:

<TICKER>_historical.csv


Show 3 charts:

Price + 20/50 MA

Daily Returns

Volatility (20D & 50D)

Print summary:

First & last date

Total return

Average daily return

Annualized volatility

🗂️ Project Structure
main.py
README.md
AAPL_historical.csv
BTC-USD_historical.csv
...

❤️ Notes

Requires the internet (Yahoo Finance data)

Works with any valid Yahoo Finance ticker

Volatility chart is always displayed
