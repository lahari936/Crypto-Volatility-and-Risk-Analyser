#!/usr/bin/env python3
"""
main.py

Python Stack for Crypto Volatility and Risk Analysis
(using yfinance for stock/crypto price data)

This script:
- Asks the user for ticker symbols and a date range.
- Downloads OHLCV data from Yahoo Finance via yfinance.
- Computes daily returns, moving averages, and rolling volatility.
- Saves processed data for each ticker into CSV files.
- Prints summary statistics (returns + volatility).
- Plots:
    1. Close price with moving averages
    2. Daily returns
    3. Rolling volatility (always shown)
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


def download_data(tickers: List[str], start: str, end: str) -> Dict[str, pd.DataFrame]:
    """
    Download daily OHLCV data for a list of tickers using yfinance.Ticker.history().

    Parameters
    ----------
    tickers : List[str]
        List of ticker symbols to download.
    start : str
        Start date string in 'YYYY-MM-DD' format.
    end : str
        End date string in 'YYYY-MM-DD' format.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary mapping ticker -> DataFrame with historical data.
        Tickers with no usable data are skipped.
    """
    data_dict: Dict[str, pd.DataFrame] = {}

    for ticker in tickers:
        print(f"\nDownloading data for: {ticker}")
        try:
            t = yf.Ticker(ticker)
            df = t.history(start=start, end=end, auto_adjust=False)
        except Exception as e:
            print(
                f"  [ERROR] Failed to download data for '{ticker}'. "
                f"Reason: {e}. Skipping this ticker."
            )
            continue

        if df is None or df.empty:
            print(
                f"  [WARNING] No data returned for '{ticker}'. "
                f"Check the ticker symbol or date range. Skipping."
            )
            continue

        # Ensure index is DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        df.index.name = "Date"

        # Ensure we have a 'Close' column.
        # Some yfinance configurations may use 'Adj Close' only.
        columns_lower = [str(c).strip().lower() for c in df.columns]
        if "close" not in columns_lower:
            if "adj close" in columns_lower:
                adj_idx = columns_lower.index("adj close")
                df["Close"] = df.iloc[:, adj_idx]
                print(
                    "  [INFO] 'Close' column not found; using 'Adj Close' as 'Close'."
                )
            else:
                print(
                    f"  [ERROR] No 'Close' or 'Adj Close' column for '{ticker}'. "
                    "Skipping this ticker."
                )
                continue

        print(f"  [OK] Retrieved {len(df)} rows for '{ticker}'.")
        data_dict[ticker] = df

    return data_dict


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to the DataFrame.

    Indicators:
    - Daily returns (percentage change of Close).
    - 20-day moving average of Close.
    - 50-day moving average of Close.
    - 20-day rolling volatility (annualized).
    - 50-day rolling volatility (annualized).

    Parameters
    ----------
    df : pd.DataFrame
        Historical OHLCV data with a 'Close' column.

    Returns
    -------
    pd.DataFrame
        DataFrame with added indicator columns.
    """
    df = df.copy()

    if "Close" not in df.columns:
        raise ValueError("Input DataFrame does not contain a 'Close' column.")

    # Daily percentage returns
    df["Daily_Return"] = df["Close"].pct_change()

    # Moving averages (on closing prices)
    df["MA_20"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["MA_50"] = df["Close"].rolling(window=50, min_periods=1).mean()

    # Rolling volatility (annualized). Use min_periods to avoid NaN explosion early on.
    df["Volatility_20"] = df["Daily_Return"].rolling(window=20, min_periods=20).std() * np.sqrt(252)
    df["Volatility_50"] = df["Daily_Return"].rolling(window=50, min_periods=50).std() * np.sqrt(252)

    return df


def save_to_csv(df_dict: Dict[str, pd.DataFrame]) -> None:
    """
    Save each ticker's processed DataFrame to a CSV file.

    Filenames follow the pattern: <TICKER>_historical.csv

    Parameters
    ----------
    df_dict : Dict[str, pd.DataFrame]
        Dictionary mapping ticker -> processed DataFrame.
    """
    for ticker, df in df_dict.items():
        filename = f"{ticker}_historical.csv"
        try:
            df.to_csv(filename)
            print(f"[SAVE] Data for '{ticker}' saved to '{filename}'.")
        except Exception as e:
            print(
                f"[ERROR] Could not save CSV for '{ticker}' "
                f"to '{filename}'. Reason: {e}"
            )


def print_summary(df_dict: Dict[str, pd.DataFrame]) -> None:
    """
    Print a short summary for each ticker.

    For each ticker:
    - First and last date in the dataset.
    - Total return over the period.
    - Average daily return.
    - Overall daily volatility (std dev of daily returns, annualized).

    Parameters
    ----------
    df_dict : Dict[str, pd.DataFrame]
        Dictionary mapping ticker -> processed DataFrame.
    """
    print("\n================ SUMMARY REPORT ================")
    for ticker, df in df_dict.items():
        if df.empty:
            print(f"\n{ticker}: DataFrame is empty. Skipping summary.")
            continue

        missing_cols = [c for c in ["Close", "Daily_Return"] if c not in df.columns]
        if missing_cols:
            print(f"\n{ticker}: Missing columns {missing_cols}. Skipping summary.")
            continue

        # Drop rows where Close is NaN for robust stats
        df_valid = df.dropna(subset=["Close"])
        if df_valid.empty:
            print(f"\n{ticker}: No valid 'Close' price data available.")
            continue

        first_date = df_valid.index.min().date()
        last_date = df_valid.index.max().date()

        # Total return over period
        start_price = df_valid["Close"].iloc[0]
        end_price = df_valid["Close"].iloc[-1]
        total_return = (end_price / start_price - 1.0) * 100.0

        # Average daily return (mean of Daily_Return)
        avg_daily_return = df_valid["Daily_Return"].mean() * 100.0

        # Overall volatility (using all daily returns)
        daily_volatility = df_valid["Daily_Return"].std()
        annual_volatility = daily_volatility * np.sqrt(252) if pd.notna(daily_volatility) else np.nan

        print(f"\nTicker: {ticker}")
        print(f"  First Date          : {first_date}")
        print(f"  Last Date           : {last_date}")
        print(f"  Total Return        : {total_return:.2f}%")
        print(f"  Avg Daily Return    : {avg_daily_return:.4f}%")
        if pd.notna(annual_volatility):
            print(f"  Annualized Volatility: {annual_volatility*100:.2f}%")
        else:
            print("  Annualized Volatility: Not enough data")


def plot_ticker(df: pd.DataFrame, ticker: str) -> None:
    """
    Plot closing price with moving averages, daily returns, and rolling volatility
    for a single ticker.

    Three subplots:
    - Top: Close price with 20-day and 50-day moving averages.
    - Middle: Daily returns.
    - Bottom: Rolling volatility (20-day & 50-day, annualized).

    Parameters
    ----------
    df : pd.DataFrame
        Processed DataFrame containing 'Close', 'MA_20', 'MA_50',
        'Daily_Return', 'Volatility_20', 'Volatility_50'.
    ticker : str
        Ticker symbol for labeling.
    """
    if df.empty:
        print(f"[PLOT] No data available to plot for '{ticker}'.")
        return

    # Ensure Date index
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        df.index.name = "Date"

    plt.figure(figsize=(12, 10))

    # 1. Price and moving averages
    plt.subplot(3, 1, 1)
    if "Close" in df.columns:
        plt.plot(df.index, df["Close"], label="Close Price")
    if "MA_20" in df.columns:
        plt.plot(df.index, df["MA_20"], label="MA 20")
    if "MA_50" in df.columns:
        plt.plot(df.index, df["MA_50"], label="MA 50")

    plt.title(f"{ticker} - Close Price with Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    # 2. Daily returns
    plt.subplot(3, 1, 2)
    if "Daily_Return" in df.columns:
        plt.plot(df.index, df["Daily_Return"], label="Daily Return")
        plt.axhline(0, linestyle="--", linewidth=1)
    else:
        plt.text(
            0.5,
            0.5,
            "Daily_Return column not found",
            horizontalalignment="center",
            verticalalignment="center",
            transform=plt.gca().transAxes,
        )
    plt.title(f"{ticker} - Daily Returns")
    plt.xlabel("Date")
    plt.ylabel("Return")
    plt.grid(True, linestyle="--", alpha=0.5)

    # 3. Volatility
    plt.subplot(3, 1, 3)
    has_vol = False
    if "Volatility_20" in df.columns:
        plt.plot(df.index, df["Volatility_20"], label="Volatility 20D")
        has_vol = True
    if "Volatility_50" in df.columns:
        plt.plot(df.index, df["Volatility_50"], label="Volatility 50D")
        has_vol = True

    if not has_vol:
        plt.text(
            0.5,
            0.5,
            "Volatility columns not found",
            horizontalalignment="center",
            verticalalignment="center",
            transform=plt.gca().transAxes,
        )

    plt.title(f"{ticker} - Rolling Volatility (Annualized)")
    plt.xlabel("Date")
    plt.ylabel("Volatility")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    print(f"[PLOT] Displaying charts for '{ticker}'. Close the window to continue.")
    plt.show()


def main() -> None:
    """
    Main function to run the full analysis pipeline.

    Steps:
    - Collect user input for tickers and date range.
    - Validate inputs.
    - Download data via yfinance.
    - Add indicators (including volatility).
    - Save CSVs.
    - Print summary.
    - Plot each ticker (including volatility chart).
    """
    try:
        print("=== Python Stack for Crypto Volatility and Risk Analysis ===")
        print("Data Source: Yahoo Finance via yfinance\n")

        # 1. User input for tickers
        tickers_input = input(
            "Enter ticker symbols (comma-separated, e.g. BTC-USD,ETH-USD,AAPL): "
        ).strip()
        if not tickers_input:
            print("[ERROR] No tickers provided. Exiting.")
            return

        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        if not tickers:
            print("[ERROR] No valid tickers after parsing input. Exiting.")
            return

        # 2. User input for dates
        start_str = input("Enter start date (YYYY-MM-DD): ").strip()
        end_str = input("Enter end date   (YYYY-MM-DD): ").strip()

        # Validate date format
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
        except ValueError:
            print(
                "[ERROR] Invalid date format. Please use 'YYYY-MM-DD' (e.g. 2023-01-01)."
            )
            return

        # Validate date order
        if start_date >= end_date:
            print(
                "[ERROR] Start date must be earlier than end date. "
                f"Received start={start_str}, end={end_str}."
            )
            return

        # 3. Download data
        df_dict = download_data(tickers, start_str, end_str)
        if not df_dict:
            print(
                "\n[ERROR] No valid data downloaded for any ticker. "
                "Please check ticker symbols and date range."
            )
            return

        # 4. Add indicators (including volatility)
        processed_dict: Dict[str, pd.DataFrame] = {}
        for ticker, df in df_dict.items():
            try:
                processed_df = add_indicators(df)
                processed_dict[ticker] = processed_df
            except Exception as e:
                print(
                    f"[ERROR] Failed to add indicators for '{ticker}'. "
                    f"Reason: {e}. Skipping this ticker."
                )

        if not processed_dict:
            print(
                "\n[ERROR] Failed to process indicators for all tickers. "
                "Nothing to save or plot."
            )
            return

        # 5. Save to CSV
        save_to_csv(processed_dict)

        # 6. Print summary
        print_summary(processed_dict)

        # 7. Plot each ticker (includes volatility chart every run)
        for ticker, df in processed_dict.items():
            plot_ticker(df, ticker)

        print("\n=== Analysis completed successfully. ===")

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user. Exiting gracefully.")
    except Exception as e:
        # Catch-all for any unexpected errors
        print(
            "\n[UNEXPECTED ERROR] Something went wrong while running the analysis.\n"
            f"Details: {e}"
        )
        # For debugging, uncomment the next line:
        # raise


if __name__ == "__main__":
    main()
