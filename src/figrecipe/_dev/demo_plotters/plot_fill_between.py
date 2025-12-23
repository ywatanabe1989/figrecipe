#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fill_between: filled area between curves demo."""

import numpy as np


def plot_fill_between(plt, rng, ax=None):
    """Filled area between curves demo.

    Demonstrates: ax.fill_between()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.sin(x) + 0.5
    ax.fill_between(x, y1, y2, alpha=0.5, id="fill_between")
    ax.plot(x, y1, id="lower")
    ax.plot(x, y2, id="upper")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("fill_between")
    return fig, ax


# EOF
