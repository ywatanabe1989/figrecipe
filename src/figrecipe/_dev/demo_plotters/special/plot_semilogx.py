#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""semilogx: semi-log X plot demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_semilogx(plt, rng, ax=None):
    """Semi-log X plot demo with multiple series and legend.

    Demonstrates: ax.semilogx() with SCITEX color palette and legend
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

    # Multiple log functions with legend
    series = [("log₁₀(x)", 1), ("2·log₁₀(x)", 2), ("0.5·log₁₀(x)", 0.5)]
    for (label, scale), color in zip(series, colors):
        y = scale * np.log10(x)
        ax.semilogx(x, y, label=label, color=color, id=f"semilogx_{scale}")

    ax.set_xlabel("X (log)")
    ax.set_ylabel("Y")
    ax.set_title("semilogx")
    ax.legend()
    return fig, ax


# EOF
