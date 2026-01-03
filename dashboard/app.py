import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import streamlit as st
from src.data_fetcher import load_crypto_csv
from src.data_processor import compute_log_returns, generate_metrics
from src.visualizations import plot_price_plotly, plot_volatility_plotly, plot_comparison_price, plot_returns_scatter, fig_to_png_bytes, dfs_to_combined_csv
from src.risk_classifier import classify_risk
from src.data_fetcher_api import fetch_coingecko_market_chart

st.set_page_config(page_title="Crypto Risk Analyzer", layout="wide")

st.title("📊 Crypto Volatility & Risk Analyzer")

# --- Sidebar controls for comparison & visualization options ---
st.sidebar.header('Visualization Controls')
section = st.sidebar.radio(
    "Select Section",
    ["Data Overview", "Risk Metrics", "Visualizations", "Risk Classification"]
)

coins_available = ['bitcoin', 'ethereum', 'litecoin', 'ripple']
selected_coins = st.sidebar.multiselect('Select assets for comparison', coins_available, default=['bitcoin', 'ethereum'])

# date range selection
import pandas as _pd
min_date = None
max_date = None
try:
    sample = load_crypto_csv(f"{selected_coins[0]}.csv") if selected_coins else load_crypto_csv('bitcoin.csv')
    min_date = sample['Date'].min()
    max_date = sample['Date'].max()
except Exception:
    min_date = None
    max_date = None

date_range = st.sidebar.date_input("Date range", value=[min_date.date() if min_date is not None else None, max_date.date() if max_date is not None else None]) if min_date is not None else None
normalize = st.sidebar.checkbox('Normalize prices (start at 1)', value=True)
vol_window = st.sidebar.slider('Volatility window (days)', 5, 90, 30)

# Load primary coin data (first selected or default)
if not selected_coins:
    st.warning('Please select at least one asset to visualize.')
    st.stop()

primary = selected_coins[0]
try:
    df = load_crypto_csv(f"{primary}.csv")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# subset by date range if provided
if date_range and len(date_range) == 2 and date_range[0] and date_range[1]:
    start, end = date_range
    df = df[(df['Date'] >= _pd.to_datetime(start)) & (df['Date'] <= _pd.to_datetime(end))]

# compute returns and metrics
try:
    df = compute_log_returns(df)
    metrics = generate_metrics(df)
except Exception as e:
    st.error(f"Error computing metrics: {e}")
    st.stop()

risk = classify_risk(metrics["annual_volatility"])

# KPI cards
col1, col2, col3 = st.columns(3)
col1.metric("Annual Volatility", f"{metrics['annual_volatility']:.2f}")
col2.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
col3.metric("Risk Level", risk)

st.divider()

# Charts - interactive with Plotly
st.subheader("Price Trend")
from src.visualizations import plot_price_plotly, plot_volatility_plotly, plot_comparison_price, plot_returns_scatter, fig_to_png_bytes, dfs_to_combined_csv, plot_risk_distribution, plot_metric_bars

# Price chart + export
fig_price = plot_price_plotly(df, primary)
st.plotly_chart(fig_price, width='stretch')
# CSV export for price
csv_price = df[['Date', 'Close']].to_csv(index=False).encode('utf-8')
st.download_button('Download Price CSV', data=csv_price, file_name=f"{primary}_price.csv", mime='text/csv')
# PNG export for price
try:
    png_price = fig_to_png_bytes(fig_price)
    st.download_button('Download Price PNG', data=png_price, file_name=f"{primary}_price.png", mime='image/png')
except Exception as e:
    st.info('Install `kaleido` to enable PNG export (pip install kaleido)')

# Summary visuals for non-technical users
st.subheader('Summary')
metrics_map = {primary: metrics}
for coin in selected_coins[1:]:
    try:
        dtmp = load_crypto_csv(f"{coin}.csv")
        mtmp = generate_metrics(compute_log_returns(dtmp))
        metrics_map[coin] = mtmp
    except Exception:
        continue

