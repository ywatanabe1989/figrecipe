#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""violinplot: violin plot demo."""

from matplotlib.patches import Patch

from figrecipe.styles import load_style


def plot_violinplot(plt, rng, ax=None):
    """Violin plot demo with colors for each group and legend.

    Demonstrates: ax.violinplot() with SCITEX color palette and legend
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
    labels = ["Group A", "Group B", "Group C", "Group D"]
    data = [rng.normal(i, 1, 100) for i in range(4)]

    # Modern style: show box inside (default from SCITEX style)
    # Colors are automatically applied from the color palette by the wrapper
    ax.violinplot(data, id="violinplot")

    ax.set_xlabel("Group")
    ax.set_ylabel("Value")
    ax.set_title("violinplot")

    # Create legend with color patches
    legend_handles = [
        Patch(facecolor=c, label=lbl, alpha=0.7) for c, lbl in zip(colors, labels)
    ]
    ax.legend(handles=legend_handles)
    return fig, ax


# EOF
