#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hist2d: 2D histogram demo."""


def plot_hist2d(plt, rng, ax=None):
    """2D histogram demo.

    Demonstrates: ax.hist2d()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = rng.normal(0, 1, 1000)
    y = rng.normal(0, 1, 1000)
    result = ax.hist2d(x, y, id="hist2d")
    # hist2d returns (h, xedges, yedges, im) - need im for colorbar
    im = result[-1] if isinstance(result, tuple) else result
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("hist2d")
    from figrecipe._utils._colorbar import add_colorbar

    add_colorbar(fig, im, ax=ax)
    return fig, ax


# EOF
