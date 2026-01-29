#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stairs: staircase plot demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_stairs(plt, rng, ax=None):
    """Staircase plot demo with legend.

    Demonstrates: ax.stairs() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    edges = np.arange(11)

    # Multiple staircase series with legend
    series = [("Series A", 0), ("Series B", 2), ("Series C", 4)]
    for (label, offset), color in zip(series, colors):
        values = rng.uniform(1, 5, 10) + offset
        ax.stairs(
            values,
            edges,
            fill=True,
            alpha=0.5,
            label=label,
            color=color,
            id=f"stairs_{label}",
        )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("stairs")
    ax.legend()
    return fig, ax


# EOF
