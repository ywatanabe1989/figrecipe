#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""triplot: triangular mesh plot demo."""


def plot_triplot(plt, rng, ax=None):
    """Triangular mesh plot demo.

    Demonstrates: ax.triplot()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = rng.uniform(0, 1, 20)
    y = rng.uniform(0, 1, 20)
    ax.triplot(x, y, id="triplot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("triplot")
    return fig, ax


# EOF
