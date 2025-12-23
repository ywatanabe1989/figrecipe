#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""streamplot: streamline plot demo."""

import numpy as np


def plot_streamplot(plt, rng, ax=None):
    """Streamline plot demo.

    Demonstrates: ax.streamplot()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.linspace(-3, 3, 30)
    y = np.linspace(-3, 3, 30)
    X, Y = np.meshgrid(x, y)
    U = -Y
    V = X
    ax.streamplot(X, Y, U, V, id="streamplot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("streamplot")
    return fig, ax


# EOF
