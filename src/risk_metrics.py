import numpy as np
from .config import TRADING_DAYS


def volatility(returns):
    r = returns.dropna()
    daily_vol = np.std(r)
    annual_vol = daily_vol * np.sqrt(TRADING_DAYS)
    return daily_vol, annual_vol


import pandas as pd

def sharpe_ratio(returns, risk_free_rate=0.01, trading_days=252, annualized=True):
    """Compute Sharpe ratio.

    returns: series of daily log returns (pandas Series or numpy array)
    risk_free_rate: annual risk-free rate (e.g., 0.01 for 1%)
    trading_days: days per year used to annualize
    annualized: if True return annualized Sharpe ratio
    """
    # Accept numpy arrays and pandas Series
    if not isinstance(returns, pd.Series):
        r = pd.Series(returns)
    else:
        r = returns.copy()

    r = r.dropna()
    if r.std() == 0 or len(r) == 0:
        return 0.0

    mean_daily = r.mean()
    std_daily = r.std()

    if annualized:
        excess_annual_return = (mean_daily * trading_days) - risk_free_rate
        annualized_vol = std_daily * np.sqrt(trading_days)
        if annualized_vol == 0:
            return 0.0
        return excess_annual_return / annualized_vol
    else:
        # non-annualized (daily)
        return (mean_daily - risk_free_rate / trading_days) / std_daily


def beta(asset_returns, benchmark_returns):
    covariance = asset_returns.cov(benchmark_returns)
    variance = benchmark_returns.var()
    return covariance / variance


def historical_var(returns, level=0.05):
    """Compute historical Value-at-Risk at the given level (e.g., 0.05 for 95% VaR)."""
    r = returns.dropna()
    if len(r) == 0:
        return 0.0
    return -np.quantile(r, level)


