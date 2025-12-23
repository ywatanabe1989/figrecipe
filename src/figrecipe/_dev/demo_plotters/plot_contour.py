#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contour: contour plot demo."""

import numpy as np


def plot_contour(plt, rng, ax=None):
    """Contour plot demo.

    Demonstrates: ax.contour()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X**2 + Y**2))
    cs = ax.contour(X, Y, Z, id="contour")
    ax.clabel(cs)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("contour")
    return fig, ax


# EOF
