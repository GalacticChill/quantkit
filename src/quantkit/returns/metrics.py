"""Performance metrics for a periodic return series.

Returns are fractional (0.01 == +1%). Annual figures use ``periods_per_year``;
if not given it is inferred from the index (monthly -> 12, daily -> 252, ...).
Risk-free ``rf`` is an *annual* rate (e.g. 0.02) and is de-annualised internally.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

_FREQ_PPY = {"A": 1, "Y": 1, "Q": 4, "M": 12, "W": 52, "D": 252}


def infer_ppy(index, default: int = 12) -> int:
    """Infer periods-per-year from a pandas index."""
    if isinstance(index, pd.PeriodIndex):
        return _FREQ_PPY.get(index.freqstr[0], default)
    if isinstance(index, pd.DatetimeIndex) and len(index) > 2:
        # resolution-independent: divide timedeltas by one day
        med_days = float(np.median(np.diff(index.values) / np.timedelta64(1, "D")))
        if med_days <= 4:
            return 252
        if med_days <= 10:
            return 52
        if med_days <= 45:
            return 12
        if med_days <= 100:
            return 4
        return 1
    return default


def _prep(returns, ppy):
    r = pd.Series(returns).astype(float).dropna()
    return r, (ppy if ppy is not None else infer_ppy(r.index))


def ann_return(returns, ppy: int = None) -> float:
    """Annualised *arithmetic* mean return."""
    r, p = _prep(returns, ppy)
    return r.mean() * p


def cagr(returns, ppy: int = None) -> float:
    """Compound annual growth rate (geometric)."""
    r, p = _prep(returns, ppy)
    if len(r) == 0:
        return float("nan")
    return float((1.0 + r).prod() ** (p / len(r)) - 1.0)


def ann_vol(returns, ppy: int = None) -> float:
    """Annualised volatility (sample std scaled by sqrt(ppy))."""
    r, p = _prep(returns, ppy)
    return r.std() * np.sqrt(p)


def sharpe(returns, rf: float = 0.0, ppy: int = None) -> float:
    """Annualised Sharpe ratio."""
    r, p = _prep(returns, ppy)
    excess = r - rf / p
    sd = r.std()
    return float("nan") if sd == 0 else (excess.mean() * p) / (sd * np.sqrt(p))


def sortino(returns, rf: float = 0.0, ppy: int = None) -> float:
    """Annualised Sortino ratio (downside deviation vs the risk-free target)."""
    r, p = _prep(returns, ppy)
    excess = r - rf / p
    downside = np.sqrt((excess.clip(upper=0.0) ** 2).mean()) * np.sqrt(p)
    return float("nan") if downside == 0 else (excess.mean() * p) / downside


def max_drawdown(returns) -> float:
    """Maximum peak-to-trough drawdown (a negative number)."""
    r = pd.Series(returns).astype(float).dropna()
    if len(r) == 0:
        return float("nan")
    equity = (1.0 + r).cumprod()
    return float((equity / equity.cummax() - 1.0).min())


def calmar(returns, ppy: int = None) -> float:
    """CAGR divided by the absolute maximum drawdown."""
    mdd = max_drawdown(returns)
    return cagr(returns, ppy) / abs(mdd) if mdd < 0 else float("nan")


def summary(returns, rf: float = 0.0, ppy: int = None) -> pd.Series:
    """Return the common metrics as a labelled ``pandas.Series``."""
    r, p = _prep(returns, ppy)
    return pd.Series({
        "n": len(r),
        "cagr": cagr(r, p),
        "ann_return": ann_return(r, p),
        "ann_vol": ann_vol(r, p),
        "sharpe": sharpe(r, rf, p),
        "sortino": sortino(r, rf, p),
        "max_drawdown": max_drawdown(r),
        "calmar": calmar(r, p),
    })
