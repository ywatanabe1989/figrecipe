#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fill: filled polygon demo."""

import numpy as np


def plot_fill(plt, rng, ax=None):
    """Filled polygon demo.

    Demonstrates: ax.fill()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    theta = np.linspace(0, 2 * np.pi, 6)
    x = np.cos(theta)
    y = np.sin(theta)
    ax.fill(x, y, alpha=0.5, id="fill")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("fill")
    ax.set_aspect("equal")
    return fig, ax


# EOF
