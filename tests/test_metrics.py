import numpy as np
import pandas as pd

import quantkit as qk


def _months(n, start="2000-01"):
    return pd.period_range(start, periods=n, freq="M")


def test_infer_ppy_monthly():
    assert qk.infer_ppy(_months(24)) == 12


def test_infer_ppy_datetime_resolutions():
    # monthly DatetimeIndex at second resolution (as Yahoo loader produces)
    dt_s = pd.to_datetime(pd.period_range("2000-01", periods=36, freq="M").to_timestamp(), unit="s")
    assert qk.infer_ppy(pd.DatetimeIndex(dt_s.values.astype("datetime64[s]"))) == 12
    # daily business-day index -> 252
    assert qk.infer_ppy(pd.bdate_range("2020-01-01", periods=60)) == 252


def test_cagr_constant():
    r = pd.Series([0.01] * 12, index=_months(12))
    # 12 monthly periods, one year -> growth ** (12/12) - 1
    assert np.isclose(qk.cagr(r), 1.01 ** 12 - 1.0)


def test_ann_vol_zero_for_constant():
    r = pd.Series([0.01] * 24, index=_months(24))
    assert np.isclose(qk.ann_vol(r), 0.0)


def test_max_drawdown():
    # equity: 1.1, 0.55, 0.605 -> trough at 0.55 vs peak 1.1 = -50%
    r = pd.Series([0.10, -0.50, 0.10])
    assert np.isclose(qk.max_drawdown(r), -0.5)


def test_sharpe_positive_and_scales():
    r = pd.Series([0.02, 0.01, 0.03, 0.02, 0.015, 0.025], index=_months(6))
    assert qk.sharpe(r) > 0
    # higher rf lowers Sharpe
    assert qk.sharpe(r, rf=0.10) < qk.sharpe(r, rf=0.0)


def test_summary_keys():
    r = pd.Series([0.01, -0.02, 0.03, 0.0, 0.015], index=_months(5))
    s = qk.summary(r)
    for key in ["cagr", "ann_vol", "sharpe", "sortino", "max_drawdown", "calmar", "n"]:
        assert key in s.index
    assert s["n"] == 5
