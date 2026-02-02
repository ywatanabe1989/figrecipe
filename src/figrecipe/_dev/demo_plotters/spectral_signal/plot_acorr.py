#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""acorr: autocorrelation demo."""

from figrecipe.styles import load_style


def plot_acorr(plt, rng, ax=None):
    """Autocorrelation demo with legend.

    Demonstrates: ax.acorr() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    color = tuple(v / 255.0 for v in palette[0])

    x = rng.normal(0, 1, 100)
    ax.acorr(x, maxlags=50, label="Signal", color=color, id="acorr")
    ax.set_xlabel("Lag")
    ax.set_ylabel("Autocorrelation")
    ax.set_title("acorr")
    ax.legend()
    return fig, ax


# EOF
