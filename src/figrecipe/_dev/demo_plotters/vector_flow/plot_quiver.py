#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quiver: vector field demo."""

import numpy as np


def plot_quiver(plt, rng, ax=None):
    """Vector field demo.

    Demonstrates: ax.quiver()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.arange(0, 10, 1)
    y = np.arange(0, 10, 1)
    X, Y = np.meshgrid(x, y)
    U = np.cos(X * 0.5)
    V = np.sin(Y * 0.5)
    ax.quiver(X, Y, U, V, id="quiver")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("quiver")
    return fig, ax


# EOF
