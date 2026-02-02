#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bar: bar chart demo."""

from figrecipe.styles import load_style


def plot_bar(plt, rng, ax=None):
    """Bar chart demo with grouped bars and legend.

    Demonstrates: ax.bar() with SCITEX color palette and legend
    """
    import numpy as np

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    # Generate grouped bar data
    categories = ["A", "B", "C", "D"]
    x = np.arange(len(categories))
    width = 0.25

    # Three groups with legend
    for i, (label, color) in enumerate(zip(["2022", "2023", "2024"], colors)):
        values = rng.integers(3, 10, len(categories))
        ax.bar(x + i * width, values, width, label=label, color=color, id=f"bar_{i}")

    ax.set_xlabel("Category")
    ax.set_ylabel("Value")
    ax.set_title("bar")
    ax.set_xticks(x + width)
    ax.set_xticklabels(categories)
    ax.legend()
    return fig, ax


# EOF
