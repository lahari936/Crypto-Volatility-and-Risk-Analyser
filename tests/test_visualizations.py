import pytest
from unittest.mock import Mock
import pandas as pd

from src.visualizations import fig_to_png_bytes, dfs_to_combined_csv


def test_fig_to_png_bytes_success():
    # Mock a figure with to_image returning PNG bytes
    mock_fig = Mock()
    mock_fig.to_image.return_value = b"PNGDATA"

    out = fig_to_png_bytes(mock_fig)
    assert isinstance(out, (bytes, bytearray))
    assert out == b"PNGDATA"


def test_fig_to_png_bytes_failure():
    # Simulate fig.to_image raising (e.g., kaleido missing)
    mock_fig = Mock()
    mock_fig.to_image.side_effect = Exception("render failed")

    with pytest.raises(RuntimeError) as exc:
        fig_to_png_bytes(mock_fig)
    assert "Could not render figure to PNG" in str(exc.value)


def test_dfs_to_combined_csv():
    df1 = pd.DataFrame({"Date": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-02")], "Close": [100, 105]})
    df2 = pd.DataFrame({"Date": [pd.Timestamp("2020-01-01")], "Close": [200]})

    combined = dfs_to_combined_csv({"btc": df1, "eth": df2})

    assert "Date" in combined.columns
    assert "Close" in combined.columns
    assert "coin" in combined.columns
    assert combined.shape[0] == 3
    assert set(combined['coin']) == {"btc", "eth"}
