"""Factor regression: OLS of excess returns on a set of factors.

Regresses an asset/portfolio's excess return on factor returns (e.g. the
Fama-French factors) and reports loadings with proper inference: standard
errors, t-stats, R^2 and adjusted R^2.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class FactorResult:
    """Result of :func:`factor_regression`."""

    params: pd.Series      # includes "alpha" (the intercept, per period)
    se: pd.Series
    tstats: pd.Series
    rsquared: float
    rsquared_adj: float
    nobs: int

    @property
    def alpha(self) -> float:
        return float(self.params["alpha"])

    @property
    def betas(self) -> pd.Series:
        return self.params.drop("alpha")

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame({"coef": self.params, "std_err": self.se, "t": self.tstats})

    def summary(self, ppy: int = 12) -> str:
        lines = [
            f"Factor regression  (n={self.nobs}, R^2={self.rsquared:.3f}, adj={self.rsquared_adj:.3f})",
            f"  alpha (annualised) : {self.alpha * ppy:+.2%}   t={self.tstats['alpha']:+.2f}",
        ]
        for name in self.betas.index:
            lines.append(f"  {name:<10s} {self.params[name]:+.3f}   t={self.tstats[name]:+.2f}")
        return "\n".join(lines)


def _to_month_period(obj):
    """Align on monthly periods when either side is dated (factors are monthly).

    Also collapses duplicate months (e.g. Yahoo appends an intraday "current"
    point in the latest month) by keeping the last observation per month.
    """
    if isinstance(obj.index, pd.DatetimeIndex):
        obj = obj.copy()
        obj.index = obj.index.to_period("M")
    if obj.index.has_duplicates:
        obj = obj.groupby(level=0).last()
    return obj


def factor_regression(asset_returns, factors, rf=None, model=None) -> FactorResult:
    """Regress ``asset_returns`` excess return on ``factors``.

    Parameters
    ----------
    asset_returns : Series
        Periodic returns of the asset/portfolio (fractional).
    factors : DataFrame
        Factor returns (fractional). If a ``"RF"`` column is present it is used
        as the risk-free rate (and excluded from the regressors) unless ``rf``
        is given explicitly.
    rf : str | float | Series | None
        Risk-free rate: a column name in ``factors``, a per-period Series, a
        constant per-period rate, or ``None`` to auto-use a ``"RF"`` column.
    model : list[str] | None
        Subset/order of factor columns to use. Defaults to all non-RF columns.

    Returns
    -------
    FactorResult
    """
    asset = _to_month_period(pd.Series(asset_returns).astype(float).rename("y"))
    fac = _to_month_period(pd.DataFrame(factors).astype(float))

    rf_series = None
    if isinstance(rf, str):
        rf_series = fac[rf]
        fac = fac.drop(columns=[rf])
    elif isinstance(rf, pd.Series):
        rf_series = _to_month_period(rf.astype(float))
    elif rf is None and "RF" in fac.columns:
        rf_series = fac["RF"]
        fac = fac.drop(columns=["RF"])

    if "RF" in fac.columns:               # never regress on RF
        fac = fac.drop(columns=["RF"])
    cols = list(fac.columns) if model is None else list(model)

    parts = {"y": asset}
    for c in cols:
        parts[c] = fac[c]
    if rf_series is not None:
        parts["__rf"] = rf_series
    df = pd.concat(parts, axis=1).dropna()

    if rf_series is not None:
        y = (df["y"] - df["__rf"]).to_numpy()
    else:
        const = float(rf) if isinstance(rf, (int, float)) else 0.0
        y = (df["y"] - const).to_numpy()

    n = len(df)
    k = len(cols) + 1
    if n <= k:
        raise ValueError(f"not enough overlapping observations ({n}) for {k} parameters")

    X = np.column_stack([np.ones(n)] + [df[c].to_numpy() for c in cols])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    rss = float(resid @ resid)
    tss = float(((y - y.mean()) ** 2).sum())
    s2 = rss / (n - k)
    xtx_inv = np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(s2 * xtx_inv))
    with np.errstate(divide="ignore", invalid="ignore"):
        t = beta / se

    names = ["alpha"] + cols
    return FactorResult(
        params=pd.Series(beta, index=names),
        se=pd.Series(se, index=names),
        tstats=pd.Series(t, index=names),
        rsquared=(1.0 - rss / tss) if tss > 0 else float("nan"),
        rsquared_adj=(1.0 - (rss / (n - k)) / (tss / (n - 1))) if tss > 0 else float("nan"),
        nobs=n,
    )
