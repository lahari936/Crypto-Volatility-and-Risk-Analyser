"""Simple runner to fetch and persist coin price data using CoinGecko."""
from src.data_fetcher_api import fetch_and_store_coins

if __name__ == "__main__":
    coins = ["bitcoin", "ethereum", "litecoin", "ripple"]
    res = fetch_and_store_coins(coins, days=365, dest_dir="data/processed", parquet=False)
    print(res)