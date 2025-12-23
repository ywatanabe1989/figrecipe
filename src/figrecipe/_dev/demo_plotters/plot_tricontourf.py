#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tricontourf: filled triangular contour demo."""

import numpy as np


def plot_tricontourf(plt, rng, ax=None):
    """Filled triangular contour demo.

    Demonstrates: ax.tricontourf()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = rng.uniform(0, 1, 50)
    y = rng.uniform(0, 1, 50)
    z = np.sin(x * 2 * np.pi) * np.cos(y * 2 * np.pi)
    ax.tricontourf(x, y, z, id="tricontourf")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("tricontourf")
    return fig, ax


# EOF
