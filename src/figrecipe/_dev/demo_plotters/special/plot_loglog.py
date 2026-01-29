#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""loglog: log-log plot demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_loglog(plt, rng, ax=None):
    """Log-log plot demo with multiple power laws and legend.

    Demonstrates: ax.loglog() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    x = np.logspace(0, 3, 50)

    # Multiple power laws with legend
    powers = [("y = x¹", 1), ("y = x²", 2), ("y = x³", 3)]
    for (label, p), color in zip(powers, colors):
        y = x**p
        ax.loglog(x, y, label=label, color=color, id=f"loglog_{p}")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("loglog")
    ax.legend()
    return fig, ax


# EOF
