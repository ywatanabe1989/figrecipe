#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stackplot: stacked area plot demo."""

import numpy as np


def plot_stackplot(plt, rng, ax=None):
    """Stacked area plot demo.

    Demonstrates: ax.stackplot()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.arange(10)
    y1 = rng.uniform(1, 3, 10)
    y2 = rng.uniform(1, 3, 10)
    y3 = rng.uniform(1, 3, 10)
    ax.stackplot(x, y1, y2, y3, id="stackplot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("stackplot")
    return fig, ax


# EOF
