#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""boxplot: box plot demo."""


def plot_boxplot(plt, rng, ax=None):
    """Box plot demo.

    Demonstrates: ax.boxplot()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    data = [rng.normal(i, 1, 100) for i in range(4)]
    ax.boxplot(data, tick_labels=["A", "B", "C", "D"], id="boxplot")
    ax.set_xlabel("Group")
    ax.set_ylabel("Value")
    ax.set_title("boxplot")
    return fig, ax


# EOF
