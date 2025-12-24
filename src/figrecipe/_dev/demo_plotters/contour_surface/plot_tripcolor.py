#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tripcolor: unstructured triangular grid demo."""

import numpy as np


def plot_tripcolor(plt, rng, ax=None):
    """Unstructured triangular grid demo.

    Demonstrates: ax.tripcolor()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Create random triangulation
    x = rng.uniform(0, 1, 30)
    y = rng.uniform(0, 1, 30)
    z = np.sin(x * 2 * np.pi) * np.cos(y * 2 * np.pi)
    ax.tripcolor(x, y, z, id="tripcolor")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("tripcolor")
    return fig, ax


# EOF
