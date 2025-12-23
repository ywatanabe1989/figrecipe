#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ecdf: empirical CDF demo."""


def plot_ecdf(plt, rng, ax=None):
    """Empirical CDF demo.

    Demonstrates: ax.ecdf()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    data = rng.normal(0, 1, 100)
    ax.ecdf(data, id="ecdf")
    ax.set_xlabel("Value")
    ax.set_ylabel("Cumulative Probability")
    ax.set_title("ecdf")
    return fig, ax


# EOF
