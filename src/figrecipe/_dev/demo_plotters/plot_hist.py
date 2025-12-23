#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hist: histogram demo."""


def plot_hist(plt, rng, ax=None):
    """Histogram demo.

    Demonstrates: ax.hist()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    data = rng.normal(0, 1, 500)
    ax.hist(data, bins=30, id="hist")
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    ax.set_title("hist")
    return fig, ax


# EOF
