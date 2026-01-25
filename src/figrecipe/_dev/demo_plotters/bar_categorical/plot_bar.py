#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bar: bar chart demo."""

from figrecipe.styles import load_style


def plot_bar(plt, rng, ax=None):
    """Bar chart demo with different colors for each bar.

    Demonstrates: ax.bar() with SCITEX color palette
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

    # Plot bars with different colors
    ax.bar(categories, values, color=colors, id="bar")
    ax.set_xlabel("Category")
    ax.set_ylabel("Value")
    ax.set_title("bar")
    return fig, ax


# EOF
