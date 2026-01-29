#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fill_betweenx: horizontal filled area demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_fill_betweenx(plt, rng, ax=None):
    """Horizontal filled area demo with multiple regions and legend.

    Demonstrates: ax.fill_betweenx() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    y = np.linspace(0, 10, 100)

    # Multiple horizontal filled regions with legend
    regions = [
        ("Region A", np.sin(y), 0.5),
        ("Region B", np.sin(y) + 2, 0.3),
        ("Region C", np.sin(y) + 4, 0.4),
    ]

    for (label, base, width), color in zip(regions, colors):
        ax.fill_betweenx(
            y,
            base - width,
            base + width,
            alpha=0.5,
            label=label,
            color=color,
            id=f"fillx_{label}",
        )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("fill_betweenx")
    ax.legend()
    return fig, ax


# EOF
