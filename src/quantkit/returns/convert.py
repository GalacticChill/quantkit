"""Series transformations: price->returns, and level transforms.

All functions take and return a ``pandas.Series`` and leave the index untouched.
Percentage-style transforms return *fractional* change (0.05 == +5%), for
consistency with returns elsewhere in the library.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def to_returns(prices, kind: str = "simple") -> pd.Series:
    """Convert a price/level series to periodic returns (drops the first NaN).

    ``kind="simple"`` -> ``p_t / p_{t-1} - 1``; ``kind="log"`` -> ``ln(p_t/p_{t-1})``.
    """
    p = pd.Series(prices).astype(float)
    if kind == "log":
        r = np.log(p).diff()
    elif kind == "simple":
        r = p.pct_change()
    else:
        raise ValueError("kind must be 'simple' or 'log'")
    return r.dropna()


def yoy(series, periods: int = 12) -> pd.Series:
    """Year-over-year fractional change (default 12 periods = monthly YoY)."""
    return pd.Series(series).astype(float).pct_change(periods)


def mom(series) -> pd.Series:
    """One-period (e.g. month-over-month) fractional change."""
    return pd.Series(series).astype(float).pct_change(1)


def change(series, periods: int = 1) -> pd.Series:
    """Absolute change (difference) over ``periods``."""
    return pd.Series(series).astype(float).diff(periods)


def rebase(series, base: float = 100.0) -> pd.Series:
    """Rescale so the first non-null observation equals ``base``."""
    s = pd.Series(series).astype(float)
    first = s.loc[s.first_valid_index()]
    return s / first * base


def zscore(series) -> pd.Series:
    """Standardise to mean 0, unit standard deviation (sample std, ddof=1)."""
    s = pd.Series(series).astype(float)
    return (s - s.mean()) / s.std()
