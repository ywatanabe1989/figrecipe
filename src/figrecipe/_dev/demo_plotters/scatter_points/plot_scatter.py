#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scatter: scatter plot demo."""

from figrecipe.styles import load_style


def plot_scatter(plt, rng, ax=None):
    """Scatter plot demo with multiple groups in different colors.

    Demonstrates: ax.scatter() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    # Generate data for 3 groups with different distributions
    groups = ["Group A", "Group B", "Group C"]
    for i, (label, color) in enumerate(zip(groups, colors)):
        x = rng.uniform(i * 3, i * 3 + 4, 20)
        y = rng.uniform(0, 10, 20)
        ax.scatter(x, y, c=[color], label=label, id=f"scatter_{i}")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("scatter")
    ax.legend()
    return fig, ax


# EOF
