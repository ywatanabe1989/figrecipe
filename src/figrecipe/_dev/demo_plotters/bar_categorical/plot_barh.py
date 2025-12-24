#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""barh: horizontal bar chart demo."""


def plot_barh(plt, rng, ax=None):
    """Horizontal bar chart demo.

    Demonstrates: ax.barh()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    categories = ["A", "B", "C", "D", "E"]
    values = rng.integers(1, 10, 5)
    ax.barh(categories, values, id="barh")
    ax.set_xlabel("Value")
    ax.set_ylabel("Category")
    ax.set_title("barh")
    return fig, ax


# EOF
