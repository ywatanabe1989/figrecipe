#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bar: bar chart demo."""


def plot_bar(plt, rng, ax=None):
    """Bar chart demo.

    Demonstrates: ax.bar()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    categories = ["A", "B", "C", "D", "E"]
    values = rng.integers(1, 10, 5)
    ax.bar(categories, values, id="bar")
    ax.set_xlabel("Category")
    ax.set_ylabel("Value")
    ax.set_title("bar")
    return fig, ax


# EOF
