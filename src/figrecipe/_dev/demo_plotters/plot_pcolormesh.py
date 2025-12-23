#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pcolormesh: pseudocolor mesh plot demo."""

import numpy as np


def plot_pcolormesh(plt, rng, ax=None):
    """Pseudocolor mesh plot demo.

    Demonstrates: ax.pcolormesh()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.linspace(0, 2 * np.pi, 50)
    y = np.linspace(0, 2 * np.pi, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    ax.pcolormesh(X, Y, Z, id="pcolormesh")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("pcolormesh")
    return fig, ax


# EOF
