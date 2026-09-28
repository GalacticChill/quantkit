"""Network integration tests. Skipped unless QUANTKIT_NET=1 is set."""
import os

import pytest

import quantkit as qk

pytestmark = pytest.mark.integration

_NET = os.environ.get("QUANTKIT_NET") == "1"
skip = pytest.mark.skipif(not _NET, reason="network test; set QUANTKIT_NET=1 to run")


@skip
def test_load_fred():
    s = qk.load_fred("UNRATE")
    assert len(s) > 500
    assert s.name == "UNRATE"


@skip
def test_load_ff_factors():
    f = qk.load_ff_factors(model="5", momentum=True)
    for col in ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF", "Mom"]:
        assert col in f.columns
    # decimal scale: monthly market factor magnitudes are well under 1
    assert f["Mkt-RF"].abs().median() < 0.1


@skip
def test_load_ff_portfolios():
    p = qk.load_ff_portfolios("6_Portfolios_2x3")
    assert p.shape[1] == 6


@skip
def test_yahoo_and_regression_end_to_end():
    px = qk.load_prices("SPY", range="10y")
    r = qk.to_returns(px)
    assert len(r) > 24
    f = qk.load_ff_factors(model="5")
    res = qk.factor_regression(r, f)
    # SPY is the market: beta near 1, high R^2
    assert 0.8 < res.params["Mkt-RF"] < 1.2
    assert res.rsquared > 0.85
