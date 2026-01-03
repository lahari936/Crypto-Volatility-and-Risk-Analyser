import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import io


def fig_to_png_bytes(fig):
    """Return PNG bytes for a Plotly figure using kaleido if available."""
    try:
        # fig.to_image uses kaleido under the hood when available
        img = fig.to_image(format='png', engine='kaleido')
        return img
    except Exception as e:
        # Could not render to image (kaleido may not be installed)
        raise RuntimeError("Could not render figure to PNG. Install 'kaleido' to enable PNG export.") from e


def dfs_to_combined_csv(dfs: dict):
    """Combine multiple dfs into a single CSV-ready DataFrame with coin column."""
    rows = []
    for coin, df in dfs.items():
        d = df.copy()
        if 'Date' not in d.columns:
            d = d.reset_index()
        d = d[['Date', 'Close']].copy()
        d['coin'] = coin
        rows.append(d)
    combined = pd.concat(rows, ignore_index=True)
    return combined


def plot_price_plotly(df: pd.DataFrame, coin: str):
    df = df.copy()
    if 'Date' in df.columns:
        x = df['Date']
    else:
        x = df.index

    fig = px.line(df, x=x, y='Close', title=f"{coin} Price Trend", labels={'Close':'Price', 'Date':'Date'})
    fig.update_layout(hovermode='x unified')
    return fig


def plot_volatility_plotly(df: pd.DataFrame, coin: str, window: int = 30):
    df = df.copy()
    if 'Log_Return' not in df.columns:
        raise ValueError('Log_Return missing; compute with compute_log_returns')

    vol = df['Log_Return'].rolling(window).std()
    x = df['Date'] if 'Date' in df.columns else df.index
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=vol, mode='lines', name=f'Rolling Vol (window={window})'))
    fig.update_layout(title=f"{coin} Rolling Volatility ({window}d)", xaxis_title='Date', yaxis_title='Volatility')
    return fig


def plot_comparison_price(dfs: dict, normalize: bool = True):
    """Plot interactive comparison of multiple assets.

    dfs: dict mapping coin->DataFrame with 'Date' and 'Close'
    normalize: if True, index prices to 1 at start (relative returns)
    """
    fig = go.Figure()

    for coin, df in dfs.items():
        d = df.copy()
        if 'Date' not in d.columns:
            d = d.reset_index()
        d = d.sort_values('Date')
        prices = d['Close'].astype(float)
        if normalize:
            prices = prices / prices.iloc[0]
            yname = 'Normalized Price'
        else:
            yname = 'Price'

        fig.add_trace(go.Scatter(x=d['Date'], y=prices, mode='lines', name=coin))

    fig.update_layout(title='Asset Comparison', xaxis_title='Date', yaxis_title=yname, hovermode='x unified')
    return fig


def plot_returns_scatter(df_map: dict, window: int = 30):
    """Create a risk-return style scatter (volatility vs mean return) for assets.

    df_map: dict coin->DataFrame with 'Log_Return'
    """
    rows = []
    for coin, df in df_map.items():
        r = df['Log_Return'].dropna()
        mean = r.mean()
        vol = r.std()
        rows.append({'coin': coin, 'mean_return': mean, 'volatility': vol})
    summary = pd.DataFrame(rows)
    fig = px.scatter(summary, x='volatility', y='mean_return', text='coin', size_max=20, title='Return vs Volatility')
    fig.update_traces(textposition='top center')
    fig.update_layout(xaxis_title='Volatility (std)', yaxis_title='Mean Log Return')
    return fig


def plot_risk_distribution(metrics_map: dict):
    """Plot a pie chart showing risk categories (High/Medium/Low) for given metrics_map coin->metrics dict."""
    from src.risk_classifier import classify_risk
    counts = {'High Risk': 0, 'Medium Risk': 0, 'Low Risk': 0}
    for coin, m in metrics_map.items():
        try:
            risk = classify_risk(m.get('annual_volatility', 0))
        except Exception:
            risk = 'Low Risk'
        counts[risk] = counts.get(risk, 0) + 1
    labels = list(counts.keys())
    values = [counts[k] for k in labels]
    fig = px.pie(names=labels, values=values, title='Risk Distribution', hole=0.4)
    return fig


def plot_metric_bars(metrics_map: dict, metric: str = 'annual_volatility'):
    """Plot bar chart of a chosen metric across assets."""
    rows = []
    for coin, m in metrics_map.items():
        if metric in m and m[metric] is not None:
            rows.append({'coin': coin, metric: m[metric]})
    df = pd.DataFrame(rows)
    fig = px.bar(df, x='coin', y=metric, title=f'{metric.replace("_"," ").title()} by Asset')
    return fig

