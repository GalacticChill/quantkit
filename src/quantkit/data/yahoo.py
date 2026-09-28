"""Load prices/returns from Yahoo Finance's public ``v8/chart`` endpoint.

Keyless. Returns adjusted-close prices (splits & dividends accounted for), so
computed returns are total returns.
"""
from __future__ import annotations

import json

import pandas as pd

from ._http import fetch
from ..returns.convert import to_returns

_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval={interval}&range={range}"


def load_prices(ticker: str, *, interval: str = "1mo", range: str = "30y",
                cache: bool = True) -> pd.Series:
    """Return adjusted-close prices for ``ticker`` as a ``pandas.Series``.

    ``interval`` is a Yahoo interval (``1d``, ``1wk``, ``1mo``); ``range`` a
    Yahoo range (``5y``, ``10y``, ``max`` ...). Dots in tickers are normalised to
    dashes (``BRK.B`` -> ``BRK-B``).
    """
    sym = ticker.replace(".", "-")
    url = _CHART.format(sym=sym, interval=interval, range=range)
    payload = json.loads(fetch(url, cache=cache).decode("utf-8"))
    res = payload["chart"]["result"][0]
    ts = res["timestamp"]
    adj = res["indicators"]["adjclose"][0]["adjclose"]
    idx = pd.to_datetime(ts, unit="s", utc=True).tz_convert(None)
    s = pd.Series(adj, index=idx, name=ticker).dropna()
    if interval.endswith("mo"):
        # Yahoo appends an intraday "current" point in the latest month; keep one
        # observation per month (the most recent) so returns are clean monthly.
        s = s[~s.index.to_period("M").duplicated(keep="last")]
    return s


def load_returns(ticker: str, *, interval: str = "1mo", range: str = "30y",
                 kind: str = "simple", cache: bool = True) -> pd.Series:
    """Return periodic returns for ``ticker`` (see :func:`load_prices`)."""
    return to_returns(load_prices(ticker, interval=interval, range=range, cache=cache), kind=kind)
