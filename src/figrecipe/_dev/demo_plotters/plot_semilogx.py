#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""semilogx: semi-log X plot demo."""

import numpy as np


def plot_semilogx(plt, rng, ax=None):
    """Semi-log X plot demo.

    Demonstrates: ax.semilogx()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.logspace(0, 3, 50)
    y = np.log10(x)
    ax.semilogx(x, y, id="semilogx")
    ax.set_xlabel("X (log)")
    ax.set_ylabel("Y")
    ax.set_title("semilogx")
    return fig, ax


# EOF
