"""Data loaders: FRED, the Ken French Data Library, and Yahoo Finance.

All loaders are keyless and cache raw downloads on disk (see ``_http``).
"""
from .fred import load_fred
from .ken_french import load_ff_factors, load_ff_portfolios
from .yahoo import load_prices, load_returns

__all__ = ["load_fred", "load_ff_factors", "load_ff_portfolios", "load_prices", "load_returns"]
