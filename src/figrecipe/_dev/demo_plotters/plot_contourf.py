#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contourf: filled contour plot demo."""

import numpy as np


def plot_contourf(plt, rng, ax=None):
    """Filled contour plot demo.

    Demonstrates: ax.contourf()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X**2 + Y**2))
    ax.contourf(X, Y, Z, id="contourf")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("contourf")
    return fig, ax


# EOF
