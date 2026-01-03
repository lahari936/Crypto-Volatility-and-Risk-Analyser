import pandas as pd
from src.storage import save_processed, latest_file_for_coin
import os

def test_save_processed_csv(tmp_path):
    df = pd.DataFrame({"Date": [pd.Timestamp('2020-01-01')], "price": [100]})
    dest = str(tmp_path)
    path = save_processed(df, 'btc', dest_dir=dest, fmt='csv', timestamp=False)
    assert os.path.exists(path)
    loaded = pd.read_csv(path)
    assert 'price' in loaded.columns


def test_latest_file_for_coin(tmp_path):
    df = pd.DataFrame({"Date": [pd.Timestamp('2020-01-01')], "price": [100]})
    dest = str(tmp_path)
    p1 = save_processed(df, 'btc', dest_dir=dest, fmt='csv', timestamp=True)
    p2 = save_processed(df, 'btc', dest_dir=dest, fmt='csv', timestamp=True)
    latest = latest_file_for_coin('btc', dest_dir=dest)
    assert latest is not None
    assert latest.endswith('.csv')