#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""errorbar: error bar plot demo."""

import numpy as np


def plot_errorbar(plt, rng, ax=None):
    """Error bar plot demo.

    Demonstrates: ax.errorbar()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.arange(5)
    y = rng.uniform(2, 8, 5)
    yerr = rng.uniform(0.3, 0.8, 5)
    ax.errorbar(x, y, yerr=yerr, id="errorbar")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("errorbar")
    return fig, ax


# EOF
