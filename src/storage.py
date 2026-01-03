import os
from datetime import datetime
import pandas as pd


def save_processed(df: pd.DataFrame, coin: str, dest_dir: str = "data/processed", fmt: str = "csv", timestamp: bool = True):
    """Save processed dataframe for a coin.

    - fmt: 'csv' or 'parquet'
    - timestamp: append YYYYMMDD_HHMM to filename to avoid overwrite
    Returns path written.
    """
    os.makedirs(dest_dir, exist_ok=True)
    tstamp = datetime.utcnow().strftime("%Y%m%d_%H%M") if timestamp else "latest"
    filename = f"{coin}_cleaned_{tstamp}.{ 'parquet' if fmt=='parquet' else 'csv' }"
    path = os.path.join(dest_dir, filename)

    if fmt == 'parquet':
        df.to_parquet(path, index=False)
    else:
        df.to_csv(path, index=False)
    return path


def latest_file_for_coin(coin: str, dest_dir: str = "data/processed"):
    """Return the most recent processed file path for a coin, or None."""
    if not os.path.exists(dest_dir):
        return None
    files = [f for f in os.listdir(dest_dir) if f.startswith(coin + "_")]
    if not files:
        return None
    files.sort(reverse=True)
    return os.path.join(dest_dir, files[0])
