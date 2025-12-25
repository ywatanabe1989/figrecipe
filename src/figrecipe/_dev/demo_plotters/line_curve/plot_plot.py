#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plot: line plot demo."""

import numpy as np


def plot_plot(plt, rng, ax=None):
    """Line plot demo.

    Demonstrates: ax.plot()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), label="sin", id="sin")
    ax.plot(x, np.cos(x), label="cos", id="cos")
    ax.legend()
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("plot")
    return fig, ax


# EOF
