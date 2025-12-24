#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""acorr: autocorrelation demo."""


def plot_acorr(plt, rng, ax=None):
    """Autocorrelation demo.

    Demonstrates: ax.acorr()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = rng.normal(0, 1, 100)
    ax.acorr(x, maxlags=50, id="acorr")
    ax.set_xlabel("Lag")
    ax.set_ylabel("Autocorrelation")
    ax.set_title("acorr")
    return fig, ax


# EOF
