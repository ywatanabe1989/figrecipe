#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fill_betweenx: horizontal filled area demo."""

import numpy as np


def plot_fill_betweenx(plt, rng, ax=None):
    """Horizontal filled area demo.

    Demonstrates: ax.fill_betweenx()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    y = np.linspace(0, 10, 100)
    x1 = np.sin(y)
    x2 = np.sin(y) + 0.5
    ax.fill_betweenx(y, x1, x2, alpha=0.5, id="fill_betweenx")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("fill_betweenx")
    return fig, ax


# EOF
