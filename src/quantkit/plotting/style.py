"""A clean, light "editorial report" matplotlib style.

This is the Python expression of the palette shared across the browser tools
(deep navy ink, emerald brand, red for negatives, steel-blue for a second
series) so charts made with quantkit match the rest of the family.
"""
from __future__ import annotations

import matplotlib as mpl
from cycler import cycler

PALETTE = {
    "ink": "#0d1b2a",
    "ink2": "#34465a",
    "muted": "#6b7c8f",
    "faint": "#9aa8b6",
    "line": "#e6e9ef",
    "paper": "#ffffff",
    "brand": "#0e8f6e",   # primary / positive
    "pos": "#1a936f",
    "neg": "#d1495b",     # negative
    "accent2": "#2f6f9f", # comparison series
    "warn": "#d98c33",
}

COLOR_CYCLE = [PALETTE["brand"], PALETTE["accent2"], PALETTE["warn"],
               PALETTE["neg"], PALETTE["ink"], PALETTE["muted"]]


def rc_params() -> dict:
    """Return the rcParams dict for the quantkit style."""
    p = PALETTE
    return {
        "figure.facecolor": p["paper"],
        "figure.edgecolor": p["paper"],
        "axes.facecolor": p["paper"],
        "axes.edgecolor": p["line"],
        "axes.labelcolor": p["ink2"],
        "axes.titlecolor": p["ink"],
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.linewidth": 1.0,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.prop_cycle": cycler(color=COLOR_CYCLE),
        "grid.color": p["line"],
        "grid.linewidth": 1.0,
        "text.color": p["ink"],
        "xtick.color": p["muted"],
        "ytick.color": p["muted"],
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "lines.linewidth": 2.2,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    }


def apply_style() -> None:
    """Apply the quantkit style to the global matplotlib rcParams."""
    mpl.rcParams.update(rc_params())


def style_context():
    """Return a context manager applying the style temporarily.

    >>> import matplotlib.pyplot as plt
    >>> with style_context():
    ...     fig, ax = plt.subplots()
    ...     ax.plot([1, 2, 3])
    """
    return mpl.rc_context(rc_params())
