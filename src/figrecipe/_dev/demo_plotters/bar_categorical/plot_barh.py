#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""barh: horizontal bar chart demo."""

from figrecipe.styles import load_style


def plot_barh(plt, rng, ax=None):
    """Horizontal bar chart demo with different colors for each bar.

    Demonstrates: ax.barh() with SCITEX color palette
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:5]]

    # Generate data for 5 categories
    categories = ["A", "B", "C", "D", "E"]
    values = rng.integers(1, 10, 5)

    # Plot horizontal bars with different colors
    ax.barh(categories, values, color=colors, id="barh")
    ax.set_xlabel("Value")
    ax.set_ylabel("Category")
    ax.set_title("barh")
    return fig, ax


# EOF
