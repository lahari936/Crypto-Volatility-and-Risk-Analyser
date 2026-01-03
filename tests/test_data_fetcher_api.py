import pytest
from src.data_fetcher_api import fetch_coingecko_market_chart, save_df


@pytest.mark.skipif(False, reason="Network may not be available in CI; this can be enabled locally")
def test_fetch_coingecko_sample():
    df = fetch_coingecko_market_chart("bitcoin", days=1)
    assert "Date" in df.columns
    assert "price" in df.columns
    assert len(df) > 0


def test_save_df(tmp_path):
    import pandas as pd
    df = pd.DataFrame({"Date": [pd.Timestamp("2020-01-01")], "price": [100.0]})
    path = tmp_path / "out.csv"
    save_df(str(path), df, parquet=False)
    assert path.exists()
    loaded = pd.read_csv(str(path))
    assert "price" in loaded.columns