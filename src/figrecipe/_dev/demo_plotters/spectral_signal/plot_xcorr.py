#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xcorr: cross-correlation demo."""


def plot_xcorr(plt, rng, ax=None):
    """Cross-correlation demo.

    Demonstrates: ax.xcorr()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = rng.normal(0, 1, 100)
    y = rng.normal(0, 1, 100)
    ax.xcorr(x, y, maxlags=50, id="xcorr")
    ax.set_xlabel("Lag")
    ax.set_ylabel("Cross-correlation")
    ax.set_title("xcorr")
    return fig, ax


# EOF
