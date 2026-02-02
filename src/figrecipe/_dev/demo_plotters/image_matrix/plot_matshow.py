#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""matshow: matrix display demo."""


def plot_matshow(plt, rng, ax=None):
    """Matrix display demo.

    Demonstrates: ax.matshow()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    data = rng.uniform(0, 1, (10, 10))
    mat = ax.matshow(data, id="matshow")
    ax.axis("off")
    ax.set_title("matshow")
    from figrecipe._utils._colorbar import add_colorbar

    add_colorbar(fig, mat, ax=ax)
    return fig, ax


# EOF
