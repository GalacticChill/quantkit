# quantkit

A small, dependency-light **quant toolkit** for Python: keyless data loaders,
return conversions & performance metrics, factor regressions, and a clean
matplotlib style.

It grew out of a stream of finance/data browser tools
([Fee Drag](https://galacticchill.github.io/fee-drag/),
[Tearsheet](https://galacticchill.github.io/tearsheet/),
[FRED Explorer](https://galacticchill.github.io/fred-explorer/),
[Factor Decomposer](https://galacticchill.github.io/factor-decomposer/)) —
the utilities those tools proved out, packaged properly with tests and docs.

## Install

```bash
pip install git+https://github.com/GalacticChill/quantkit
# or, for local development:
git clone https://github.com/GalacticChill/quantkit && cd quantkit
pip install -e ".[dev]"
```

Requires Python ≥ 3.9 and `numpy`, `pandas`, `matplotlib`.

## What's inside

| Module | Functions |
| --- | --- |
| `quantkit.data` | `load_fred`, `load_ff_factors`, `load_ff_portfolios`, `load_prices`, `load_returns` |
| `quantkit.returns` | `to_returns`, `yoy`, `mom`, `change`, `rebase`, `zscore` · `cagr`, `ann_return`, `ann_vol`, `sharpe`, `sortino`, `max_drawdown`, `calmar`, `summary` · `factor_regression` |
| `quantkit.plotting` | `apply_style`, `style_context`, `PALETTE` |

All loaders are **keyless** and cache raw downloads under `~/.cache/quantkit`.

## Quick start

```python
import quantkit as qk

# 1. Load some economic data (keyless FRED)
unrate = qk.load_fred("UNRATE")
print(qk.yoy(qk.load_fred("CPIAUCSL")).tail())   # CPI inflation, YoY

# 2. Performance metrics on a return series
px = qk.load_prices("SPY")            # Yahoo adjusted close
r  = qk.to_returns(px)
print(qk.summary(r, rf=0.02))          # cagr, vol, Sharpe, max drawdown, ...

# 3. Factor exposure (Fama-French 5 + Momentum)
factors = qk.load_ff_factors(model="5", momentum=True)
res = qk.factor_regression(r, factors)  # 'RF' column auto-used for excess return
print(res.summary())
#   alpha (annualised) : +1.2%   t=+0.8
#   Mkt-RF     +0.99   t=+61.2
#   SMB        -0.14   t=-4.1
#   ...

# 4. Plots that match the tool family's look
import matplotlib.pyplot as plt
with qk.style_context():
    ((1 + r).cumprod()).plot(title="SPY — growth of $1")
    plt.show()
```

## Data sources & attribution

- **FRED** — Federal Reserve Bank of St. Louis (`fredgraph.csv`), public-domain U.S. series.
- **Ken French Data Library** — Fama-French factors and portfolios (Eugene F. Fama & Kenneth R. French).
- **Yahoo Finance** — adjusted-close prices via the public chart endpoint, for educational use.

This library is for research/education and is **not investment advice**.

## Development

```bash
pip install -e ".[dev]"
pytest                 # unit tests (offline)
QUANTKIT_NET=1 pytest  # also run the network integration tests
```

## License

MIT — see [LICENSE](LICENSE).
