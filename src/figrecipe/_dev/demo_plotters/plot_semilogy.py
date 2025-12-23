#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""semilogy: semi-log Y plot demo."""

import numpy as np


def plot_semilogy(plt, rng, ax=None):
    """Semi-log Y plot demo.

    Demonstrates: ax.semilogy()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.linspace(0, 5, 50)
    y = np.exp(x)
    ax.semilogy(x, y, id="semilogy")
    ax.set_xlabel("X")
    ax.set_ylabel("Y (log)")
    ax.set_title("semilogy")
    return fig, ax


# EOF
