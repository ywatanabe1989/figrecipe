#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stem: stem plot demo."""

import numpy as np


def plot_stem(plt, rng, ax=None):
    """Stem plot demo.

    Demonstrates: ax.stem()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.arange(10)
    y = rng.uniform(0, 1, 10)
    ax.stem(x, y, id="stem")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("stem")
    return fig, ax


# EOF
