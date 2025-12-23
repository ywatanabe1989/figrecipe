#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spy: sparse matrix visualization demo."""

import numpy as np


def plot_spy(plt, rng, ax=None):
    """Sparse matrix visualization demo.

    Demonstrates: ax.spy()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Create sparse-like matrix
    data = np.zeros((20, 20))
    for _ in range(50):
        i, j = rng.integers(0, 20, 2)
        data[i, j] = 1
    ax.spy(data, id="spy")
    ax.axis("off")
    ax.set_title("spy")
    return fig, ax


# EOF
