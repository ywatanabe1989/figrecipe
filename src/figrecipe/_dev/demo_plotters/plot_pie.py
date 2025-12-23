#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pie: pie chart demo."""


def plot_pie(plt, rng, ax=None):
    """Pie chart demo.

    Demonstrates: ax.pie()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    sizes = [35, 25, 20, 20]
    labels = ["A", "B", "C", "D"]
    ax.pie(sizes, labels=labels, id="pie")
    ax.set_title("pie")
    return fig, ax


# EOF
