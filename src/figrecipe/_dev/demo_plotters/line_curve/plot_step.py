#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""step: step plot demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_step(plt, rng, ax=None):
    """Step plot demo with multiple series and legend.

    Demonstrates: ax.step() with SCITEX color palette and legend
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

    # Multiple step series with legend
    series = [("Baseline", 0), ("Treatment", 0.3), ("Control", -0.2)]
    for (label, offset), color in zip(series, colors):
        y = rng.uniform(0, 1, 10) + offset
        ax.step(x, y, where="mid", label=label, color=color, id=f"step_{label}")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("step")
    ax.legend()
    return fig, ax


# EOF
