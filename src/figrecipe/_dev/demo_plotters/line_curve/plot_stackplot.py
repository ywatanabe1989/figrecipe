#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stackplot: stacked area plot demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_stackplot(plt, rng, ax=None):
    """Stacked area plot demo with legend.

    Demonstrates: ax.stackplot() with SCITEX color palette and legend
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
    y1 = rng.uniform(1, 3, 10)
    y2 = rng.uniform(1, 3, 10)
    y3 = rng.uniform(1, 3, 10)

    ax.stackplot(
        x,
        y1,
        y2,
        y3,
        labels=["Layer A", "Layer B", "Layer C"],
        colors=colors,
        id="stackplot",
    )
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("stackplot")
    ax.legend(loc="upper left")
    return fig, ax


# EOF
