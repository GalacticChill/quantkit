"""Load economic series from FRED via the keyless ``fredgraph.csv`` endpoint.

No API key is required and no CORS is involved (this runs server-side / in a
notebook, not in a browser). Returns a ``pandas.Series`` indexed by date.
"""
from __future__ import annotations

import io
from typing import Optional

import pandas as pd

from ._http import fetch

_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"


def load_fred(series_id: str, *, start=None, end=None, cache: bool = True) -> pd.Series:
    """Return a FRED series as a ``pandas.Series`` (missing values as ``NaN``).

    Parameters
    ----------
    series_id : str
        FRED series id, e.g. ``"UNRATE"``, ``"CPIAUCSL"``, ``"GS10"``.
    start, end : date-like, optional
        Inclusive bounds to slice the series to.
    cache : bool
        Cache the raw CSV on disk (default True).

    Examples
    --------
    >>> load_fred("UNRATE").tail(1)          # doctest: +SKIP
    """
    raw = fetch(_CSV.format(series_id), cache=cache).decode("utf-8")
    df = pd.read_csv(io.StringIO(raw))
    date_col, val_col = df.columns[0], df.columns[1]
    idx = pd.to_datetime(df[date_col])
    s = pd.Series(pd.to_numeric(df[val_col], errors="coerce").values, index=idx, name=series_id)
    if start is not None:
        s = s[s.index >= pd.Timestamp(start)]
    if end is not None:
        s = s[s.index <= pd.Timestamp(end)]
    return s
