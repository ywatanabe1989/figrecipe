#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hist: histogram demo."""

from figrecipe.styles import load_style


def plot_hist(plt, rng, ax=None):
    """Histogram demo with multiple distributions and legend.

    Demonstrates: ax.hist() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    # Multiple distributions with legend
    distributions = [
        ("Normal", rng.normal(0, 1, 300)),
        ("Shifted", rng.normal(2, 0.8, 300)),
        ("Wide", rng.normal(-1, 1.5, 300)),
    ]

    for (label, data), color in zip(distributions, colors):
        ax.hist(data, bins=20, alpha=0.6, label=label, color=color, id=f"hist_{label}")

    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    ax.set_title("hist")
    ax.legend()
    return fig, ax


# EOF
