#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""semilogy: semi-log Y plot demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_semilogy(plt, rng, ax=None):
    """Semi-log Y plot demo with multiple exponentials and legend.

    Demonstrates: ax.semilogy() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    x = np.linspace(0, 5, 50)

    # Multiple exponentials with legend
    series = [("e^x", 1), ("e^(2x)", 2), ("e^(0.5x)", 0.5)]
    for (label, scale), color in zip(series, colors):
        y = np.exp(scale * x)
        ax.semilogy(x, y, label=label, color=color, id=f"semilogy_{scale}")

    ax.set_xlabel("X")
    ax.set_ylabel("Y (log)")
    ax.set_title("semilogy")
    ax.legend()
    return fig, ax


# EOF
