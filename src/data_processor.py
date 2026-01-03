import numpy as np
from .risk_metrics import volatility, sharpe_ratio


def compute_log_returns(df):
    df = df.copy()
    if 'Close' not in df.columns:
        if 'price' in df.columns:
            df['Close'] = df['price']
        else:
            raise ValueError("No Close/price column found")

    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
    return df.dropna()


def generate_metrics(df, benchmark_returns=None):
    if 'Log_Return' not in df.columns:
        raise ValueError("Log_Return column missing. Run compute_log_returns first.")

    daily_vol, annual_vol = volatility(df['Log_Return'])
    sharpe = sharpe_ratio(df['Log_Return'], trading_days=252, annualized=True)

    metrics = {
        "daily_volatility": float(daily_vol),
        "annual_volatility": float(annual_vol),
        "sharpe_ratio": float(sharpe)
    }

    # Value at Risk (historical VaR 95%)
    try:
        from .risk_metrics import historical_var
        metrics['var_95'] = float(historical_var(df['Log_Return'], level=0.05))
    except Exception:
        metrics['var_95'] = None

    # Beta vs benchmark if provided
    if benchmark_returns is not None:
        try:
            from .risk_metrics import beta
            metrics['beta'] = float(beta(df['Log_Return'], benchmark_returns))
        except Exception:
            metrics['beta'] = None

    return metrics

