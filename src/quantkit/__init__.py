"""quantkit — a small quant toolkit.

Born from a stream of finance/data browser tools; the utilities those tools
proved out (data loading, return conversion, performance metrics, factor
regression, and a shared plotting style) live here as a real library.

Quick start
-----------
>>> import quantkit as qk
>>> unrate = qk.load_fred("UNRATE")                 # keyless FRED loader
>>> factors = qk.load_ff_factors(model="5")         # Fama-French 5 + Momentum
>>> px = qk.load_prices("SPY")                       # Yahoo adjusted close
>>> res = qk.factor_regression(qk.to_returns(px), factors)
>>> res.summary()
"""
from .data.fred import load_fred
from .data.ken_french import load_ff_factors, load_ff_portfolios
from .data.yahoo import load_prices, load_returns
from .returns.convert import to_returns, yoy, mom, change, rebase, zscore
from .returns.metrics import (
    ann_return, cagr, ann_vol, sharpe, sortino, max_drawdown, calmar, summary, infer_ppy,
)
from .returns.factors import factor_regression, FactorResult
from .plotting.style import apply_style, style_context, PALETTE

__version__ = "0.1.0"

__all__ = [
    "load_fred", "load_ff_factors", "load_ff_portfolios", "load_prices", "load_returns",
    "to_returns", "yoy", "mom", "change", "rebase", "zscore",
    "ann_return", "cagr", "ann_vol", "sharpe", "sortino", "max_drawdown", "calmar",
    "summary", "infer_ppy", "factor_regression", "FactorResult",
    "apply_style", "style_context", "PALETTE", "__version__",
]
