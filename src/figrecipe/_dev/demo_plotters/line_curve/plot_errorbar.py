#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""errorbar: error bar plot demo."""

import numpy as np

from figrecipe.styles import load_style


def plot_errorbar(plt, rng, ax=None):
    """Error bar plot demo with multiple series and legend.

    Demonstrates: ax.errorbar() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    x = np.arange(5)

    # Multiple series with legend
    series = [("Control", 0), ("Treatment A", 1.5), ("Treatment B", 3)]
    for (label, offset), color in zip(series, colors):
        y = rng.uniform(2, 8, 5) + offset
        yerr = rng.uniform(0.3, 0.8, 5)
        # Cap width 0.8mm, line thickness 0.12mm (converted to points: mm * 72/25.4)
        ax.errorbar(
            x,
            y,
            yerr=yerr,
            label=label,
            color=color,
            capsize=0.8 * 72 / 25.4,  # 0.8mm
            elinewidth=0.12 * 72 / 25.4,  # 0.12mm
            capthick=0.12 * 72 / 25.4,  # 0.12mm
            id=f"errorbar_{label}",
        )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("errorbar")
    ax.legend()
    return fig, ax


# EOF