# Risk distribution pie
fig_risk = plot_risk_distribution(metrics_map)
st.plotly_chart(fig_risk, width='stretch')
# Bars for annual volatility
fig_vol_bars = plot_metric_bars(metrics_map, metric='annual_volatility')
st.plotly_chart(fig_vol_bars, width='stretch')

st.subheader(f"Rolling Volatility ({vol_window} days)")
fig_vol = plot_volatility_plotly(df, primary, window=vol_window)
st.plotly_chart(fig_vol, width='stretch')
vol_df = df[['Date', 'Log_Return']].copy()
vol_df['rolling_vol'] = vol_df['Log_Return'].rolling(vol_window).std()
# CSV export for volatility
csv_vol = vol_df[['Date', 'rolling_vol']].dropna().to_csv(index=False).encode('utf-8')
st.download_button('Download Volatility CSV', data=csv_vol, file_name=f"{primary}_volatility_{vol_window}d.csv", mime='text/csv')
# PNG export for volatility
try:
    png_vol = fig_to_png_bytes(fig_vol)
    st.download_button('Download Volatility PNG', data=png_vol, file_name=f"{primary}_volatility.png", mime='image/png')
except Exception:
    st.info('Install `kaleido` to enable PNG export (pip install kaleido)')

# Asset comparison
if len(selected_coins) > 1:
    st.subheader("Asset Comparison")
    dfs = {}
    for coin in selected_coins:
        try:
            d = load_crypto_csv(f"{coin}.csv")
            # apply date range
            if date_range and len(date_range) == 2 and date_range[0] and date_range[1]:
                s, e = date_range
                d = d[(d['Date'] >= _pd.to_datetime(s)) & (d['Date'] <= _pd.to_datetime(e))]
            dfs[coin] = d
        except Exception as e:
            st.warning(f"Could not load {coin}: {e}")

    fig_comp = plot_comparison_price(dfs, normalize=normalize)
    st.plotly_chart(fig_comp, width='stretch')

    # Combined CSV export for comparison
    combined_df = dfs_to_combined_csv(dfs)
    csv_comb = combined_df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Comparison CSV', data=csv_comb, file_name='asset_comparison.csv', mime='text/csv')
    # PNG export for comparison
    try:
        png_comp = fig_to_png_bytes(fig_comp)
        st.download_button('Download Comparison PNG', data=png_comp, file_name='asset_comparison.png', mime='image/png')
    except Exception:
        st.info('Install `kaleido` to enable PNG export (pip install kaleido)')

    # Risk-return scatter
    st.subheader('Risk vs Return')
    rr_map = {}
    for c in selected_coins:
        try:
            d = load_crypto_csv(f"{c}.csv")
            rr_map[c] = compute_log_returns(d)
        except Exception as e:
            st.warning(f"Skipping {c} for risk-return: {e}")

    if rr_map:
        fig_rr = plot_returns_scatter(rr_map, window=vol_window)
        st.plotly_chart(fig_rr, width='stretch')
        # CSV export for risk-return
        rr_rows = []
        for coin, d in rr_map.items():
            r = d['Log_Return'].dropna()
            rr_rows.append({'coin': coin, 'mean_return': r.mean(), 'volatility': r.std()})
        rr_df = _pd.DataFrame(rr_rows)
        st.download_button('Download Risk-Return CSV', data=rr_df.to_csv(index=False).encode('utf-8'), file_name='risk_return.csv', mime='text/csv')
        try:
            png_rr = fig_to_png_bytes(fig_rr)
            st.download_button('Download Risk-Return PNG', data=png_rr, file_name='risk_return.png', mime='image/png')
        except Exception:
            st.info('Install `kaleido` to enable PNG export (pip install kaleido)')
    else:
        st.info('No assets available for risk-return chart')

# Data overview table
with st.expander('Data Overview - sample rows'):
    st.dataframe(df.head())
