#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stem: stem plot demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_stem(plt, rng, ax=None):
    """Stem plot demo with multiple series and legend.

    Demonstrates: ax.stem() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    x = np.arange(10)

    # Multiple stem series with legend
    # Use color kwarg (figrecipe extension) for reproducible coloring
    series = [("Signal A", 0), ("Signal B", 0.3), ("Signal C", -0.3)]
    for (label, offset), color in zip(series, colors):
        y = rng.uniform(0, 1, 10) + offset
        ax.stem(x, y, label=label, color=color, id=f"stem_{label}")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("stem")
    ax.legend()
    return fig, ax


# EOF
