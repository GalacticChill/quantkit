"""Load factors and portfolios from the Ken French Data Library.

The library ships zipped CSVs whose first table is monthly returns *in percent*,
followed by other tables (equal-weighted, annual, firm counts, ...). We parse
only that first monthly block and convert to decimal returns.
"""
from __future__ import annotations

import io
import re
import zipfile

import pandas as pd

from ._http import fetch

_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/{}_CSV.zip"
_MISSING = (-99.99, -999.0)


def _first_monthly_block(text: str) -> pd.DataFrame:
    """Parse the first ``YYYYMM,...`` monthly table into a DataFrame (percent)."""
    lines = text.split("\n")
    header, rows, periods, started = None, [], [], False
    for i, ln in enumerate(lines):
        s = ln.strip()
        m = re.match(r"^(\d{6}),(.+)$", s)
        if m:
            if not started:
                j = i - 1
                while j >= 0 and not lines[j].strip():
                    j -= 1
                header = [c.strip() for c in lines[j].split(",")][1:]  # drop leading blank
                started = True
            periods.append(m.group(1))
            vals = []
            for c in s.split(",")[1:]:
                try:
                    f = float(c)
                except ValueError:
                    f = float("nan")
                vals.append(float("nan") if f in _MISSING else f)
            rows.append(vals)
        elif started:
            break  # end of the first monthly block
    idx = pd.PeriodIndex([f"{p[:4]}-{p[4:]}" for p in periods], freq="M", name="date")
    return pd.DataFrame(rows, columns=header, index=idx)


def _load_first_block(name: str, cache: bool = True) -> pd.DataFrame:
    data = fetch(_URL.format(name), cache=cache)
    zf = zipfile.ZipFile(io.BytesIO(data))
    member = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
    return _first_monthly_block(zf.read(member).decode("latin-1"))


def load_ff_factors(model: str = "5", momentum: bool = True, cache: bool = True) -> pd.DataFrame:
    """Return Fama-French factors (decimal, monthly ``PeriodIndex``).

    Parameters
    ----------
    model : {"3", "5"}
        FF3 (``Mkt-RF, SMB, HML, RF``) or FF5 (adds ``RMW, CMA``).
    momentum : bool
        Join the momentum factor as column ``Mom`` (default True).
    """
    key = str(model)
    if key in ("5", "ff5"):
        df = _load_first_block("F-F_Research_Data_5_Factors_2x3", cache)
    elif key in ("3", "ff3"):
        df = _load_first_block("F-F_Research_Data_Factors", cache)
    else:
        raise ValueError("model must be '3' or '5'")
    df = df / 100.0
    if momentum:
        mom = _load_first_block("F-F_Momentum_Factor", cache) / 100.0
        mom.columns = ["Mom"]
        df = df.join(mom, how="inner")
    return df


def load_ff_portfolios(name: str, cache: bool = True) -> pd.DataFrame:
    """Return the first monthly block of any Ken French dataset (decimal).

    ``name`` is the library's dataset stem, e.g. ``"6_Portfolios_2x3"`` or
    ``"10_Portfolios_Prior_12_2"``.
    """
    return _load_first_block(name, cache) / 100.0
