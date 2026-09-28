import numpy as np
import pandas as pd

import quantkit as qk


def _months(n, start="2020-01"):
    return pd.period_range(start, periods=n, freq="M")


def test_to_returns_simple():
    p = pd.Series([100.0, 110.0, 99.0], index=_months(3))
    r = qk.to_returns(p)
    assert len(r) == 2
    assert np.isclose(r.iloc[0], 0.10)
    assert np.isclose(r.iloc[1], -0.10)


def test_to_returns_log():
    p = pd.Series([100.0, 200.0], index=_months(2))
    r = qk.to_returns(p, kind="log")
    assert np.isclose(r.iloc[0], np.log(2.0))


def test_rebase():
    s = pd.Series([50.0, 75.0, 100.0])
    r = qk.rebase(s)
    assert np.isclose(r.iloc[0], 100.0)
    assert np.isclose(r.iloc[-1], 200.0)


def test_yoy():
    s = pd.Series(np.arange(1, 25, dtype=float), index=_months(24))
    y = qk.yoy(s)
    assert np.isnan(y.iloc[0])
    # value 13 twelve months after value 1 -> +1200%
    assert np.isclose(y.iloc[12], 13.0 / 1.0 - 1.0)


def test_mom_and_change():
    s = pd.Series([10.0, 11.0, 11.0], index=_months(3))
    assert np.isclose(qk.mom(s).iloc[1], 0.10)
    assert np.isclose(qk.change(s).iloc[1], 1.0)


def test_zscore():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    z = qk.zscore(s)
    assert np.isclose(z.mean(), 0.0, atol=1e-12)
    assert np.isclose(z.std(), 1.0)
