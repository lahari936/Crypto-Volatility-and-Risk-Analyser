import os
import pandas as pd
from .config import RAW_DATA_PATH, PROCESSED_DATA_PATH, COINS


def load_crypto_csv(filename):
    path = os.path.join(RAW_DATA_PATH, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")

    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    # Ensure Date column exists
    if 'Date' not in df.columns:
        cols_lower = {c.lower(): c for c in df.columns}
        if 'date' in cols_lower:
            df.rename(columns={cols_lower['date']: 'Date'}, inplace=True)
        else:
            raise ValueError("No 'Date' column found")

    df['Date'] = pd.to_datetime(df['Date'])

    # Find price/close column and standardize to 'Close'
    price_col = None
    for candidate in ['Close', 'close', 'Price', 'price']:
        if candidate in df.columns:
            price_col = candidate
            break

    if price_col is None:
        raise ValueError("No price column found (expected 'Close' or 'Price')")

    if price_col != 'Close':
        df.rename(columns={price_col: 'Close'}, inplace=True)

    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df.sort_values('Date', inplace=True)
    return df


def fetch_coin_data(coin_id):
    # Loads raw file named <coin_id>.csv and returns a standardized DataFrame
    filename = f"{coin_id}.csv"
    path = os.path.join(RAW_DATA_PATH, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")

    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    # Ensure Date column exists
    if 'Date' not in df.columns:
        cols_lower = {c.lower(): c for c in df.columns}
        if 'date' in cols_lower:
            df.rename(columns={cols_lower['date']: 'Date'}, inplace=True)
        else:
            raise ValueError("No 'Date' column found")

    df['Date'] = pd.to_datetime(df['Date'])

    # Find price/close column and standardize to 'Close'
    price_col = None
    for candidate in ['Close', 'close', 'Price', 'price']:
        if candidate in df.columns:
            price_col = candidate
            break

    if price_col is None:
        raise ValueError("No price column found (expected 'Close' or 'Price')")

    if price_col != 'Close':
        df.rename(columns={price_col: 'Close'}, inplace=True)

    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df.sort_values('Date', inplace=True)
    return df



def fetch_all():
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    for coin_id in COINS:
        df = fetch_coin_data(coin_id)
        df_clean = df[['Date', 'Close']].copy()
        df_clean.rename(columns={'Close': 'price'}, inplace=True)
        df_clean.to_csv(os.path.join(PROCESSED_DATA_PATH, f"{coin_id}_cleaned.csv"), index=False)
        print(f"Loaded & cleaned {coin_id}")

# 'load_crypto_csv' is implemented above and can be used directly by other modules
def load_crypto_csv_alias(filename):
    return load_crypto_csv(filename)
