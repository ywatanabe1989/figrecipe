#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""loglog: log-log plot demo."""

import numpy as np


def plot_loglog(plt, rng, ax=None):
    """Log-log plot demo.

    Demonstrates: ax.loglog()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.logspace(0, 3, 50)
    y = x**2
    ax.loglog(x, y, id="loglog")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("loglog")
    return fig, ax


# EOF
