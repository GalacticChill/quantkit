import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

import quantkit as qk  # noqa: E402


def test_palette_has_core_colors():
    for key in ["ink", "brand", "neg", "accent2"]:
        assert key in qk.PALETTE
        assert qk.PALETTE[key].startswith("#")


def test_apply_style_sets_rcparams():
    qk.apply_style()
    assert matplotlib.rcParams["axes.spines.top"] is False
    assert matplotlib.rcParams["axes.spines.right"] is False


def test_style_context_plots_without_error():
    with qk.style_context():
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [3, 1, 2])
        ax.set_title("quantkit")
    plt.close("all")
