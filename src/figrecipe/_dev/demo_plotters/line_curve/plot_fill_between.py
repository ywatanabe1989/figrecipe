#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fill_between: filled area between curves demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_fill_between(plt, rng, ax=None):
    """Filled area between curves demo with multiple regions and legend.

    Demonstrates: ax.fill_between() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    x = np.linspace(0, 10, 100)

    # Multiple filled regions with legend
    regions = [
        ("Signal ± 1σ", np.sin(x), 0.5),
        ("Signal ± 2σ", np.sin(x) * 0.7 + 2, 0.3),
        ("Signal ± 3σ", np.sin(x) * 0.5 + 4, 0.2),
    ]

    for (label, base, width), color in zip(regions, colors):
        ax.fill_between(
            x,
            base - width,
            base + width,
            alpha=0.5,
            label=label,
            color=color,
            id=f"fill_{label}",
        )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("fill_between")
    ax.legend()
    return fig, ax


# EOF
