#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pie: pie chart demo."""

import matplotlib.pyplot as mpl_plt


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
    # Get colors from current style's color cycle
    colors = mpl_plt.rcParams["axes.prop_cycle"].by_key()["color"][:4]
    ax.pie(sizes, labels=labels, colors=colors, id="pie")
    ax.set_title("pie")
    return fig, ax


# EOF
