#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stairs: staircase plot demo."""

import numpy as np


def plot_stairs(plt, rng, ax=None):
    """Staircase plot demo.

    Demonstrates: ax.stairs()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    values = rng.uniform(1, 5, 10)
    edges = np.arange(11)
    ax.stairs(values, edges, fill=True, alpha=0.5, id="stairs")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("stairs")
    return fig, ax


# EOF
