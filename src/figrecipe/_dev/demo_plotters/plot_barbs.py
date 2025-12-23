#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""barbs: wind barbs demo."""

import numpy as np


def plot_barbs(plt, rng, ax=None):
    """Wind barbs demo.

    Demonstrates: ax.barbs()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.arange(0, 5, 1)
    y = np.arange(0, 5, 1)
    X, Y = np.meshgrid(x, y)
    U = rng.uniform(-10, 10, X.shape)
    V = rng.uniform(-10, 10, Y.shape)
    ax.barbs(X, Y, U, V, id="barbs")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("barbs")
    return fig, ax


# EOF
