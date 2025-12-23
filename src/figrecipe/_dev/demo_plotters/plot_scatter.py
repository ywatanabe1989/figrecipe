#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scatter: scatter plot demo."""


def plot_scatter(plt, rng, ax=None):
    """Scatter plot demo.

    Demonstrates: ax.scatter()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x, y = rng.uniform(0, 10, 50), rng.uniform(0, 10, 50)
    ax.scatter(x, y, id="scatter")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("scatter")
    return fig, ax


# EOF
