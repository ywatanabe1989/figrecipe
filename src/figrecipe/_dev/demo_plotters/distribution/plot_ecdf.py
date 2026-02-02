#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ecdf: empirical CDF demo."""

from figrecipe.styles import load_style


def plot_ecdf(plt, rng, ax=None):
    """Empirical CDF demo with multiple distributions and legend.

    Demonstrates: ax.ecdf() with SCITEX color palette and legend
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
        ("Normal (μ=0)", rng.normal(0, 1, 100)),
        ("Shifted (μ=2)", rng.normal(2, 1, 100)),
        ("Wide (σ=2)", rng.normal(0, 2, 100)),
    ]

    for (label, data), color in zip(distributions, colors):
        ax.ecdf(data, label=label, color=color, id=f"ecdf_{label}")

    ax.set_xlabel("Value")
    ax.set_ylabel("Cumulative Probability")
    ax.set_title("ecdf")
    ax.legend()
    return fig, ax


# EOF
