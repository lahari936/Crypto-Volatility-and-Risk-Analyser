import requests
import pandas as pd
import os
from datetime import datetime

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def fetch_coingecko_market_chart(coin_id: str = "bitcoin", vs_currency: str = "usd", days: int = 30) -> pd.DataFrame:
    """Fetch historical market chart data from CoinGecko.

    Returns DataFrame with columns ['Date', 'price'] where Date is a datetime and price is float.
    """
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    prices = data.get("prices", [])
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df[["Date", "price"]]
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def save_df(path: str, df: pd.DataFrame, parquet: bool = False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if parquet:
        df.to_parquet(path)
    else:
        df.to_csv(path, index=False)


def fetch_and_store_coins(coin_ids, vs_currency="usd", days=30, dest_dir="data/processed", parquet: bool = False):
    """Fetch from CoinGecko and save to dest_dir in CSV or Parquet. Returns dict coin->path or error string."""
    results = {}
    os.makedirs(dest_dir, exist_ok=True)
    for coin in coin_ids:
        try:
            df = fetch_coingecko_market_chart(coin, vs_currency=vs_currency, days=days)
            # standardize column name
            df = df.rename(columns={'price': 'price'})
            # save with storage helper if available
            try:
                from .storage import save_processed
                df_to_save = df.rename(columns={'price':'price'})
                # Align with processed format: Date, price
                path = save_processed(df_to_save, coin, dest_dir=dest_dir, fmt='parquet' if parquet else 'csv')
            except Exception:
                filename = f"{coin}_coingecko_{days}d"
                path = os.path.join(dest_dir, filename + (".parquet" if parquet else ".csv"))
                save_df(path, df, parquet=parquet)

            results[coin] = path
        except requests.RequestException as e:
            # record failure
            results[coin] = str(e)
    return results


# Minimal placeholder Binance REST call - fetch current price for a symbol like 'BTCUSDT'
BINANCE_BASE = "https://api.binance.com/api/v3"

def fetch_binance_price(symbol: str = "BTCUSDT") -> float:
    url = f"{BINANCE_BASE}/ticker/price"
    resp = requests.get(url, params={"symbol": symbol}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return float(data["price"])