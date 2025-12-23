#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pcolor: pseudocolor plot demo."""

import numpy as np


def plot_pcolor(plt, rng, ax=None):
    """Pseudocolor plot demo.

    Demonstrates: ax.pcolor()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.arange(0, 10, 1)
    y = np.arange(0, 10, 1)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    ax.pcolor(X, Y, Z, id="pcolor")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("pcolor")
    return fig, ax


# EOF
