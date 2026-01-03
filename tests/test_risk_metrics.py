import numpy as np
from src.risk_metrics import sharpe_ratio


def test_sharpe_annualized():
    # create synthetic daily returns with mean 0.001 and std 0.02
    r = np.random.normal(loc=0.001, scale=0.02, size=252)
    s = sharpe_ratio(r, risk_free_rate=0.01, trading_days=252, annualized=True)
    assert isinstance(s, float)
    # Sharpe should be a finite number
    assert not np.isnan(s) and np.isfinite(s)
