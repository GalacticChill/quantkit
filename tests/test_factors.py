import numpy as np
import pandas as pd

import quantkit as qk


def _factors(n=120, seed=0):
    idx = pd.period_range("2005-01", periods=n, freq="M")
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "Mkt-RF": rng.normal(0.008, 0.043, n),
        "SMB": rng.normal(0.001, 0.030, n),
        "HML": rng.normal(0.002, 0.028, n),
        "RF": np.full(n, 0.002),
    }, index=idx)


def test_recovers_known_betas_and_uses_rf():
    f = _factors()
    # asset RAW return = RF + alpha + 1.2*Mkt + 0.4*SMB - 0.3*HML  (no noise)
    y = f["RF"] + 0.001 + 1.2 * f["Mkt-RF"] + 0.4 * f["SMB"] - 0.3 * f["HML"]
    res = qk.factor_regression(y, f)  # RF auto-detected -> excess return
    assert np.isclose(res.params["Mkt-RF"], 1.2, atol=1e-9)
    assert np.isclose(res.params["SMB"], 0.4, atol=1e-9)
    assert np.isclose(res.params["HML"], -0.3, atol=1e-9)
    assert np.isclose(res.alpha, 0.001, atol=1e-9)
    assert res.rsquared > 0.9999
    assert res.nobs == 120


def test_rf_column_not_used_as_regressor():
    f = _factors()
    y = f["RF"] + 1.0 * f["Mkt-RF"]
    res = qk.factor_regression(y, f)
    assert "RF" not in res.betas.index
    assert list(res.betas.index) == ["Mkt-RF", "SMB", "HML"]


def test_model_subset():
    f = _factors()
    y = f["RF"] + 1.1 * f["Mkt-RF"] + 0.5 * f["SMB"]
    res = qk.factor_regression(y, f, model=["Mkt-RF", "SMB"])
    assert list(res.betas.index) == ["Mkt-RF", "SMB"]
    assert np.isclose(res.params["Mkt-RF"], 1.1, atol=1e-9)


def test_datetime_index_aligns_to_monthly():
    f = _factors()
    y = f["RF"] + 0.9 * f["Mkt-RF"]
    y_dt = y.copy()
    y_dt.index = y.index.to_timestamp()  # DatetimeIndex asset vs PeriodIndex factors
    res = qk.factor_regression(y_dt, f)
    assert np.isclose(res.params["Mkt-RF"], 0.9, atol=1e-9)
    assert res.nobs == 120


def test_too_few_obs_raises():
    f = _factors(n=3)
    y = f["RF"] + f["Mkt-RF"]
    try:
        qk.factor_regression(y, f)
        assert False, "expected ValueError"
    except ValueError:
        pass
