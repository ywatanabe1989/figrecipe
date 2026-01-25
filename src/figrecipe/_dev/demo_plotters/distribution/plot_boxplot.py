#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""boxplot: box plot demo."""

from figrecipe.styles import load_style


def plot_boxplot(plt, rng, ax=None):
    """Box plot demo with different colors for each group.

    Demonstrates: ax.boxplot() with SCITEX color palette
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:4]]

    # Generate data for 4 groups
    data = [rng.normal(i, 1, 100) for i in range(4)]

    # Plot boxplot with different colors for each box
    ax.boxplot(data, tick_labels=["A", "B", "C", "D"], color=colors, id="boxplot")
    ax.set_xlabel("Group")
    ax.set_ylabel("Value")
    ax.set_title("boxplot")
    return fig, ax


# EOF
