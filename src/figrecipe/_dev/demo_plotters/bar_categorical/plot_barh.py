#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""barh: horizontal bar chart demo."""

from figrecipe.styles import load_style


def plot_barh(plt, rng, ax=None):
    """Horizontal bar chart demo with grouped bars and legend.

    Demonstrates: ax.barh() with SCITEX color palette and legend
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
    y = np.arange(len(categories))
    height = 0.25

    # Three groups with legend
    for i, (label, color) in enumerate(zip(["2022", "2023", "2024"], colors)):
        values = rng.integers(3, 10, len(categories))
        ax.barh(
            y + i * height, values, height, label=label, color=color, id=f"barh_{i}"
        )

    ax.set_xlabel("Value")
    ax.set_ylabel("Category")
    ax.set_title("barh")
    ax.set_yticks(y + height)
    ax.set_yticklabels(categories)
    ax.legend()
    return fig, ax


# EOF
