#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fill: filled polygon demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_fill(plt, rng, ax=None):
    """Filled polygon demo with multiple shapes and legend.

    Demonstrates: ax.fill() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    # Multiple polygons with legend
    shapes = [
        ("Pentagon", 5, 0, 0),
        ("Hexagon", 6, 2.5, 0),
        ("Heptagon", 7, 1.25, 2),
    ]

    for (label, n_sides, cx, cy), color in zip(shapes, colors):
        theta = np.linspace(0, 2 * np.pi, n_sides + 1)
        x = np.cos(theta) * 0.8 + cx
        y = np.sin(theta) * 0.8 + cy
        ax.fill(x, y, alpha=0.6, label=label, color=color, id=f"fill_{label}")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("fill")
    ax.set_aspect("equal")
    ax.legend()
    return fig, ax


# EOF
