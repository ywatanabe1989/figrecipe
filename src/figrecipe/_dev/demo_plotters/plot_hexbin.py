#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hexbin: hexagonal binning demo."""


def plot_hexbin(plt, rng, ax=None):
    """Hexagonal binning demo.

    Demonstrates: ax.hexbin()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = rng.normal(0, 1, 1000)
    y = rng.normal(0, 1, 1000)
    ax.hexbin(x, y, id="hexbin")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("hexbin")
    return fig, ax


# EOF
